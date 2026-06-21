from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.inference import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/v1", tags=["inference"])


def get_llm_service(config: Settings = Depends(get_settings)) -> LLMService:
    return LLMService(config)


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: LLMService = Depends(get_llm_service),
) -> GenerateResponse:
    return await service.generate(request)
