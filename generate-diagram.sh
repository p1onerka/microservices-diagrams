if [ $# -eq 0 ]; then
    echo "Script should be called with $0 <project_name>"
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR=$2
BQRS_DIR_NAME="$PROJECT_NAME/bqrs"

# TODO: make function for codeql queries

echo "Collecting data about services"
mkdir -p "diag-data/$PROJECT_NAME"
mkdir -p "diag-data/$BQRS_DIR_NAME"

# searching for eureka disovery clients
codeql query run codeql-query/eureka-discovery-clients.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/discovery-clients.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/discovery-clients.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/discovery-clients.csv

# searching for eureka discovery server
codeql query run codeql-query/eureka-discovery-server.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/discovery-server.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/discovery-server.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/discovery-server.csv

# searching for load-balanced requesters
codeql query run codeql-query/eureka-load-balanced.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/eureka-load-balanced.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/eureka-load-balanced.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/eureka-load-balanced.csv

# searching for REST requesters
codeql query run codeql-query/rest-requesters.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/rest-requesters.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/rest-requesters.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/rest-requesters.csv

# searching for app names in Eureka (for mapping them with REST requests later)
# ./find-yml-app-configs.sh $PROJECT_DIR diag-data/$PROJECT_NAME

# searching for GET requests in javascript code
codeql query run codeql-query-js/rest-requests-javascript-fontend.ql   --database codeql-dbs/codeql-db-javascript-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/js-gets.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/js-gets.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/js-gets.csv   

# searching for app names in Eureka (for mapping them with REST requests later)
codeql query run codeql-query-js/locate-service-names.ql   --database codeql-dbs/codeql-db-javascript-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/service-names.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/service-names.bqrs   --format=csv   --output diag-data/petclinic/service-names.csv

# find link to github config server
codeql query run codeql-query-js/locate-config-server.ql   --database codeql-dbs/codeql-db-javascript-petclinic-microservices   --output diag-data/$BQRS_DIR_NAME/config-server-link.bqrs
codeql bqrs decode diag-data/$BQRS_DIR_NAME/config-server-link.bqrs   --format=csv   --output diag-data/petclinic/config-server-link.csv

echo "Building diagram"
if [ -d "diag-data/.venv" ]; then
    (
        source diag-data/.venv/bin/activate
        python3 diag-data/diag-drawer.py "$PROJECT_NAME"
    )
else
    (
        cd diag-data
        python3 -m venv .venv
        source .venv/bin/activate
        pip3 install pandas networkx matplotlib
        cd ..
        python3 diag-data/diag-drawer.py "$PROJECT_NAME"
    )
fi
