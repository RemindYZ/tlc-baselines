from . import BaseAgent

class MPModefyAgent(BaseAgent):
    """
    Agent using Max-Pressure method to control traffic light
    """
    def __init__(self, action_space, I, world, ob_generator=None):
        super().__init__(action_space)
        self.I = I
        self.world = world
        self.world.subscribe("lane_count")
        self.ob_generator = ob_generator
        
        # the minimum duration of time of one phase
        self.t_min = 10

    def get_ob(self):
        if self.ob_generator is not None:
            return self.ob_generator.generate() 
        else:
            return None

    def get_action(self, ob):
        # get lane pressure
        lvc = self.world.get_info("lane_count")

        action = self.I.current_phase
        if self.I.current_phase_time < self.t_min:
            return action
        phase_id_list = [action, (action + 1)%self.action_space.n]
        max_pressure = None
        for phase_id in phase_id_list:
            pressure = sum([lvc[start] - lvc[end] for start, end in self.I.phase_available_lanelinks[phase_id]])
            if max_pressure is None or pressure > max_pressure:
                action = phase_id
                max_pressure = pressure

        return action

    def get_reward(self):
        return None