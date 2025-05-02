class xAppBase:
    def __init__(self, ric=None):
        self.ric = ric
    
    @property
    def xapp_id(self):
        return self.__class__.__name__

    @property
    def base_station_list(self):
        return self.ric.simulation_engine.base_station_list

    @property
    def cell_list(self):
        return self.ric.simulation_engine.cell_list
    
    @property
    def ue_list(self):
        return self.ric.simulation_engine.ue_list

    def start(self):
        assert False, "Not implemented in base class"