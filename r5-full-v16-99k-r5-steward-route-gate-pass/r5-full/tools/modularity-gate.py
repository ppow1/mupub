#!/usr/bin/env python3
# tools/modularity-gate.py - lean gate <2KB - checks socket <15KB and no hardcoded BLOCKED/bounded/demo_mode/safe_mode
import pathlib, sys
ROOT = pathlib.Path(__file__).parent.parent
SOCKET = ROOT / "cme" / "socket.py"
FAIL = 0
if not SOCKET.exists():
    print(f"FAIL missing {SOCKET}"); sys.exit(1)
size = SOCKET.stat().st_size
if size > 15360:
    print(f"FAIL size cme/socket.py {size} > 15360"); FAIL=1
else:
    print(f"PASS size cme/socket.py {size} <15KB")
text = SOCKET.read_text(errors="ignore").lower()
blocked_terms = ["blocked", "bounded", "demo_mode", "safe_mode"]
found = [t for t in blocked_terms if t in text]
if found:
    print(f"FAIL socket.py contains hardcoded terms: {found}"); FAIL=1
else:
    print(f"PASS socket.py no hardcoded BLOCKED/bounded/demo_mode/safe_mode")
sys.exit(FAIL)
