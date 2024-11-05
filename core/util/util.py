import copy
import math

from cluster import Cluster
from core.util.forecast import Forecast
import random

from node import Node


def get_node_position(nodes, node):
    for i in range(len(nodes)):
        if node.id == nodes[i].id:
            return i
    return -1


def get_underloaded_nodes(underloaded_clusters):
    nodes = []
    for c in underloaded_clusters:
        for node in c.nodes:
            if node.status == 1:
                nodes.append(node)
    return nodes


# NOTE Verified
def get_closest_node(cluster, underloaded_nodes):
    centroid_nodes_network_delay = cluster.centroid_nodes_network_delay
    delay = centroid_nodes_network_delay[underloaded_nodes[0].id]
    closest_node = underloaded_nodes[0]
    i = 0
    pos = 0
    for node in underloaded_nodes:
        if delay > centroid_nodes_network_delay[node.id]:
            delay = centroid_nodes_network_delay[node.id]
            closest_node = node
            pos = i
        i = i+1
    return closest_node, pos


# return the cluster in current clusters which the node belongs to (not shared with)
def get_initial_cluster(initial_clusters, node):
    cluster = Cluster(0)
    # first get the correspondent c.id from initial cluster and use it to search the cluster on current cluster
    for c in copy.deepcopy(initial_clusters):
        pos = get_node_position(c.nodes, node)
        if pos >= 0:
            return c
    return cluster


# Get the prediction of external workload (entry point function) in a single cluster and function NOTE: DONE
def get_cluster_function_external_workload_prediction(cluster_workload, function_id, num_points_sample,
                                                      num_forecast_points, slot_length, freq):
    forecast = Forecast()
    data = cluster_workload[function_id]
    external_predicted_workload = forecast.list_forecasted_data_poits(data, num_points_sample, num_forecast_points,
                                                                      slot_length=slot_length, freq=freq)
    return external_predicted_workload


def generate_network_topology(k, a, b, c, d, min_cores=1, max_cores=16, min_memory=4, max_memory=64):
    """
    Generate a random network topology with k servers, each having random (x, y) coordinates, cores, and memory.

    Parameters:
    k (int): Number of servers
    a, b (int): Range for x-coordinates
    c, d (int): Range for y-coordinates
    min_cores, max_cores (int): Range for random number of cores for each server
    min_memory, max_memory (int): Range for random memory (in GB) for each server

    Returns:
    list of dicts: A list where each dict represents a server with its attributes
    """
    servers = []
    for i in range(k):
        # Generate random x and y coordinates
        x = round(random.uniform(a, b),2)
        y = round(random.uniform(c, d),2)

        # Randomly assign cores and memory to the server
        cores = random.randint(min_cores, max_cores)
        memory = random.randint(min_memory, max_memory)
        node = Node(i)
        # Create a server representation
        node.location = (x, y)
        node.cores = cores
        node.memory = memory
        node.cores_available = cores
        node.memory_available = memory
        node.initialization()
        servers.append(node)
    return servers


def get_severs_list(total_servers=1, cores=2000, memory=4000, location=(0, 0)):
    servers = []
    for i in range(total_servers):
        node = Node(i)
        node.location = (location[i])
        node.cores = cores
        node.cores_available = cores
        node.memory_available = memory
        node.memory = memory
        node.initialization()
        servers.append(node)
    return servers


def get_distance(location1, location2):
    euclidian_distance = round(math.sqrt((location1[0] - location2[0]) ** 2 + (location1[1] - location2[1]) ** 2),2)
    return euclidian_distance
