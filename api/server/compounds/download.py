from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.exceptions import HTTPException
from fastapi_versioning import version
from pathlib import Path
import os

from api.server.util import SapiCustomRoute
from api.server import FASTAPI_VERSION
from api.common import router_decorator
from api.siibra_api_config import ROLE
from api.common.data_handlers.compounds.download import download_all
from api.models._commons import TaskIdResp

router = APIRouter(route_class=SapiCustomRoute, tags=["download"])
"""HTTP download bundle router"""

def cleanup(filepath: Path):
    """On downloaded callback
    
    Args:
        filepath: Path to cleanup"""
    filepath.unlink()

@router.get("")
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=download_all, queue_as_async=(ROLE=="server"))
def get_download_bundle(space_id: str, parcellation_id: str, region_id: str=None, feature_id: str=None, *, background: BackgroundTasks, func):
    """Prepare the bundle. Given a specification, prepare/bundle according to the specification."""
    returnval = func(space_id=space_id, parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id)
    try:
        path_to_file = Path(returnval)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    else:
        # TODO returning different shape is kind of ugly
        # fix in next version
        if path_to_file.exists() and path_to_file.is_file():
            
            background.add_task(cleanup, path_to_file)

            headers={
                "content-type": "application/octet-stream",
                "content-disposition": f'attachment; filename="{path_to_file.name}"'
            }
            return FileResponse(returnval, headers=headers)
        return TaskIdResp(task_id=returnval)

if ROLE == "server":
    @router.get("/{task_id:str}")
    @version(*FASTAPI_VERSION)
    def get_download_progress(task_id:str):
        """Get download task progress with task_id"""
        res = download_all.AsyncResult(task_id)
        if res.state == "FAILURE":
            result = res.get()
            res.forget()
            raise HTTPException(500, detail=str(result))
        if res.state == "SUCCESS":
            return TaskIdResp(task_id=task_id, status="SUCCESS")
        # no result yet
        return TaskIdResp(task_id=task_id, status="PENDING")


    @router.get("/{task_id:str}/download")
    @version(*FASTAPI_VERSION)
    def get_download_result(task_id:str, background: BackgroundTasks):
        """Download the bundle"""
        res = download_all.AsyncResult(task_id)
        
        if res.state == "FAILURE":
            result = res.get()
            res.forget()
            raise HTTPException(500, detail=str(result))
        if res.state == "SUCCESS":
            result = res.get()
            res.forget()
            
            path_to_file = Path(result)
            if path_to_file.exists() and path_to_file.is_file():

                background.add_task(cleanup, path_to_file)

                headers={
                    "content-type": "application/octet-stream",
                    "content-disposition": f'attachment; filename="{path_to_file.name}"'
                }
                return FileResponse(result, headers=headers)
            else:
                raise HTTPException(500, detail=f"file {path_to_file} not found!")
            
        # no result yet
        raise HTTPException(404,detail=f"Not found {task_id}")
