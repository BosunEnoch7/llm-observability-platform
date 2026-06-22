from functools import lru_cache

from fastapi import APIRouter, Depends, status

from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/v1", tags=["feedback"])


@lru_cache
def get_feedback_service() -> FeedbackService:
    return FeedbackService()


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def record_feedback(
    feedback: FeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> FeedbackResponse:
    return service.record(feedback)
