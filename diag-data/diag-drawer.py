from collections import defaultdict
import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

REGISTER_IN_DISC_SERVER_MESSAGE = "register"
FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE = "get apps instances"
REGISTER_IN_DISC_SERVER_COLOR = "red"
FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR = "green"

def build_diag(project_name:str):
    discovery_server_data = pd.read_csv(f"diag-data/{project_name}/discovery-server.csv", header=None, skiprows=1)
    discovery_clients_data = pd.read_csv(f"diag-data/{project_name}/discovery-clients.csv", header=None, skiprows=1)
    load_balanced_requesters_data = pd.read_csv(f"diag-data/{project_name}/eureka-load-balanced.csv", header=None, skiprows=1)

    discovery_servers = discovery_server_data[0].dropna().unique().tolist()
    discovery_clients = discovery_clients_data[0].dropna().unique().tolist()
    load_balanced_requesters = load_balanced_requesters_data[0].dropna().unique().tolist()

    diag = nx.MultiDiGraph()

    for s in discovery_servers:
        diag.add_node(s, color="green", size=1000)
    for c in discovery_clients:
        diag.add_node(c, color="purple", size=1000)
    for lbr in load_balanced_requesters:
        if lbr not in diag.nodes:
            diag.add_node(lbr, color="blue", size=1000)

    for s in discovery_servers:
        for c in discovery_clients: 
            diag.add_edge(c, s, color=REGISTER_IN_DISC_SERVER_COLOR, label=REGISTER_IN_DISC_SERVER_MESSAGE)
        for ldr in load_balanced_requesters:
            diag.add_edge(ldr, s, color=FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR, label=FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE)
    
    edge_labels = nx.get_edge_attributes(diag, "color")
    node_colors = [data["color"] for _, data in diag.nodes(data=True)]
    node_sizes = [data["size"] for _, data in diag.nodes(data=True)]
    
    pos = nx.spring_layout(diag)
    nx.draw_networkx_nodes(diag, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(diag, pos)

    edge_counts = defaultdict(int)
    edge_labels = {(u, v): data["label"] for u, v, data in diag.edges(data=True)}
    for (u, v, data) in diag.edges(data=True):
        count = edge_counts[(u, v)]
        rad = 0.15 * (-1)**count
        edge_counts[(u, v)] += 1
        nx.draw_networkx_edges(
            diag,
            pos,
            edgelist=[(u, v)],
            edge_color=data["color"],
            connectionstyle=f"arc3,rad={rad}",
            arrows=True,
            arrowstyle="-|>",
            min_source_margin=15,
            min_target_margin=15,
        )
    nx.draw_networkx_edge_labels(diag, pos, edge_labels=edge_labels,)
    #nx.draw(diag, pos, with_labels=True, edge_color=edge_colors, node_color=node_colors, node_size=node_sizes)
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        project_name = sys.argv[1]
        build_diag(project_name)
    else:
        print("too many arguments: the function expects only project name")
