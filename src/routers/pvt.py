from fastapi import APIRouter, Body
from schemas import PvtResponse, PvtRequest
from controllers import pvt as pvt_controller

router = APIRouter(prefix="/pvt", tags=["pvt_service"])


@router.post("", response_model=PvtResponse)
async def calculate_pvt_data(
    pvt_data: PvtRequest = Body(...),
):
    """
    Вычисляет параметры расхода, плотности и вязкости смеси
    """
    return await pvt_controller.calculate_pvt_data(pvt_data=pvt_data)
