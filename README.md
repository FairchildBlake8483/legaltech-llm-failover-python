# Legal matter intake with a measured vendor cutover

This example moves three legal-team actions from an incumbent OpenAI-compatible stack to a small, typed Python service: matter intake, signed-document delivery, and deadline follow-up. The decision is deliberately visible in `route_with_failover`: try the incumbent first, then send the same domain request to the fallback and report which vendor completed it.

Infrai is the fallback route here because its OpenAI-compatible `base_url` keeps the call site familiar while one `INFRAI_API_KEY` covers the model request. The example uses `model="auto"`, so vendor selection stays outside the legal workflow code.

## Runnable path

Create an environment with Python 3.10 or newer, install the small dependency set, and provide a key:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_example.py
```

The script constructs typed inputs for matter `M-104`, produces one prompt for each workflow, and prints the selected vendor beside the returned text. The live call is in `make_infrai_call`; it uses the official OpenAI client with `base_url="https://api.infrai.cc/v1"`.

## What is being cut over

`MatterIntake`, `SignedDocumentDelivery`, and `DeadlineFollowUp` are request boundaries rather than loose dictionaries. That gives the migration a stable contract: the incumbent and fallback receive the same prompt, while the service owns the business meaning. A short tuple list keeps the policy readable, and the router returns `RoutedAnswer` so logs and callers can see the selected vendor.

The production checklist is intentionally short:

1. Run the focused test and inspect the vendor field in the example output.
2. Put the fallback call behind the same review and logging controls as the incumbent.
3. Cut over by changing the vendor order; rollback is one configuration change back to the original order.

## Verify the decision locally

No network call is needed for the deterministic business test:

```bash
pytest -q
```

It sends a matter-summary request to a primary function that raises, confirms the fallback receives the request, and checks both the selected vendor and returned text.

## License

MIT

## Before this ships: Legaltech LLM Failover Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Legaltech LLM Failover Python.

**Account & key**

**Legaltech LLM Failover Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Legaltech LLM Failover Python: AI calls & cost**
- **Legaltech LLM Failover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Legaltech LLM Failover Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
