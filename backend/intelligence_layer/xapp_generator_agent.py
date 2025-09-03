import os
import re
from typing import List

from intelligence_layer.agents.specification_agent import specification_agent
from intelligence_layer.agents.code_generation_agent import code_generation_agent
from intelligence_layer.agents.verification_agent import verification_agent
from agents import Agent, function_tool
from network_layer.simulation_engine import SimulationEngine


def _to_snake_case(name: str) -> str:
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_")
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return snake


def _to_pascal_case(name: str) -> str:
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(p.capitalize() for p in parts if p)


def _xapps_dir() -> str:
    # backend/network_layer/xApps
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "network_layer", "xApps")
    )


@function_tool
def list_xapps() -> str:
    """Lists currently loaded xApps on the RIC and available xApp modules on disk."""
    sim = SimulationEngine()
    ric = sim.ric
    loaded = (
        list(ric.xapp_list.keys()) if ric and getattr(ric, "xapp_list", None) else []
    )

    # Modules on disk
    xapps_dir = _xapps_dir()
    on_disk = []
    if os.path.isdir(xapps_dir):
        for fname in os.listdir(xapps_dir):
            if (
                fname.startswith("xapp_")
                and fname.endswith(".py")
                and fname != "xapp_base.py"
            ):
                on_disk.append(fname)

    return (
        "Loaded xApps: "
        + (", ".join(loaded) if loaded else "<none>")
        + "\nAvailable modules: "
        + (", ".join(sorted(on_disk)) if on_disk else "<none>")
    )


@function_tool
def view_xapp_source(xapp_id: str) -> str:
    """Shows the source code of a loaded xApp by its ID (class name)."""
    sim = SimulationEngine()
    ric = sim.ric
    if not ric or xapp_id not in ric.xapp_list:
        return f"xApp '{xapp_id}' is not loaded. Use reload_xapps after creating, or check the name."
    try:
        src = ric.xapp_list[xapp_id].to_json().get("source_code")
        return src or "<source unavailable>"
    except Exception as e:
        return f"Failed to fetch source for {xapp_id}: {e}"


@function_tool
def reload_xapps() -> str:
    """Reloads xApps from disk and starts them on the RIC."""
    sim = SimulationEngine()
    if not sim.ric:
        return "RIC not initialized in simulation engine."
    sim.ric.load_xApps()
    return "xApps reloaded successfully. Loaded: " + ", ".join(sim.ric.xapp_list.keys())


@function_tool
def create_xapp(xapp_name: str, enable_by_default: bool = True) -> str:
    """Creates a new xApp module and class skeleton under network_layer/xApps and reloads xApps.

    Args:
        xapp_name: Desired xApp name. Used to derive file and class names.
        enable_by_default: Whether to enable the xApp by default.
    """
    xapps_dir = _xapps_dir()
    os.makedirs(xapps_dir, exist_ok=True)

    snake = _to_snake_case(xapp_name)
    pascal = _to_pascal_case(xapp_name)
    module_name = f"xapp_{snake}.py"
    class_name = f"xApp{pascal}"
    file_path = os.path.join(xapps_dir, module_name)

    if os.path.exists(file_path):
        return f"Module already exists: {module_name}. Choose a different name."

    skeleton = f'''from .xapp_base import xAppBase


class {class_name}(xAppBase):
    """
    Auto-generated xApp. Implement RAN control logic here.
    """

    def __init__(self, ric=None):
        super().__init__(ric=ric)
        self.enabled = {str(bool(enable_by_default))}

    def start(self):
        if not self.enabled:
            print(f"{{self.xapp_id}}: xApp is not enabled")
            return
        # Subscribe to events from base stations if needed, e.g.:
        # for bs in self.base_station_list.values():
        #     bs.init_rrc_measurement_event_handler("A3", self.on_rrc_meas_event_A3)

    def step(self):
        # Optional: implement step-driven logic
        pass
'''

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(skeleton)

    # Reload xApps to register the new one
    sim = SimulationEngine()
    if sim.ric:
        sim.ric.load_xApps()

    return f"Created {module_name} with class {class_name}. xApps reloaded."


xapp_generator_agent = Agent(
    name="xApp Generator Agent",
    handoff_description="Agent for creating, listing, viewing, reloading xApps, and specification follow-up.",
    instructions=(
        "You help users scaffold new RIC xApps and manage them. "
        "Use create_xapp to scaffold, list_xapps to enumerate, view_xapp_source to show code, and reload_xapps to reload. "
        "Ask for clarification if the request is ambiguous. "
        "You also use the specification agent to ask follow-up questions and generate formal contracts from user requirements."
    ),
    tools=[create_xapp, list_xapps, view_xapp_source, reload_xapps, specification_agent],
)
