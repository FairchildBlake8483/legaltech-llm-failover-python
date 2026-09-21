from src.legal_failover import route_with_failover


def test_business_request_moves_to_fallback_after_primary_failure() -> None:
    attempts: list[str] = []

    def primary(_: str) -> str:
        attempts.append("incumbent")
        raise RuntimeError("vendor unavailable for this request")

    def fallback(prompt: str) -> str:
        attempts.append("fallback")
        return f"ready: {prompt}"

    result = route_with_failover(
        "Summarize matter M-104 before the filing deadline",
        [("incumbent", primary), ("fallback", fallback)],
    )

    assert attempts == ["incumbent", "fallback"]
    assert result.vendor == "fallback"
    assert result.text.startswith("ready:")
