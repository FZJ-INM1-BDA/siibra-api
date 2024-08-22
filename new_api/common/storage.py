from new_api.siibra_api_config import SIIBRA_API_SHARED_DIR
import hashlib
import os
from typing import List

def get_filename(*args: List[str], ext:str=None) -> str:
    """Get a hashed filename based on positional arguments.

    Will also honor `SIIBRA_API_SHARED_DIR` in config, if defined.
    
    Args:
        args: positional arguments
        ext: extension
    
    Returns:
        hashed path, in the form of `{SIIBRA_API_SHARED_DIR}/{hash(*args)} + ('.{ext}' if ext else '')`
    """
    assert all(isinstance(arg, str) for arg in args), f"all args to get_filename must be str"
    return os.path.join(SIIBRA_API_SHARED_DIR, hashlib.md5("".join(args).encode("utf-8")).hexdigest() + (f".{ext.lstrip('.')}") if ext else "")
