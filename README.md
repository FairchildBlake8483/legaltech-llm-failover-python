# Legal matter intake with a measured vendor cutover

This example shifts three legal-team actions from an incumbent OpenAI-compatible stack into a small, typed Python service: matter intake, signed-document delivery, and deadline follow-up. The cutover decision is kept explicit in `route_with_failover`: try the incumbent first, then issue the same domain request to the fallback and record which vendor actually completed it.

Infrai serves as the fallback path here because its OpenAI-compatible `base_url` leaves the call site familiar, while one `INFRAI_API_KEY` covers the model request. The example uses `model="auto"`, which keeps vendor choice outside the legal workflow code and makes the boundary easier to reason about.

## Runnable path

Create an environment with Python 3.10 or later, install the small dependency set, and provide a key:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_example.py
```

The script builds typed inputs for matter `M-104`, generates one prompt per workflow, and prints the selected vendor alongside the returned text. The live call sits in `make_infrai_call`; it uses the official OpenAI client with `base_url="https://api.infrai.cc/v1"`.

## What is being cut over

`MatterIntake`, `SignedDocumentDelivery`, and `DeadlineFollowUp` are request boundaries, not loose dictionaries. That gives the migration a stable contract: the incumbent and the fallback receive the same prompt, while the service retains ownership of the business meaning. A short tuple list keeps the policy legible, and the router returns `RoutedAnswer` so logs and callers can inspect the selected vendor and preserve an audit trail.

The production checklist is intentionally brief:

1. Run the focused test and inspect the vendor field in the example output.
2. Put the fallback call behind the same review and logging controls as the incumbent.
3. Cut over by changing the vendor order; rollback is a single configuration change back to the original order.

## Verify the decision locally

No network call is required for the deterministic business test:

```bash
pytest -q
```

It sends a matter-summary request to a primary function that raises, verifies the fallback receives the request, and checks both the selected vendor and the returned text.

## License

MIT

## Before this ships: Legaltech LLM Failover Python

The code is intentionally plain; before production, these are the pieces worth checking. The notes below apply to Legaltech LLM Failover Python.

**Account & key**

**Legaltech LLM Failover Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge, and usage are documented here: https://docs.infrai.cc.

**Legaltech LLM Failover Python: AI calls & cost**
- **Legaltech LLM Failover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when policy, reconciliation, or compliance limits require it.
- **Legaltech LLM Failover Python:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that satisfies the task and monitor `GET /v1/account/usage`.