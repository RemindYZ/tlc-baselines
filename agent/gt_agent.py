from . import BaseAgent

def sgn(x):
    return 1 if x else 0

class GTAgent(BaseAgent):
    """
    Coodination Game Method
    Traffic Signal Control for Isolated Intersection Based on Coordination Game and Pareto Efficiency(ITSC 2019)
    """
    def __init__(self, action_space, I, world, delta_t = 10, yellow_time = 3):
        super().__init__(action_space)
        self.I = I
        self.world = world
        self.world.subscribe(["lane_vehicles", "lane_waiting_count"])
        self.delta_t = delta_t # 预估时间
        self.yellow_time = yellow_time #黄灯时间
        self.right_lane = ['road_2_1_2_2', 'road_1_0_1_2', 'road_0_1_0_2', 'road_1_2_3_2'] # 不考虑右转车道影响
        self.vehicle_gap = 7.5

        self.t_min = 3 # 最短绿灯时间
        self.t_max = 30 # 最长绿灯时间
        self.weight = [0.55, 0.45] # 权重比例
        self.speed_threshold = 0.1
        self.pareto = 1
        self.n_phase = len(self.I.phases)
        if len(self.weight) < self.n_phase:
            self.weight += [0] * (self.n_phase - len(self.weight))
        assert self.n_phase >= 2
        assert len(self.weight) == self.n_phase
    
    def get_ob(self):
        return None

    def get_reward(self):
        return None

    def get_action(self, ob):
        lane_vehicles = self.world.get_info("lane_vehicles")
        lane_waiting_count = self.world.get_info("lane_waiting_count")
        vehicle_speed = self.world.eng.get_vehicle_speed()
        vehicle_distance = self.world.eng.get_vehicle_distance()

        action = self.I.current_phase
        if self.I.current_phase_time >= self.t_min:
            start_lanes = [[lane for lane in self.I.phase_available_startlanes[i % self.n_phase] if lane not in self.right_lane]\
                 for i in range(action, action + self.n_phase)]
            payoff = self.get_keep_payoff(start_lanes, lane_vehicles, lane_waiting_count, vehicle_speed, vehicle_distance)
            keep_payoff = [self.weight[0] * payoff[0], sum([self.weight[i] * payoff[i] for i in range(1, len(self.weight))])]
            payoff = self.get_switch_payoff(start_lanes, lane_vehicles, lane_waiting_count, vehicle_speed, vehicle_distance)
            switch_payoff = [self.weight[0] * payoff[0], sum([self.weight[i] * payoff[i] for i in range(1, len(self.weight))])]
            if keep_payoff[0] > self.pareto:
                return action
            elif keep_payoff[0] + keep_payoff[1] <= switch_payoff[0] + switch_payoff[1]:
                return action
            else:
                return (action + 1) % self.action_space.n
        elif self.I.current_phase_time == self.t_max:
            return (action + 1) % self.action_space.n
        else:
            return action
    
    def get_keep_payoff(self, start_lanes, lane_vehicles, lane_waiting_count, vehicle_speed, vehicle_distance):
        res_payoff = []
        for i, s_lanes in enumerate(start_lanes):
            payoff = 0
            for lane in s_lanes:
                lane_vehicle_id_list = lane_vehicles[lane]
                ql = lane_waiting_count[lane]
                road_length = self.world.all_roads_info[lane[:-2]]["length"] - self.I.width
                if i == 0:
                    departure = sum([sgn((road_length - vehicle_distance[v_id])/vehicle_speed[v_id] < self.delta_t) \
                        for v_id in lane_vehicle_id_list if vehicle_speed[v_id] >= self.speed_threshold])
                    arrival = sum([sgn((road_length - vehicle_distance[v_id])/vehicle_speed[v_id] >= self.delta_t) \
                        for v_id in lane_vehicle_id_list if vehicle_speed[v_id] >= self.speed_threshold])
                else:
                    departure = 0
                    arrival = sum([sgn((road_length - vehicle_distance[v_id]) >= ql * self.vehicle_gap) for v_id in lane_vehicle_id_list])
                payoff += ql + arrival - departure
            res_payoff.append(payoff)
        return res_payoff

    def get_switch_payoff(self, start_lanes, lane_vehicles, lane_waiting_count, vehicle_speed, vehicle_distance):
        res_payoff = []
        for i, s_lanes in enumerate(start_lanes):
            payoff = 0
            for lane in s_lanes:
                lane_vehicle_id_list = lane_vehicles[lane]
                ql = lane_waiting_count[lane]
                road_length = self.world.all_roads_info[lane[:-2]]["length"] - self.I.width
                max_speed = self.world.all_lanes_info[lane]["maxSpeed"]
                if i == 1:
                    departure = sum([sgn((self.delta_t - self.yellow_time) * max_speed / 2 > (road_length - vehicle_distance[v_id])) \
                        for v_id in lane_vehicle_id_list])
                    arrival = sum([sgn((road_length - vehicle_distance[v_id])/vehicle_speed[v_id] >= self.delta_t) \
                        for v_id in lane_vehicle_id_list if vehicle_speed[v_id] >= self.speed_threshold])
                else:
                    departure = 0
                    arrival = sum([sgn((road_length - vehicle_distance[v_id]) >= ql * self.vehicle_gap) for v_id in lane_vehicle_id_list])
                payoff += ql + arrival - departure
            res_payoff.append(payoff)
        return res_payoff
