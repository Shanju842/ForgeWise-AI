import re
import pandas as pd

def rfq_agent(text, product, material, quantity, due_date, complexity):
    """RFQ & Manufacturing Intelligence Agent: structured intake and clarification checks."""
    text = text or ""
    missing = []
    if not product.strip(): missing.append("product / part description")
    if quantity <= 0: missing.append("valid order quantity")
    if not material: missing.append("material specification")
    if not due_date: missing.append("delivery date")
    if len(text.strip()) < 15: missing.append("detailed customer requirements / drawing / tolerance")
    return {
        "status": "Needs clarification" if missing else "Ready for costing",
        "clarifications": missing,
        "extracted": {"product": product, "material": material, "quantity": quantity,
                      "due_date": str(due_date), "complexity": complexity}
    }

def procurement_agent(df, material, quantity, kg_per_unit, wastage_pct):
    """Ranks compatible sample suppliers by landed cost; delivery is a tie-breaker."""
    required = quantity * kg_per_unit * (1 + wastage_pct / 100)
    work = df.copy()
    work["landed_rate"] = work["price_per_kg"] + work["freight_per_kg"]
    work["material_match"] = work["material"].str.lower().eq(material.lower())
    candidates = work[work["material_match"]]
    if candidates.empty:
        candidates = work
    candidates = candidates.sort_values(["landed_rate", "lead_time_days"])
    row = candidates.iloc[0].to_dict()
    return {"required_kg": required, "best_supplier": row,
            "ranked": candidates.to_dict("records"),
            "reason": "Lowest landed cost among the available demo quotations; confirm grade, tax, MOQ and delivery before ordering."}

def inventory_agent(df, material, required_kg):
    rows = df[df["material"].str.lower() == material.lower()]
    available = float(rows["available_kg"].sum()) if not rows.empty else 0.0
    return {"available_kg": available, "purchase_kg": max(0.0, required_kg - available)}

def costing_agent(quantity, material_kg, landed_rate, labour_per_unit,
                  machine_per_unit, overhead_per_unit, packaging_per_unit):
    material_cost = material_kg * landed_rate
    labour = quantity * labour_per_unit
    machine = quantity * machine_per_unit
    overhead = quantity * overhead_per_unit
    packaging = quantity * packaging_per_unit
    total = material_cost + labour + machine + overhead + packaging
    return {"material_cost": material_cost, "labour_cost": labour,
            "machine_cost": machine, "overhead_cost": overhead + packaging,
            "packaging_cost": packaging, "total_cost": total,
            "cost_per_unit": total / quantity if quantity else 0}

def profitguard_agent(total_cost, quantity, proposed_price, target_margin, contingency_pct):
    """Deterministic ProfitGuard; all arithmetic is auditable."""
    base_per_unit = total_cost / quantity if quantity else 0
    buffered_cost = base_per_unit * (1 + contingency_pct / 100)
    margin_factor = max(0.01, 1 - target_margin / 100)
    minimum = buffered_cost / margin_factor
    expected_margin = ((proposed_price - base_per_unit) / proposed_price * 100) if proposed_price > 0 else -100
    if proposed_price < buffered_cost:
        risk = "HIGH"
        message = "High risk: proposed price is below the buffered estimated cost. Do not quote without review."
    elif proposed_price < minimum:
        risk = "MEDIUM"
        message = "Margin risk: price covers buffered cost but misses the target margin."
    else:
        risk = "LOW"
        message = "The proposed price meets the target margin under the current demo assumptions."
    return {"cost_per_unit": base_per_unit, "buffered_cost": buffered_cost,
            "minimum_price": minimum, "recommended_price": max(proposed_price, minimum),
            "expected_margin": expected_margin, "risk": risk, "message": message}

def quotation_agent(factory, customer, product, quantity, material, due_date,
                    unit_price, total_cost, validity, symbol):
    subtotal = unit_price * quantity
    return f"""QUOTATION — DRAFT FOR OWNER REVIEW
{factory}
--------------------------------------------------
Customer: {customer}
Product: {product}
Material: {material}
Quantity: {quantity:,} units
Requested delivery: {due_date}

Proposed unit price: {symbol}{unit_price:,.2f}
Quoted subtotal: {symbol}{subtotal:,.2f}
Estimated production cost (internal): {symbol}{total_cost:,.2f}
Quote validity: {validity} days

Commercial notes:
• Final price is subject to drawing, tolerance, specification and sample approval.
• Taxes, freight, tooling and payment terms must be confirmed before issue.
• Delivery schedule is subject to material availability and production capacity.
• This is a prototype-generated draft and is not a binding offer.

Prepared by ForgeWise AI — requires factory owner approval.
"""
