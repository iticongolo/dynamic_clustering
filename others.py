# import networkx as nx
# import random
# import matplotlib.pyplot as plt
# from matplotlib import colormaps  # Use the new colormaps API
# import numpy as np
#
#
# def generate_random_topology(k, a, b, c, d):
#     """Generates k servers with random (x, y) coordinates and returns a list of servers."""
#     servers = []
#     for i in range(k):
#         x = random.uniform(a, b)
#         y = random.uniform(c, d)
#         memory = random.randint(4, 64)  # Assign random memory to the server
#         cores = random.randint(1, 16)  # Assign random number of cores
#         servers.append({'id': i, 'x': x, 'y': y, 'memory': memory, 'cores': cores})
#     return servers
#
#
# def build_network_graph(servers, delay_threshold):
#     """Creates a graph where each server is a node and edges represent delay between them."""
#     G = nx.Graph()
#
#     # Add nodes (servers) to the graph
#     for server in servers:
#         G.add_node(server['id'], pos=(server['x'], server['y']))
#
#     # Add edges based on distance (or delay)
#     for i in range(len(servers)):
#         for j in range(i + 1, len(servers)):
#             server_a = servers[i]
#             server_b = servers[j]
#             distance = ((server_a['x'] - server_b['x']) ** 2 + (
#                         server_a['y'] - server_b['y']) ** 2) ** 0.5  # Euclidean distance
#             if distance <= delay_threshold:
#                 G.add_edge(server_a['id'], server_b['id'], weight=distance)
#
#     return G
#
#
# def partition_graph_by_delay(G, max_cluster_size, min_cluster_size):
#     """Applies a community detection algorithm to partition the network graph."""
#     from networkx.algorithms.community import girvan_newman
#     comp = girvan_newman(G)
#     initial_clusters = tuple(sorted(c) for c in next(comp))  # First partition
#
#     # Ensure cluster size constraints
#     clusters = balance_clusters_by_size(initial_clusters, max_cluster_size, min_cluster_size)
#
#     return clusters
#
#
# def balance_clusters_by_size(initial_clusters, max_cluster_size, min_cluster_size):
#     """Balances clusters based on the max and min cluster size constraints."""
#     clusters = [list(cluster) for cluster in initial_clusters]  # Convert tuples to lists
#     underloaded_clusters = [c for c in clusters if len(c) < min_cluster_size]
#     overloaded_clusters = [c for c in clusters if len(c) > max_cluster_size]
#
#     # Try to balance clusters by moving nodes from overloaded to underloaded clusters
#     for overloaded in overloaded_clusters:
#         while len(overloaded) > max_cluster_size:
#             # Find a node to move from the overloaded cluster
#             node_to_move = overloaded.pop()
#
#             # Move the node to an underloaded cluster (if possible)
#             for underloaded in underloaded_clusters:
#                 if len(underloaded) < min_cluster_size:
#                     underloaded.append(node_to_move)
#                     break  # Break once we successfully move the node to a valid cluster
#
#             # Update underloaded clusters after each move
#             underloaded_clusters = [c for c in clusters if len(c) < min_cluster_size]
#
#     # Ensure no cluster is underloaded anymore
#     for underloaded in underloaded_clusters:
#         while len(underloaded) < min_cluster_size:
#             # Try to add nodes from any other cluster
#             for cluster in clusters:
#                 if len(cluster) > min_cluster_size:
#                     node_to_move = cluster.pop()
#                     underloaded.append(node_to_move)
#                     break
#
#     return clusters
#
#
# def assign_clusters(clusters, servers):
#     """Assigns servers to their clusters."""
#     cluster_map = {}
#     for cluster_id, cluster_nodes in enumerate(clusters):
#         for node_id in cluster_nodes:
#             cluster_map[node_id] = cluster_id
#     return cluster_map
#
#
# def visualize_clusters(G, cluster_map):
#     """Visualizes the clusters with different colors."""
#     pos = nx.get_node_attributes(G, 'pos')  # Get positions of nodes
#     num_clusters = len(set(cluster_map.values()))  # Number of clusters
#
#     # Use the updated colormaps API
#     color_map = colormaps.get_cmap('tab20')  # Choose the colormap with only one argument
#
#     # Draw nodes, color by cluster
#     for cluster_id in range(num_clusters):
#         nodes_in_cluster = [node for node, cid in cluster_map.items() if cid == cluster_id]
#         # Scale the color by the cluster ID and the number of clusters
#         cluster_color = [color_map(cluster_id / num_clusters)] * len(nodes_in_cluster)
#         nx.draw_networkx_nodes(G, pos, nodelist=nodes_in_cluster, node_size=200, node_color=cluster_color)
#
#     # Draw edges
#     nx.draw_networkx_edges(G, pos)
#
#     # Draw node labels
#     nx.draw_networkx_labels(G, pos, font_size=10)
#
#     plt.show()
#
#
# # Step 1: Generate Random Topology
# k = 30  # Number of servers
# a, b, c, d = 0, 100, 0, 100  # Range for x, y coordinates
# delay_threshold = 15  # Max allowable distance for network delay
# min_cluster_size = 3
# max_cluster_size = 6
#
# servers = generate_random_topology(k, a, b, c, d)
#
# # Step 2: Build Network Graph based on Delay
# G = build_network_graph(servers, delay_threshold)
#
# # Step 3: Partition the Graph into Clusters
# clusters = partition_graph_by_delay(G, max_cluster_size, min_cluster_size)
#
# # Step 4: Assign Servers to Clusters
# cluster_map = assign_clusters(clusters, servers)
#
# # Step 5: Visualize the Clusters with Different Colors
# visualize_clusters(G, cluster_map)


a= [0 for _ in range(3)]
print(a)