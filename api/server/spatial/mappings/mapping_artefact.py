from dataclasses import dataclass
from enum import StrEnum, auto
from functools import cached_property
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import json

from ebrains_drive import BucketApiClient
from ebrains_drive.bucket import Bucket
from ebrains_drive.exceptions import DoesNotExist
from ebrains_iam.client_credential import ClientCredentialsSession
import requests
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException

from .const import (
    GEOMSVC_MAPPING_DATAPROXY_BASEURL,
    GEOMSVC_MAPPING_BUCKET_NAME,
    GEOMSVC_MAPPING_BUCKET_PATH,
    GEOMSVC_MAPPING_BUCKET_PROGRESS,
    GEOMSVC_SCHEMA_NS,
    WfEnum,
    NUTIL_PARAM_KEY,
    NutilParam,
    MetaResp,
    get_ts,
    MAPPING_TASKNAME_GEOMSVC_DATUM_FN,
    DATUM_FMT_KEY,
)
from .mapping_data import uuid_to_mapping
from .lock import lock_key
from api.siibra_api_config import SIIBRA_API_SA_CLIENTID, SIIBRA_API_SA_CLIENTSECRET, SIIBRA_API_INGSVC_URL
from api.common.logger import logger as general_logger


def check_dataproxy_health() -> bool:
    """Return True when the data-proxy backing the mapping bucket is reachable.

    When the proxy is down it can answer with a 404-like response that is
    indistinguishable from a genuinely-absent artefact, which would make every
    request fall through and spawn the ingestion service. Callers must treat a
    False return as "infra down" and respond 503 rather than build anything.

    """
    bb_saneurl = "https://data-proxy.ebrains.eu/api/v1/buckets/interactive-atlas-viewer/saneUrl/bigbrain.json"
    resp = requests.get(bb_saneurl, timeout=5)
    try:
        resp.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        return False


class ArtefactEnum(StrEnum):
    ABSENT = auto()
    PRESENT = auto()
    PENDING = auto()
    RUNNING = auto()
    ERROR = auto()

    def to_msg(self):
        return f"workflow::{self}"


def _get_massage_wf(bucketname: str, destprefix: str, payload: dict):
    return {
        "name": "massage_metadata",
        "io_bucketname": bucketname,
        "io_destprefix": destprefix,
        "param_merge_dict": payload,
    }


