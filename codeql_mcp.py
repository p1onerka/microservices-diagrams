import time

from mcp.server import MCPServer
from pathlib import Path
from agent_helpers import (
    create_and_execute_java_annotation_to_classes_query,
    create_and_execute_java_method_calls_to_classes_query,
    create_and_execute_java_services_dependencies_query,
)

TOOL_TIME_FILE = Path("codeql_tools_time.txt")


def log_tool_time(tool_name: str, duration: float):
    with TOOL_TIME_FILE.open("a") as f:
        f.write(f"{tool_name}\t{duration:.6f}\n")


mcp = MCPServer("CodeQL")


@mcp.tool()
def search_java_annotation(annotation: str, proj_name: str) -> str:
    """
    Creates and executes java codeQL query that finds all classes with given annotation

    Args:
        ann: Annotation without the @ symbol.
        proj_name: the name of project to perform the query on.
    Returns:
        The contents of .csv table with query results.
    """
    start = time.perf_counter()
    res = create_and_execute_java_annotation_to_classes_query(annotation, proj_name)
    end = time.perf_counter()
    print(end - start)
    log_tool_time("search_java_annotation", end - start)
    return res


@mcp.tool()
def search_java_method_calls(method: str, proj_name: str) -> str:
    """
    Creates and executes java codeQL query that finds all classes with given method calls and returns their name and file with main class

    Args:
        method: Method to find calls of.
        proj_name: the name of project to perform the query on.
    Returns:
        The contents of .csv table with query results.
    """
    start = time.perf_counter()
    res = create_and_execute_java_method_calls_to_classes_query(method, proj_name)
    end = time.perf_counter()
    log_tool_time("search_java_annotation", end - start)
    return res


@mcp.tool()
def get_java_dependencies(proj_name: str) -> str:
    """
    Creates and executes java codeQL query that finds all pom.xml files in the project and maps modules' names to their dependencies

    Args:
        db_name: the name of project to perform the query on.
    Returns:
        The contents of .csv table with query results.
    """
    start = time.perf_counter()
    res = create_and_execute_java_services_dependencies_query(proj_name)
    end = time.perf_counter()
    log_tool_time("search_java_annotation", end - start)
    return res


if __name__ == "__main__":
    mcp.run(transport="stdio")
