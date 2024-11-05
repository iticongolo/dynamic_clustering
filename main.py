import pandas as pd

from core.util.data import Data
from core.util.input_to_data import *
from core.util.util import *
from dynamic_clustering import DynamicClustering
from function import Function
from generators import SinGen, RampGen
from network_topology import Topology
from core.util import *
import matplotlib.pyplot as plt
import matplotlib.dates as m_dates
from simulations.json_file_test import JsonfileTest as app


class FunctionData:
    def __init__(self, id, data):
        self.id = id
        self.data = data


forecast = Forecast()

# Generate the network topology
servers_location = [(3.75, 14.5), (4.5, 11.25), (8.5, 13.5), (13.75, 6.25), (14.5, 3.0), (19.5, 2.0), (21.5, 4.5),
                    (17.5, 5.5), (15.75, 15.0), (19.75, 14.5), (22.5, 17.5), (24.75, 15.0), (22.5, 12.5)]
servers = get_severs_list(total_servers=13, cores=2000, memory=4000, location=servers_location)

topology = Topology(nodes=servers)
topology.generate_network_delays()

# for node in topology.nodes:
#     print(f'Node{node.id}-Location={node.location}')
clusters = topology.generate_balanced_clusters(delay_threshold=5)

# print('+++++++++++++++++++++++++++BEFORE PREDICTION+++++++++++++++++++++++++++++++++++++')
# for cluster in clusters:
#     print(f'Cluster{cluster.id}={cluster.list_nodes()}')
#     for node in cluster.nodes:
#         print(f'Node{node.id}| U={node.cores} |Uav={node.cores_available}| M={node.memory} |Mav={node.memory_available}')
#     print(f'#Cluster{cluster.id}={len(cluster.nodes)}| Cores={cluster.capacity_cores} '
#           f'|Cores-available={cluster.cores_available}|Memory={cluster.capacity_memory}'
#           f'|Memory-available={cluster.memory_available}')
#     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
#
# print('+++++++++++++++++++++++++++AFTER PREDICTION++++++++++++++++++++++++++++++++++++')
# for cluster in clusters:
#     print(f'Cluster{cluster.id}={cluster.list_nodes()}')
#     for node in cluster.nodes:
#         print(f'Node{node.id}| U={node.cores} |Uav={node.cores_available}| M={node.memory} |Mav={node.memory_available}')
#     print(f'#Cluster{cluster.id}={len(cluster.nodes)}| Cores={cluster.capacity_cores} '
#           f'|Cores-available={cluster.cores_available}|Memory={cluster.capacity_memory}'
#           f'|Memory-available={cluster.memory_available}')
#     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
# # # Display the generated servers and their attributes
# # for server in network_topology:
# #     print(f"Server {server.id}: Location={server.location}, Cores={server.cores}, Memory={server.memory}GB")


functions_names = ['f0','f1','f2','f3','f4']
functions=[]
for i in range(len(functions_names)):
    functions.append(Function(i, name=functions_names[i]))

clusters[0].functions = functions
clusters[1].functions = functions
clusters[2].functions = functions
topology.initial_clusters = copy.deepcopy(clusters)
topology.current_clusters = clusters

dynamic_clustering = DynamicClustering(topology, functions)



# [c0[id_f|data_frame|...],... ck[id_f|data_frame|...]]
list_historical_workload = [[] for _ in range(len(clusters))]
list_predicted_workload = [[] for _ in range(len(clusters))]


