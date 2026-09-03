from ollama import chat
import sys

from agent_helpers import (
    make_project_related_tools,
    list_codeql_queries,
    read_codeql_query_by_name,
    save_codeql_query,
    execute_codeql_query,
    save_and_execute_codeql_query,
    create_java_annotation_to_classes_query,
    create_java_method_calls_to_classes_query,
    create_js_dir_to_yaml_query,
)

from prompts import (
    create_no_codeql_prompt,
    create_codeql_without_patterns_prompt,
    create_codeql_with_patterns_prompt,
)


def run_agent_simple(project_path: str, tools):
    available_functions = {}
    for tool in tools:
        available_functions[tool.__name__] = tool

    prompt = create_no_codeql_prompt(project_path)
    messages = [
        {
            "role": "user",
            "content": prompt,
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
    prompt = create_codeql_without_patterns_prompt(project_path)
    # available_functions = {
    #    "read_source_file": read_source_file,
    #    "list_directory": list_directory,
    #    "save_codeql_query": save_codeql_query,
    #    "execute_codeql_query": execute_codeql_query,
    # }
    messages = [
        {
            "role": "user",
            "content": prompt,
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


def run_agent_codeql_with_patterns(project_path: str, tools):
    available_functions = {}
    for tool in tools:
        available_functions[tool.__name__] = tool
    print(available_functions)
    prompt = create_codeql_with_patterns_prompt(project_path)
    messages = [
        {
            "role": "user",
            "content": prompt,
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

    """print(list_codeql_queries())
    print(read_codeql_query_by_name("eureka-discovery-server"))"""

    '''res = save_codeql_query("""import java

    from Class c, Annotation ann
    where
        ann = c.getAnAnnotation() and
        ann.getType().getQualifiedName().matches("%EnableDiscoveryClient")
    select c, c.getFile().getRelativePath()""" ,"testie", "java")

        print(res)

        execute_codeql_query(res, "codeql-dbs/petclinic-java", "")'''

    """
    if len(sys.argv) == 2:
        project_path = sys.argv[1]
        run_agent_simple(project_path)
    else:
        print("too many arguments: the function expects only project path")"""

    if len(sys.argv) == 2:
        project_path = sys.argv[1]
        read_project_file, list_project_directory, list_dir_structure = (
            make_project_related_tools(project_path)
        )
        tools = [
            read_project_file,
            list_project_directory,
            save_codeql_query,
            execute_codeql_query,
            list_codeql_queries,
            read_codeql_query_by_name,
            list_dir_structure,
        ]
        tools_simple = [
            read_project_file,
            list_project_directory,
            list_dir_structure,
        ]
        tools_patterns = [
            read_project_file,
            list_project_directory,
            list_dir_structure,
            save_and_execute_codeql_query,
            create_java_annotation_to_classes_query,
            create_java_method_calls_to_classes_query,
            create_js_dir_to_yaml_query,
        ]
        # run_agent_codeql(project_path, tools)
        run_agent_simple(project_path, tools_simple)
        # run_agent_codeql_with_patterns(project_path, tools_patterns)

    else:
        print("too many arguments: the function expects only project path")
