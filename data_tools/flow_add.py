import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--tf_file_list', type=str, help='list of path of traffic flow file, split by comma')
parser.add_argument('--s_interval', type=int, default=3600, help='the interval of each flow file')
parser.add_argument('--output', type=str, help='path file to output')
args = parser.parse_args()

path_list = list(args.tf_file_list.split(','))
s_interval = args.s_interval
output = args.output

start_interval = 0

for file in path_list:
    if start_interval == 0:
        with open(file) as f:
            res_flow = json.load(f)
        start_interval += s_interval
    else:
        with open(file) as f:
            traffic_flow = json.load(f)
        for flow in traffic_flow:
            flow['startTime'] += start_interval
            flow['endTime'] += start_interval
            res_flow.append(flow)
        start_interval += s_interval

with open(output, 'w') as f:
    f.write(json.dumps(res_flow, indent=4))
        

