import copy

from core.util.util import *


class Topology:

    def __init__(self, status=1, nodes=None, network_delays=None, initial_clusters=None):
        self.status = status
        self.nodes = nodes if nodes is not None else []  # a list

        # e.g.: [[0,3,1],[3,0,5],[1,5,0]] delays of nodes n0, n1, n2
        self.network_delays = network_delays if network_delays is not None else []

        # e.g.: [n0|c1|, n1|c3|, n2|c5|, n3|c1|...] node is the index
        self.static_node_cluster = [None for _ in range(len(nodes))]
        self.initial_clusters = initial_clusters if initial_clusters is not None else []  # a list
        self.current_clusters = copy.deepcopy(self.initial_clusters)

    def generate_clusters(self, delay_threshold=10):
        clusters = []
        nodes = copy.deepcopy(self.nodes)
        cluster_id = 0
        while len(nodes) > 0:
            cluster = Cluster(cluster_id, all_nodes=self.nodes)
            i = 0
            j = 1
            cluster.add_node(nodes[0], nodes[0].cores, nodes[0].memory, cluster_generation=1)
            nodes.pop(0)
            while i < j:
                k = 0
                for near_node in nodes:
                    if self.network_delays[cluster.nodes[i].id][near_node.id] <= delay_threshold:
                        cluster.add_node(near_node, near_node.cores, near_node.memory, cluster_generation=1)
                        nodes.pop(k)
                        j = j + 1
                    k = k+1
                i = i+1
            cluster.initialize_cluster()
            clusters.append(cluster)
            cluster_id = cluster_id+1
        self.generate_static_node_cluster(clusters)
        return clusters

    def generate_balanced_clusters(self, delay_threshold=10, max_nodes_threshold=10):
        clusters = []
        nodes = copy.deepcopy(self.nodes)
        cluster_id = 0
        while len(nodes) > 0:
            cluster = Cluster(cluster_id, all_nodes=self.nodes)
            i = 0
            j = 1
            cluster.add_node(nodes[0], nodes[0].cores, nodes[0].memory, cluster_generation=1)
            cluster.update_original_resources(nodes[0].cores, nodes[0].memory)
            nodes.pop(0)
            while i < j:
                k = 0
                for near_node in nodes:
                    if len(cluster.nodes) >= max_nodes_threshold:
                        break
                    if self.network_delays[cluster.nodes[i].id][near_node.id] <= delay_threshold:
                        cluster.add_node(near_node, near_node.cores, near_node.memory, cluster_generation=1)
                        cluster.update_original_resources(near_node.cores, near_node.memory)
                        nodes.pop(k)
                        j = j + 1
                    k = k+1
                i = i+1

            cluster.minimum_capacity_cores = 0.2 * cluster.original_cores
            cluster.minimum_capacity_memory = 0.2 * cluster.original_memory
            # cluster.initialize_cluster()
            cluster.update_centroid()
            clusters.append(cluster)
            cluster_id = cluster_id+1
        self.generate_static_node_cluster(clusters)
        # for cluster in clusters:
        #     print(f'AAA-Cluster{cluster.id}|Cores={cluster.capacity_cores}|Cores_av=
        #     {cluster.cores_available}|M={cluster.capacity_memory}|Mav={cluster.memory_available}')
        return clusters

    # def re_balancing_clusters(self, ):

    def set_status(self, status):
        self.status = status

    def generate_static_node_cluster(self, clusters):
        for c in copy.deepcopy(clusters):
            for node in c.nodes:
                self.static_node_cluster[node.id] = c

    def set_network_delays(self, delays):
        self.network_delays = delays

    def generate_network_delays(self):
        self. network_delays = [[0 for _ in range(len(self.nodes))] for _ in range(len(self.nodes))]
        for node1 in self.nodes:
            for node2 in self.nodes:
                if node1.id == node2.id:
                    self.network_delays[node1.id][node2.id] = 0
                else:
                    self.network_delays[node1.id][node2.id] = get_distance(node1.location, node2.location)
