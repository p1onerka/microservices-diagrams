import sys
import os
from data_analyzer import (
    CorruptedCodeQLDataException,
    extract_name_with_mask,
    map_backend_rest_requests,
    map_config_server_to_link,
    map_directories_to_names,
    map_frontend_rest_requests,
    map_services_to_names,
    extract_config_server,
)

TEST_TABLES_DIR = "tests/test_query_data"


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_extract_name_with_mask_match():
    mask = r"will be extracted: ([^/]+)"
    string = "will be extracted: data"
    res = extract_name_with_mask(string, mask).group(1)
    assert res == "data"


def test_extract_name_with_mask_no_match():
    mask = r"will be extracted: ([^/]+)"
    string = "this will not be extracted: data"
    res = extract_name_with_mask(string, mask)
    assert res is None


def test_CorruptedCodeQLDataException_message():
    exception = CorruptedCodeQLDataException(
        "some/invalid/path", "there should be file"
    )
    assert (
        str(exception)
        == "CodeQL data in file some/invalid/path behaves unexpectedly: there should be file"
    )


def test_map_directories_to_names_corrupted_data(capsys):
    res = map_directories_to_names(f"{TEST_TABLES_DIR}/one-col-table.csv")
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "CodeQL data in file tests/test_query_data/one-col-table.csv behaves unexpectedly: there should be exactly 2 columns in this table, but there is 1\n"
    )
    assert res == ({}, {})


def test_map_directories_to_names_file_not_found(capsys):
    res = map_directories_to_names("invalid_path")
    captured_message = capsys.readouterr()
    assert captured_message.out == "File not found: invalid_path\n"
    assert res == ({}, {})


def test_map_directories_to_names_wrong_file_type(capsys):
    res = map_directories_to_names(f"{TEST_TABLES_DIR}/not_csv.png")
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "Exception while reading file tests/test_query_data/not_csv.png: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte\n"
    )
    assert res == ({}, {})


def test_map_directories_to_names_valid_file():
    res = map_directories_to_names(f"{TEST_TABLES_DIR}/service-names.csv")
    expected = (
        {
            "admin-server": "spring-petclinic-admin-server",
            "api-gateway": "spring-petclinic-api-gateway",
            "customers-service": "spring-petclinic-customers-service",
            "discovery-server": "spring-petclinic-discovery-server",
            "genai-service": "spring-petclinic-genai-service",
            "vets-service": "spring-petclinic-vets-service",
            "visits-service": "spring-petclinic-visits-service",
        },
        {
            "spring-petclinic-admin-server": "admin-server",
            "spring-petclinic-api-gateway": "api-gateway",
            "spring-petclinic-customers-service": "customers-service",
            "spring-petclinic-discovery-server": "discovery-server",
            "spring-petclinic-genai-service": "genai-service",
            "spring-petclinic-vets-service": "vets-service",
            "spring-petclinic-visits-service": "visits-service",
        },
    )
    assert res == expected


def test_map_frontend_rest_requests_corrupted_data(capsys):
    res = map_frontend_rest_requests(f"{TEST_TABLES_DIR}/one-col-table.csv")
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "CodeQL data in file tests/test_query_data/one-col-table.csv behaves unexpectedly: there should be exactly 5 columns in this table, but there is 1\n"
    )
    assert res == {}


def test_map_frontend_rest_requests_file_not_found(capsys):
    res = map_frontend_rest_requests("invalid_path")
    captured_message = capsys.readouterr()
    assert captured_message.out == "File not found: invalid_path\n"
    assert res == {}


def test_map_frontend_rest_requests_wrong_file_type(capsys):
    res = map_frontend_rest_requests(f"{TEST_TABLES_DIR}/not_csv.png")
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "Exception while reading file tests/test_query_data/not_csv.png: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte\n"
    )
    assert res == {}


def test_map_frontend_rest_requests_valid_file():
    res = map_frontend_rest_requests(
        f"{TEST_TABLES_DIR}/routes-of-services-in-frontend.csv"
    )
    expected = {
        "customers-service": (
            "spring-petclinic-api-gateway",
            "pet-form.controller.js",
        ),
        "genai-service": (
            "spring-petclinic-api-gateway",
            "chat.js",
        ),
        "vets-service": (
            "spring-petclinic-api-gateway",
            "vet-list.controller.js",
        ),
        "visits-service": (
            "spring-petclinic-api-gateway",
            "visits.controller.js",
        ),
    }
    assert res == expected


def test_map_services_to_names_corrupted_data(capsys):
    res = map_services_to_names(f"{TEST_TABLES_DIR}/one-col-table.csv", {})
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "CodeQL data in file tests/test_query_data/one-col-table.csv behaves unexpectedly: there should be exactly 5 columns in this table, but there is 1\n"
    )
    assert res == {}


