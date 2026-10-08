#!/usr/bin/env python3
"""Offline reference helpers. Import data; never run binaries, browsers or commands."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from check_reference_obligations import canonical, load_json, text, strings, HEX, contained_file, evidence_integrity

ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def compile_observations(data, root):
    """Produce deterministic replay specifications, not executed test results."""
    require(isinstance(data, dict) and strings(data.get("inventory")), "inventory required")
    observations = data.get("observations")
    require(isinstance(observations, list), "observations required")
    found, cases = set(), set()
    fixtures = []
    for record in observations:
        require(isinstance(record, dict) and record.get("behavior_id") in data["inventory"], "unknown observation behavior")
        require(text(record.get("case_id")) and record["case_id"] not in cases, "unique case ID required")
        require(record.get("claim_status") in {"PROVEN","OBSERVED"}, "inference cannot become a test oracle")
        require(evidence_integrity(record, root), "observation artifact hash/path mismatch")
        require(all(k in record for k in ("preconditions","input","action","expected","environment")), "observation needs complete replay contract")
        require(text(record["action"]) and text(record["environment"]) and text(record.get("evidence_id")), "action/environment/Evidence ID missing")
        found.add(record["behavior_id"])
        cases.add(record["case_id"])
        fixtures.append({k:record[k] for k in ("behavior_id","case_id","preconditions","input","action","expected","environment","evidence_id","artifact_sha256")})
    gaps = sorted(set(data["inventory"]) - found)
    return {"status":"BLOCKED" if gaps else "PASS", "scope":"fixture-generation", "execution_status":"NOT_RUN",
            "unobserved_behaviors":gaps,"fixtures":fixtures}

def compare_traces(data):
    require(isinstance(data,dict) and isinstance(data.get("reference"),list) and isinstance(data.get("candidate"),list), "two event arrays required")
    require(data.get("reference_environment") == data.get("candidate_environment") and text(data.get("reference_environment")), "matched environment required")
    # Exact event comparison; cancellation/error/recovery are ordinary explicit events.
    left, right = data["reference"], data["candidate"]
    for i in range(max(len(left),len(right))):
        a, b = left[i] if i < len(left) else None, right[i] if i < len(right) else None
        if i >= len(left) or i >= len(right) or canonical(a) != canonical(b):
            return {"status":"FAIL","scope":"event-trace-comparison","first_divergence":i,"reference_event":a,"candidate_event":b}
    return {"status":"PASS","scope":"event-trace-comparison","first_divergence":None}

def graph(data):
    require(isinstance(data,dict) and isinstance(data.get("nodes"),list) and isinstance(data.get("edges"),list), "graph nodes/edges required")
    nodes = {}
    for node in data["nodes"]:
        require(isinstance(node,dict) and isinstance(node.get("id"),str) and ID.fullmatch(node["id"]) and node["id"] not in nodes, "invalid/duplicate graph ID")
        require(node.get("claim_status") in {"PROVEN","OBSERVED","INFERRED","UNKNOWN"} and text(node.get("layer")), "graph claim/layer required")
        if node["claim_status"] in {"PROVEN","OBSERVED"}:
            require(text(node.get("evidence_id")), "graph fact needs Evidence")
        nodes[node["id"]] = node
    lines = ["flowchart LR"]
    for ident, node in sorted(nodes.items()):
        lines.append('  ' + ident + '["' + ident + ' (' + node["claim_status"] + ')"]')
    seen = set()
    for edge in data["edges"]:
        require(isinstance(edge,dict) and edge.get("from") in nodes and edge.get("to") in nodes, "dangling graph edge")
        require(edge.get("claim_status") in {"PROVEN","OBSERVED","INFERRED","UNKNOWN"}, "edge claim required")
        if edge["claim_status"] in {"PROVEN","OBSERVED"}:
            require(text(edge.get("evidence_id")), "edge fact needs Evidence")
        pair = (edge["from"],edge["to"])
        require(pair not in seen,"duplicate graph edge")
        seen.add(pair)
        lines.append('  ' + pair[0] + ' -->|' + edge["claim_status"] + '| ' + pair[1])
    return {"status":"PASS","scope":"declared-graph","mermaid":"\n".join(lines),"unknown_nodes":[k for k,v in nodes.items() if v["claim_status"] in {"UNKNOWN","INFERRED"}]}

def version_diff(data):
    def snapshot(value):
        require(isinstance(value,dict) and isinstance(value.get("artifact_sha256"),str) and HEX.fullmatch(value["artifact_sha256"]), "snapshot artifact digest required")
        require(isinstance(value.get("components"),dict), "component map required")
        for key, component in value["components"].items():
            require(text(key) and isinstance(component,dict) and isinstance(component.get("sha256"),str) and HEX.fullmatch(component["sha256"]), "component hash required")
            require(strings(component.get("obligation_ids")), "component impact map required")
        return value["components"]
    require(isinstance(data,dict),"diff input must be object")
    before, after = snapshot(data.get("before")), snapshot(data.get("after"))
    changed = sorted(k for k in set(before)|set(after) if before.get(k) != after.get(k))
    impacted = sorted({o for k in changed for side in (before,after) for o in side.get(k,{}).get("obligation_ids",[])})
    return {"status":"PASS","scope":"declared-component-diff","changed_components":changed,"rerun_obligations":impacted,
            "reuse_requires_review":True,"binary_semantics_proven":False}

def route(path, capabilities):
    raw = Path(path).read_bytes()[:4096]
    suffix = Path(path).suffix.lower()
    if raw[:4] in (b'\xfe\xed\xfa\xce',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xcf\xfa\xed\xfe',b'\xca\xfe\xba\xbe',b'\xbe\xba\xfe\xca'):
        kind, required = "mach-o", {"ghidra":{"decompile","xrefs"}}
    elif raw[:2] == b'MZ':
        kind, required = "pe-candidate", {"ghidra":{"decompile","xrefs"}}
    elif raw[:4] == b'\x7fELF':
        kind, required = "elf", {"ghidra":{"decompile","xrefs"}}
    elif raw[:2] == b'PK':
        kind, required = "archive", {"archive-inspector":{"inventory"}}
    elif suffix in {".json",".har"}:
        kind, required = "trace-data", {"offline":{"compare"}}
    else:
        kind, required = "unknown", {}
    require(isinstance(capabilities,dict) and isinstance(capabilities.get("tools"),list), "capability inventory required")
    tools = {}
    for tool in capabilities["tools"]:
        require(isinstance(tool,dict) and text(tool.get("name")) and tool["name"] not in tools, "invalid/duplicate tool")
        require(text(tool.get("version")) and isinstance(tool.get("operations"),list) and all(text(x) for x in tool["operations"]), "tool version/operations required")
        tools[tool["name"]] = tool
    missing = [name for name, ops in required.items() if name not in tools or tools[name].get("probe_status") != "PASS" or not ops <= set(tools[name]["operations"])]
    return {"status":"BLOCKED" if missing or kind=="unknown" else "PASS","scope":"tool-routing-plan","kind":kind,
            "required_operations":{k:sorted(v) for k,v in required.items()},"unavailable_tools":missing,"execution_status":"NOT_RUN",
            "artifact_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()}

def metrics(data):
    require(isinstance(data,dict) and isinstance(data.get("calls"),list),"actual call trace required")
    seen, repeated, failed, tokens, cost = set(), 0, 0, 0, 0
    for call in data["calls"]:
        require(isinstance(call,dict) and all(text(call.get(k)) for k in ("tool","operation","input_digest")),"call identity missing")
        key = (call["tool"],call["operation"],call["input_digest"])
        if key in seen and not text(call.get("retry_reason")):
            repeated += 1
        seen.add(key)
        if call.get("usable") is not True:
            failed += 1
        for field in ("tokens","cost"):
            require(type(call.get(field)) in {int,float} and math.isfinite(call[field]) and call[field]>=0,"explicit nonnegative usage required; unknown is not zero")
        tokens += call["tokens"]
        cost += call["cost"]
    return {"status":"PASS","scope":"reported-agent-usage","calls":len(data["calls"]),"unjustified_repeats":repeated,
            "unusable_calls":failed,"tokens":tokens,"cost":cost,"first_tool_matches_plan":data.get("selected_first_tool")==data.get("expected_first_tool") if text(data.get("expected_first_tool")) else None,
            "agent_behavior_certified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("operation", choices=["compile","compare","graph","version-diff","route","metrics"])
    p.add_argument("input",type=Path)
    p.add_argument("--evidence-root",type=Path)
    p.add_argument("--capabilities",type=Path)
    args=p.parse_args()
    try:
        if args.operation=="route":
            result=route(args.input,load_json(args.capabilities))
        else:
            data=load_json(args.input)
            if args.operation=="compile":
                require(args.evidence_root is not None,"Evidence root required")
                result=compile_observations(data,args.evidence_root)
            else:
                result={"compare":compare_traces,"graph":graph,"version-diff":version_diff,"metrics":metrics}[args.operation](data)
    except (OSError,ValueError,TypeError,RuntimeError) as exc:
        result={"status":"FAIL","errors":[str(exc)]}
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__":
    sys.exit(main())
