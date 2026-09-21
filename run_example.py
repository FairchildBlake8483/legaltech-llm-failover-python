"""Run the three legal workflow steps against the configured OpenAI-compatible route."""

from src.legal_failover import (
    DeadlineFollowUp,
    MatterIntake,
    SignedDocumentDelivery,
    delivery_prompt,
    follow_up_prompt,
    intake_prompt,
    make_infrai_call,
    route_with_failover,
)


def main() -> None:
    call = make_infrai_call()
    vendors = [("incumbent", call), ("fallback", call)]
    requests = [
        ("intake", intake_prompt(MatterIntake(matter_id="M-104", client_name="Northwind", facts="Lease renewal due next month."))),
        ("delivery", delivery_prompt(SignedDocumentDelivery(matter_id="M-104", document_name="lease.pdf", recipient="counsel@example.com", signed_text="Signed by all parties."))),
        ("follow-up", follow_up_prompt(DeadlineFollowUp(matter_id="M-104", deadline="2026-10-01", task="Confirm filing receipt."))),
    ]
    for label, prompt in requests:
        result = route_with_failover(prompt, vendors)
        print(f"{label}: vendor={result.vendor}\n{result.text}\n")


if __name__ == "__main__":
    main()