def test_map_services_to_names_file_not_found(capsys):
    res = map_services_to_names("invalid_path", {})
    captured_message = capsys.readouterr()
    assert captured_message.out == "File not found: invalid_path\n"
    assert res == {}


def test_map_services_to_names_wrong_file_type(capsys):
    res = map_services_to_names(f"{TEST_TABLES_DIR}/not_csv.png", {})
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "Exception while reading file tests/test_query_data/not_csv.png: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte\n"
    )
    assert res == {}


def test_map_services_to_names_valid_file():
    _, dir_to_name = map_directories_to_names(f"{TEST_TABLES_DIR}/service-names.csv")
    expected = {
        "admin-server": "spring-petclinic-admin-server",
        "api-gateway": "spring-petclinic-api-gateway",
        "customers-service": "spring-petclinic-customers-service",
        "genai-service": "spring-petclinic-genai-service",
        "vets-service": "spring-petclinic-vets-service",
        "visits-service": "spring-petclinic-visits-service",
    }
    res = map_services_to_names(f"{TEST_TABLES_DIR}/discovery-clients.csv", dir_to_name)
    assert res == expected


def test_map_backend_rest_requests_corrupted_data(capsys):
    res = map_backend_rest_requests(f"{TEST_TABLES_DIR}/one-col-table.csv", {})
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "CodeQL data in file tests/test_query_data/one-col-table.csv behaves unexpectedly: there should be exactly 3 columns in this table, but there is 1\n"
    )
    assert res == set()


def test_map_backend_rest_requests_file_not_found(capsys):
    res = map_backend_rest_requests("invalid_path", {})
    captured_message = capsys.readouterr()
    assert captured_message.out == "File not found: invalid_path\n"
    assert res == set()


def test_map_backend_rest_requests_wrong_file_type(capsys):
    res = map_backend_rest_requests(f"{TEST_TABLES_DIR}/not_csv.png", {})
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "Exception while reading file tests/test_query_data/not_csv.png: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte\n"
    )
    assert res == set()


def test_map_backend_rest_requests_valid_file():
    _, dir_to_name = map_directories_to_names(f"{TEST_TABLES_DIR}/service-names.csv")
    expected = {
        (
            "api-gateway",
            "CustomersServiceClient.java",
            "customers-service",
        ),
        (
            "api-gateway",
            "VisitsServiceClient.java",
            "visits-service",
        ),
        (
            "genai-service",
            "AIDataProvider.java",
            "customers-service",
        ),
        (
            "genai-service",
            "VectorStoreController.java",
            "vets-service",
        ),
    }
    res = map_backend_rest_requests(
        f"{TEST_TABLES_DIR}/rest-requesters.csv", dir_to_name
    )
    assert res == expected


def test_extract_config_server_file_not_found(capsys):
    res = extract_config_server("invalid_path")
    captured_message = capsys.readouterr()
    assert captured_message.out == "File not found: invalid_path\n"
    assert res == set()


def test_extract_config_server_wrong_file_type(capsys):
    res = extract_config_server(f"{TEST_TABLES_DIR}/not_csv.png")
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "Exception while reading file tests/test_query_data/not_csv.png: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte\n"
    )
    assert res == set()


def test_extract_config_server_valid_file():
    res = extract_config_server(f"{TEST_TABLES_DIR}/config-server.csv")
    expected = {"spring-petclinic-config-server"}
    assert res == expected


def test_map_config_server_to_link_corrupted_data(capsys):
    res = map_config_server_to_link(f"{TEST_TABLES_DIR}/one-col-table.csv", set())
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "CodeQL data in file tests/test_query_data/one-col-table.csv behaves unexpectedly: there should be exactly 2 columns in this table, but there is 1\n"
    )
    assert res == {}


def test_map_config_server_to_link_file_not_found(capsys):
    res = map_config_server_to_link("invalid_path", set())
    captured_message = capsys.readouterr()
    assert captured_message.out == "File not found: invalid_path\n"
    assert res == {}


def test_map_config_server_to_link_wrong_file_type(capsys):
    res = map_config_server_to_link(f"{TEST_TABLES_DIR}/not_csv.png", set())
    captured_message = capsys.readouterr()
    assert (
        captured_message.out
        == "Exception while reading file tests/test_query_data/not_csv.png: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte\n"
    )
    assert res == {}


def test_map_config_server_to_link_valid_file():
    servers = extract_config_server(f"{TEST_TABLES_DIR}/config-server.csv")
    expected = {
        "spring-petclinic-config-server": "https://github.com/spring-petclinic/spring-petclinic-microservices-config"
    }
    res = map_config_server_to_link(
        f"{TEST_TABLES_DIR}/config-server-link.csv", servers
    )
    assert res == expected
