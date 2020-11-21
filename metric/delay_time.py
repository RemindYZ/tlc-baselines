from . import BaseMetric
import numpy as np

class DelayTimeMetric(BaseMetric):
    """
    Calculate average delay time for each vehicle
    """
    def __init__(self, world):
        super().__init__(world)
        # self.world.subscribe([""])
        self.vehicle_delaytime = {}
    
    def update(self):
        vehicles = self.world.eng.get_vehicles(include_waiting=False)
        vehicle_speed = self.world.eng.get_vehicle_speed()
        for vehicle in vehicles:
            if vehicle not in self.vehicle_delaytime.keys():
                self.vehicle_delaytime[vehicle] = 0
            if vehicle_speed[vehicle] < 0.1:
                self.vehicle_delaytime[vehicle] += 1
        return np.mean([v for v in self.vehicle_delaytime.values()]) if len(self.vehicle_delaytime.values()) else 0
    
    def reset(self):
        self.vehicle_delaytime = {}
    
    def get_info(self):
        return np.mean([v for v in self.vehicle_delaytime.values()]) if len(self.vehicle_delaytime.values()) else 0
            