@dataclass
class MappingArtefact:
    uuid: str
    artefact: str

    @cached_property
    def _resolved_mapping(self):
        mapping_val = uuid_to_mapping[self.uuid]

        if resolved_artefact := mapping_val.path_alias_mapping.get(self.artefact):
            self.artefact = resolved_artefact
        assert self.artefact in mapping_val.paths, f"{self.artefact} not in mapping_obj"
        return mapping_val

    @property
    def src_url(self):
        return f"{self._resolved_mapping.base}{self.artefact}"

    @property
    def wf_name(self):
        defaultwf = self._resolved_mapping.use_wf.get("default")
        return self._resolved_mapping.use_wf.get(self.artefact) or defaultwf

    @property
    def bucketpath_base(self):
        return (
            f"{GEOMSVC_MAPPING_BUCKET_PATH.rstrip('/')}/"
            f"{self._resolved_mapping.uuid}/{self.artefact}"
        )

    @property
    def bucketpath_prog(self):
        return f"{self.bucketpath_base}/{GEOMSVC_MAPPING_BUCKET_PROGRESS}"

    @property
    def geomsvc_metafname(self):
        return self.bucketpath_base.rstrip("/") + "/meta.json"

    def get_artefact_urls(
        self, refresh=False, background_tasks: BackgroundTasks = None
    ) -> MetaResp:
        # 1. check if ingested sample already exist
        # 2a. if exist, return ingested URLs
        # 2b. if does not exist:
        # 2b1. get workflows
        # 2b2. return workflows
        # 2b3. (in background) start workflows
        # 2b4. (in background) write ingested log

        # n.b. gate on data-proxy health up front: an unhealthy proxy can
        # return a 404-like response that is indistinguishable from a
        # genuinely-absent artefact, which would make every request fall
        # through and spawn the ingestion service. Fail fast with 503 instead
        # of returning URLs we can neither serve nor build.
        if not check_dataproxy_health():
            raise HTTPException(
                status_code=503,
                detail="data-proxy is unavailable; cannot serve or build artefacts",
            )

        ro_client = BucketApiClient()
        ro_bucket = Bucket(ro_client, GEOMSVC_MAPPING_BUCKET_NAME, None, None)

        if not refresh:
            try:
                f = ro_bucket.get_file(self.geomsvc_metafname)
                general_logger.info(f"{self.uuid} :: {self.artefact} already present.")
                return json.loads(f.get_content().decode())
            except DoesNotExist:
                ...

        if not SIIBRA_API_SA_CLIENTID or not SIIBRA_API_SA_CLIENTSECRET:
            raise RuntimeError(
                "SIIBRA_API_SA_CLIENTID / SIIBRA_API_SA_CLIENTSECRET not provided, cannot execute workflow"
            )

        if not SIIBRA_API_INGSVC_URL:
            raise RuntimeError("SIIBRA_API_INGSVC_URL not defined, cannot run workflow")

        wfs = self.get_workflows()
        baseurl = f"{GEOMSVC_MAPPING_DATAPROXY_BASEURL}/buckets/{GEOMSVC_MAPPING_BUCKET_NAME}"

        urls = [
            f"{baseurl}/{prefix}"
            for wf in wfs
            if (prefix := wf.get("output_destprefix"))
        ]

        meta_log_fname = f"{self.geomsvc_metafname}.log"

        payload = {
            "version": "2.0",
            GEOMSVC_SCHEMA_NS: {
                "ingArtfactsUrls": urls,
                "ingArtfactsUrls.log": f"{baseurl}/{meta_log_fname}",
            },
        }

        def _exec_mut_ops():
            def helper_fn(fn, *args):
                return fn(*args)

            def append_geom_meta_log(msg: str, *args):
                try:
                    current_content = (
                        writable_bucket.get_file(meta_log_fname).get_content().decode()
                    )
                except DoesNotExist:
                    current_content = ""

                current_content += f"[{get_ts()}] {msg}\n"
                bio = BytesIO(current_content.encode())
                bio.seek(0)
                writable_bucket.upload(bio, meta_log_fname)

            def write_geom_meta(*args):
                bio = BytesIO(json.dumps(payload).encode())
                bio.seek(0)
                writable_bucket.upload(bio, self.geomsvc_metafname)

            reqsess = requests.Session()

            def trigger_tasks(wf, *args):
                resp = reqsess.post(
                    SIIBRA_API_INGSVC_URL.rstrip("/") + "/workflow",
                    json={"workflow_spec": wf},
                    headers={"Authorization": f"Bearer {token}"},
                )
                resp.raise_for_status()

            sess = ClientCredentialsSession(
                client_id=SIIBRA_API_SA_CLIENTID,
                client_secret=SIIBRA_API_SA_CLIENTSECRET,
                scope=["team"],
            )

            token = sess.get_token()
            writable_client = BucketApiClient(token=token)
            writable_bucket = Bucket(
                writable_client, GEOMSVC_MAPPING_BUCKET_NAME, None, None
            )

            with ThreadPoolExecutor() as ex:
                list(
                    ex.map(
                        helper_fn,
                        [append_geom_meta_log, write_geom_meta],
                        ["trigger artefact build", None],
                    )
                )

            meta_wfs = [
                _get_massage_wf(
                    bucketname,
                    destprefix,
                    {
                        "https://schema.brainatlas.eu/apps.ebrains.eu/geom-svc/datum": datum
                    },
                )
                for wf in wfs
                if (
                    (destprefix := wf.get("output_destprefix"))
                    and isinstance(destprefix, str)
                    and (bucketname := wf.get("output_bucketname"))
                    and isinstance(bucketname, str)
                    and (fn := MAPPING_TASKNAME_GEOMSVC_DATUM_FN.get(wf.get("name")))
                    and (datum := fn(
                        **self._resolved_mapping.use_wf.get(DATUM_FMT_KEY, {})
                    ))
                    and isinstance(datum, dict)
                )
            ]
            with ThreadPoolExecutor() as ex:
                list(ex.map(trigger_tasks, [*wfs, *meta_wfs]))

        def longtask():
            # n.b. per-artefact lock (keyed on the meta.json path, never
            # global) so concurrent requests/replicas for the same artefact
            # don't each trigger the ingestion service. See mappings.lock for
            # the redis-vs-threading backend selection.
            with lock_key(self.geomsvc_metafname) as acquired:
                if not acquired:
                    general_logger.info("Another worker got task")
                    # another worker already owns this build.
                    return

                # double-checked locking: a concurrent request may have written
                # meta.json between the existence check above and us acquiring
                # the lock, so re-check before triggering the ingestion service.
                try:
                    ro_bucket.get_file(self.geomsvc_metafname)
                    general_logger.info("Request already placed")
                    return
                except DoesNotExist:
                    ...
                _exec_mut_ops()

        if background_tasks:
            background_tasks.add_task(longtask)
        else:
            longtask()

        return payload

    def get_workflows(self) -> list[dict]:
        match self.wf_name:
            case WfEnum.TSV:
                return [
                    {
                        "name": "tsv_to_ngp",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/kde/",
                        "param_delimiter": "\t",
                        "param_voxel_size_mm": 0.025,
                        "param_bandwidth_vox": 1,
                    },
                    {
                        "name": "tsv_to_rtree",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/rtree/",
                        "param_delimiter": "\t",
                    },
                    {
                        "name": "tsv_to_multires",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/multires/",
                        "param_delimiter": "\t",
                    },
                ]
            case WfEnum.NUTIL_JSON:
                nutil_param: NutilParam = self._resolved_mapping.use_wf.get(
                    NUTIL_PARAM_KEY
                )
                param_space = nutil_param.get("space")
                if param_space is None:
                    raise RuntimeError(
                        f"malformed mapping. NUTIL_PARAM_KEY must be defined for the mapping"
                    )
                match param_space:
                    case "allenccfv3":
                        param_voxel_size_mm = 0.025
                    case "waxholm":
                        param_voxel_size_mm = 0.039
                    case _:
                        param_voxel_size_mm = 0.01
                return [
                    {
                        "name": "nutil_json_to_ngp",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/kde/",
                        "param_space": param_space,
                        "param_voxel_size_mm": param_voxel_size_mm,
                        "param_bandwidth_vox": 5,
                    },
                    {
                        "name": "nutil_json_to_rtree",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/rtree/",
                        "param_space": param_space,
                    },
                    {
                        "name": "nutil_json_to_multires",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/multires/",
                        "param_space": param_space,
                    },
                    {
                        "name": "nutil_json_to_tsv",
                        "input_public_url": self.src_url,
                        "output_bucketname": GEOMSVC_MAPPING_BUCKET_NAME,
                        "output_destprefix": f"{self.bucketpath_base}/tsv/",
                        "param_space": param_space,
                    },
                ]
            case _:
                raise FileNotFoundError(
                    f"mapping not properly configured! it needs at least a default value!"
                )
