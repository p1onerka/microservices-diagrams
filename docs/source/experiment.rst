Agent Helpers
=============

Functions that save, run and delete CodeQL queries for the OpenCode agents.
A query is written to ``codeql-query`` or ``codeql-query-js``, executed against a database in ``codeql-dbs``, and the CSV result is returned.
The higher-level helpers build a Java or JavaScript query, run it on ``<project>-java`` or ``<project>-js``, and remove the temporary query file.

.. automodule:: agent_helpers
    :members:
    :undoc-members:

CodeQL MCP Server
=================

MCP server that gives the codeql-agent three CodeQL lookups: classes with an annotation, classes that call a method, and Maven module dependencies.
Start it as a stdio server:

.. code-block:: bash

    python codeql_mcp.py

Each tool call is timed. The duration is appended to ``codeql_tools_time``, which ``opencode_exp.sh`` reads after a ``codeql-agent`` run.
Pass the project name (the last path segment), not the filesystem path, as ``proj_name``.

.. automodule:: codeql_mcp
    :members:
    :undoc-members:

Metrics Writer
==============

Appends one experiment row to a CSV file.
``opencode_exp.sh`` calls it after every run:

.. code-block:: bash

    python3 append_metrics.py <csv_file> <value> [<value> ...]

Every argument after the file path becomes one cell of the new row. The header is written by the shell script, not by this file.

.. literalinclude:: ../../append_metrics.py
    :language: python
    :linenos:

OpenCode Experiment
===================

Runs one project through an OpenCode agent thirty times and records llama.cpp and agent metrics.

.. code-block:: bash

    ./opencode_exp.sh <project_path>

``AGENT_NAME`` at the top of the script selects the agent (``reading-agent`` or ``codeql-agent``).
For each repetition the script starts a local llama server, waits until ``http://127.0.0.1:8080/health`` answers, then runs ``opencode run`` on the given project.
After the agent exits it reads ``http://127.0.0.1:8080/metrics`` and, for ``codeql-agent``, the tool timings from ``codeql_tools_time``.
The agent report is taken from ``report.json`` when that file exists.
The row is appended to ``opencode-exp/<project>-<agent>.csv``.
OpenCode sessions created during the run are deleted before the next repetition.

.. literalinclude:: ../../opencode_exp.sh
    :language: bash
    :linenos:

Experiment Launcher
===================

Runs ``opencode_exp.sh`` once for every project in the list inside the script.

Set ``PROJECTS_DIR`` to the directory that contains the cloned projects, then launch:

.. code-block:: bash

    ./exp_launcher.sh

A project that is not a directory, or whose run exits with a non-zero status, is reported at the end. The launcher itself exits with status 0.

.. literalinclude:: ../../exp_launcher.sh
    :language: bash
    :linenos:

OpenCode Agents
===============

Agent definitions live in ``.opencode/agents/``.
Both agents analyse a Java (Spring) microservice project and write one JSON report, ``report.json``, with two lists: ``services`` (name and description) and ``relationships`` (source, target, purpose, description, evidence).
The report is the last action of the agent.

reading-agent
-------------

File ``.opencode/agents/reading-agent.md``. CodeQL tools are denied.
The agent discovers services from the root build file or the directory layout, then reads each module's configuration, its ``@SpringBootApplication`` class, and the classes that take part in communication (controllers, clients, messaging, gateway routes).

codeql-agent
------------

File ``.opencode/agents/codeql-agent.md``. CodeQL tools are allowed and are the primary source of evidence.
The agent calls ``get_java_dependencies`` once, then ``search_java_annotation`` and ``search_java_method_calls`` for communication-related annotations and methods.
File reads are limited to the root build file and to service configuration (``.yml``, ``.yaml``, ``.properties``), including Spring Cloud Config files when a config server is present.
The ``proj_name`` argument of every CodeQL tool is the last segment of the project path, not the path itself.
