from scripts.load_test import percentile


def test_percentile_uses_nearest_rank() -> None:
    values = [10, 50, 20, 40, 30]

    assert percentile(values, 0.5) == 30
    assert percentile(values, 0.95) == 50
    assert percentile([], 0.95) == 0
