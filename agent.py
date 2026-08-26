from ollama import chat
import os
import sys


def read_source_file(file_path: str, project_path: str) -> str:
    """
    Read a source file in the project.

    Args:
        file_path: Local path to the source file.
        project_path: Global path to the home dir of the project.

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


def list_directory(dir_path: str, project_path: str) -> str:
    """
    Look into directory contents.

    Args:
        dir_path: Local path of directory to inspect.
        project_path: Global path to the home dir of the project.

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


def run_agent_simple(project_path: str):
    available_functions = {
        "read_source_file": read_source_file,
        "list_directory": list_directory,
    }
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
            tools=[read_source_file, list_directory],
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
    if len(sys.argv) == 2:
        project_path = sys.argv[1]
        run_agent_simple(project_path)
    else:
        print("too many arguments: the function expects only project path")
