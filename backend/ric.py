import settings

class RICApp:
    def __init__(self, ric=None):
        self.ric = ric

class xApp(RICApp):
    def __init__(self, ric=None):
        super().__init__(ric)  # Call the parent class's constructor


class rApp(RICApp):
    def __init__(self, ric=None):
        super().__init__(ric)

class RanIntelligentController:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        pass