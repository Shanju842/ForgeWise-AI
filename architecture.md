# System architecture

The Streamlit UI collects an RFQ and factory assumptions. It calls five Python decision modules:
1. RFQ agent — checks the minimum required order information.
2. Procurement agent — compares supplier landed cost and lead time.
3. Inventory agent — calculates stock coverage and net purchase requirement.
4. Costing agent — calculates material, labour, machine and overhead cost.
5. ProfitGuard and quotation action — checks margin risk and prepares a draft for human review.

Financial calculations are deterministic and auditable. The current prototype uses local CSV demo records and has no external service dependency.
