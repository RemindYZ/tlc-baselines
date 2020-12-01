from . import BaseAgent

class FPAgent(BaseAgent):
    """
    Agent using Fix-Plan Control method to control traffic light
    """
    def __init__(self, action_space, I, green_time):
        super().__init__(action_space)
        self.I = I
        self.green_time = green_time

    def get_ob(self):
        return None

    def get_action(self, ob):
        action = self.I.current_phase
        if self.I.current_phase_time >= self.green_time[action]:
            action = (action + 1) % self.action_space.n
        else:
            action = action
        return action

    def get_reward(self):
        return None