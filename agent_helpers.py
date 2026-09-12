import os
import subprocess

JAVA_QUERIES_PATH = "codeql-query"
JS_QUERIES_PATH = "codeql-query-js"
DBS_PATH = "codeql-dbs"
JAVA = "java"
JAVASCRIPT = "javascript"


def make_project_related_tools(project_path: str):
    """
    Makes tools that can be used to gain information about the project

    Args:
        project_path: Global path to the home dir of the project.
    """
    def read_source_file(file_path: str) -> str:
        """
        Read a source file in the project.

        Args:
            file_path: Local path to the source file.

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
        Look into project's directory contents.

        Args:
            dir_path: Local path of directory to inspect.

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

    def list_dir_structure(dir_path: str) -> str:
        """
        Fetches the file structure of the directory

        Args:
            dir_path: Global path to the dir to inspect
        Returns:
            File structure in text format
        """
        res = subprocess.run(["tree", f"{dir_path}"], capture_output=True, text=True)
        return res.stdout

    return read_source_file, list_directory, list_dir_structure


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
# TODO: do smth with return value?
def save_codeql_query(query: str, query_name: str, query_language: str) -> str:
    """
    Save the given codeQL query

    Args:
        query: query text in str format
        query_name: requested name of the file with query (with .ql extension)
        query_language: currently supports java/javascript. Depending on language, the query will be saved in one of the directories with according setup

    Returns:
        name of the query or error message
    """

    if query_language == "java":
        query_path = f"{JAVA_QUERIES_PATH}/{query_name}"
    elif query_language == "javascript":
        query_path = f"{JS_QUERIES_PATH}/{query_name}"
    else:
        return f"Error: the tool currently does not support queries in {query_language}"

    try:
        with open(query_path, "w", encoding="utf-8") as file:
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
            os.remove(f"{output_path}.bqrs")
            os.remove(f"{output_path}.csv")
            return content
    except Exception as e:
        return f"Error reading results {output_path} of query {query_path} on db {db_path}: {str(e)}"


def save_and_execute_codeql_query(query: str, query_name: str, db_name: str, language: str) -> str:
    """
    Saves and executes passed codeQL query

    Args:
        query: query text in str format
        query_name: the name of file with codeQL query (with the .ql extension)
        db_name: the name of database to perform the query on
        language: the target language of the query (currently java | javascript)

    Returns:
        the contents of .csv table with query results
    """
    save_codeql_query(query, query_name, language)
    return execute_codeql_query(query_name, db_name, language)


# TODO: refactor DB connection. maybe create factory for query execution methods with db_names as parameters
# or move dbs inside project dir to infer their path as <project_path>/db_java
def create_and_execute_java_annotation_to_classes_query(ann: str, db_name: str) -> str:
    """
    Creates and executes java codeQL query that finds all classes with given annotation

    Args:
        ann: Annotation without the @ symbol.
        db_name: the name of database to perform the query on.
    Returns:
        The contents of .csv table with query results.

    """
    query = f"""
        import java

        from Class c, Annotation ann
        where
            ann = c.getAnAnnotation() and
            ann.getType().getQualifiedName().matches("%{ann}")
        select c, c.getFile().getRelativePath()
    """
    query_name = f"search-for-{ann}-annotation.ql"
    save_codeql_query(query, query_name, JAVA)
    return execute_codeql_query(query_name, db_name, JAVA)


def create_and_execute_java_method_calls_to_classes_query(method: str, db_name: str) -> str:
    """
        Creates and executes java codeQL query that finds all classes with given method calls and returns their name and file with main class
    
        Args:
            method: Method to find calls of.
            db_name: the name of database to perform the query on.
        Returns:
            The contents of .csv table with query results.
    """
    query = f"""
        import java

        from MethodCall mc
        where mc.getMethod().getName() = "{method}"
        select mc.getCompilationUnit(), mc.getCompilationUnit().getRelativePath()
    """
    query_name = f"search-for-{method}-calls.ql"
    save_codeql_query(query, query_name, JAVA)
    return execute_codeql_query(query_name, db_name, JAVA)

# TODO: add .properties?
def create_and_execute_js_dir_to_yaml_query(dir_name: str, db_name: str) -> str:
    """
        Creates and executes java codeQL query that finds paths to microservice's configuration YAML based on its home directory.
    
        Args:
            dir_name: Home directory of service to inspect.
            db_name: the name of database to perform the query on.
        Returns:
            The contents of .csv table with query results.
    """
    query = f"""
        import javascript

        from YamlDocument doc
        where doc.getFile().getExtension() in ["yml", "yaml"] and
            doc.getFile().toString().matches("%{dir_name}%")
        select doc.getFile().getRelativePath()
    """
    query_name = f"search-for-{dir_name}-yml-config.ql"
    save_codeql_query(query, query_name, JAVASCRIPT)
    return execute_codeql_query(query_name, db_name, JAVASCRIPT)


# if create_and_execute_java_services_dependencies_query is too heavy on tokens
def create_and_execute_java_dir_to_dependencies_query(dir_name: str, query_name: str, db_name: str) -> str:
    pass


# TODO: rename all of this to smth like "perform query"?
def create_and_execute_java_services_dependencies_query(db_name: str) -> str:
    """
        Creates and executes java codeQL query that finds all pom.xml files in the project and maps modules' names to their dependencies
    
        Args:
            db_name: the name of database to perform the query on.
        Returns:
            The contents of .csv table with query results.
    """
    query = """
        import java
        import semmle.code.xml.MavenPom

        from Pom pom
        select pom, pom.getArtifact().getValue(), pom.getDependencies().getADependency().getArtifact().getValue()
    """
    query_name = f"search-for-modules-dependencies.ql"
    save_codeql_query(query, query_name, JAVA)
    return execute_codeql_query(query_name, db_name, JAVA)


#q = create_js_dir_to_yaml_query("spring-petclinic-genai-service")
#print(save_and_execute_codeql_query(q, "find-genai.ql", "spring-petclinic-microservices-js", "javascript"))
#print(execute_codeql_query("testie.ql", "piggymetrics-java", "java"))
#print(create_and_execute_js_dir_to_yaml_query("statistics-service", "piggymetrics-js"))
#print(execute_codeql_query("testie.ql", "SpringBootMicroservices-java","java"))
