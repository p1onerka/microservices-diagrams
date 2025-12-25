import csv
import re

YAML_CONFIG_MASK = r"(?:.*/)?([^/]+)/src/main/resources/"
FRONTEND_REST_REQUESTS_MASK = r"(?:.*/)?([^/]+)/src/main/resources/.*/([^/]+)$"
INSIDE_REST_REQUESTS_MASK = r"http://([^/]+)/.*"
FILE_MASK = r"(?:.*/)?([^/]+)"
SERVICE_MASK = r"(?:.*/)?([^/]+)/src/main/java/"


class CorruptedCodeQLDataException(Exception):
    """
        An exception for case when table with CodeQL query results behaves unexpected,
        eg. has a different numbers of columns than expected.
    """
    def __init__(self, file_path: str, message: str):
        super().__init__(
            f"CodeQL data in file {file_path} behaves unexpectedly: {message}"
        )


def extract_name_with_mask(path: str, mask: str) -> re.Match[str] | None:
    """
        A function for extracting part of the string via SQL-like regular expressions.
        Is used in other functions for finding patterns in strings, eg. when searching for
        module of file by its relative path (in that case, mask should look like this 
        `"(?:.*/)?([^/]+)/src/main/java/"`. For more info about mask syntax, check module `re`). 
    """
    match = re.match(mask, path)
    if match:
        return match
    return None


def map_directories_to_names(path: str) -> tuple[dict[str, str], dict[str, str]]:
    """
        A function for mapping the home directories of services to their names fetched from configuration JSONs.
        Output consists of dict `({service name : service dir}, {service dir : service name})`.
    """
    name_to_dir = {}
    dir_to_name = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) != 2:
                    raise CorruptedCodeQLDataException(
                        path,
                        f"there should be exactly 2 columns in this table, but there is {len(row)}",
                    )
                microservice_config_file_path = row[0].strip('"')
                microservice_dir_match = extract_name_with_mask(
                    microservice_config_file_path, YAML_CONFIG_MASK
                )
                if microservice_dir_match:
                    microservice_dir = microservice_dir_match.group(1)
                    microservice_name = row[1].strip('"')
                    name_to_dir[microservice_name] = microservice_dir
                    dir_to_name[microservice_dir] = microservice_name

    except FileNotFoundError:
        print(f"File not found: {path}")
        return ({}, {})
    except CorruptedCodeQLDataException as e:
        print(e)
        return ({}, {})
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
        return ({}, {})
    return (name_to_dir, dir_to_name)


def map_frontend_rest_requests(path: str) -> dict[str, tuple[str, str]]:
    """
        A function for mapping inner names of services to REST-requests made from javascript frontend.
        Output consists of dict `{callee service name : (caller dir, caller file)}`.
    """
    names_to_caller_dir_and_file = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) < 5:
                    raise CorruptedCodeQLDataException(
                        path,
                        f"there should be exactly 5 columns in this table, but there is {len(row)}",
                    )
                microservice_name = row[1].strip('"')
                microservice_caller_file_path = row[4].strip('"')
                match = extract_name_with_mask(
                    microservice_caller_file_path, FRONTEND_REST_REQUESTS_MASK
                )
                if match:
                    names_to_caller_dir_and_file[microservice_name] = (
                        match.group(1),
                        match.group(2),
                    )

    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}
    except CorruptedCodeQLDataException as e:
        print(e)
        return {}
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
        return {}
    return names_to_caller_dir_and_file


def map_services_to_names(
    path: str, dir_to_name: dict[str, str], column: int = 1
) -> dict[str, str]:
    """
        A function for extracting service home dir from path and mapping it to one of the previously extracted names.
        Output consists of dict `{service name : service dir}`.
    """
    services_with_names = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) < 2:
                    raise CorruptedCodeQLDataException(
                        path,
                        f"there should be exactly 5 columns in this table, but there is {len(row)}",
                    )
                microservice_path = row[column].strip('"')
                microservice_dir_match = extract_name_with_mask(
                    microservice_path, SERVICE_MASK
                )
                if microservice_dir_match:
                    microservice_dir = microservice_dir_match.group(1)
                    if dir_to_name.get(microservice_dir):
                        services_with_names[dir_to_name[microservice_dir]] = (
                            microservice_dir
                        )

    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}
    except CorruptedCodeQLDataException as e:
        print(e)
        return {}
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
        return {}
    return services_with_names


def map_backend_rest_requests(
    path: str, dir_to_name: dict[str, str]
) -> set[tuple[str, str, str]]:
    """
        A function for mapping backend REST-requests (made from Java code) to the names of caller and callee.
        Output consists of dict `{(caller name, caller file, callee name)}`.
    """
    caller_to_callee = set()
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) < 3:
                    raise CorruptedCodeQLDataException(
                        path,
                        f"there should be exactly 3 columns in this table, but there is {len(row)}",
                    )
                requester_path = row[1].strip('"')
                requester_dir_match = extract_name_with_mask(
                    requester_path, SERVICE_MASK
                )
                requester_file_match = extract_name_with_mask(requester_path, FILE_MASK)
                request_link = row[2].strip('"')
                requested_service_match = extract_name_with_mask(
                    request_link, INSIDE_REST_REQUESTS_MASK
                )
                if (
                    requester_dir_match
                    and requested_service_match
                    and requester_file_match
                ):
                    requester_dir = requester_dir_match.group(1)
                    requested_service = requested_service_match.group(1)
                    requester_file = requester_file_match.group(1)
                    requester_name = dir_to_name[requester_dir]
                    caller_to_callee.add(
                        (requester_name, requester_file, requested_service)
                    )
    except FileNotFoundError:
        print(f"File not found: {path}")
        return set()
    except CorruptedCodeQLDataException as e:
        print(e)
        return set()
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
        return set()
    return caller_to_callee


def extract_config_server(path: str) -> set[str]:
    """
        A function for extracting home directory of configuration server (or servers).
        Output consists of `{config server dir}`.
    """
    config_servers = set()
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                server_path = row[0].strip('"')
                server_dir_match = extract_name_with_mask(server_path, YAML_CONFIG_MASK)
                if server_dir_match:
                    server_dir = server_dir_match.group(1)
                    config_servers.add(server_dir)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return set()
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
        return set()
    return config_servers


def map_config_server_to_link(path: str, servers: set[str]) -> dict[str, str]:
    """
        A function for mapping configuration server home dir to its main server on github, in case there is one.
        Output consists of dict `{config server dir : config server link on github}`.
    """
    name_to_link = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) < 2:
                    raise CorruptedCodeQLDataException(
                        path,
                        f"there should be exactly 2 columns in this table, but there is {len(row)}",
                    )
                config_server_path = row[0].strip('"')
                config_server_name_match = extract_name_with_mask(
                    config_server_path, YAML_CONFIG_MASK
                )
                if (
                    config_server_name_match
                    and config_server_name_match.group(1) in servers
                ):
                    server = config_server_name_match.group(1)
                    config_server_link = row[1].strip('"')
                    name_to_link[server] = config_server_link

    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}
    except CorruptedCodeQLDataException as e:
        print(e)
        return {}
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
        return {}
    return name_to_link
