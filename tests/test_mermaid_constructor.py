import sys
import os
from mermaid_constructor import (
    create_edge,
    create_link,
    create_link_style,
    create_node,
    create_type,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_create_node():
    node = create_node("node1", "this is node1", "server")
    assert node == "node1[this is node1]:::server"


def test_create_edge():
    edge = create_edge("node1", "node2", "edge")
    assert edge == "node1 -->|edge| node2"


def test_create_type():
    type = create_type("type", 0x060606, 0x606060, 4)
    assert type == "classDef type fill:#60606,stroke:#606060,stroke-width:4px;"


def test_create_type_default_width():
    type = create_type("type", 0x060606, 0x606060)
    assert type == "classDef type fill:#60606,stroke:#606060,stroke-width:2px;"


def test_create_link_style():
    link_style = create_link_style(1, 0x060606, 3)
    assert link_style == "linkStyle 1 stroke:#60606,stroke-width:3px;"


def test_create_link_style_default_width():
    link_style = create_link_style(1, 0x060606)
    assert link_style == "linkStyle 1 stroke:#60606,stroke-width:2px;"


def test_create_link():
    link = create_link("node1", "http://somelink")
    assert link == 'node1["<a href=http://somelink>node1</a>"];'
