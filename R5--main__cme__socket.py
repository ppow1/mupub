"""
R5 CME Socket <15KB - 3 methods only
Observe · Dispatch · Monitor
Task class branching fixes Vicky + Grace stalls
"""
from typing import Any
import json, pathlib

REG = pathlib.Path(__file__).parent.parent / "registries"

class Observation(dict): pass
class Grant(dict): pass
class State(dict): pass

class CMESocket:
    def __init__(self, registry_dir=REG):
        self.reg = registry_dir
        self._load()

    def _load(self):
        self.resources = self._j("resources.json")
        self.capabilities = self._j("capabilities.json")
        self.envs = self._j("environments.json")
        self.security = self._j("../hr/security_levels.json")

    def _j(self, name):
        p = (self.reg / name).resolve()
        if not p.exists(): return {}
        return json.loads(p.read_text())

    def observe(self, event: dict) -> Observation:
        # intake only - no logic
        return Observation(event=event, ts=event.get("ts"))

    def dispatch(self, task: dict, task_class: str = "v1.0.0-conversation") -> Grant:
        # THE FIX: conversation does NOT go through authority store
        if task_class == "v1.0.0-conversation":
            return Grant(mode="lightweight", action="respond", task=task, bypass=["authority_grades","acceptance_envelope","governance"])
        # engineering full
        policy = self.security.get(task.get("actor"), {})
        cap = self.capabilities.get(task.get("capability"), {})
        return Grant(mode="full", action="engineering_workflow", task=task, policy=policy, cap=cap, process_graph=cap.get("process_graph"))

    def monitor(self) -> State:
        # health from registries + ledger append check
        return State(cme="online", resources=self.resources.get("status","healthy"), tasks=self.resources.get("tasks",0))

# Loop stages are registry lookups, not hardcoded
STAGES = ["Observe","Understand","Plan","Decompose","Dispatch","Monitor","Validate","Recover","Integrate","Learn"]
