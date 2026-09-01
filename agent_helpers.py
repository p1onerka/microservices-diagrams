import os
import subprocess

JAVA_QUERIES_PATH = "codeql-query"
JS_QUERIES_PATH = "codeql-query-js"
DBS_PATH = "codeql-dbs"


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


def list_codeql_queries() -> dict[str, list[str]]:
    """
    Get the list of available codeQL queries in java and javascript languages

    Returns: the dictionary with "java" and "javascript" keys with lists of queries for each language as values
    """

    items = os.listdir(JAVA_QUERIES_PATH)
    result_java = []
    for item in sorted(items):
        if item[-3:] == ".ql":
            result_java.append(f"{item}")

    items = os.listdir(JS_QUERIES_PATH)
    result_js = []
    for item in sorted(items):
        if item[-3:] == ".ql":
            result_js.append(f"{item}")
    return {"java": result_java, "javascript": result_js}


def read_codeql_query_by_name(name: str) -> str:
    """
    Read the codeQL query by given name

    Args:
        name: the name of the query to read without the .ql extension
    Returns:
        The text of query via str
    """
    dirs = [JAVA_QUERIES_PATH, JS_QUERIES_PATH]
    try:
        for dir in dirs:
            path = f"{dir}/{name}.ql"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read(12000)
                    if len(content) == 12000:
                        return content + "\n... (file was cut due to size)"
                    return content
            except FileNotFoundError:
                continue  # to not stop after fst dir. TODO: fix?
        return f"Error: query {name} not found"
    except Exception as e:
        return f"Error reading query {name}: {str(e)}"


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
        query_name = f"{JAVA_QUERIES_PATH}/{query_name}.ql"
    elif query_language == "javascript":
        query_name = f"{JS_QUERIES_PATH}/{query_name}.ql"
    else:
        return f"Error: the tool currently does not support queries in {query_language}"

    try:
        with open(query_name, "w", encoding="utf-8") as file:
            file.write(query)
        return query_name
    except Exception as e:
        return f"Error creating {query_name} query file: {str(e)}"


# TODO: make language argument optional? can be prob infered from db name
# TODO: ADT for language
# TODO: exceptions in separate file
def execute_codeql_query(query_name: str, db_name: str, language: str) -> str:
    """
    Executes passed codeQL query

    Args:
        query_name: the name of file with codeQL query (with the .ql extension)
        db_name: the name of database to perform the query on
        language: the target language of the query (currently java | javascript)

    Returns:
        the contents of .csv table with query results
    """
    if language == "java":
        query_path = f"{JAVA_QUERIES_PATH}/{query_name}"
        db_path = f"{DBS_PATH}/{db_name}"
    elif language == "javascript":
        query_path = f"{JS_QUERIES_PATH}/{query_name}"
        db_path = f"{DBS_PATH}/{db_name}"
    else:
        return f"Error: the tools does not support the queries in {language}"

    output_path = "query-result"

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

    try:
        with open(f"{output_path}.csv", "r", encoding="utf-8") as f:
            content = f.read(12000)
            if len(content) == 12000:
                return content + "\n... (file was cut due to size)"
            return content
    except Exception as e:
        return f"Error reading results {output_path} of query {query_path} on db {db_path}: {str(e)}"
