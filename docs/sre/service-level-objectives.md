# Service-level objectives

## Availability SLO

The generation API targets **99% successful requests over a rolling 30-day
window**. The initial service-level indicator treats HTTP 5xx responses from
`/v1/generate` as bad events and all responses on that route as total events.

```text
availability = 1 - (5xx generation requests / all generation requests)
error budget = 1 - 0.99 = 1%
burn rate = observed error ratio / 0.01
```

Client-side 4xx responses do not consume this availability budget because they
do not indicate a service failure. Separate product or correctness objectives
can be added when real LLM quality evaluation is available.

## Alert strategy

The fast-burn alert pairs 5-minute and 1-hour windows at 14.4x budget burn. The
slow-burn alert pairs 30-minute and 6-hour windows at 6x. Requiring both windows
reduces transient noise while retaining fast detection of sustained incidents.

The dashboard uses short-window recording rules for immediate operations.
Long-term SLO reporting will use Azure managed Prometheus retention or a durable
metrics backend when the cloud phase begins.
