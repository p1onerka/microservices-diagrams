from collections import defaultdict
import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from mermaid_constructor import create_node, create_edge, create_type, CONFIG_SERVER_TYPE, CONFIG_SERVER_FILL, CONFIG_SERVER_STROKE, DISCOVERY_SERVER_TYPE, DISCOVERY_SERVER_FILL, DISCOVERY_SERVER_STROKE, EUREKA_CLIENT_TYPE, EUREKA_CLIENT_FILL, EUREKA_CLIENT_STROKE, REGISTER_IN_DISC_SERVER_MESSAGE, FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE, REGISTER_IN_DISC_SERVER_COLOR, FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR


def build_diag(project_name: str):
    discovery_server_data = pd.read_csv(
        f"diag-data/{project_name}/discovery-server.csv", header=None, skiprows=1)
    discovery_clients_data = pd.read_csv(
        f"diag-data/{project_name}/discovery-clients.csv", header=None, skiprows=1)
    load_balanced_requesters_data = pd.read_csv(
        f"diag-data/{project_name}/eureka-load-balanced.csv", header=None, skiprows=1)

    discovery_servers = discovery_server_data[0].dropna().unique().tolist()
    discovery_clients = discovery_clients_data[0].dropna().unique().tolist()
    load_balanced_requesters = load_balanced_requesters_data[0].dropna(
    ).unique().tolist()

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
            diag.add_edge(c, s, color=REGISTER_IN_DISC_SERVER_COLOR,
                          label=REGISTER_IN_DISC_SERVER_MESSAGE)
        for ldr in load_balanced_requesters:
            diag.add_edge(ldr, s, color=FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR,
                          label=FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE)

    edge_labels = nx.get_edge_attributes(diag, "color")
    node_colors = [data["color"] for _, data in diag.nodes(data=True)]
    node_sizes = [data["size"] for _, data in diag.nodes(data=True)]

    pos = nx.spring_layout(diag)
    plt.figure(figsize=(20, 12))
    nx.draw_networkx_nodes(
        diag, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(diag, pos)

    edge_counts = defaultdict(int)
    edge_labels = {(u, v): data["label"]
                   for u, v, data in diag.edges(data=True)}
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
    # nx.draw(diag, pos, with_labels=True, edge_color=edge_colors, node_color=node_colors, node_size=node_sizes)
    plt.axis("off")
    plt.show()


def generate_html_visualisation(project_name: str, diag: str):
    HTML_PAGE_TEMPLATE = f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Microservice interactions diagram</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{startOnLoad: true}});
        </script>
        <style>
            body {{
                font-family: sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background-color: #f4f4f4;
            }}
            .mermaid {{
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
        </style>
    </head>
    <body>
        <pre class="mermaid">{diag}</pre>
    </body>
    </html>'''
    try:
        with open(f"{project_name}-output-diag-page.html", "w") as f:
            f.write(HTML_PAGE_TEMPLATE)
    except IOError as e:
        print(f"Error with opening HTML file {e}")


def build_diag_mermaid(project_name: str):
    discovery_server_data = pd.read_csv(
        f"diag-data/{project_name}/discovery-server.csv", header=None, skiprows=1)
    discovery_clients_data = pd.read_csv(
        f"diag-data/{project_name}/discovery-clients.csv", header=None, skiprows=1)
    load_balanced_requesters_data = pd.read_csv(
        f"diag-data/{project_name}/eureka-load-balanced.csv", header=None, skiprows=1)

    discovery_servers = discovery_server_data[0].dropna().unique().tolist()
    discovery_clients = discovery_clients_data[0].dropna().unique().tolist()
    load_balanced_requesters = load_balanced_requesters_data[0].dropna(
    ).unique().tolist()

    # mermaid header
    res = []
    # res.append('```mermaid')
    res.append('graph LR')

    # entities
    for s in discovery_servers:
        res.append(create_node(s, s, DISCOVERY_SERVER_TYPE))
    for c in discovery_clients:
        res.append(create_node(c, c, EUREKA_CLIENT_TYPE))
    for lbr in load_balanced_requesters:
        if lbr not in discovery_clients and lbr not in discovery_servers:
            res.append(create_node(lbr, lbr, "lbr"))

    # relations
    for s in discovery_servers:
        for c in discovery_clients:
            res.append(create_edge(c, s, REGISTER_IN_DISC_SERVER_MESSAGE))
        for lbr in load_balanced_requesters:
            res.append(create_edge(lbr, s, FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE))


    if len(s) > 0:
        res.append(create_type(DISCOVERY_SERVER_TYPE, DISCOVERY_SERVER_FILL, DISCOVERY_SERVER_STROKE))
    if len(c) > 0:
        res.append(create_type(EUREKA_CLIENT_TYPE, EUREKA_CLIENT_FILL, EUREKA_CLIENT_STROKE))
    if len(lbr) > 0:
        res.append(create_type("load-balanced requests", 0xcce0ff, 0x003366))

    # res.append('```')

    res_string = "\n".join(res)

    generate_html_visualisation(project_name, res_string)

    # with open("output_diag.mmd", "w") as f:
    #    f.write(res_string)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        project_name = sys.argv[1]
        build_diag_mermaid(project_name)
    else:
        print("too many arguments: the function expects only project name")
