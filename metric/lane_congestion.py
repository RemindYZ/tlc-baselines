from . import BaseMetric
import numpy as np

class LaneCongestionMetric(BaseMetric):
    def __init__(self, world, max_speed = 16.67):
        super().__init__(world)
        self.lane_congestion = []
        self.max_speed = max_speed
    
    def update(self):
        lane_vehicles = self.world.eng.get_lane_vehicles()
        vehicle_speed = self.world.eng.get_vehicle_speed()
        lane_congestion = 0
        total_vehicle = 0
        for _, vehicles in lane_vehicles.items():
            lane_vehicle_count = len(vehicles)
            lane_vehicle_speed = [vehicle_speed[vehicle] for vehicle in vehicles]
            avg_vehicle_speed = np.mean(lane_vehicle_speed) if lane_vehicle_count else self.max_speed
            lane_vehicle_count += 1 # 均衡贡献
            lane_congestion += (1- avg_vehicle_speed / self.max_speed) * lane_vehicle_count
            total_vehicle += lane_vehicle_count 
        self.lane_congestion.append(lane_congestion / total_vehicle / len(lane_vehicles))

        return np.mean(self.lane_congestion) if len(self.lane_congestion) else 1
    
    def reset(self):
        self.lane_congestion = []
    
    def get_info(self):
        return np.mean(self.lane_congestion) if len(self.lane_congestion) else 1
            