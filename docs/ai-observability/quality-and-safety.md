# Quality and safety observability

Traditional reliability metrics cannot determine whether an HTTP 200 response
was useful or appropriate. This project therefore adds two deliberately bounded
signal families: explicit user feedback and categorized safety findings.

## Quality feedback

`POST /v1/feedback` accepts an inference UUID, a one-to-five rating, a helpful
flag, and a fixed category. Prometheus receives only aggregate rating,
sentiment, and category metrics. The inference UUID is never a metric label.

The local endpoint does not provide durable feedback storage or verify that an
inference UUID exists. In Azure, detailed events should be authenticated and
sent to a durable, access-controlled analytics path such as Service Bus plus
Data Explorer or another approved store. Prometheus remains the aggregate
operational view.

## Safety signals

The built-in evaluator recognizes a tiny deterministic ruleset so monitor and
enforce behavior can be tested locally. It is not a production content-safety
system and must not be presented as one. The modes are:

- `disabled`: no local evaluation or safety metrics;
- `monitor`: emit categorized findings and continue inference;
- `enforce`: return HTTP 422 when input or output findings occur.

Prompts and responses are never included in labels, spans, or ordinary logs.
Production Azure deployment should integrate an approved content-safety service,
policy governance, durable audit events, access control, and human escalation.

## Prompt versions

`PROMPT_VERSION` is operator-controlled configuration and is safe as a bounded
metric label when release values follow a managed naming policy. Arbitrary user
values must never be accepted as prompt-version labels.
