# ForgeWise AI — Manufacturing Intelligence MVP

**Industrial Manufacturing · Problem Statement 4.1**  
**An Agentic Manufacturing Intelligence Copilot for Smart Procurement and Profit-Safe Quoting**

ForgeWise AI is a student-built prototype exploring how small manufacturers can connect customer RFQs, supplier quote comparison, inventory checks, manufacturing cost estimation and profit-safe quotation drafting in one workflow.

## Current working features
- RFQ intake and missing-information checks.
- Supplier comparison using landed price (unit price + freight) and lead-time tie-break.
- Inventory availability and net material purchase calculation.
- Deterministic manufacturing cost calculation.
- ProfitGuard margin and risk assessment.
- Customer quotation draft with an explicit human approval checkbox before download.
- Estimated-versus-actual cost variance view.
- SQLite storage module for cost-review records (available for extension/integration).
- Unit tests for core decision functions.

## Run locally
Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in the terminal, normally `http://localhost:8501`.

## Run tests
```bash
pip install pytest
pytest -q
```

## Demo flow
1. Enter a customer RFQ.
2. Review supplier quotes and the recommended supplier.
3. Check inventory and net purchase requirement.
4. Adjust material usage, wastage, labour, machine and overhead assumptions.
5. Enter the customer's expected unit price and inspect ProfitGuard.
6. Review the generated quotation draft and approve it for download.
7. Enter actual cost and inspect the variance.

## Architecture
The initial implementation uses a Streamlit interface and transparent Python modules in `forgewise/agents.py`. Financial arithmetic is deterministic and auditable; it is not delegated to an LLM.

## Honest scope statement
This is a functional prototype, not a production-ready factory platform. Sample supplier quotations, inventory and default cost inputs are synthetic. The five named agents are currently implemented as Python decision modules/rules, not autonomous LLM agents. The current app does not connect to live supplier feeds, ERP, WhatsApp, OCR, speech services or an external LLM. No purchase order or customer quotation is sent automatically. The SQLite storage module is provided as a foundation; the current dashboard's demo session is not yet fully wired to persistent order history.

## Planned next steps
- Wire cost-review persistence into the dashboard.
- Add supplier quote file upload with validation and traceable source records.
- Add RFQ PDF/image extraction with human verification.
- Add capacity and BOM/routing checks.
- Add optional LLM orchestration with tool permissions, audit logs and human approval.
- Add multilingual Tamil/English voice and WhatsApp workflows after privacy/security review.

## Reference research
See [`docs/reference-research.md`](docs/reference-research.md) for public repositories studied as architectural/workflow references. ForgeWise AI is independently implemented; no upstream code is copied.

## License
MIT — see `LICENSE`.
