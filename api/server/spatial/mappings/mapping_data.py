from .const import Mapping, MappingAlias, WfEnum, NUTIL_PARAM_KEY, NutilParam
from api.common.logger import logger as general_logger

alias = [
    MappingAlias(
        from_key="d-019f935b-9b63-4f59-98c0-a49e035eb426",
        to_key="doi.org/10.25493/19ED-N2A",
    ),
    MappingAlias(
        from_key="019f935b-9b63-4f59-98c0-a49e035eb426",
        to_key="doi.org/10.25493/19ED-N2A",
    ),
    
    MappingAlias(
        from_key="c25f0a96-cdf0-4277-ba3c-495de13f3ccd",
        to_key="doi.org/10.25493/BT8X-FN9",
    ),
    
    MappingAlias(
        from_key="73c1fa55-d099-4854-8cda-c9a403c6080a",
        to_key="doi.org/10.25493/JWTF-PAB",
    ),

    MappingAlias(
        from_key="494818fa-9126-4432-a167-52ff02534a8b",
        to_key="doi.org/10.25493/Y7J0-8S9",
    )
]

# since paths will be exposed to the frontend, will be easier if the path matches that in the bucket
lsfm_paths = [
    "derivatives/sub-PV27/sub-PV27_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-PV28/sub-PV28_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-PV29/sub-PV29_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-PV30/sub-PV30_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-PV31/sub-PV31_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-SST38/sub-SST38_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-SST40/sub-SST40_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-SST42/sub-SST42_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-VIP17/sub-VIP17_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-VIP21/sub-VIP21_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-VIP22/sub-VIP22_space-CCFv3_desc-cellCentroids_coords.tsv",
    "derivatives/sub-VIP37/sub-VIP37_space-CCFv3_desc-cellCentroids_coords.tsv",
]


def _extract_sub(p: str):
    _, sub, *_ = p.split("/")
    return sub


mapping_list = [
    Mapping(
        uuid="doi.org/10.25493/19ED-N2A",
        base="https://data-proxy.ebrains.eu/api/v1/buckets/d-019f935b-9b63-4f59-98c0-a49e035eb426/",
        paths=lsfm_paths,
        path_alias={_extract_sub(p): p for p in lsfm_paths},
        use_wf={
            "default": WfEnum.TSV
        }
    ),
    Mapping(
        uuid="doi.org/10.25493/BT8X-FN9",
        base="https://data-proxy.ebrains.eu/api/v1/buckets/p4791e-ext-d000033_PVMouseExtraction_pub/",
        paths=[
            "Nutil_Quantifier_analysis/81264/Output_dir/Coordinates/3D_combined.json",
            "Nutil_Quantifier_analysis/81265/Output_dir_brainstem/Coordinates/3D_combined.json",
            "Nutil_Quantifier_analysis/81265/Output_dir/Coordinates/3D_combined.json",
            "Nutil_Quantifier_analysis/81266/Output_dir/Coordinates/3D_combined.json",
            "Nutil_Quantifier_analysis/81267/Output_dir_colliculi/Coordinates/3D_combined.json",
            "Nutil_Quantifier_analysis/81267/Output_dir/Coordinates/3D_combined.json",
        ],
        path_alias={
            "81264": "Nutil_Quantifier_analysis/81264/Output_dir/Coordinates/3D_combined.json",
            "81265_brainstem": "Nutil_Quantifier_analysis/81265/Output_dir_brainstem/Coordinates/3D_combined.json",
            "81265": "Nutil_Quantifier_analysis/81265/Output_dir/Coordinates/3D_combined.json",
            "81266": "Nutil_Quantifier_analysis/81266/Output_dir/Coordinates/3D_combined.json",
            "81267_colliculi": "Nutil_Quantifier_analysis/81267/Output_dir_colliculi/Coordinates/3D_combined.json",
            "81267": "Nutil_Quantifier_analysis/81267/Output_dir/Coordinates/3D_combined.json",
        },
        use_wf={
            "default": WfEnum.NUTIL_JSON,
            NUTIL_PARAM_KEY: NutilParam(space="waxholm")
        }
    ),
    
    Mapping(
        uuid="doi.org/10.25493/JWTF-PAB",
        base="https://data-proxy.ebrains.eu/api/v1/buckets/reference-atlas-data/temp/",
        paths=[
            "geomsvc-data/B20_7300.centroids.tsv",
        ],
        path_alias={
            "94c92ffa642b3cf4eb2c2f39f3baf16f": "geomsvc-data/B20_7300.centroids.tsv",
        },
        use_wf={
            "default": WfEnum.TSV,
        }
    ),
    
    Mapping(
        uuid="10.25493/Y7J0-8S9",
        base="https://data.kg.ebrains.eu/zip?container=https://data-proxy.ebrains.eu/api/v1/buckets/d-494818fa-9126-4432-a167-52ff02534a8b?prefix=",
        paths=[
            "sub-chenonceau/derivatives/sub-chenonceau_space-MNI152NLin2009cAsym_model-global-tractography_desc-deep-white-matter-atlas.trx",
        ],
        path_alias={
            "icbm152": "sub-chenonceau/derivatives/sub-chenonceau_space-MNI152NLin2009cAsym_model-global-tractography_desc-deep-white-matter-atlas.trx",
        },
        use_wf={
            "default": WfEnum.TRX_ZIP,
        }
    ),
]

# https://data.kg.ebrains.eu/zip?container=https://data-proxy.ebrains.eu/api/v1/buckets/d-494818fa-9126-4432-a167-52ff02534a8b?prefix=sub-chenonceau/derivatives/sub-chenonceau_space-MNI152NLin2009cAsym_model-global-tractography_desc-deep-white-matter-atlas.trx

uuid_to_mapping: dict[str, Mapping] = {m.uuid: m for m in mapping_list}

for a in alias:
    if resolved_mapping := uuid_to_mapping.get(a.to_key):
        uuid_to_mapping[a.from_key] = resolved_mapping



# breaks data proxy
# https://data-proxy.ebrains.eu/reference-atlas-data?prefix=geomsvc%2Fv0%2Fdoi.org%2F10.25493%2FBT8X-FN9%2FNutil_Quantifier_analysis%2F81264%2F