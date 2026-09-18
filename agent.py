from ollama import chat

from prompts import (
    create_no_codeql_prompt,
    create_codeql_without_patterns_prompt,
    create_codeql_with_patterns_prompt,
)


def run_agent_simple(project_path: str, tools) -> str:
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
            return response.message.content


def run_agent_codeql(project_path: str, tools) -> str:
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
            return response.message.content


def run_agent_codeql_with_patterns(project_path: str, tools) -> str:
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
            return response.message.content
