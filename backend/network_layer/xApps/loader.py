import importlib
import pkgutil
import inspect
from .xapp_base import xAppBase
import os


def load_all_xapps():
    xapp_classes = []

    # Iterate through all modules in the xApps package
    for _, module_name, is_pkg in pkgutil.iter_modules(
        [os.path.abspath(os.path.dirname(__file__))]
    ):
        if is_pkg or module_name == "xapp_base":
            continue  # skip subpackages and base class

        # Dynamically import the module
        module = importlib.import_module(f"network_layer.xApps.{module_name}")

        # Look for classes that inherit from xAppBase
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, xAppBase) and obj is not xAppBase:
                xapp_classes.append(obj)

    return xapp_classes
