from ollama import chat
import os
import sys
import subprocess


def make_project_related_tools(project_path: str):
    def read_source_file(file_path: str) -> str:
        """
        Read a source file in the project.

        Args:
            file_path: Local path to the source file.
            project_path: Global path to the home dir of the project.
                If provided, file_path is resolved relative to the project root and must remain inside the project.
                If left empty, file_path is resolved relative to the current working directory.

        Returns:
            First 12000 characters of file.
        """
        full_path = os.path.abspath(os.path.join(project_path, file_path))
        abs_project_root = os.path.abspath(project_path)

        if (
            not full_path.startswith(abs_project_root + os.sep)
            and full_path != abs_project_root
        ):
            return f"Error: file {full_path} is outside the project directory"

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read(12000)
                if len(content) == 12000:
                    return content + "\n... (file was cut due to size)"
                return content
        except FileNotFoundError:
            return f"Error: file {full_path} not found"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def list_directory(dir_path: str) -> str:
        """
        Look into directory contents.

        Args:
            dir_path: Local path of directory to inspect.
            project_path: Global path to the home dir of the project.
                If provided, dir_path is resolved relative to the project root and must remain inside the project.
                If left empty, dir_path is resolved relative to the current working directory.

        Returns:
            The list of files and directories inside the given directory.
        """
        full_path = os.path.abspath(os.path.join(project_path, dir_path))
        abs_project_root = os.path.abspath(project_path)

        if (
            not full_path.startswith(abs_project_root + os.sep)
            and full_path != abs_project_root
        ):
            return f"Error: directory {full_path} is outside the project"

        try:
            items = os.listdir(full_path)
            result = []
            for item in sorted(items):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    result.append(f"{item}/")
                else:
                    result.append(f"{item}")
            return "\n".join(result) if result else "Directory is empty"
        except FileNotFoundError:
            return f"Directory not found: {full_path}"
        except Exception as e:
            return f"Error reading directory: {str(e)}"

    return read_source_file, list_directory


def list_codeql_queries():
    pass


# WIP: doesnt support infrastructure setup (qlpack.yml). prb make some function before agent later on
def save_codeql_query(query: str, query_name: str, query_language: str) -> str:
    """
    Save the given codeQL query

    Args:
        query: query text in str format
        query_name: requested name of the file with query
        query_language: currently supports java/javascript. Depending on language, the query will be saved in one of the directories with according setup

    Returns:
        path to the query file with name <query_name>.ql
    """

    if query_language == "java":
        query_name = f"codeql-query/{query_name}.ql"
    elif query_language == "javascript":
        query_name = f"codeql-query-js/{query_name}.ql"
    else:
        return f"Error: the tool currently does not support queries in {query_language}"

    try:
        with open(query_name, "w", encoding="utf-8") as file:
            file.write(query)
        return query_name
    except Exception as e:
        return f"Error creating {query_name} query file: {str(e)}"


# TODO: change return value? current one isnt informative
def execute_codeql_query(query_path: str, db_path: str, output_path: str) -> str:
    """
    Executes codeQL query in given file

    Args:
        query_path: path to codeQL query
        db_path: path to codeQL database
        output_path: where to place the result. Pass empty string to place it in the current directory

    Returns:
        path to the result in CSV with name <output_path>/query-result.csv
    """
    if not output_path:
        output_path = "query-result"
    else:
        output_path = f"{output_path}/query-result"
    subprocess.run(["ls"])
    subprocess.run(
        [
            "codeql",
            "query",
            "run",
            f"{query_path}",
            "--database",
            f"{db_path}",
            "--output",
            f"{output_path}.bqrs",
        ]
    )
    subprocess.run(
        [
            "codeql",
            "bqrs",
            "decode",
            f"{output_path}.bqrs",
            "--format=csv",
            "--output",
            f"{output_path}.csv",
        ]
    )
    return f"{output_path}.csv"


def run_agent_simple(project_path: str, tools):
    available_functions = {}
    for tool in tools:
        available_functions[tool.__name__] = tool

    messages = [
        {
            "role": "user",
            "content": f"""
    You are an expert in analyzing microservice architecture apps written in Java.

    The project root is {project_path}.

    Your task is to determine:
    1. What services are in the application.
    2. What each service does.
    3. How the services interact with each other.
    4. What communication mechanisms are used.

    You can use tools to read source code and inspect directories.

    Start by looking at pom.xml, build.gradle and directory structure.

    Do not guess service names or file names. You MUST discover them by inspecting the project.

    Do not stop after analyzing one service.
    You MUST inspect ALL service modules listed in the root pom.xml or in file structure.

    For every service:
    - inspect its pom.xml
    - inspect its application.yml/application.properties
    - inspect its main application class
    - inspect relevant controllers and clients
    - inspect configuration related to service communication

    Continue using tools until you have enough information to describe ALL services
    and their interactions.

    Only when the analysis is complete, provide the final report in the form of JSON file with these fields:
    {{
        "services": [...],
        "relationships": [...]
        }}
    For every relationship you must include:
        - source
        - target
        - purpose (what role does relationship play in services' work)
        - description (protocol, mechanism of connection)
        - evidence (place in source code that describes the relationship)

    You must return only JSON.
    """,
        }
    ]

    while True:
        response = chat(
            model="qwen3:14b",
            messages=messages,
            tools=tools,
            think=True,
            options={
                "num_ctx": 32000,
            },
        )
        # print("\nMODEL RESPONSE")
        # print("THINKING:")
        # print(response.message.thinking)
        # print("CONTENT:")
        # print(repr(response.message.content))
        # print("TOOL CALLS:")
        # print(response.message.tool_calls)
        messages.append(response.message)
        if response.message.tool_calls:
            for call in response.message.tool_calls:
                if call.function.name in available_functions:
                    print(
                        f"calling {call.function.name} with arguments {call.function.arguments}"
                    )
                    result = available_functions[call.function.name](
                        **call.function.arguments
                    )
                    print(f"result: {result}")
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": call.function.name,
                            "content": str(result),
                        }
                    )
        else:
            print("\nFINAL ANSWER")
            print(response.message.content)
            break


