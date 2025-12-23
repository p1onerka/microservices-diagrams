CONFIG_SERVER_TYPE = "config_server"
CONFIG_SERVER_FILL = 0xd8a059
CONFIG_SERVER_STROKE = 0x956e3d
DISCOVERY_SERVER_TYPE = "discovery_server"
DISCOVERY_SERVER_FILL = 0x79eaec
DISCOVERY_SERVER_STROKE = 0x55b8b9
EUREKA_CLIENT_TYPE = "eureka_client"
EUREKA_CLIENT_FILL = 0x8ae692
EUREKA_CLIENT_STROKE = 0x55b95e

REGISTER_IN_DISC_SERVER_MESSAGE = "register"
REGISTER_IN_DISC_SERVER_COLOR = 0x117a1a
REGISTER_IN_DISC_SERVER_WIDTH = 5
FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE = "get apps instances"
FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR = 0x0074d9
FETCH_DATA_ABOUT_APPS_INSTANCES_WIDTH = 5
HTTP_REQUESTS_MESSAGE = "http requests from "
HTTP_REQUESTS_COLOR = 0x4a4599
HTTP_REQUESTS_WIDTH = 5


def create_node(name: str, description: str, type: str):
    return f"{name}[{description}]:::{type}"


def create_edge(from_node: str, to_node: str, description: str):
    return f"{from_node} -->|{description}| {to_node}"


def create_type(type_name: str, fill: int, stroke: int, stroke_width: int = 2):
    return f"classDef {type_name} fill:#{fill:x},stroke:#{stroke:x},stroke-width:{stroke_width}px;"

def create_link_style(edge_num: int, stroke: int, width: int = 2):
    return f"linkStyle {edge_num} stroke:#{stroke:x},stroke-width:{width}px;"
