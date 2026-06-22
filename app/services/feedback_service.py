from app.observability.metrics import FEEDBACK, QUALITY_RATING
from app.schemas.feedback import FeedbackRequest, FeedbackResponse


class FeedbackService:
    def record(self, feedback: FeedbackRequest) -> FeedbackResponse:
        sentiment = "positive" if feedback.helpful else "negative"
        QUALITY_RATING.labels(category=feedback.category).observe(feedback.rating)
        FEEDBACK.labels(sentiment=sentiment, category=feedback.category).inc()
        return FeedbackResponse()
