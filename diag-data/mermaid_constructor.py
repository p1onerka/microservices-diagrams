CONFIG_SERVER_TYPE = "config_server"
CONFIG_SERVER_FILL = 0xd8a059
CONFIG_SERVER_STROKE = 0x956e3d
DISCOVERY_SERVER_TYPE = "discovery_server"
DISCOVERY_SERVER_FILL = 0x93dcd9
DISCOVERY_SERVER_STROKE = 0x54b9b4
EUREKA_CLIENT_TYPE = "eureka_client"
EUREKA_CLIENT_FILL = 0x8ae692
EUREKA_CLIENT_STROKE = 0x55b95e

REGISTER_IN_DISC_SERVER_MESSAGE = "register"
FETCH_DATA_ABOUT_APPS_INSTANCES_MESSAGE = "get apps instances"
REGISTER_IN_DISC_SERVER_COLOR = "red"
FETCH_DATA_ABOUT_APPS_INSTANCES_COLOR = "green"


def create_node(name: str, description: str, type: str):
    return f"{name}[{description}]:::{type}"


def create_edge(from_node: str, to_node: str, description: str):
    return f"{from_node} -->|{description}| {to_node}"


def create_type(type_name: str, fill: int, stroke: int, stroke_width: int = 2):
    return f"classDef {type_name} fill:#{fill:x},stroke:#{stroke:x},stroke-width:{stroke_width}px;"