# # GENERATE WORKLOAD
# gen_sin_f0_c0 = SinGen(20, 50, 110)
# gen_sin_f0_c0.name = "SIN20,50,110"
# gen_ramp_f1_c0 = RampGen(1, 1200)
# gen_ramp_f1_c0.name = "RAMP1,400"
#
# # gen_c3 = RampGen(2, 260)
# # gen_c3.name = "RAMP2,260"
# data_f0_c0 = forecast.generate_initial_dataset(gen_sin_f0_c0, periods=1000)
# data_f1_c0 = forecast.generate_initial_dataset(gen_ramp_f1_c0, periods=1000)
#
# # create initial dataframe for entrypoint functions on each cluster
# df_f0_c0 = pd.DataFrame(data_f0_c0)
# df_f0_c0.name = gen_sin_f0_c0.name
# df_f1_c0 = pd.DataFrame(data_f1_c0)
# df_f1_c0.name = gen_ramp_f1_c0.name
#
# df_f0_c0.set_index('time', inplace=True)
# df_f1_c0.set_index('time', inplace=True)
#
# list_historical_workload[0].append(FunctionData(0, df_f0_c0))
# list_historical_workload[0].append(FunctionData(1, df_f1_c0))
#
# dynamic_clustering.historical_topology_workload = list_historical_workload
# external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
#                                         for _ in range(len(topology.initial_clusters))]
# sample_data = 80
# forecast_points = 30
# # df_list = [df_c1, df_c2, df_c3]
# i = 0  # cluster id
# for c_hist in list_historical_workload:
#     if len(c_hist) > 0:
#         j = 0
#         for f_data in c_hist:
#             f_id = f_data.id
#             f_df = f_data.data
#             forecast_df = forecast.list_forecasted_data_poits(f_df, sample_data, forecast_points)
#             list_predicted_workload[i].append(FunctionData(f_id, forecast_df))
#
#             # to be conservative, take the maximum predicted workload for each external function in each cluster
#             external_predicted_topology_workload[i][f_id] = round(max(forecast_df["forecast"].values.tolist()))
#             # print(f'F{f_id}_forecast={round(max(forecast_df["forecast"].values.tolist()))}')
#
#             plt.plot(f_df.index, f_df['workload'], label='Real data')
#             plt.plot(forecast_df.index, forecast_df['forecast'], label='Forcast', color='red')
#             plt.legend()
#             plt.title(f'Workload Forecast in the next 15 min F{f_id} in cluster {i}')
#             plt.xlabel('time(s)')
#             plt.ylabel('workload')
#             # Access the current axis
#             ax = plt.gca()
#             # Set major ticks to every 30 seconds
#             ax.xaxis.set_major_locator(m_dates.SecondLocator(interval=600))
#
#             # Set formatter to display only minutes and seconds
#             ax.xaxis.set_major_formatter(m_dates.DateFormatter('%M:%S'))
#
#             # Reduce overlap by setting the maximum number of ticks and rotating labels
#             plt.gcf().autofmt_xdate()  # Auto format the x-axis labels
#
#             # Rotate and format the x-axis labels
#             plt.xticks(rotation=45)
#             plt.tight_layout()
#             plt.show()
#             plt.clf()  # Clears the current plot
#             j = j+1
#     i = i+1
# dynamic_clustering.external_predicted_topology_workload = external_predicted_topology_workload
input = app.input
data = Data()
data.clusters = clusters
setup_community_data(data, input)
setup_runtime_data(data, input)

# total_workload_predict = dynamic_clustering.get_topology_total_workload_prediction(data)
#
# dynamic_clustering.change_clusters(data)  # TODO Follow
#
# print(f'++++++++++++++++break++++++++++++++++')
# print(f'Nodes={[[node.id for node in c.nodes] for c in topology.initial_clusters]}')
# overloaded, underloaded = dynamic_clustering.get_topology_status_prediction(data)
#
# print(f'++++++++++++++++break 1++++++++++++++++')
# print(f'status={[c.status for c in clusters]}')
# over = []
# under = []
#
# for c_o in overloaded:
#     over.append(c_o.id)
#
# for c_u in underloaded:
#     under.append(c_u.id)
# print(f'OVER={over}, UNDER={under}')
#
# for cluster in clusters:
#     print(f'All_Nodes C{cluster.id}={[node.id for node in cluster.all_nodes]}')
#     print(f'Cluster{cluster.id}={cluster.list_nodes()}')
#     for node in cluster.nodes:
#         print(f'Node{node.id}| U={node.cores} |Uav={node.cores_available}| M={node.memory} |Mav={node.memory_available}')
#     print(f'#Cluster{cluster.id}={len(cluster.nodes)}| Cores={cluster.capacity_cores} '
#           f'|Cores-available={cluster.cores_available}|Memory={cluster.capacity_memory}'
#           f'|Memory-available={cluster.memory_available}')
#     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
hist_cores = dynamic_clustering.historical_total_requested_cores_topology


def print_all(dynamic_clustering, topology, data):
    dynamic_clustering.external_predicted_topology_workload = external_predicted_topology_workload
    total_workload_predict = dynamic_clustering.get_topology_total_workload_prediction(data)
    print(f'Total W={total_workload_predict}')
    print(f'CLUSTERS-BEFORE={[[node.id for node in c.nodes] for c in topology.current_clusters]}')
    print(f'CAPACITY-CLUSTERS-BEFORE={[c.capacity_cores for c in topology.current_clusters]}')
    print(f'PREDICTED-CORES-AVAILABLE-BEFORE={[c.predicted_cores_available for c in topology.current_clusters]}')
    for c in topology.current_clusters:
        print(f'RECEIVED-NODES-BEFORE[C{c.id}]={[node.id for node in c.received_nodes]}')
        print(f'RECEIVED-NODES-ALLOCATED-CORES-BEFORE[C{c.id}]={[(node.id, c.received_nodes_allocated_cores[node.id]) for node in c.received_nodes]}')
    dynamic_clustering.change_clusters(data)
    print(f'Historical-Cores_needed={dynamic_clustering.historical_total_requested_cores_topology}')
    print(f'CLUSTERS-AFTER={[[node.id for node in c.nodes] for c in topology.current_clusters]}')
    print(f'CAPACITY-CLUSTERS-AFTER={[c.capacity_cores for c in topology.current_clusters]}')
    for c in topology.current_clusters:
        print(f'RECEIVED-AFTER[C{c.id}]={[node.id for node in c.received_nodes]}')
        print(
            f'RECEIVED-NODES-ALLOCATED-CORES-AFTER[C{c.id}]={[(node.id, c.received_nodes_allocated_cores[node.id]) for node in c.received_nodes]}')
    print(f'status-after={[c.status for c in topology.current_clusters]}')
    over = []
    under = []
    requested_cores = dynamic_clustering.cluster_cores_requested(data)
    overloaded, underloaded = dynamic_clustering.get_underloaded_overloaded_clusters(requested_cores)
    for c_o in overloaded:
        over.append(c_o.id)
    for c_u in underloaded:
        under.append(c_u.id)
    print(f'OVERLOADED={over}, UNDERLOADED={under}')
