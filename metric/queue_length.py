from . import BaseMetric
import numpy as np

class QueueLengthMetric(BaseMetric):
    """
    Calculate average queue length
    L_avg = sum_t(sum_i(L_i_t))/T/n_l
    """
    def __init__(self, world):
        super().__init__(world)
        self.world.subscribe(["lane_waiting_count"])
        self.queuelength = []
    
    def update(self):
        lane_waiting_count_dict = self.world.get_info("lane_waiting_count")
        lane_waiting_count_list = [waiting_count for waiting_count in lane_waiting_count_dict.values()]
        queuelength_current = np.mean(lane_waiting_count_list) if len(lane_waiting_count_list) else 0 
        self.queuelength.append(queuelength_current)

        return np.mean(self.queuelength) if len(self.queuelength) else 0
    
    def reset(self):
        self.queuelength = []
    
    def get_info(self):
        return np.mean(self.queuelength) if len(self.queuelength) else 0