class CoreNetworkFunction:
    def __init__(self, core_network=None):
        self.core_network = core_network
        pass


class PolicyControlFunction:
    def __init__(self, core_network=None):
        self.core_network = core_network
        pass

class NetworkSliceManagementFunction:
    def __init__(self, core_network=None):
        self.core_network = core_network
        self.network_slices = {}

class NetworkSliceSelectionFunction:
    def __init__(self, core_network=None):
        self.core_network = core_network
        pass

class CoreNetwork:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        self.pcf = PolicyControlFunction(self)
        self.nssf = NetworkSliceSelectionFunction(self)    
        self.nsmf = NetworkSliceManagementFunction(self)

class NetworkSlice:

    SLICE_TYPE_EMBB = "eMBB"
    SLICE_TYPE_URLLC = "uRLLC"
    SLICE_TYPE_MMT = "mMTC"
    SLICE_TYPE_V2X = "V2X"
    SLICE_TYPE_CUSTOMIZE = "customize"

    def __init__(self):
        self.slice_id = None
        self.slice_type = None