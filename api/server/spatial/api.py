import json
from enum import StrEnum

import requests
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi_pagination import Page, paginate

from api.siibra_api_config import (
    SIIBRA_API_GEOMSVC_ENDPOINT,
    SIIBRA_API_SPATIAL_BACKEND,
)
from .models import (
    GeomSvcModel,
    SpatialBackendPostModel,
    SpatialBackendRespModel,
    SpatialBackendMultiRespModel,
    GeomSvcArtefactStatus,
    GeomSvcArtefactEnum,
)

router = APIRouter(tags=["spatial"])


class SpaceIDS(StrEnum):
    MNI152 = "minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2"
    COLIN27 = "minds/core/referencespace/v1.0.0/7f39f7be-445b-47c0-9791-e971c0b6d992"
    BIGBRAIN = "minds/core/referencespace/v1.0.0/a1655b99-82f1-420f-a3c2-fe80fd4c8588"
    MARMOSET = "nencki/nm/referencespace/v1.0.0/MARMOSET_NM_NISSL_2020"
    MEBRAINS = "minds/core/referencespace/v1.0.0/MEBRAINS"
    ALLENCCFV3 = "minds/core/referencespace/v1.0.0/265d32a0-3d84-40a5-926f-bf89f68212b9"
    WAXHOLM = "minds/core/referencespace/v1.0.0/d5717c4a-0fa1-46e6-918c-b8003069ade8"


_space_id_spatial_enum = {
    SpaceIDS.MNI152: "MNI 152 ICBM 2009c Nonlinear Asymmetric",
    SpaceIDS.COLIN27: "MNI Colin 27",
    SpaceIDS.BIGBRAIN: "Big Brain (Histology)",
}


@router.get("/transform")
def transform(
    from_space_id: str, to_space_id: str, x: float, y: float, z: float
) -> SpatialBackendRespModel:
    url = f"{SIIBRA_API_SPATIAL_BACKEND}/v1/transform-point"
    if (source_space := _space_id_spatial_enum.get(from_space_id)) and (
        target_space := _space_id_spatial_enum.get(to_space_id)
    ):
        resp = requests.get(
            url,
            params={
                "source_space": source_space,
                "target_space": target_space,
                "x": x,
                "y": y,
                "z": z,
            },
        )
        resp.raise_for_status()
        return resp.json()
    raise HTTPException(400, detail="from_space_id or to_space_id")


@router.post("/transform")
def transform_multi(body: SpatialBackendPostModel) -> SpatialBackendMultiRespModel:
    from_space_id, to_space_id, source_points = (
        body["from_space_id"],
        body["to_space_id"],
        body["from_points"],
    )
    url = f"{SIIBRA_API_SPATIAL_BACKEND}/v1/transform-points"
    if (source_space := _space_id_spatial_enum.get(from_space_id)) and (
        target_space := _space_id_spatial_enum.get(to_space_id)
    ):
        resp = requests.post(
            url,
            json={
                "source_space": source_space,
                "target_space": target_space,
                "source_points": source_points,
            },
        )
        resp.raise_for_status()
        return resp.json()
    raise HTTPException(400, detail="from_space_id or to_space_id")


_space_id_enum = {
    SpaceIDS.WAXHOLM: "waxholm_rat",
    SpaceIDS.ALLENCCFV3: "allenccf_v3",
    SpaceIDS.MNI152: "icbm152_nonlin_asym_2009c",
    SpaceIDS.BIGBRAIN: "bigbrain",
    SpaceIDS.MARMOSET: "marmoset",
    SpaceIDS.MEBRAINS: "mebrains",
}


def _iter_all(url: str, params: dict = None):
    sess = requests.Session()
    size = 50
    page = 1
    while True:
        resp = sess.get(
            url,
            params={
                **(params or {}),
                "page": page,
                "size": size,
            },
        )
        resp.raise_for_status()
        items: list = resp.json()["items"]
        if len(items) == 0:
            break
        yield from items
        page += 1


@router.get("/features")
def features(space_id: str, bbox: str) -> Page[GeomSvcModel]:
    loaded_bbox = json.loads(bbox)
    bbox_min = ",".join([str(v) for v in loaded_bbox[0]])
    bbox_max = ",".join([str(v) for v in loaded_bbox[1]])

    if space_enum := _space_id_enum.get(space_id):
        url = f"{SIIBRA_API_GEOMSVC_ENDPOINT}/spaces/{space_enum}"

        result = _iter_all(
            url,
            params={
                "space": space_enum,
                "bbox_min": bbox_min,
                "bbox_max": bbox_max,
            },
        )
        return paginate(list(result))
        # https://geom-svc.apps.ebrains.eu/spaces/bigbrain?bbox_min=-100%2C-100%2C-100&bbox_max=100%2C100%2C100&page=1&size=50
    else:
        return paginate([])


@router.get("/geometry/{uuid:path}")
def geometries(uuid: str) -> GeomSvcArtefactStatus:
    if "--" not in uuid:
        raise HTTPException(404)
    mapping_uuid, mapping_artefact = uuid.split("--", maxsplit=1)
    url = f"{SIIBRA_API_GEOMSVC_ENDPOINT}/mapping/{mapping_uuid}/artefacts/{mapping_artefact}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp_json: GeomSvcArtefactStatus = resp.json()
        if resp_json["status"] != GeomSvcArtefactEnum.ABSENT:
            return resp.json()
        resp = requests.post(url)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(e.response.status_code) from e