def run_agent_codeql(project_path: str, tools):
    available_functions = {}
    for tool in tools:
        available_functions[tool.__name__] = tool
    print(available_functions)
    # available_functions = {
    #    "read_source_file": read_source_file,
    #    "list_directory": list_directory,
    #    "save_codeql_query": save_codeql_query,
    #    "execute_codeql_query": execute_codeql_query,
    # }
    messages = [
        {
            "role": "user",
            "content": f"""

    You are an expert in analyzing microservice architecture apps written in Java.

    Your task is to determine:
    1. What services are in the application.
    2. What each service does.
    3. How the services interact with each other.
    4. What communication mechanisms are used.

    The project root is {project_path}.

    You have two analysis modes:

    1. CodeQL analysis — preferred
    2. Manual source inspection — fallback

    IMPORTANT:
    You MUST use CodeQL before performing extensive manual source inspection.

    Your required workflow is:

    PHASE 1 — Discover project structure
    - Inspect root pom.xml / build.gradle.
    - Identify all service modules.

    PHASE 2 — CodeQL analysis
    - ALWAYS Inspect available CodeQL queries from directories /codeql-query and /codeql-query-js from your current location
    - Run relevant existing queries. Databases are stored in /codeql-dbs from your current directory in format "<project name>-java|javascript"
    - If existing queries are insufficient, create new CodeQL queries.
    - Execute the queries.
    - Use their results to identify:
    - REST controllers
    - REST clients
    - Feign clients
    - Kafka producers/consumers
    - RabbitMQ producers/consumers
    - gRPC clients/servers
    - service discovery
    - HTTP calls
    - messaging relationships

    PHASE 3 — Manual verification
    Only after CodeQL analysis, inspect source files to verify and understand
    the relationships discovered by CodeQL.

    PHASE 4 — Complete analysis
    Verify that ALL services have been analyzed.

    Do NOT perform extensive manual source inspection before attempting CodeQL.
        Continue using tools until you have enough information to describe ALL services
    and their interactions.

    Do not stop after analyzing one service.
    You MUST inspect ALL service modules listed in the root pom.xml or in file structure.
    Only when the analysis is complete, provide the final report in the form of JSON file with these fields:
    {{
        "services": [...],
        "relationships": [...]
        }}
    For every relationship you must include:
        - source
        - target
        - purpose (what role does relationship play in services' work)
        - description (protocol, mechanism of connection)
        - evidence (place in source code that describes the relationship)

    You must return only JSON.
    """,
        }
    ]

    while True:
        response = chat(
            model="qwen3:14b",
            messages=messages,
            tools=tools,
            think=True,
            options={
                "num_ctx": 32000,
            },
        )
        # print("\nMODEL RESPONSE")
        # print("THINKING:")
        # print(response.message.thinking)
        # print("CONTENT:")
        # print(repr(response.message.content))
        # print("TOOL CALLS:")
        # print(response.message.tool_calls)
        messages.append(response.message)
        if response.message.tool_calls:
            for call in response.message.tool_calls:
                if call.function.name in available_functions:
                    print(
                        f"calling {call.function.name} with arguments {call.function.arguments}"
                    )
                    result = available_functions[call.function.name](
                        **call.function.arguments
                    )
                    print(f"result: {result}")
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": call.function.name,
                            "content": str(result),
                        }
                    )
        else:
            print("\nFINAL ANSWER")
            print(response.message.content)
            break


if __name__ == "__main__":

    '''res = save_codeql_query("""import java

    from Class c, Annotation ann
    where
        ann = c.getAnAnnotation() and
        ann.getType().getQualifiedName().matches("%EnableDiscoveryClient")
    select c, c.getFile().getRelativePath()""" ,"testie", "java")

        print(res)

        execute_codeql_query(res, "codeql-dbs/petclinic-java", "")'''

    """if len(sys.argv) == 2:
        project_path = sys.argv[1]
        run_agent_simple(project_path)
    else:
        print("too many arguments: the function expects only project path")"""

    if len(sys.argv) == 2:
        project_path = sys.argv[1]
        read_project_file, list_project_directory = make_project_related_tools(
            project_path
        )
        tools = [
            read_project_file,
            list_project_directory,
            save_codeql_query,
            execute_codeql_query,
        ]
        run_agent_codeql(project_path, tools)
    else:
        print("too many arguments: the function expects only project path")
