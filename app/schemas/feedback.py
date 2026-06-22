from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    inference_id: UUID
    rating: int = Field(ge=1, le=5)
    helpful: bool
    category: Literal["accuracy", "relevance", "safety", "latency", "other"] = "other"


class FeedbackResponse(BaseModel):
    status: Literal["recorded"] = "recorded"
