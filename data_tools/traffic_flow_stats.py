# 车流OD矩阵统计文件
# 要求intersection和road的命名和syn中的规律一致，因此不适用与曼哈顿数据集
# 命名规律：intersection_a_b，那么该intersection的出车的approach满足road_a_b_n的规则

# 可以针对很长时间的车流划分时间段统计
# total_time最好小于s_interval的整数倍，比如--total_time 3599 --s_interval 3600或者类似--total_time 7199 --s_interval 3600都ok
# 不要出现--total_time 3600 --s_interval 3600或者类似--total_time 7200 --s_interval 3600，会导致多一个全为0的OD矩阵



import argparse
import json
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--tf_file', type=str, help='path of traffic flow file')
parser.add_argument('--roadnet_file', type=str, help='path of roadnet file')
parser.add_argument('--total_time', type=int, default=3599, help='the total time of this flow file')
parser.add_argument('--s_interval', type=int, default=3600, help='the interval of statistic')
args = parser.parse_args()

total_time = args.total_time
s_interval = args.s_interval

# if total_time%s_interval == 0:
#     N = int(total_time / s_interval)
# else:
N = int(total_time / s_interval) + 1

with open(args.tf_file) as f:
    traffic_flow = json.load(f)

with open(args.roadnet_file) as f:
    road_net = json.load(f)

virtual_intersections =[inter for inter in road_net["intersections"] if inter['virtual']]
n_origin = len(virtual_intersections)
# origin_roads = []
# destination_roads = []


# for vir_inter in virtual_intersections:
#     for road in vir_inter["roads"]:
#         if vir_inter.find(road) == 0:
#             origin_roads.append(road)
#         elif vir_inter.find(road) == -1:
#             destination_roads.append(road)
#         else:
#             raise ValueError('the name of road({}) does not match the inter({})'.format(road, vir_inter))

# assert len(origin_roads) == len(destination_roads)

time_intervals = [[int(i*s_interval), min(int((i+1)*s_interval), total_time)] for i in range(N)]

# n_origin_road = len(origin_roads)
# n_destination_road = len(destination_roads)
od_matrix = np.zeros(shape=(N, n_origin, n_origin))

wrong_num = 0
for vehicle in traffic_flow:
    route = vehicle['route']
    interval = vehicle['interval']
    start_time = vehicle['startTime']
    end_time = vehicle['endTime']
    if end_time > total_time:
        end_time = total_time

    origin_road, destination_road = route[0], route[-1]
    origin_ind, destination_ind = -1, -1
    for i in range(n_origin):
        if virtual_intersections[i]["id"] == 'intersection' + origin_road[4:8]:
            origin_ind = i
        if destination_road in virtual_intersections[i]["roads"]:
            destination_ind = i
    if origin_ind == -1 or destination_ind == -1:
        # print(vehicle)
        wrong_num += 1
        # raise ValueError('the origin has wrong value')

    if start_time == end_time:
        n = int(start_time / s_interval)
        od_matrix[n, origin_ind, destination_ind] += 1
    else:
        n_start = int(start_time / s_interval)
        n_end = int(end_time / s_interval)
        if n_start == n_end:
            od_matrix[n_start, origin_ind, destination_ind] += int((end_time - start_time)/interval)
        else:
            for i in range(n_start, n_end + 1, 1):
                if i == n_start:
                    od_matrix[i, origin_ind, destination_ind] += int(((i+1)*s_interval - start_time)/interval)
                elif i == n_end:
                    od_matrix[i, origin_ind, destination_ind] += int((end_time - i*s_interval)/interval)
                else:
                    od_matrix[i, origin_ind, destination_ind] += int(s_interval/interval)
print('total number of vehicles:' + str(len(traffic_flow)))
print('total number of wrong route: '+ str(wrong_num))
print('O-D intersection names：')
print([vir_inter["id"] for vir_inter in virtual_intersections])
for i in range(len(time_intervals)):
    print("====================")
    print(time_intervals[i])
    print(od_matrix[i])
print(np.sum(od_matrix))