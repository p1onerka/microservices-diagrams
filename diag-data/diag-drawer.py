from collections import defaultdict
import sys
import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt

from mermaid_constructor import (create_node, create_edge, create_type, create_link_style, create_link, CONFIG_SERVER_TYPE, CONFIG_SERVER_FILL, CONFIG_SERVER_STROKE, DISCOVERY_SERVER_TYPE, DISCOVERY_SERVER_FILL, DISCOVERY_SERVER_STROKE,
                                 EUREKA_CLIENT_TYPE, EUREKA_CLIENT_FILL, EUREKA_CLIENT_STROKE, REGISTER_IN_DISC_SERVER_MESSAGE, FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE, CONFIG_SERVER_DESCRIPTION,
                                 FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR, FETCH_DATA_ABOUT_APPS_INSTANCES_WIDTH, HTTP_REQUESTS_MESSAGE, HTTP_REQUESTS_COLOR, HTTP_REQUESTS_WIDTH, REGISTER_IN_DISC_SERVER_COLOR, REGISTER_IN_DISC_SERVER_WIDTH)

from data_analyzer import (map_directories_to_names, map_frontend_rest_requests, map_services_to_names, map_backend_rest_requests, extract_config_server, map_config_server_to_link)


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


'''def build_diag_mermaid(project_name: str):
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
            res.append(create_edge(
                lbr, s, FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE))

    if len(s) > 0:
        res.append(create_type(DISCOVERY_SERVER_TYPE,
                   DISCOVERY_SERVER_FILL, DISCOVERY_SERVER_STROKE))
    if len(c) > 0:
        res.append(create_type(EUREKA_CLIENT_TYPE,
                   EUREKA_CLIENT_FILL, EUREKA_CLIENT_STROKE))
    if len(lbr) > 0:
        res.append(create_type("load-balanced requests", 0xcce0ff, 0x003366))

    # res.append('```')

    res_string = "\n".join(res)

    generate_html_visualisation(project_name, res_string)

    # with open("output_diag.mmd", "w") as f:
    #    f.write(res_string)'''

def build_diag_mermaid(project_name: str):
    diag_lines = []
    edges_count = 0
    diag_lines.append('graph LR')

    name_to_dir, dir_to_name = map_directories_to_names(f"diag-data/{project_name}/service-names.csv")
    names_called_by_frontend = map_frontend_rest_requests(f"diag-data/{project_name}/routes-of-services-in-frontend.csv")
    names_of_eureka_clients = map_services_to_names(f"diag-data/{project_name}/discovery-clients.csv", dir_to_name)
    names_of_eureka_servers = map_services_to_names(f"diag-data/{project_name}/discovery-server.csv", dir_to_name)
    names_of_balanced_requesters = map_services_to_names(f"diag-data/{project_name}/eureka-load-balanced.csv", dir_to_name)
    names_of_inner_rest_callers = map_backend_rest_requests(f"diag-data/{project_name}/rest-requesters.csv", dir_to_name)
    names_of_config_servers = extract_config_server(f"diag-data/{project_name}/config-server.csv")
    config_servers_to_link = map_config_server_to_link(f"diag-data/{project_name}/config-server-link.csv", names_of_config_servers)

    # classes
    if len(names_of_eureka_servers) > 0:
        diag_lines.append(create_type(DISCOVERY_SERVER_TYPE,
                   DISCOVERY_SERVER_FILL, DISCOVERY_SERVER_STROKE))
    if len(names_of_eureka_clients) > 0:
        diag_lines.append(create_type(EUREKA_CLIENT_TYPE,
                   EUREKA_CLIENT_FILL, EUREKA_CLIENT_STROKE))
    if len(names_of_config_servers) > 0:
        diag_lines.append(create_type(CONFIG_SERVER_TYPE,
                   CONFIG_SERVER_FILL, CONFIG_SERVER_STROKE))

    # nodes
    for discovery_server in names_of_eureka_servers:
        diag_lines.append(create_node(discovery_server, discovery_server, DISCOVERY_SERVER_TYPE))
    for service in names_of_eureka_clients:
        diag_lines.append(create_node(service, service, EUREKA_CLIENT_TYPE))
    for config_server in names_of_config_servers:
        #diag_lines.append(create_node(config_server, config_server, CONFIG_SERVER_TYPE))
        #if config_servers_to_link[config_server]:
        #    link = config_servers_to_link[config_server]
        #    diag_lines.append(create_link(config_server, link))
        diag_lines.append(f'subgraph LEGEND["{CONFIG_SERVER_DESCRIPTION}"]\ndirection LR\n')
        diag_lines.append(create_node(config_server, config_server, CONFIG_SERVER_TYPE))
        if config_servers_to_link[config_server]:
            link = config_servers_to_link[config_server]
            diag_lines.append(create_link(config_server, link))
        diag_lines.append("end")

    # edges
    for server in names_of_eureka_servers:
        for client in names_of_eureka_clients:
            diag_lines.append(create_edge(client, server, REGISTER_IN_DISC_SERVER_MESSAGE))
            diag_lines.append(create_link_style(edges_count, REGISTER_IN_DISC_SERVER_COLOR, REGISTER_IN_DISC_SERVER_WIDTH))
            edges_count += 1
    for service in names_called_by_frontend:
        caller_name = dir_to_name[names_called_by_frontend[service][0]]
        diag_lines.append(create_edge(caller_name, service, f"{HTTP_REQUESTS_MESSAGE}\n{names_called_by_frontend[service][1]}"))
        diag_lines.append(create_link_style(edges_count, HTTP_REQUESTS_COLOR, HTTP_REQUESTS_WIDTH))
        edges_count += 1
    for requester in names_of_balanced_requesters:
        for server in names_of_eureka_servers:
            diag_lines.append(create_edge(requester, server, FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE))
            diag_lines.append(create_link_style(edges_count, FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR, FETCH_DATA_ABOUT_APPS_INSTANCES_WIDTH))
            edges_count += 1
    for requester, requester_file, requested in names_of_inner_rest_callers:
        diag_lines.append(create_edge(requester, requested, f"{HTTP_REQUESTS_MESSAGE}\n{requester_file}"))
        diag_lines.append(create_link_style(edges_count, HTTP_REQUESTS_COLOR, HTTP_REQUESTS_WIDTH))
        edges_count += 1
    
    diag_string = "\n".join(diag_lines)

    generate_html_visualisation(project_name, diag_string)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        project_name = sys.argv[1]
        build_diag_mermaid(project_name)
    else:
        print("too many arguments: the function expects only project name")
