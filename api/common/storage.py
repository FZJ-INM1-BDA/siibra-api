from api.siibra_api_config import SIIBRA_API_SHARED_DIR
import hashlib
import os

def get_filename(*args, ext:str=None):
    assert all(isinstance(arg, str) for arg in args), f"all args to get_filename must be str"
    return os.path.join(SIIBRA_API_SHARED_DIR, hashlib.md5("".join(args).encode("utf-8")).hexdigest() + (f".{ext.lstrip('.')}") if ext else "")
