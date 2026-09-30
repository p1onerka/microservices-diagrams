import os
import sys
import pytest
import agent_helpers
from agent_helpers import (
    create_and_execute_java_annotation_to_classes_query,
    create_and_execute_java_method_calls_to_classes_query,
    create_and_execute_java_services_config_paths_query,
    create_and_execute_java_services_dependencies_query,
    delete_codeql_query,
    execute_codeql_query,
    save_codeql_query,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


RESULT_LIMIT = 12000


class FakeCodeQL:
    """Imitates the `codeql` CLI as used by agent_helpers.execute_codeql_query."""

    def __init__(self):
        self.commands = []  # every command that was "run"
        self.executed_queries = []  # (query_path, db_path, query_text)
        self.results = {}  # query file stem -> csv content
        self.default_result = "col\nvalue\n"
        self.write_csv = True  # set to False to simulate a failed `bqrs decode`

    @staticmethod
    def _arg_after(cmd, flag):
        return cmd[cmd.index(flag) + 1]

    def __call__(self, cmd, *args, **kwargs):
        self.commands.append(list(cmd))
        assert cmd[0] == "codeql", "only the codeql CLI may be spawned"

        if cmd[1:3] == ["query", "run"]:
            query_path = cmd[3]
            db_path = self._arg_after(cmd, "--database")
            with open(query_path, "r", encoding="utf-8") as f:
                self.executed_queries.append((query_path, db_path, f.read()))
            with open(self._arg_after(cmd, "--output"), "wb") as f:
                f.write(b"bqrs")
        elif cmd[1:3] == ["bqrs", "decode"]:
            if self.write_csv:
                bqrs_path = cmd[3]
                stem = os.path.basename(bqrs_path)[: -len(".bqrs")]
                content = self.results.get(stem, self.default_result)
                with open(self._arg_after(cmd, "--output"), "w", encoding="utf-8") as f:
                    f.write(content)
        else:
            raise AssertionError(f"unexpected command: {cmd}")


@pytest.fixture(autouse=True)
def sandbox(tmp_path, monkeypatch):
    """Redirect every filesystem path used by agent_helpers to tmp_path."""
    java_dir = tmp_path / "codeql-query"
    js_dir = tmp_path / "codeql-query-js"
    dbs_dir = tmp_path / "codeql-dbs"
    for d in (java_dir, js_dir, dbs_dir):
        d.mkdir()

    monkeypatch.setattr(agent_helpers, "JAVA_QUERIES_PATH", str(java_dir))
    monkeypatch.setattr(agent_helpers, "JS_QUERIES_PATH", str(js_dir))
    monkeypatch.setattr(agent_helpers, "DBS_PATH", str(dbs_dir))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def fake_codeql(monkeypatch):
    fake = FakeCodeQL()
    monkeypatch.setattr(agent_helpers.subprocess, "run", fake)
    return fake


@pytest.fixture
def java_dir(sandbox):
    return sandbox / "codeql-query"


@pytest.fixture
def js_dir(sandbox):
    return sandbox / "codeql-query-js"


# container sanity check
def test_sandbox_paths_are_inside_tmp(sandbox):
    for path in (
        agent_helpers.JAVA_QUERIES_PATH,
        agent_helpers.JS_QUERIES_PATH,
        agent_helpers.DBS_PATH,
    ):
        assert os.path.abspath(path).startswith(str(sandbox))
    assert os.getcwd() == str(sandbox)


# save_codeql_query
def test_save_java_query(java_dir, js_dir):
    res = save_codeql_query("import java", "q.ql", "java")

    assert res == "q.ql"
    assert (java_dir / "q.ql").read_text(encoding="utf-8") == "import java"
    assert not (js_dir / "q.ql").exists()


def test_save_javascript_query(java_dir, js_dir):
    res = save_codeql_query("import javascript", "q.ql", "javascript")

    assert res == "q.ql"
    assert (js_dir / "q.ql").read_text(encoding="utf-8") == "import javascript"
    assert not (java_dir / "q.ql").exists()


def test_save_query_overwrites_existing_file(java_dir):
    save_codeql_query("old", "q.ql", "java")
    save_codeql_query("new", "q.ql", "java")

    assert (java_dir / "q.ql").read_text(encoding="utf-8") == "new"


def test_save_query_keeps_non_ascii_text(java_dir):
    text = "// сорокдва\nimport java"
    save_codeql_query(text, "q.ql", "java")

    assert (java_dir / "q.ql").read_text(encoding="utf-8") == text


def test_save_query_unsupported_language(sandbox):
    res = save_codeql_query("select 1", "q.ql", "python")

    assert res.startswith("Error:")
    assert "python" in res
    assert not (sandbox / "q.ql").exists()


def test_save_query_io_error_is_reported(java_dir):
    java_dir.rmdir()

    res = save_codeql_query("select 1", "q.ql", "java")

    assert res.startswith("Error creating q.ql query file")


# delete_codeql_query
def test_delete_java_query(java_dir):
    save_codeql_query("select 1", "tmp.ql", "java")

    delete_codeql_query("tmp.ql", "java")

    assert not (java_dir / "tmp.ql").exists()


def test_delete_javascript_query(js_dir):
    save_codeql_query("select 1", "tmp.ql", "javascript")

    delete_codeql_query("tmp.ql", "javascript")

    assert not (js_dir / "tmp.ql").exists()


def test_delete_only_removes_requested_file(java_dir, js_dir):
    save_codeql_query("a", "a.ql", "java")
    save_codeql_query("b", "b.ql", "java")
    save_codeql_query("a", "a.ql", "javascript")

    delete_codeql_query("a.ql", "java")

    assert not (java_dir / "a.ql").exists()
    assert (java_dir / "b.ql").exists()
    assert (js_dir / "a.ql").exists()


def test_delete_missing_query_returns_error(java_dir):
    res = delete_codeql_query("missing.ql", "java")

    assert res.startswith("Error deleting missing.ql query file")


def test_delete_unsupported_language(java_dir):
    save_codeql_query("select 1", "tmp.ql", "java")

    res = delete_codeql_query("tmp.ql", "cobol")

    assert res.startswith("Error:")
    assert "cobol" in res
    assert (java_dir / "tmp.ql").exists()


# execute_codeql_query
def test_execute_java_query_returns_csv(java_dir, sandbox, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")
    fake_codeql.results["query-result-q"] = "a,b\n1,2\n"

    res = execute_codeql_query("q.ql", "proj-java", "java")

    assert res == "a,b\n1,2\n"


def test_execute_java_query_builds_correct_commands(java_dir, sandbox, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")

    execute_codeql_query("q.ql", "proj-java", "java")

    run_cmd, decode_cmd = fake_codeql.commands
    assert run_cmd == [
        "codeql",
        "query",
        "run",
        f"{java_dir}/q.ql",
        "--database",
        f"{sandbox}/codeql-dbs/proj-java",
        "--output",
        "query-result-q.bqrs",
    ]
    assert decode_cmd == [
        "codeql",
        "bqrs",
        "decode",
        "query-result-q.bqrs",
        "--format=csv",
        "--output",
        "query-result-q.csv",
    ]


def test_execute_javascript_query_uses_js_directory(js_dir, sandbox, fake_codeql):
    save_codeql_query("select 1", "q.ql", "javascript")

    execute_codeql_query("q.ql", "proj-js", "javascript")

    query_path, db_path, _ = fake_codeql.executed_queries[0]
    assert query_path == f"{js_dir}/q.ql"
    assert db_path == f"{sandbox}/codeql-dbs/proj-js"


def test_execute_removes_temporary_result_files(java_dir, sandbox):
    save_codeql_query("select 1", "q.ql", "java")

    execute_codeql_query("q.ql", "proj-java", "java")

    assert not (sandbox / "query-result-q.bqrs").exists()
    assert not (sandbox / "query-result-q.csv").exists()


def test_execute_unsupported_language(sandbox, fake_codeql):
    res = execute_codeql_query("q.ql", "db", "go")

    assert res.startswith("Error:")
    assert "go" in res
    assert fake_codeql.commands == []


def test_execute_short_result_is_not_truncated(java_dir, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")
    content = "x" * (RESULT_LIMIT - 1)
    fake_codeql.results["query-result-q"] = content

    res = execute_codeql_query("q.ql", "db", "java")

    assert res == content


def test_execute_long_result_is_truncated(java_dir, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")
    fake_codeql.results["query-result-q"] = "x" * (RESULT_LIMIT * 2)

    res = execute_codeql_query("q.ql", "db", "java")

    assert res == "x" * RESULT_LIMIT + "\n... (file was cut due to size)"


def test_execute_result_of_exact_limit_is_marked_as_cut(java_dir, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")
    fake_codeql.results["query-result-q"] = "x" * RESULT_LIMIT

    res = execute_codeql_query("q.ql", "db", "java")

    assert res.endswith("... (file was cut due to size)")


def test_execute_reports_missing_result_file(java_dir, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")
    fake_codeql.write_csv = False  # decode step produced nothing

    res = execute_codeql_query("q.ql", "proj-java", "java")

    assert res.startswith("Error reading results query-result-q of query")
    assert "proj-java" in res


def test_execute_empty_result(java_dir, fake_codeql):
    save_codeql_query("select 1", "q.ql", "java")
    fake_codeql.results["query-result-q"] = ""

    assert execute_codeql_query("q.ql", "db", "java") == ""


# create_and_execute_java_annotation_to_classes_query
def test_annotation_query_result_and_cleanup(java_dir, fake_codeql):
    fake_codeql.results["query-result-search-for-RestController-annotation"] = "c,f\nA,a.java\n"

    res = create_and_execute_java_annotation_to_classes_query("RestController", "petclinic")

    assert res == "c,f\nA,a.java\n"
    assert list(java_dir.iterdir()) == []  # temporary query was deleted


def test_annotation_query_content_and_db(java_dir, sandbox, fake_codeql):
    create_and_execute_java_annotation_to_classes_query("RestController", "petclinic")

    (query_path, db_path, text), = fake_codeql.executed_queries
    assert query_path == f"{java_dir}/search-for-RestController-annotation.ql"
    assert db_path == f"{sandbox}/codeql-dbs/petclinic-java"
    assert "import java" in text
    assert 'matches("%RestController")' in text


# create_and_execute_java_method_calls_to_classes_query
def test_method_calls_query_result_and_cleanup(java_dir, fake_codeql):
    fake_codeql.results["query-result-search-for-exchange-calls"] = "u,p\nX,x.java\n"

    res = create_and_execute_java_method_calls_to_classes_query("exchange", "petclinic")

    assert res == "u,p\nX,x.java\n"
    assert list(java_dir.iterdir()) == []


def test_method_calls_query_content_and_db(java_dir, sandbox, fake_codeql):
    create_and_execute_java_method_calls_to_classes_query("exchange", "petclinic")

    (query_path, db_path, text), = fake_codeql.executed_queries
    assert query_path == f"{java_dir}/search-for-exchange-calls.ql"
    assert db_path == f"{sandbox}/codeql-dbs/petclinic-java"
    assert 'mc.getMethod().getName() = "exchange"' in text


# create_and_execute_java_services_dependencies_query
def test_dependencies_query_result_and_cleanup(java_dir, fake_codeql):
    fake_codeql.results["query-result-search-for-modules-dependencies"] = "p,a,d\n"

    res = create_and_execute_java_services_dependencies_query("petclinic")

    assert res == "p,a,d\n"
    assert list(java_dir.iterdir()) == []


def test_dependencies_query_content_and_db(java_dir, sandbox, fake_codeql):
    create_and_execute_java_services_dependencies_query("petclinic")

    (query_path, db_path, text), = fake_codeql.executed_queries
    assert query_path == f"{java_dir}/search-for-modules-dependencies.ql"
    assert db_path == f"{sandbox}/codeql-dbs/petclinic-java"
    assert "MavenPom" in text



# create_and_execute_java_services_config_paths_query
def test_config_paths_concatenates_yaml_and_properties(fake_codeql):
    fake_codeql.results["query-result-search-for-services-yml-config"] = "yml\n"
    fake_codeql.results["query-result-search-for-services-properties-config"] = "props\n"

    res = create_and_execute_java_services_config_paths_query("petclinic")

    assert res == "yml\nprops\n"


def test_config_paths_runs_each_query_on_matching_db(java_dir, js_dir, sandbox, fake_codeql):
    create_and_execute_java_services_config_paths_query("petclinic")

    (yaml_q, yaml_db, yaml_text), (prop_q, prop_db, prop_text) = fake_codeql.executed_queries
    assert yaml_q == f"{js_dir}/search-for-services-yml-config.ql"
    assert yaml_db == f"{sandbox}/codeql-dbs/petclinic-js"
    assert "YamlDocument" in yaml_text
    assert prop_q == f"{java_dir}/search-for-services-properties-config.ql"
    assert prop_db == f"{sandbox}/codeql-dbs/petclinic-java"
    assert "PropertiesFile" in prop_text