#     print(f'Historical Cores Request0={[[cores for cores in c] for c in hist_cores]}')
#
# # print(f'EXTERNAL={external_predicted_topology_workload}')
# # compute the total workload (internal workload) for each function in each cluster
#
#  ROUND 2
print('==================ROUND 1===============================')
external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
                                        for _ in range(len(topology.initial_clusters))]

external_predicted_topology_workload[0][0] = 400  # workload of C0|f0
external_predicted_topology_workload[0][1] = 900  # workload of C0|f1
external_predicted_topology_workload[1][0] = 15  # workload of C1|f0
external_predicted_topology_workload[1][1] = 10  # workload of C1|f1
print_all(dynamic_clustering, topology, data)


# for cluster in clusters:
#     print(f'Cluster{cluster.id}={cluster.list_nodes()}')
#     for node in cluster.nodes:
#         print(f'Node{node.id}| U={node.cores} |Uav={node.cores_available}| M={node.memory} |Mav={node.memory_available}')
#     print(f'#Cluster{cluster.id}={len(cluster.nodes)}| Cluster-status={cluster.status}| Cores={cluster.capacity_cores} '
#           f'|Cores-available={cluster.cores_available}|Memory={cluster.capacity_memory}'
#           f'|Memory-available={cluster.memory_available}')
#     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

# # ROUND 3
# print('==================ROUND 3===============================')
# external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
#                                         for _ in range(len(topology.initial_clusters))]
#
# external_predicted_topology_workload[2][0] = 100  # workload of C2|f0
# external_predicted_topology_workload[2][1] = 100  # workload of C2|f1
# dynamic_clustering.external_predicted_topology_workload = external_predicted_topology_workload
# total_workload_predict = dynamic_clustering.get_topology_total_workload_prediction(data)
#
# dynamic_clustering.change_clusters(data)
# print(f'++++++++++++++++break++++++++++++++++')
# print(f'Nodes={[[node.id for node in c.nodes] for c in clusters]}')
# overloaded, underloaded = dynamic_clustering.get_topology_status_prediction(data)
#
# print(f'++++++++++++++++break 1++++++++++++++++')
# print(f'status={[c.status for c in clusters]}')
# over = []
# under = []
#
# for c_o in overloaded:
#     over.append(c_o.id)
#
# for c_u in underloaded:
#     under.append(c_u.id)
# print(f'OVER={over}, UNDER={under}')
#
# hist_cores = dynamic_clustering.historical_total_requested_cores_topology
# print(f'Historical Cores Request={[[cores for cores in c] for c in hist_cores]}')
#
#
# for cluster in clusters:
#     print(f'Cluster{cluster.id}={cluster.list_nodes()}')
#     for node in cluster.nodes:
#         print(f'Node{node.id}| U={node.cores} |Uav={node.cores_available}| M={node.memory} |Mav={node.memory_available}')
#     print(f'#Cluster{cluster.id}={len(cluster.nodes)}| Cores={cluster.capacity_cores} '
#           f'|Cores-available={cluster.cores_available}|Memory={cluster.capacity_memory}'
#           f'|Memory-available={cluster.memory_available}')
#     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
# # Display the generated servers and their attributes
# for server in network_topology:
#     print(f"Server {server.id}: Location={server.location}, Cores={server.cores}, Memory={server.memory}GB")


print('==================ROUND 2 ===============================')
external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
                                        for _ in range(len(topology.initial_clusters))]

external_predicted_topology_workload[1][0] = 400  # workload of C2|f0
external_predicted_topology_workload[1][1] = 200  # workload of C2|f1
print_all(dynamic_clustering, topology, data)


print('==================ROUND 3 ===============================')
external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
                                        for _ in range(len(topology.initial_clusters))]

external_predicted_topology_workload[2][0] = 800  # workload of C2|f0
external_predicted_topology_workload[2][1] = 500  # workload of C2|f1
print_all(dynamic_clustering, topology, data)


print('==================ROUND 4===============================')
external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
                                        for _ in range(len(topology.initial_clusters))]

external_predicted_topology_workload[0][0] = 5  # workload of C2|f0
external_predicted_topology_workload[0][1] = 10  # workload of C2|f1
print_all(dynamic_clustering, topology, data)


print('==================ROUND 5===============================')
external_predicted_topology_workload = [[0 for _ in range(len(dynamic_clustering.functions))]
                                        for _ in range(len(topology.initial_clusters))]

external_predicted_topology_workload[1][0] = 800  # workload of C2|f0
external_predicted_topology_workload[1][1] = 700  # workload of C2|f1
print_all(dynamic_clustering, topology, data)


