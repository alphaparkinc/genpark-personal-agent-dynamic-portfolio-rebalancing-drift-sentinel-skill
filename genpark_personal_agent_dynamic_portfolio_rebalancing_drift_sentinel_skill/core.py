# -*- coding: utf-8 -*-
"""Dynamic Portfolio Rebalancing & Asset Drift Sentinel Skill for GenPark Personal Agents."""
import json
from typing import Dict, Any, List

def audit_portfolio_asset_drift(total_portfolio_value_usd: float, tolerance_band_pct: float, allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    if total_portfolio_value_usd <= 0 or not allocations:
        return {"error": "Invalid portfolio value or empty allocations"}

    drift_reports = []
    rebalance_required = False

    for item in allocations:
        asset = item.get("asset_class", "Unknown")
        target_pct = item.get("target_weight_pct", 0.0)
        curr_val = item.get("current_value_usd", 0.0)
        
        current_pct = round((curr_val / total_portfolio_value_usd) * 100.0, 2)
        target_val = round(total_portfolio_value_usd * (target_pct / 100.0), 2)
        delta_val = round(curr_val - target_val, 2)
        drift_pct = round(current_pct - target_pct, 2)

        # Tolerance band check: relative drift |drift| > target * (band/100) or absolute drift > band
        threshold_breached = abs(drift_pct) >= tolerance_band_pct
        if threshold_breached:
            rebalance_required = True

        drift_reports.append({
            "asset_class": asset,
            "target_pct": target_pct,
            "current_pct": current_pct,
            "drift_pct": drift_pct,
            "target_value_usd": target_val,
            "current_value_usd": curr_val,
            "delta_usd": delta_val,
            "trigger_breached": threshold_breached,
            "action_needed": "TRIM" if delta_val > 0 else ("ACCUMULATE" if delta_val < 0 else "MAINTAIN")
        })

    return {
        "portfolio_total_usd": total_portfolio_value_usd,
        "tolerance_band_pct": tolerance_band_pct,
        "rebalance_triggered": rebalance_required,
        "asset_drift_summary": drift_reports,
        "recommendation": "Execute rebalancing orders using opportunistic cash inflows or low-tax lots." if rebalance_required else "Portfolio within optimal tolerance bands; maintain current allocations.",
        "guardian": "GenPark Quantitative Asset Allocator"
    }

def synthesize_tax_efficient_rebalance_orders(incoming_cash_flow_usd: float, drifted_allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    orders = []
    remaining_cash = incoming_cash_flow_usd

    # Sort underweights by highest negative delta (needing most cash)
    underweights = []
    for item in drifted_allocations:
        cur = item.get("current_value_usd", 0.0)
        tgt = item.get("target_value_usd", 0.0)
        delta = tgt - cur
        if delta > 0:
            underweights.append((item.get("asset_class"), delta))

    underweights.sort(key=lambda x: x[1], reverse=True)
    total_underweight = sum(x[1] for x in underweights)

    for asset, needed in underweights:
        if remaining_cash > 0:
            allocation_share = (needed / total_underweight) if total_underweight > 0 else 0
            buy_amt = round(min(needed, incoming_cash_flow_usd * allocation_share), 2)
            orders.append({
                "action": "BUY",
                "asset_class": asset,
                "amount_usd": buy_amt,
                "funding_source": "INCOMING_CASH_INFLOW (Zero Tax Drag)"
            })
            remaining_cash -= buy_amt

    return {
        "inbound_cash_utilized_usd": round(incoming_cash_flow_usd - remaining_cash, 2),
        "unallocated_cash_reserve_usd": round(remaining_cash, 2),
        "generated_orders": orders,
        "strategy": "Cash-Flow Rebalancing: Direct new cash to underweighted assets to avoid capital gains liquidation tax."
    }
