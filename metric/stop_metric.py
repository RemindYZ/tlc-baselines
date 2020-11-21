from . import BaseMetric
import numpy as np

class StopTimesMetric(BaseMetric):
    """
    Calculate Average Stop tims
    """
    def __init__(self, world):
        super().__init__(world)
        self.stoptimes = {}
        self.speed_stop = 0.1
        self.speed_run = 100
        self.vehicle_status = {}

    def update(self):
        vehicles = self.world.eng.get_vehicles(include_waiting=False)
        vehicle_speed = self.world.eng.get_vehicle_speed()
        for vehicle in vehicles:
            if vehicle not in self.stoptimes.keys():
                self.stoptimes[vehicle] = 0
            if vehicle not in self.vehicle_status.keys():
                self.vehicle_status[vehicle] = "running"
            elif vehicle_speed[vehicle] < self.speed_stop and self.vehicle_status[vehicle] == "running":
                self.stoptimes[vehicle] += 1
                self.vehicle_status[vehicle] = "stop"
            elif vehicle_speed[vehicle] > self.speed_run and self.vehicle_status[vehicle] == "stop":
                self.vehicle_status[vehicle] = "running"
        return np.mean([v for v in self.stoptimes.values()]) if len(self.stoptimes.values()) else 0
    
    def reset(self):
        self.stoptimes = {}
        self.vehicle_status = {}
    
    def get_info(self):
        return np.mean([v for v in self.stoptimes.values()]) if len(self.stoptimes.values()) else 0
