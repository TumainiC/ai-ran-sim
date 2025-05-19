import importlib
import pkgutil
import inspect
import os
from network_layer.xApps.xapp_base import xAppBase


class NearRTRIC:
    # Near Real-Time Ran Intelligent Controller
    def __init__(self, simulation_engine=None):
        self.ric_id = "NearRT-RIC"
        self.simulation_engine = simulation_engine
        self.xapp_list = {}

    def load_xApps(self):
        # dynamically load xApps from the xApp directory
        self.xapp_list = {}

        xapp_classes = []
        xapps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "xApps"))
        for _, module_name, is_pkg in pkgutil.iter_modules([xapps_dir]):
            if is_pkg or module_name == "xapp_base":
                continue  # skip subpackages and base class

            module = importlib.import_module(f"network_layer.xApps.{module_name}")

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, xAppBase) and obj is not xAppBase:
                    xapp_classes.append(obj)

        for xapp_cls in xapp_classes:
            xapp_instance = xapp_cls(ric=self)
            assert (
                xapp_instance.xapp_id not in self.xapp_list
            ), f"xApp {xapp_instance.xapp_id} already exists"
            self.xapp_list[xapp_instance.xapp_id] = xapp_instance
            print(f"NearRT RIC: Loaded xApp: {xapp_instance.xapp_id}")

        for xapp in self.xapp_list.values():
            xapp.start()
