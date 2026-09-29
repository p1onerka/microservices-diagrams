import os
import subprocess

JAVA_QUERIES_PATH = "codeql-query"
JS_QUERIES_PATH = "codeql-query-js"
DBS_PATH = "codeql-dbs"
JAVA = "java"
JAVASCRIPT = "javascript"


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

    output_path = f"query-result-{query_name[:-3]}"

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


def delete_codeql_query(query_name: str, query_language: str):
    """
    Deletes the given codeQL query

    Args:
        query_name: requested name of the file with query (with .ql extension)
        query_language: currently supports java/javascript

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
        os.remove(query_path)
    except Exception as e:
        return f"Error deleting {query_name} query file: {str(e)}"



# TODO: refactor DB connection. maybe create factory for query execution methods with db_names as parameters
# or move dbs inside project dir to infer their path as <project_path>/db_java
def create_and_execute_java_annotation_to_classes_query(
    ann: str, proj_name: str
) -> str:
    """
    Creates and executes java codeQL query that finds all classes with given annotation

    Args:
        ann: Annotation without the @ symbol.
        proj_name: the name of project to perform the query on.
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
    db_name = f"{proj_name}-java"
    query_name = f"search-for-{ann}-annotation.ql"
    save_codeql_query(query, query_name, JAVA)
    res = execute_codeql_query(query_name, db_name, JAVA)
    delete_codeql_query(query_name, JAVA)
    return res


def create_and_execute_java_method_calls_to_classes_query(
    method: str, proj_name: str
) -> str:
    """
    Creates and executes java codeQL query that finds all classes with given method calls and returns their name and file with main class

    Args:
        method: Method to find calls of.
        proj_name: the name of project to perform the query on.
    Returns:
        The contents of .csv table with query results.
    """
    query = f"""
        import java

        from MethodCall mc
        where mc.getMethod().getName() = "{method}"
        select mc.getCompilationUnit(), mc.getCompilationUnit().getRelativePath()
    """
    db_name = f"{proj_name}-java"
    query_name = f"search-for-{method}-calls.ql"
    save_codeql_query(query, query_name, JAVA)
    res = execute_codeql_query(query_name, db_name, JAVA)
    delete_codeql_query(query_name, JAVA)
    return res


# TODO: add .properties?
def create_and_execute_java_services_config_paths_query(proj_name: str) -> str:
    """
    Creates and executes java codeQL query that finds paths to microservices' configuration YAMLs and .properties.

    Args:
        proj_name: the name of project to perform the query on.
    Returns:
        The contents of .csv table with query results.
    """
    query_yaml = """
        import javascript

        from YamlDocument doc
        where doc.getFile().getExtension() in ["yml", "yaml"] and
            doc.getFile().toString().matches("%/src/main/resources%")
        select doc.getFile().getRelativePath()
    """
    query_properties = """import java
        import semmle.code.configfiles.ConfigFiles

        from PropertiesFile config
        where config.getRelativePath().toString().matches("%/src/main/resources%")
        select config.getRelativePath()
    """
    query_yaml_name = "search-for-services-yml-config.ql"
    query_properties_name = "search-for-services-properties-config.ql"
    save_codeql_query(query_yaml, query_yaml_name, JAVASCRIPT)
    save_codeql_query(query_properties, query_properties_name, JAVA)
    res_yaml = execute_codeql_query(query_yaml_name, f"{proj_name}-js", JAVASCRIPT)
    res_properties = execute_codeql_query(
        query_properties_name, f"{proj_name}-java", JAVA
    )
    return res_yaml + res_properties


# if create_and_execute_java_services_dependencies_query is too heavy on tokens
def create_and_execute_java_dir_to_dependencies_query(
    dir_name: str, query_name: str, db_name: str
) -> str:
    pass


# TODO: rename all of this to smth like "perform query"?
def create_and_execute_java_services_dependencies_query(proj_name: str) -> str:
    """
    Creates and executes java codeQL query that finds all pom.xml files in the project and maps modules' names to their dependencies

    Args:
        proj_name: the name of project to perform the query on.
    Returns:
        The contents of .csv table with query results.
    """
    query = """
        import java
        import semmle.code.xml.MavenPom

        from Pom pom
        select pom, pom.getArtifact().getValue(), pom.getDependencies().getADependency().getArtifact().getValue()
    """
    db_name = f"{proj_name}-java"
    query_name = f"search-for-modules-dependencies.ql"
    save_codeql_query(query, query_name, JAVA)
    res = execute_codeql_query(query_name, db_name, JAVA)
    delete_codeql_query(query_name, JAVA)
    return res
