import pandas as pd
from datetime import date
from forgewise.agents import rfq_agent, procurement_agent, inventory_agent, costing_agent, profitguard_agent

def test_rfq_flags_missing_detail():
    result = rfq_agent("short", "Bracket", "Mild Steel", 10, date.today(), "Standard")
    assert result["status"] == "Needs clarification"

def test_procurement_calculates_required_material_and_landed_rate():
    df = pd.DataFrame([
        {"supplier":"A", "material":"Mild Steel", "price_per_kg":10, "freight_per_kg":2, "lead_time_days":4},
        {"supplier":"B", "material":"Mild Steel", "price_per_kg":11, "freight_per_kg":1, "lead_time_days":3},
    ])
    result = procurement_agent(df, "Mild Steel", 100, 0.5, 10)
    assert result["required_kg"] == 55
    assert result["best_supplier"]["landed_rate"] == 12

def test_inventory_purchase_requirement():
    df = pd.DataFrame([{"material":"Mild Steel", "available_kg":20}])
    result = inventory_agent(df, "Mild Steel", 50)
    assert result["purchase_kg"] == 30

def test_costing_total_is_sum_of_components():
    result = costing_agent(10, 5, 2, 1, 1, 1, 1)
    assert result["total_cost"] == 25

def test_profitguard_flags_price_below_cost():
    result = profitguard_agent(1000, 10, 50, 20, 5)
    assert result["risk"] == "HIGH"
