from network_layer.xApps.loader import load_all_xapps

class NearRTRIC:
    # Near Real-Time Ran Intelligent Controller
    def __init__(self, simulation_engine=None):
        self.ric_id = "NearRT-RIC"
        self.simulation_engine = simulation_engine
        self.xapp_list = {}

    def load_xApps(self):
        # dynamically load xApps from the xApp directory
        self.xapp_list = {}

        for xapp_cls in load_all_xapps():
            xapp_instance = xapp_cls(ric=self)
            assert (
                xapp_instance.xapp_id not in self.xapp_list
            ), f"xApp {xapp_instance.xapp_id} already exists"
            self.xapp_list[xapp_instance.xapp_id] = xapp_instance
            print(f"NearRT RIC: Loaded xApp: {xapp_instance.xapp_id}")

        for xapp in self.xapp_list.values():
            xapp.start()
