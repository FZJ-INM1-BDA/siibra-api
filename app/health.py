from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get('/health')
def get_all_parcellations():
    return JSONResponse(
        status_code=200,
        content={'health': 'UP'}
    )
