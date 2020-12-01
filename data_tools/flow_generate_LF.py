import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('config_file', type=str, help='vehicle config')
parser.add_argument('--output', type=str, help='the output path of flow file')
args = parser.parse_args()

config_file = args.config_file
output_file = args.output

with open(config_file) as f:
    flow_config = json.load(f)

vehicle = flow_config["vehicle"]
roadnet_file = flow_config["roadnet"]
flow_file = flow_config["flow"]
start_time = flow_config["start_time"]

with open(roadnet_file) as f:
    roadnet = json.load(f)


def gen(L):
    return [int(L[7]), int(L[8]), int(L[19]), int(L[20]), int(L[21])]

with open(flow_file) as f:
    flow_list =[gen(line.split(',')) for line in f.readlines()]

flow_list.sort(key=lambda x: (x[2], x[3], x[4]))

in_approach_dict = {
    1: {
        "in":"intersection_1_0",
        2: "intersection_0_1",
        3: "intersection_1_2",
        4: "intersection_2_1"
    },
    2: {
        "in":"intersection_2_1",
        2: "intersection_1_0",
        3: "intersection_0_1",
        4: "intersection_1_2"
    },
    3: {
        "in":"intersection_1_2",
        2: "intersection_2_1",
        3: "intersection_1_0",
        4: "intersection_0_1"
    },
    4: {
        "in":"intersection_0_1",
        2: "intersection_1_2",
        3: "intersection_2_1",
        4: "intersection_1_0"
    }
}

virtual_intersections = [vir_inter for vir_inter in roadnet["intersections"] if vir_inter["virtual"]]

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
    intersection_dict[vir_inter["id"]]={"in_approach": in_approach, "out_approach": out_approach}

flow_list_cityflow = []

for flow in flow_list:
    in_approach = intersection_dict[in_approach_dict[flow[0]]["in"]]["in_approach"]
    out_approach = intersection_dict[in_approach_dict[flow[0]][flow[1]]]["out_approach"]
    time = (flow[2]-start_time) * 3600 + flow[3] * 60 + flow[4]
    flow_list_cityflow.append({"vehicle": vehicle, "route": [in_approach, out_approach], "interval": 5, "startTime": time, "endTime": time})


with open(output_file, 'w') as f:
    f.write(json.dumps(flow_list_cityflow, indent=4))