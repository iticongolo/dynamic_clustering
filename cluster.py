import math

from core.util.util import *


class Cluster:
    def __init__(self, id, cores=0, memory=0, cores_available=0, memory_available=0, cluster_nodes=None,
                 all_nodes=None, centroid=(float('inf'), float('inf')), functions=None, status=1):
        self.id = id
        self.status = status
        self.original_cores = cores  # exclude cores allocated from another clusters by sharing cluster_nodes
        self.original_memory = memory  # exclude memory allocated to another clusters by sharing cluster_nodes
        self.cores_available = cores_available
        self.predicted_cores_available = cores_available
        self.memory_available = memory_available
        self.minimum_capacity_cores = 0  # recommended 20% of the cluster capacity
        self.minimum_capacity_memory = 0  # recommended 20% of the cluster capacity
        self.nodes = cluster_nodes if cluster_nodes is not None else []  # a list
        self.all_nodes = all_nodes if all_nodes is not None else []

        self.centroid = centroid  # (x,y)
        # e.g.: [n0|2ms|, n1|1ms|, n3|10ms|, ...] i.e. delay from centroid to node 0 is 2ms
        # we initialize the delays by infinity
        self.centroid_nodes_network_delay = [float('inf') for _ in range(len(self.all_nodes))]
        self.received_nodes = []

        # include all the cluster_nodes here and put zero by default
        self.received_nodes_allocated_cores = [0 for _ in range(len(self.all_nodes))]
        self.received_nodes_allocated_memory = []
        self.capacity_cores = cores  # include cores received from shared cluster_nodes
        self.capacity_memory = memory  # include memory received from shared cluster_nodes
        self.additional_cores_needed = 0
        self.functions = functions if functions is not None else []

    def set_centroid(self, centroid):
        self.centroid = centroid

    def set_status(self, status):
        self.status = status

    def set_cores_available(self, cores):
        self.cores_available = cores

    def set_functions(self, functions):
        self.functions = functions

    def set_memory_available(self, memory):
        self.memory_available = memory

    def set_received_node(self, node):
        self.received_nodes.append(node)

    def has_received_shared_nodes(self):
        return len(self.received_nodes) > 0

    def update_available_cores(self, new_cores):
        self.cores_available = self.cores_available + new_cores
        self.predicted_cores_available = self.predicted_cores_available + new_cores
        self.update_status_()

    def update_capacity_cores(self, new_cores):
        self.capacity_cores = self.capacity_cores + new_cores

    def update_original_resources(self, new_cores, new_memory):
        self.original_cores = self.original_cores+new_cores
        self.original_memory = self.original_memory + new_memory

    def update_available_memory(self, new_memory):
        self.memory_available = self.memory_available + new_memory

    def update_capacity_memory(self, new_memory):
        self.capacity_memory = self.capacity_memory + new_memory

    def update_status(self, required_cores):
        # print(f'required_cores AAAA={required_cores}')
        # print(f'capacity-cores AAAA={self.capacity_cores}')
        remained_cores = self.capacity_cores-required_cores
        if remained_cores < 0:
            self.status = -1  # overloaded
        else:
            if remained_cores <= 0.2*self.capacity_cores:
                self.status = 0  # fine
            else:
                self.status = 1  # underloaded

    def update_status_(self):
        if self.cores_available <= 0.2*self.capacity_cores:
            self.status = 0  # fine
        else:
            self.status = 1  # underloaded

    def initialize_cluster(self):
        for node in self.nodes:
            self.update_capacity_cores(node.cores)
            self.update_available_cores(node.cores)
            self.update_capacity_memory(node.memory)
            self.update_available_memory(node.memory)
            self.update_centroid()

    # Add a new shared node or only add the new cores allocation corresponding to the existing shared node
    def update_received_nodes(self, new_node, new_cores):
        node_not_exists = 1
        for node in self.received_nodes:
            if node.id == new_node.id:
                node_not_exists = 0
                break
        if node_not_exists:
            self.received_nodes.append(new_node)
        self.add_node(new_node, new_cores, new_node.memory_available)
        # self.update_capacity_cores(new_cores)
        self.received_nodes_allocated_cores[new_node.id] = self.received_nodes_allocated_cores[new_node.id] + new_cores
        # update the

    def add_node(self, new_node, new_cores, new_memory, cluster_generation=0):
        node_not_exists = 1
        for node in self.nodes:
            if node.id == new_node.id:
                node_not_exists = 0
                break
        if node_not_exists:
            self.nodes.append(new_node)
        if cluster_generation:
            self.update_resources(new_cores=new_cores, new_memory=new_memory)
        else:
            self.update_resources_capacity(new_cores=new_cores, new_memory=new_memory)

    # we only remove nodes shared with this cluster and never the nodes from initial cluster
    # when removing a node, the capacity of the cluster changes
    def remove(self, node):
        # print(f'Cluster [{self.id}]-Nodes BF={self.nodes}')
        pos = self.get_node_position(self.nodes, node)
        if pos >= 0:
            allocated_cores = self.received_nodes_allocated_cores[node.id]
            # node.memory_available is valid since the memory is not our focos
            self.update_resources_capacity(new_cores=-allocated_cores, new_memory=-node.memory_available)
            self.nodes.pop(pos)

        # print(f'Cluster [{self.id}]-Nodes AF={self.nodes}')

    def update_centroid(self):
        sum_x = 0
        sum_y = 0
        for node in self.nodes:
            sum_x = sum_x+node.location[0]
            sum_y = sum_y + node.location[1]
        self.centroid = (sum_x/len(self.nodes), sum_y / len(self.nodes))

    def update_centroid_nodes_network_delay(self, new_nodes):
        for node in new_nodes:
            eu_distance = round(
                math.sqrt((self.centroid[0] - node.location[0]) ** 2 + (self.centroid[1] - node.location[1]) ** 2), 2)
            self.centroid_nodes_network_delay[node.id] = eu_distance

    def list_nodes(self):
        list_nodes = []
        for node in self.nodes:
            list_nodes.append(f'Node{node.id}')
        return list_nodes
    # # update all the resources that will be available after serving the cluster
    # # workload on cluster_nodes received from other clusters. Remove the received cluster_nodes that will not be used
    # def update_cores_received_nodes(self, remain_cores_needed):  # TODO check later, seems to be inconcistente.
    #     # structure of cores_received_nodes [[node_id,cores allocated to this cluster],...]
    #     # e.g.: [[0,200],[11,500],[4,100],...]
    #     cores_needed = remain_cores_needed
    #     i = 0
    #     while i < len(self.received_nodes) and cores_needed > 0:
    #         diff = cores_needed - self.received_nodes[i].cores_available
    #         if diff > 0:  # the cores needed are more than available on the current node
    #             self.received_nodes_allocated_cores.append([self.received_nodes[i].id, self.received_nodes[i].cores_available])
    #             cores_needed = cores_needed - self.received_nodes[i].cores_available
    #             self.received_nodes[i].set_cores_available(0)  # all the remained cores were used
    #         else:
    #             self.received_nodes_allocated_cores.append(
    #                 [self.received_nodes[i].id, self.received_nodes[i].cores_available])
    #             self.received_nodes[i].set_cores_available(
    #                 self.received_nodes[i].cores_available - cores_needed)  # use all the remained cores
    #             cores_needed = 0
    #             self.received_nodes = self.received_nodes[:i+1]
    #             break
    #         i = i+1
    #     self.additional_cores_needed = cores_needed

    # def remove_received_node(self, node_id):
    #     for i in range(self.received_nodes.len):
    #         if self.received_nodes[i].id == node_id:
    #             self.received_nodes.pop(i)
    #             break

    # Check whether the cluster is predicted to be overloaded, fine or underloaded NOTE: DONE
    def update_resources_capacity(self, new_cores=0, new_memory=0):
        # remove= 1 remove resources, remove=0 add resources
        self.update_capacity_cores(new_cores)
        self.update_capacity_memory(new_memory)

    def update_resources(self, new_cores=0, new_memory=0):
        # remove= 1 remove resources, remove=0 add resources
        self.update_capacity_cores(new_cores)
        self.update_capacity_memory(new_memory)
        self.update_available_cores(new_cores)
        self.update_available_memory(new_memory)

    def update(self, cores_requested=0):
        if cores_requested > self.cores_available:
            self.cores_available = 0
        else:
            self.cores_available = self.cores_available-cores_requested

    def update_predicted_cores_available(self, requested_cores):
        self.predicted_cores_available = self.capacity_cores-requested_cores

    def get_node_available_resources(self, node):
        return min(node.cores_available, self.predicted_cores_available)

    @staticmethod
    def get_node_position(nodes, node):
        for i in range(len(nodes)):
            if node.id == nodes[i].id:
                return i
        return -1
