if [ $# -eq 0 ]; then
    echo "Script should be called with $0 <project_name>"
fi

PROJECT_NAME=$1
PROJECT_DIR=$2

# TODO: make function for codeql queries

echo "Collecting data about services"
mkdir -p "diag-data/$PROJECT_NAME"

# searching for eureka disovery clients
codeql query run codeql-query/eureka-discovery-clients.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$PROJECT_NAME/discovery-clients.bqrs
codeql bqrs decode diag-data/$PROJECT_NAME/discovery-clients.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/discovery-clients.csv

# searching for eureka discovery server
codeql query run codeql-query/eureka-discovery-server.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$PROJECT_NAME/discovery-server.bqrs
codeql bqrs decode diag-data/$PROJECT_NAME/discovery-server.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/discovery-server.csv

# searching for load-balanced requesters
codeql query run codeql-query/eureka-load-balanced.ql   --database codeql-dbs/codeql-db-petclinic-microservices   --output diag-data/$PROJECT_NAME/eureka-load-balanced.bqrs
codeql bqrs decode diag-data/$PROJECT_NAME/eureka-load-balanced.bqrs   --format=csv   --output diag-data/$PROJECT_NAME/eureka-load-balanced.csv

./find-yml-app-configs.sh $PROJECT_DIR diag-data/$PROJECT_NAME

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
