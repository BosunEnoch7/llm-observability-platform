import argparse
import asyncio
import math
import sys
import time
from collections import Counter

import httpx


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * quantile) - 1)
    return ordered[index]


async def run_load(target: str, duration: float, concurrency: int) -> int:
    deadline = time.monotonic() + duration
    latencies_ms: list[float] = []
    statuses: Counter[str] = Counter()
    limits = httpx.Limits(
        max_connections=concurrency, max_keepalive_connections=concurrency
    )

    async with httpx.AsyncClient(timeout=35, limits=limits) as client:

        async def worker(worker_id: int) -> None:
            while time.monotonic() < deadline:
                started = time.perf_counter()
                try:
                    response = await client.post(
                        target,
                        json={
                            "prompt": f"Observability load-test request {worker_id}",
                            "max_tokens": 64,
                        },
                    )
                    statuses[str(response.status_code)] += 1
                except httpx.HTTPError:
                    statuses["transport_error"] += 1
                finally:
                    latencies_ms.append((time.perf_counter() - started) * 1000)

        await asyncio.gather(*(worker(worker_id) for worker_id in range(concurrency)))

    total = sum(statuses.values())
    throughput = total / duration if duration else 0
    print(f"requests={total} throughput_rps={throughput:.2f}")
    print(f"statuses={dict(sorted(statuses.items()))}")
    print(
        f"latency_ms p50={percentile(latencies_ms, 0.50):.2f} "
        f"p95={percentile(latencies_ms, 0.95):.2f} "
        f"p99={percentile(latencies_ms, 0.99):.2f}"
    )
    return 1 if statuses["transport_error"] else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate controlled LLM API load.")
    parser.add_argument(
        "--target",
        default="http://localhost:8000/v1/generate",
        help="Generation endpoint URL.",
    )
    parser.add_argument(
        "--duration", type=float, default=30, help="Duration in seconds."
    )
    parser.add_argument(
        "--concurrency", type=int, default=5, help="Concurrent workers."
    )
    args = parser.parse_args()
    if args.duration <= 0 or args.concurrency <= 0:
        parser.error("duration and concurrency must be positive")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    sys.exit(
        asyncio.run(
            run_load(arguments.target, arguments.duration, arguments.concurrency)
        )
    )
