if [ $# -lt 4 ]; then
    echo "Script should be called with $0 <project_name> <project_dir> <java_database_name> <javascript_database_name>"
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR=$2
JAVA_DB_NAME=$3
JS_DB_NAME=$4

BQRS_DIR_NAME="$PROJECT_NAME/bqrs"

# TODO: make function for codeql queries

echo "Searching for databases in codeql-dbs directory. In case there are not, creating them"
if [ ! -d "codeql-dbs" ]; then
    mkdir -p "codeql-dbs"
fi
JAVA_DB_PATH="codeql-dbs/$JAVA_DB_NAME"
JS_DB_PATH="codeql-dbs/$JS_DB_NAME"
if [ ! -d "$JAVA_DB_PATH" ]; then
    echo "Creating java database"
    codeql database create "$JAVA_DB_PATH" --language=java --source-root="$PROJECT_DIR"
fi
if [ ! -d "$JS_DB_PATH" ]; then
    echo "Creating javascript database"
    codeql database create "$JS_DB_PATH" --language=javascript --source-root="$PROJECT_DIR"
fi

echo "Collecting data about services"
mkdir -p "diag_data/$PROJECT_NAME"
mkdir -p "diag_data/$BQRS_DIR_NAME"

# ------------------------ JAVA BLOCK ------------------------ 

# searching for eureka disovery clients
codeql query run codeql-query/eureka-discovery-clients.ql   --database $JAVA_DB_PATH   --output diag_data/$BQRS_DIR_NAME/discovery-clients.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/discovery-clients.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/discovery-clients.csv

# searching for eureka discovery server
codeql query run codeql-query/eureka-discovery-server.ql   --database $JAVA_DB_PATH   --output diag_data/$BQRS_DIR_NAME/discovery-server.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/discovery-server.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/discovery-server.csv

# searching for load-balanced requesters
codeql query run codeql-query/eureka-load-balanced.ql   --database $JAVA_DB_PATH   --output diag_data/$BQRS_DIR_NAME/eureka-load-balanced.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/eureka-load-balanced.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/eureka-load-balanced.csv

# searching for REST requesters
codeql query run codeql-query/rest-requesters.ql   --database $JAVA_DB_PATH   --output diag_data/$BQRS_DIR_NAME/rest-requesters.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/rest-requesters.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/rest-requesters.csv

# ---------------------- CONFIG BLOCK ---------------------- 

# searching for app names in Eureka (for mapping them with REST requests later)
codeql query run codeql-query-js/locate-service-names.ql   --database $JS_DB_PATH   --output diag_data/$BQRS_DIR_NAME/service-names.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/service-names.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/service-names.csv

# searching for config server
codeql query run codeql-query-js/locate-config-server.ql   --database $JS_DB_PATH   --output diag_data/$BQRS_DIR_NAME/config-server.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/config-server.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/config-server.csv

# searching for link to github config server if there is one
codeql query run codeql-query-js/locate-config-server-link.ql   --database $JS_DB_PATH   --output diag_data/$BQRS_DIR_NAME/config-server-link.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/config-server-link.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/config-server-link.csv

# --------------------- JAVASCRIPT BLOCK --------------------- 

# searching for GET requests in javascript code
codeql query run codeql-query-js/rest-requests-javascript-fontend.ql   --database $JS_DB_PATH   --output diag_data/$BQRS_DIR_NAME/js-gets.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/js-gets.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/js-gets.csv 

# searching for routes of services in frontend
codeql query run codeql-query-js/locate-routes-of-services-in-frontend.ql   --database $JS_DB_PATH   --output diag_data/$BQRS_DIR_NAME/routes-of-services-in-frontend.bqrs
codeql bqrs decode diag_data/$BQRS_DIR_NAME/routes-of-services-in-frontend.bqrs   --format=csv   --output diag_data/$PROJECT_NAME/routes-of-services-in-frontend.csv 

echo "Building diagram"
if [ -d "diag_data/.venv" ]; then
    (
        source diag_data/.venv/bin/activate
        python3 diag_data/diag_drawer.py "$PROJECT_NAME"
    )
else
    (
        cd diag_data
        python3 -m venv .venv
        source .venv/bin/activate
        #pip3 install pandas networkx matplotlib
        cd ..
        python3 diag_data/diag_drawer.py "$PROJECT_NAME"
    )
fi
