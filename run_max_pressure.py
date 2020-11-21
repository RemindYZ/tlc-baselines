import gym
from environment import TSCEnv
from world import World
from generator import LaneVehicleGenerator
from agent import MaxPressureAgent
from metric import TravelTimeMetric, QueueLengthMetric
import argparse

# parse args
parser = argparse.ArgumentParser(description='Run Example')
parser.add_argument('config_file', type=str, help='path of config file')
parser.add_argument('--thread', type=int, default=1, help='number of threads')
parser.add_argument('--steps', type=int, default=100, help='number of steps')
parser.add_argument('--delta_t', type=int, default=20, help='how often agent make decisions')
args = parser.parse_args()

# create world
world = World(args.config_file, thread_num=args.thread)

# create agents
agents = []
for i in world.intersections:
    action_space = gym.spaces.Discrete(len(i.phases))
    agents.append(MaxPressureAgent(
        action_space, i, world, 
        LaneVehicleGenerator(world, i, ["lane_count"], in_only=True)
    ))

# create metric
metric = [TravelTimeMetric(world), QueueLengthMetric(world)]
world.subscribe("lane_waiting_time_count")

# create env
env = TSCEnv(world, agents, metric)

# simulate
obs = env.reset()
actions = []
for i in range(args.steps):
    actions = []
    for agent_id, agent in enumerate(agents):
        actions.append(agent.get_action(obs[agent_id]))
    obs, rewards, dones, info = env.step(actions)
    for metric_obj in env.metric:
        metric_obj.update()
    #print(world.intersections[0]._current_phase, end=",")
    # print(obs, actions)
    # if i % 100 == 50:
    #     print(str(i)+'-th steps')
    #     print(env.eng.get_average_travel_time())
    #     print("=====================")
    #print(obs)
    #print(rewards)
    # print(info["metric"])

print("Final Travel Time is %.4f" % env.metric[0].update(done=True))
print("Average Queue Length is %.4f" % env.metric[1].update())
print("Average Delay Time is %.4f" % (sum([v for v in env.world.vehicle_waiting_time.values()])/len(env.world.vehicle_waiting_time)))
