import copy

import numpy as np

from cluster import Cluster
from core.util.forecast import Forecast
from core.util.util import *
from node import Node


class DynamicClustering:

    def __init__(self, topology, functions, historical_workload=None):
        self.topology = topology
        self.functions = functions
        # historical workload is a list of lists of dataframes (time, external_workload)
        # for each function on each cluster on the topology
        # e.g.: [c1[f1|time,workload|,f2|time,workload|...], c2[f1|time,workload|,f2|time,workload|...]
        self.historical_topology_workload = historical_workload
        self.external_predicted_topology_workload = []
        # print(f'Clusters-Availability-Change Clusters-000= {[c.cores_available for c in self.topology.current_clusters]}')
        # two lists: (i) previous cores per cluster, (ii) predicted cores per cluster
        # e.g.: [4000,1000,2400] three clusters
        self.historical_total_requested_cores_topology = [0 for _ in range(len(topology.current_clusters))] # TODO verify if its being updated
        self.historical_cluster_status = [1 for _ in range(len(topology.current_clusters))]
        self.total_predicted_topology_workload = []

    def initialize_historical(self):
        self.historical_total_requested_cores_topology = [0 for _ in range(len(self.topology.current_clusters))]

    def set_historical_workload(self, new_historical_workload):
        self.historical_topology_workload = new_historical_workload

    # Predict the external workload for each function in each cluster NOTE: DONE
    # e.g.: [c1[f1|time,workload|,f2|time,workload|...], c2[f1|time,workload|,f2|time,workload|...]
    def get_cluster_function_workload_prediction(self, num_points_sample, num_forecast_points, slot_length, freq):
        external_predicted_workload_topology = []
        for cluster_workload in self.historical_topology_workload:
            external_predicted_workload_cluster = []
            for f in cluster_workload:
                external_predicted_function_workload = get_cluster_function_external_workload_prediction\
                    (cluster_workload, f.id, num_points_sample, num_forecast_points, slot_length=slot_length, freq=freq)
                external_predicted_workload_cluster.append(external_predicted_function_workload)
            external_predicted_workload_topology.append(external_predicted_workload_cluster)
        return external_predicted_workload_topology

    # predict the total workload for each function in each cluster (internal and external workload) NOTE: DONE
    def get_topology_total_workload_prediction(self, data):
        clusters = copy.deepcopy(self.topology.initial_clusters) # request sent to a shared node must be managed on initial cluster of the node
        # print(f'INITIAL-CLUSTERS={[[node.id for node in c.nodes] for c in clusters]}')
        self.total_predicted_topology_workload = copy.deepcopy(self.external_predicted_topology_workload)
        for c in clusters:
            total_workload = [0] * len(self.functions)
            # print(f'workload_{c.id}_{0}={self.total_predicted_topology_workload[c.id][0]}')
            for f in c.functions:
                # print(f'FUNCTIONS={[(f.id, f.name) for f in c.functions]}')
                total_workload[f.id] = self.total_predicted_topology_workload[c.id][f.id]
                function_name = f.name  # function names are unique, e.g.: f0, f1- where 0 and 1 are the ids
                successors_f = data.dag.get_successors_ids(function_name)  # returns e.g.: [1,4,6,7] ids of successors
                # print(f'successors_{f.id}={successors_f}')
                for f_id in successors_f:
                    workload_c_f = self.total_predicted_topology_workload[c.id][f_id] + data.m[f.id][f_id] * \
                                   total_workload[f.id]
                    total_workload[f_id] = workload_c_f
                    self.total_predicted_topology_workload[c.id][f_id] = workload_c_f
                    # print(f'workload_{c.id}_{f_id}={workload_c_f}')
        # output e.g.: # e.g.: [c1[f1|time,workload|,f2|time,workload|...], c2[f1|time,workload|,f2|time,workload|...]
        return self.total_predicted_topology_workload

    # determine the cores needed to serve the predicted workload.
    # NOTE: update the apps json files to include cores_cluster[cluster_id][f_id]§t
    def cluster_cores_requested(self, data):  # TODO revise the historical needed cores updates
        total_workload = self.get_topology_total_workload_prediction(data)
        cores_needed = [0] * len(total_workload)  # initialize the list by 0 for all the cluster positions

        # ( the capacity of the list is equal to the number of clusters)
        cluster_id = 0
        for cluster_workload in total_workload:
            for f_id in range(len(cluster_workload)):
                cores_needed[cluster_id] = cores_needed[cluster_id]+cluster_workload[f_id]*data.cores_cluster[cluster_id][f_id]
                # cores_cluster[f_id] is the avg of cores needed to execute one request of f, obtained by
                # profiling f in each node of the cluster and take the average of the cores needed
            cluster_id = cluster_id+1
        # output e.g.: [c1|1000|,c2|4000|...ck|2000|]
        # print(f'cores_needed ={cores_needed}')
        return cores_needed

    # return the clusters predicted to be overloaded or underloaded NOTE:DONE
    # def get_topology_status_prediction(self, data):
    #     # overloaded_clusters = []
    #     # underloaded_clusters = []
    #     cores_needed = self.cluster_cores_requested(data)
    #     clusters = self.topology.current_clusters
    #     for i in range(len(clusters)):
    #         # cores_not_needed = clusters[i].capacity_cores - self.historical_total_requested_cores_topology[clusters[i].id]
    #         # cores_not_needed = clusters[i].capacity_cores - cores_needed[i]
    #         clusters[i].update_status(cores_needed[i])
    #         # if cores_not_needed == 0:
    #         #     clusters[i].status = 0  # the cluster is fine, is not underloaded
    #         # else:
    #         #     if clusters[i].status == -1:
    #         #         overloaded_clusters.append(clusters[i])
    #         #     else:
    #         #         if clusters[i].status == 1:
    #         #             clusters[i].available_cores = cores_not_needed  # TODO check
    #         #             underloaded_clusters.append(clusters[i])
    #     # return overloaded_clusters, underloaded_clusters

    def update_topology_status_prediction(self, data):
        # overloaded_clusters = []
        # underloaded_clusters = []
        cores_needed = self.cluster_cores_requested(data)
        clusters = self.topology.current_clusters
        for i in range(len(clusters)):
            # cores_not_needed = clusters[i].capacity_cores - self.historical_total_requested_cores_topology[clusters[i].id]
            # cores_not_needed = clusters[i].capacity_cores - cores_needed[i]
            clusters[i].update_status(cores_needed[clusters[i].id])
            print(f'HIST={self.historical_total_requested_cores_topology[clusters[i].id]}, CORES-NEEDED={cores_needed[clusters[i].id]}')
            # if cores_not_needed == 0:
            #     clusters[i].status = 0  # the cluster is fine, is not underloaded
            # else:
            #     if clusters[i].status == -1:
            #         overloaded_clusters.append(clusters[i])
            #     else:
            #         if clusters[i].status == 1:
            #             clusters[i].available_cores = cores_not_needed  # TODO check
            #             underloaded_clusters.append(clusters[i])
        # return overloaded_clusters, underloaded_clusters

    def get_underloaded_overloaded_clusters(self, requested_cores):
        overloaded_clusters = []
        underloaded_clusters = []
        clusters = self.topology.current_clusters
        for i in range(len(clusters)):
            if clusters[i].status == -1:
                overloaded_clusters.append(clusters[i])
            else:
                cores_available = clusters[i].capacity_cores - max(self.historical_total_requested_cores_topology[clusters[i].id],
                                       requested_cores[clusters[i].id])
                if clusters[i].status == 1 and cores_available > 0:
                    underloaded_clusters.append(clusters[i])
        return overloaded_clusters, underloaded_clusters

    # update the list of two lists (last window and current ones) of status NOTE:DONE
    def update_historical_topology_status_prediction(self):
        clusters = self.topology.current_clusters
        status = []
        for i in range(len(clusters)):
            status.append(clusters[i].status)
        self.historical_cluster_status = status

    def update_historical_total_requested_cores_topology(self, cores_needed):
        # update the historical requested cores
        # print(f'FFFFFF-cores_needed={cores_needed}')
        self.historical_total_requested_cores_topology = cores_needed

    # Release  shared cluster_nodes from the clusters shared with, if possible (if in the previous time window
    # prediction was not used and won't be used for the current time window prediction) NOTE:DONE
    def __release_shared_nodes(self, requested_cores):
        # self.update_topology_status_prediction(data)  # TODO new
        # _, underloaded_clusters = self.get_topology_status_prediction(data)
        _, underloaded_clusters = self.get_underloaded_overloaded_clusters(requested_cores)
        print(
            f']]]]]]Underloaded C={[(c.id, c.cores_available) for c in underloaded_clusters]}, LEN={len(underloaded_clusters)}')
        # from underloaded clusters take only the ones predicted to be underloaded in the previous time window
        # that have received shared nodes
        underloaded_clusters_temp1 = []
        print(f'////// historical_cluster_status={[self.historical_cluster_status[c.id] for c in underloaded_clusters]}')
        print(
            f'////// Has received Nodes={[(c.id,  c.has_received_shared_nodes()) for c in underloaded_clusters]}')
        for c in underloaded_clusters:
            if self.historical_cluster_status[c.id] == 1:

                if c.has_received_shared_nodes():
                    underloaded_clusters_temp1.append(c)

        print(f']]]]]]cores_not_needed={[(c.id, c.cores_available) for c in underloaded_clusters_temp1]}, LEN={len(underloaded_clusters_temp1)}')
        # print(f'Status1={[st for st in self.historical_cluster_status]}')
        # print(f'underloaded_clusters_temp1={[c.id for c in underloaded_clusters]}')
        for c in underloaded_clusters_temp1:
            cores_not_needed = c.capacity_cores-max(self.historical_total_requested_cores_topology[c.id],
                                                    requested_cores[c.id])
            print(f']]]]]]cores_not_needed[{c.id}]={cores_not_needed}')
            if cores_not_needed == 0:
                c.status = 0  # the cluster is fine, is not underloaded
                continue
            received_shared_nodes = copy.deepcopy(c.received_nodes)
            pos = 0
            for node in received_shared_nodes:
                cores_allocated = c.received_nodes_allocated_cores[node.id]
                if cores_allocated <= cores_not_needed:
                    cores_not_needed = cores_not_needed - cores_allocated
                    node.update_available_cores(cores_allocated)  # free up the cores shared with this cluster TODO update the real ones also because this is a copy
                    c.received_nodes[pos].update_available_cores(cores_allocated)
                    c.received_nodes.pop(pos)  # remove the node from the list of shared cluster_nodes on the cluster
                    c.remove(node)  # remove the node from the cluster
                    c.update_status(requested_cores[c.id])  # update the status of c

                    source_node_cluster = self.topology.static_node_cluster[node.id]

                    self.topology.current_clusters[source_node_cluster.id].update_available_cores(cores_allocated)  # update cores availability of
                    # the source cluster
                    self.topology.current_clusters[source_node_cluster.id].update_capacity_cores(cores_allocated)  # update de capacity of the cluster
                    self.topology.current_clusters[source_node_cluster.id].update_status(requested_cores[source_node_cluster.id])  # update de status of the cluster
                else:
                    pos = pos+1
        self.update_historical_topology_status_prediction()

    def __list_needed_cores_topology(self, requested_cores):
        needed_cores_clusters = []
        # self.update_topology_status_prediction(data)
        overloaded_clusters, _ = self.get_underloaded_overloaded_clusters(requested_cores)
        for c in overloaded_clusters:
            cores_needed = max(self.historical_total_requested_cores_topology[c.id],
                               requested_cores[c.id])-c.capacity_cores
            if cores_needed > 0:
                needed_cores_clusters.append((c, cores_needed))
        return needed_cores_clusters

    # only share underloaded cluster_nodes (available_cores>20%cores_node)
    # to (1) avoid the source clusters overloading and
    # (2) avoid that a cluster receives many shared cluster_nodes
    # with fewer capacity which would imply higher transmission cost and network delay NOTE:DONE
    def change_clusters(self, data):

        requested_cores = self.cluster_cores_requested(data)
        print(f'CORES_REQUESTED={requested_cores}')
        self.update_topology_status_prediction(data)
        self.__release_shared_nodes(requested_cores)
        print(f'status-before={[c.status for c in self.topology.current_clusters]}')
        overloaded_clusters, underloaded_clusters = self.get_underloaded_overloaded_clusters(requested_cores)
        if len(overloaded_clusters) == 0 or len(underloaded_clusters) == 0:
            self.historical_total_requested_cores_topology = requested_cores
            return
        print(f'++++++++++ AVAILABLE CORES = {[(c.id, c.cores_available) for c in underloaded_clusters]}')
        self.update_clusters_predicted_cores_available(data, underloaded_clusters)
        # get a list of (cluster, cores_missing_on_cluster) for each cluster predicted to be overloaded
        list_needed_cores = self.__list_needed_cores_topology(requested_cores)

        # sort the list by number of cores needed for each cluster in descendent
        sorted_list_needed_cores = sorted(list_needed_cores, key=lambda x: x[1], reverse=True)
        print(f'Needed_cores={[(core[0].id, core[1]) for core in sorted_list_needed_cores]}')
        underloaded_nodes = get_underloaded_nodes(underloaded_clusters)
        print(
            f'######## Node,Cores_Available={[(node.id, node.cores_available) for node in underloaded_nodes]}')
        k = 0
        while len(sorted_list_needed_cores) > 0 and len(underloaded_clusters) > 0:
            print(f'Underloaded_clusters={[(c.id, c.cores_available) for c in underloaded_clusters]}')
            print(f'len(sorted_list_needed_cores)={len(sorted_list_needed_cores)}, len(underloaded_clusters)={len(underloaded_clusters)}')
            print(f'underloaded_nodes={[(node.id, node.cores_available) for node in underloaded_nodes]}')
            cluster_need_cores = sorted_list_needed_cores[0]
            c = cluster_need_cores[0]
            needed_cores = copy.deepcopy(cluster_need_cores[1])
            j = 0
            if len(underloaded_nodes) == 0:
                print(f'++++++++++ AVAILABLE CORES1 = {[(c.id, c.cores_available) for c in underloaded_clusters]}')
                return

            while needed_cores > 0 and len(underloaded_nodes) > 0:
                print(f'needed_cores[c{c.id}] ={needed_cores }, {[(node.id, node.cores_available) for node in underloaded_nodes]}')
                print(f'len(sorted_list_needed_cores)={len(sorted_list_needed_cores)}, len(underloaded_clusters) =C,cores{[(c.id, c.cores_available) for c in underloaded_clusters] }')
                print(f'needed_cores={needed_cores}, len(underloaded_nodes)={len(underloaded_nodes)}')
                if k==50:
                    return
                c.update_centroid()
                c.update_centroid_nodes_network_delay(underloaded_nodes)
                closest_node, index = get_closest_node(c, underloaded_nodes)

                initial_cluster = get_initial_cluster(self.topology.initial_clusters, closest_node)
                current_cluster = self.topology.current_clusters[initial_cluster.id]
                # underloaded_cluster_needed_cores = max(self.historical_total_requested_cores_topology[current_cluster.id],
                #                                        requested_cores[current_cluster.id])
                # print(f'underloaded_cluster_needed_cores[C{current_cluster.id}]={underloaded_cluster_needed_cores}')
                # current_cluster.update_predicted_cores_available(underloaded_cluster_needed_cores)
                closest_node_available_resources = current_cluster.get_node_available_resources(closest_node)
                # print(f'Node{closest_node.id}, C{current_cluster.id}-closest_node_available_resources={closest_node_available_resources}')

                if closest_node_available_resources <= 0:
                    current_cluster.set_status = 0  # turn the cluster from underloaded status fine
                    underloaded_nodes.pop(index)
                    continue
                cores_diff = closest_node_available_resources - needed_cores
                new_cores = 0
                if cores_diff <= 0:
                    new_cores = closest_node_available_resources
                    needed_cores = needed_cores - new_cores
                    # underloaded_nodes.pop(index)
                else:
                    new_cores = needed_cores
                    needed_cores = 0

                current_cluster.update_capacity_cores(-new_cores)
                current_cluster.update_available_cores(-new_cores)
                current_cluster.update_status(requested_cores[current_cluster.id])
                # print(f'closest_node_available_resources={closest_node_available_resources}')
                c.update_received_nodes(closest_node, new_cores)
                closest_node.update_available_cores(-new_cores)  # includes status update
                if closest_node.status == 0:  # the node is not underloaded anymore
                    underloaded_nodes.pop(index)

                j = j+1
            if needed_cores == 0:
                c.status = 0  # fine
                sorted_list_needed_cores.pop(0)
            else:
                c.status = -1  # overloaded
            _, underloaded_clusters = self.get_underloaded_overloaded_clusters(requested_cores)
            underloaded_nodes = get_underloaded_nodes(underloaded_clusters)
            k=k+1

        self.historical_total_requested_cores_topology = requested_cores

    def update_clusters_predicted_cores_available(self, data, clusters):
        requested_cores = self.cluster_cores_requested(data)
        for c in clusters:
            predicted_cluster_needed_cores = max(self.historical_total_requested_cores_topology[c.id],
                                                 requested_cores[c.id])
            c.update_predicted_cores_available(predicted_cluster_needed_cores)


