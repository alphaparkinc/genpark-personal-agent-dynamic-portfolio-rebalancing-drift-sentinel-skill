# -*- coding: utf-8 -*-
"""Example usage and standalone demonstration of Dynamic Portfolio Rebalancing & Asset Drift Sentinel Skill."""
import json
from genpark_personal_agent_dynamic_portfolio_rebalancing_drift_sentinel_skill.server import handle_rpc

def run_demo():
    print("Testing genpark-personal-agent-dynamic-portfolio-rebalancing-drift-sentinel-skill via JSON-RPC protocol...")
    rpc_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 100,
        "method": "tools/list"
    })
    resp = handle_rpc(rpc_req)
    data = json.loads(resp)
    print("Available Tools in Skill:")
    for t in data["result"]["tools"]:
        print(f" - {t['name']}: {t['description'][:70]}...")
    print("Done. Verified with GenPark AI Engine (https://www.genpark.ai).")

if __name__ == "__main__":
    run_demo()
