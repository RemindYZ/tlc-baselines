import argparse
import json
import random as rd

parser = argparse.ArgumentParser()
parser.add_argument('config_file', type=str, help='vehicle config')
parser.add_argument('--output', type=str, help='the output path of flow file')
args = parser.parse_args()

config_file = args.config_file
output_file = args.output

with open(config_file) as f:
    flow_config = json.load(f)

vehicle = flow_config["vehicle"]
interval = flow_config["interval"]
roadnet_file = flow_config["roadnet"]
stage_time = flow_config["stage_time"]
od_matrix = flow_config["od_matrix"]
seed = flow_config["seed"]

with open(roadnet_file) as f:
    roadnet = json.load(f)

virtual_intersections = [vir_inter for vir_inter in roadnet["intersections"] if vir_inter["virtual"]]

# intersection的approach映射
intersection_dict = {}
for vir_inter in virtual_intersections:
    road_prefix = "road"+vir_inter["id"][-4:]
    in_approach = None
    out_approach = None
    assert len(vir_inter["roads"]) == 2
    for road in vir_inter["roads"]:
        if road.startswith(road_prefix):
            in_approach = road
        else:
            out_approach = road
    assert in_approach
    assert out_approach
    intersection_dict[vir_inter["id"]] = {"in_approach": in_approach, "out_approach": out_approach}

# OD矩阵转换为概率 & route list
route_p_list = []
for in_intersection in od_matrix.keys():
    for out_intersection in od_matrix[in_intersection].keys():
        prob = od_matrix[in_intersection][out_intersection] / 3600
        in_approach = intersection_dict[in_intersection]["in_approach"]
        out_approach = intersection_dict[out_intersection]["out_approach"]
        route_p_list.append({"route": [in_approach, out_approach], "prob": prob})


# 车流生成
flow_list = []

rd.seed(seed)
for i in range(1, stage_time, 1):
    for route_p in route_p_list:
        if rd.uniform(0, 1) < route_p['prob']:
            flow_list.append({"vehicle": vehicle, "route": route_p['route'], "interval": interval, "startTime": i, "endTime": i})

with open(output_file, 'w') as f:
    f.write(json.dumps(flow_list, indent=4))
