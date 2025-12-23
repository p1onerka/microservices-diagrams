import csv
import re

YAML_CONFIG_MASK = r"(?:.*/)?([^/]+)/src/main/resources/"
FRONTEND_REST_REQUESTS_MASK = r"(?:.*/)?([^/]+)/src/main/resources/.*/([^/]+)$"
SERVICE_MASK = r"(?:.*/)?([^/]+)/src/main/java/org/"

class CorruptedCodeQLDataException(Exception):
    def __init__(self, file_path: str, message: str):
        super().__init__(f"CodeQL data in file {file_path} behaves unexpectedly: {message}")


def extract_name_with_mask(path: str, mask: str) -> (re.Match[str] | None):
    #regex = re.compile(mask)
    #match = regex.search(path)
    match = re.match(mask, path)
    if match:
        return match
    return None


'''
So basically we have two names that we should map to eachother:
    1. The name of the directory in which microservice is placed.
    2. The name of microservice in Eureka system. All of REST calls will be made using that names.
Additionally third name can tale place:
    3. Routes to service in javascript frontend.
Ergo, first thing we need to do is map all of the names
'''
def map_directories_to_names(path: str) -> tuple[dict[str, str], dict[str, str]]:
    name_to_dir = {}
    dir_to_name = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) != 2:
                    raise CorruptedCodeQLDataException(path, f"there should be exactly 2 columns in this table, but there is {len(row)}")
                microservice_config_file_path = row[0].strip('"')
                microservice_dir = extract_name_with_mask(microservice_config_file_path, YAML_CONFIG_MASK).group(1)
                if microservice_dir:
                    microservice_name = row[1].strip('"')
                    name_to_dir[microservice_name] = microservice_dir
                    dir_to_name[microservice_dir] = microservice_name

    except FileNotFoundError:
        print(f"File not found: {path}")
    except CorruptedCodeQLDataException as e:
        print(e)
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
    return (name_to_dir, dir_to_name)

#map_directories_to_names("diag-data/petclinic/routes-of-services-in-frontend.csv")
#map_directories_to_names("diag-data/petclinic/routes1-of-services-in-frontend.csv")
#print(map_directories_to_names("diag-data/petclinic/service-names.csv"))

'''
Spring maps all services names in format of lb://<service name> to routes used in frontend.
Current version of locate-routes-of-servies-in-frontend query allows to find occurences of these routes
in javascript code and map them with names. What is left is pick the exact file from which
call is been made via mask
'''
def map_frontend_rest_requests(path: str) -> dict[str, tuple[str, str]]:
    names_to_caller_dir_and_file = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                if len(row) < 5:
                    raise CorruptedCodeQLDataException(path, f"there should be exactly 5 columns in this table, but there is {len(row)}")
                microservice_name = row[1].strip('"')
                microservice_caller_file_path = row[4].strip('"')
                match = extract_name_with_mask(microservice_caller_file_path, FRONTEND_REST_REQUESTS_MASK)
                names_to_caller_dir_and_file[microservice_name] = (match.group(1), match.group(2))

    except FileNotFoundError:
        print(f"File not found: {path}")
    except CorruptedCodeQLDataException as e:
        print(e)
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
    return names_to_caller_dir_and_file

#print(map_frontend_rest_requests("diag-data/petclinic/routes-of-services-in-frontend.csv"))

'''
Now, having maps of names to directories, we can analyze different kinds of services
based on their specific functions. For example, link the name "discovery-server" to real
discovery server that was found via query based on @DiscoveryServerApplication annotation
'''
def map_services_to_names(path: str, dir_to_name: dict[str, str]) -> dict[str, str]:
    services_with_names = {}
    try:
        with open(path, "r") as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader, None)
            for row in csv_reader:
                # TODO: maybe add parameter for num of column? now invariant is 2nd
                if len(row) < 2:
                    raise CorruptedCodeQLDataException(path, f"there should be exactly 5 columns in this table, but there is {len(row)}")
                microservice_path = row[1].strip('"')
                microservice_dir = extract_name_with_mask(microservice_path, SERVICE_MASK).group(1)
                services_with_names[dir_to_name[microservice_dir]] = microservice_dir

    except FileNotFoundError:
        print(f"File not found: {path}")
    except CorruptedCodeQLDataException as e:
        print(e)
    except Exception as e:
        print(f"Exception while reading file {path}: {e}")
    return services_with_names

#name_to_dir, dir_to_name = map_directories_to_names("diag-data/petclinic/service-names.csv")
#print(map_services_to_names("diag-data/petclinic/discovery-clients.csv", dir_to_name))
#print(map_services_to_names("diag-data/petclinic/discovery-server.csv", dir_to_name))