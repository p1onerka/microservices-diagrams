CONFIG_SERVER_TYPE = "config_server"
CONFIG_SERVER_DESCRIPTION = "configs for all services"
CONFIG_SERVER_FILL = 0xD8A059
CONFIG_SERVER_STROKE = 0x956E3D
DISCOVERY_SERVER_TYPE = "discovery_server"
DISCOVERY_SERVER_FILL = 0x79EAEC
DISCOVERY_SERVER_STROKE = 0x55B8B9
EUREKA_CLIENT_TYPE = "eureka_client"
EUREKA_CLIENT_FILL = 0x8AE692
EUREKA_CLIENT_STROKE = 0x55B95E

REGISTER_IN_DISC_SERVER_MESSAGE = "register"
REGISTER_IN_DISC_SERVER_COLOR = 0x117A1A
REGISTER_IN_DISC_SERVER_WIDTH = 5
FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE = "get apps instances"
FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR = 0x0074D9
FETCH_DATA_ABOUT_APPS_INSTANCES_WIDTH = 5
HTTP_REQUESTS_MESSAGE = "http requests from "
HTTP_REQUESTS_COLOR = 0x4A4599
HTTP_REQUESTS_WIDTH = 5


def create_node(name: str, description: str, type: str) -> str:
    """
    A function for creating a definition of node in Mermaid syntax.
    """
    return f"{name}[{description}]:::{type}"


def create_edge(from_node: str, to_node: str, description: str) -> str:
    """
    A function for creating a definition of edge in Mermaid syntax.
    """
    return f"{from_node} -->|{description}| {to_node}"


def create_type(type_name: str, fill: int, stroke: int, stroke_width: int = 2) -> str:
    """
    A function for creating a definition of type in Mermaid syntax.
    """
    return f"classDef {type_name} fill:#{fill:x},stroke:#{stroke:x},stroke-width:{stroke_width}px;"


def create_link_style(edge_num: int, stroke: int, width: int = 2) -> str:
    """
    A function for creating a definition of edge style in Mermaid syntax.
    """
    return f"linkStyle {edge_num} stroke:#{stroke:x},stroke-width:{width}px;"


def create_link(node_name: str, link: str) -> str:
    """
    A function for creating a definition of link in Mermaid syntax.
    """
    return f'{node_name}["<a href={link}>{node_name}</a>"];'
