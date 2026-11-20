import streamlit as st
import pandas as pd
from datetime import date, timedelta
from forgewise.agents import (
    rfq_agent, procurement_agent, inventory_agent,
    costing_agent, profitguard_agent, quotation_agent
)

st.set_page_config(page_title="ForgeWise AI", page_icon="🏭", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 1.2rem 1.5rem; border-radius: 16px; background: linear-gradient(120deg,#10243a,#1c5270); color: white; margin-bottom: 1rem;}
.hero h1 {font-size: 2.1rem; margin: 0;}
.hero p {color:#d8e8f2; margin:.4rem 0 0 0;}
.metric-card {border:1px solid #dce3ea; border-radius:12px; padding:12px;}
.small-note {font-size: .85rem; color: #687787;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🏭 ForgeWise AI</h1><p>Agentic manufacturing intelligence copilot · Smart procurement · Profit-safe quoting</p></div>', unsafe_allow_html=True)
st.caption("Prototype mode · Demonstration data is synthetic · No purchase or customer commitment is made automatically")

with st.sidebar:
    st.header("Factory profile")
    factory = st.text_input("Factory name", "Sri Lakshmi Engineering Works")
    currency = st.selectbox("Currency", ["INR (₹)", "USD ($)"])
    symbol = "₹" if currency.startswith("INR") else "$"
    st.divider()
    st.markdown("**Agent pipeline**")
    st.write("1. RFQ & Manufacturing Intelligence")
    st.write("2. Procurement & Inventory")
    st.write("3. Manufacturing Cost Intelligence")
    st.write("4. ProfitGuard")
    st.write("5. Negotiation & Business Action")
    st.divider()
    st.info("All financial arithmetic is performed by transparent Python functions. AI-generated commitments are not enabled.")

st.subheader("1 · Customer enquiry / RFQ")
c1, c2, c3 = st.columns(3)
with c1:
    customer = st.text_input("Customer name", "ABC Industries")
    product = st.text_input("Product / part", "Mild steel mounting bracket")
with c2:
    quantity = st.number_input("Order quantity (units)", min_value=1, value=500, step=10)
    material = st.selectbox("Primary material", ["Mild Steel", "Stainless Steel 304", "Aluminium 6061", "Copper"])
with c3:
    due_date = st.date_input("Required delivery date", date.today() + timedelta(days=21))
    complexity = st.selectbox("Manufacturing complexity", ["Standard", "Moderate", "High"])

with st.expander("RFQ details (paste customer enquiry)", expanded=True):
    rfq_text = st.text_area("Customer message / RFQ", value=f"Please quote {quantity} units of {product}. Material: {material}. Delivery required by {due_date}. Please confirm price and lead time.", height=90)

rfq = rfq_agent(rfq_text, product, material, int(quantity), due_date, complexity)
r1, r2, r3 = st.columns(3)
r1.metric("RFQ status", rfq["status"])
r2.metric("Order quantity", f'{quantity:,} units')
r3.metric("Delivery target", due_date.strftime("%d %b %Y"))
if rfq["clarifications"]:
    st.warning("Clarifications to confirm: " + " · ".join(rfq["clarifications"]))
else:
    st.success("RFQ has the minimum information required for this demonstration.")

st.divider()
st.subheader("2 · Smart procurement & inventory")
supplier_df = pd.read_csv(Path(__file__).parent / "data" / "supplier-quotations.csv")
inventory_df = pd.read_csv(Path(__file__).parent / "data" / "inventory.csv")
col_a, col_b = st.columns([1.1, 1])
with col_a:
    st.markdown("**Supplier quotations**")
    st.dataframe(supplier_df, use_container_width=True, hide_index=True)
    procurement = procurement_agent(supplier_df, material, int(quantity), float(st.number_input("Material required per unit (kg)", min_value=0.01, value=0.8, step=0.05)), float(st.number_input("Expected wastage (%)", min_value=0.0, value=5.0, step=0.5)))
    best = procurement["best_supplier"]
    st.success(f"Recommended supplier: {best['supplier']} · Landed rate {symbol}{best['landed_rate']:,.2f}/kg")
    st.caption(f"Recommendation considers material match, unit price, freight and delivery lead time. {procurement['reason']}")
with col_b:
    st.markdown("**Current inventory (demo)**")
    st.dataframe(inventory_df, use_container_width=True, hide_index=True)
    inv = inventory_agent(inventory_df, material, procurement["required_kg"])
    st.metric("Material required", f'{procurement["required_kg"]:,.1f} kg')
    st.metric("Available stock", f'{inv["available_kg"]:,.1f} kg')
    st.metric("Net purchase required", f'{inv["purchase_kg"]:,.1f} kg')
    if inv["purchase_kg"] <= 0:
        st.success("Existing inventory covers this order.")
    else:
        st.warning(f"Purchase approximately {inv['purchase_kg']:,.1f} kg, subject to owner approval.")

st.divider()
st.subheader("3 · Manufacturing cost intelligence")
cc1, cc2, cc3, cc4 = st.columns(4)
with cc1:
    labour_per_unit = st.number_input("Labour / unit", min_value=0.0, value=18.0, step=1.0)
with cc2:
    machine_per_unit = st.number_input("Machine / unit", min_value=0.0, value=12.0, step=1.0)
with cc3:
    overhead_per_unit = st.number_input("Overheads / unit", min_value=0.0, value=8.0, step=1.0)
with cc4:
    packaging_per_unit = st.number_input("Packaging / unit", min_value=0.0, value=3.0, step=0.5)

cost = costing_agent(
    quantity=int(quantity),
    material_kg=procurement["required_kg"],
    landed_rate=best["landed_rate"],
    labour_per_unit=labour_per_unit,
    machine_per_unit=machine_per_unit,
    overhead_per_unit=overhead_per_unit,
    packaging_per_unit=packaging_per_unit
)
cost_cols = st.columns(5)
for col, (label, value) in zip(cost_cols, [
    ("Material", cost["material_cost"]), ("Labour", cost["labour_cost"]),
    ("Machine", cost["machine_cost"]), ("Overheads", cost["overhead_cost"]),
    ("Total estimated cost", cost["total_cost"])
]):
    col.metric(label, f"{symbol}{value:,.2f}")

st.divider()
st.subheader("4 · ProfitGuard: protect the margin")
p1, p2 = st.columns(2)
with p1:
    target_margin = st.slider("Target gross margin (%)", min_value=5, max_value=60, value=20)
    proposed_price = st.number_input("Customer's expected price per unit", min_value=0.0, value=75.0, step=1.0)
with p2:
    contingency = st.slider("Contingency buffer (%)", min_value=0, max_value=20, value=5)
    quote_validity = st.number_input("Quote validity (days)", min_value=1, max_value=90, value=15)

guard = profitguard_agent(cost["total_cost"], int(quantity), proposed_price, target_margin, contingency)
g1, g2, g3 = st.columns(3)
g1.metric("Estimated cost / unit", f'{symbol}{guard["cost_per_unit"]:,.2f}')
g2.metric("Minimum safe price / unit", f'{symbol}{guard["minimum_price"]:,.2f}')
g3.metric("Expected gross margin", f'{guard["expected_margin"]:.1f}%')
if guard["risk"] == "HIGH":
    st.error(guard["message"])
elif guard["risk"] == "MEDIUM":
    st.warning(guard["message"])
else:
    st.success(guard["message"])

st.divider()
st.subheader("5 · Draft quotation & owner approval")
quote = quotation_agent(
    factory, customer, product, int(quantity), material, due_date,
    guard["recommended_price"], cost["total_cost"], quote_validity, symbol
)
st.text_area("Quotation preview", quote, height=270)
approved = st.checkbox("I have reviewed the assumptions and approve this quotation draft for export.")
if approved:
    st.download_button("⬇️ Download quotation (.txt)", quote, file_name="forgewise_customer_quotation.txt", mime="text/plain")
else:
    st.info("Owner approval is required before the quotation can be downloaded. This prototype never sends quotations or places purchase orders automatically.")

st.divider()
st.subheader("6 · Estimated vs actual learning loop")
st.write("Record actual cost after production to compare against the estimate. This demo stores the comparison in the current session only.")
actual = st.number_input("Actual total production cost", min_value=0.0, value=float(cost["total_cost"]), step=100.0)
variance = actual - cost["total_cost"]
v1, v2 = st.columns(2)
v1.metric("Cost variance", f"{symbol}{variance:,.2f}", delta=f"{(variance / cost['total_cost'] * 100) if cost['total_cost'] else 0:.1f}%")
v2.metric("Variance status", "Over budget" if variance > 0 else "At / below estimate")
st.caption("Prototype limitations: supplier and inventory records are sample data; no ERP, WhatsApp, live supplier feeds, cloud database, OCR or external LLM is connected. Replace demo data with verified factory records before operational use.")
