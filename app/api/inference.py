from functools import lru_cache

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.schemas.inference import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/v1", tags=["inference"])


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService(settings)


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: LLMService = Depends(get_llm_service),
) -> GenerateResponse:
    return await service.generate(request)
