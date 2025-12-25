Data Analyzer
==================================

A module of functions that find a correspondence between data from different tables.
Is used for processing the output of CodeQL queries, mainly by mapping entities to their properties.
For example, the name of the service to its directory and then name to REST-request to it.

.. automodule:: data_analyzer
    :members:
    :undoc-members:

Mermaid Constructor
============================================

A module for generating entities of Mermaid diagram in Mermaid syntax from their properties.
Is needed for giving the project uniformity and eliminating typos inside diagram generation.

.. automodule:: mermaid_constructor
    :members:
    :undoc-members:

Diagram Drawer
==================================

A module for processing data obtained from CodeQL queries, 
building Mermaid diagrams based on it and generating output HTML document that contains diagram.

.. automodule:: diag_drawer
    :members:
    :undoc-members:

Main Script
============

A script for executing the tool. 
Should be launched with the following args:

1. `<project name>` -- how you would like to call the project inside the tool's system. All generated files will be placed in corresponding directory
2. `<project dir>` -- path to the project
3. `<java db name>` -- the name of your project's Java CodeQL database in codeql-dbs/ folder, or how would you like to call it
4. `<js db name>` -- the name of your project's Javascript CodeQL database in codeql-dbs/ folder, or how would you like to call it

When launched, script first checks for databases and creates them in case they are unavailible.
Then it performs all needed queries for each database, storing the results in `<project name>` folder.
Each query writes its results in `.bqrs` format, which is then being decoded into `.csv` format.
After data capture, script sets up python environment in case it's not set and calls the main `diag_drawer.py` module.

.. literalinclude:: ../../generate-diagram.sh
    :language: bash
    :linenos: