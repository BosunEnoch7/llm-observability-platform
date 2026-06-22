from prometheus_client import Counter, Gauge, Histogram, Info

HTTP_REQUESTS = Counter(
    "llm_http_requests_total",
    "Total HTTP requests handled by the service.",
    ("method", "route", "status_code"),
)

HTTP_REQUEST_DURATION = Histogram(
    "llm_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

INFERENCE_REQUESTS = Counter(
    "llm_inference_requests_total",
    "Total LLM inference attempts.",
    ("model", "outcome"),
)

PROVIDER_ATTEMPTS = Counter(
    "llm_provider_attempts_total",
    "Total provider call attempts, including retries.",
    ("provider", "outcome"),
)

PROVIDER_RETRIES = Counter(
    "llm_provider_retries_total",
    "Total provider retries.",
    ("provider",),
)

INFERENCE_DURATION = Histogram(
    "llm_inference_duration_seconds",
    "LLM inference duration in seconds.",
    ("model",),
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)

TOKENS = Counter(
    "llm_tokens_total",
    "Estimated tokens consumed.",
    ("model", "direction"),
)

ESTIMATED_COST = Counter(
    "llm_estimated_cost_usd_total",
    "Estimated cumulative inference cost in US dollars.",
    ("model",),
)

SERVICE_READY = Gauge(
    "llm_service_ready",
    "Whether the service is ready to receive traffic.",
)

SERVICE_INFO = Info(
    "llm_service",
    "Static service build and environment information.",
)

PROMPT_VERSION_REQUESTS = Counter(
    "llm_prompt_version_requests_total",
    "Inference requests by operator-controlled prompt version.",
    ("model", "prompt_version"),
)

SAFETY_EVALUATIONS = Counter(
    "llm_safety_evaluations_total",
    "Total local safety evaluations.",
    ("stage", "outcome"),
)

SAFETY_EVENTS = Counter(
    "llm_safety_events_total",
    "Categorized safety findings and actions.",
    ("stage", "category", "action"),
)

QUALITY_RATING = Histogram(
    "llm_quality_rating",
    "User-submitted response quality rating from one to five.",
    ("category",),
    buckets=(1, 2, 3, 4, 5),
)

FEEDBACK = Counter(
    "llm_feedback_total",
    "Aggregate user feedback by sentiment and category.",
    ("sentiment", "category"),
)
