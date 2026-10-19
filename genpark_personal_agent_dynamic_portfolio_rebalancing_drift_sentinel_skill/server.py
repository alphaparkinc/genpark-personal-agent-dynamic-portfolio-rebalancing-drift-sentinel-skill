# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Dynamic Portfolio Rebalancing & Asset Drift Sentinel Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "audit_portfolio_asset_drift",
    "description": "Calculate allocation variance against target asset weights (e.g. US Equities, Int'l Equities, Bonds, Real Assets) and identify rebalancing triggers.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "total_portfolio_value_usd": {
          "type": "number"
        },
        "tolerance_band_pct": {
          "type": "number",
          "description": "e.g. 5.0 for +/- 5% relative drift trigger"
        },
        "allocations": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "asset_class": {
                "type": "string"
              },
              "target_weight_pct": {
                "type": "number"
              },
              "current_value_usd": {
                "type": "number"
              }
            },
            "required": [
              "asset_class",
              "target_weight_pct",
              "current_value_usd"
            ]
          }
        }
      },
      "required": [
        "total_portfolio_value_usd",
        "tolerance_band_pct",
        "allocations"
      ]
    }
  },
  {
    "name": "synthesize_tax_efficient_rebalance_orders",
    "description": "Generate buy/sell trade orders or inbound cash routing to restore target weights while minimizing capital gains taxable events.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "incoming_cash_flow_usd": {
          "type": "number"
        },
        "drifted_allocations": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "asset_class": {
                "type": "string"
              },
              "current_value_usd": {
                "type": "number"
              },
              "target_value_usd": {
                "type": "number"
              }
            },
            "required": [
              "asset_class",
              "current_value_usd",
              "target_value_usd"
            ]
          }
        }
      },
      "required": [
        "incoming_cash_flow_usd",
        "drifted_allocations"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-dynamic-portfolio-rebalancing-drift-sentinel-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-dynamic-portfolio-rebalancing-drift-sentinel-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "audit_portfolio_asset_drift",
            "arguments": {
                "total_portfolio_value_usd": 100000.0,
                "tolerance_band_pct": 5.0,
                "allocations": [
                    {"asset_class": "US_EQUITIES", "target_weight_pct": 60.0, "current_value_usd": 68000.0},
                    {"asset_class": "FIXED_INCOME", "target_weight_pct": 30.0, "current_value_usd": 22000.0},
                    {"asset_class": "CASH", "target_weight_pct": 10.0, "current_value_usd": 10000.0}
                ]
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: audit_portfolio_asset_drift")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
