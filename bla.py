feature_types = [
    ((), "FunctionalConnectivity",)
    ((), "ReceptorDensityFingerprint",)
    ((), "ReceptorDensityProfile",)
    ((), "MRIVolumeOfInterest",)
    ((), "BlockfaceVolumeOfInterest",)
    ((), "RegionalBOLD",)
    ((), "PLIVolumeOfInterest",)
    ((), "DTIVolumeOfInterest",)
    ((), "TracingConnectivity",)
    ((), "StreamlineLengths",)
    ((), "StreamlineCounts",)
    ((), "AnatomoFunctionalConnectivity",)
]

import os
from subprocess import run
MONITOR_FIRSTLVL_DIR = os.getenv("MONITOR_FIRSTLVL_DIR")
dirs = os.listdir(MONITOR_FIRSTLVL_DIR)
for dir in dirs:
    result = run(["du", "-s", f"{MONITOR_FIRSTLVL_DIR}/{dir}"], capture_output=True, text=True)
    size_b, *_ = result.stdout.split("\t")
    print(size_b)
    print("dir", size_b, int(size_b))