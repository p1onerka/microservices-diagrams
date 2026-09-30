#!/bin/bash

set -u

SCRIPT="./opencode_exp.sh"
PROJECTS_DIR=""

PROJECTS=(
    "spring-kafka-microservices"
    "microservices-architecture-mongodb"
    "roshanadh-springboot-microservices"
    "spring-rabbitmq-messaging-microservices"
    "ecommerce-microservices"
    "Microservices-example"
    "sample-spring-kafka-microservices"
    "distributed-systems-microservice"
    "E-Commerce-app"
    "spring-kafka-microservices-app"
    "sample-spring-microservices-new"
    "pandaind-springboot-microservices"
    "kafka-microservices-with-saga"
    "ghifariyudha-spring-boot-microservices"
    "SpringBootMicroservices"
    "spring-microservices-blueprint"
    "spring-petclinic-microservices"
    "library-microservices"
    "piggymetrics"
    "spring-boot-microservices-series-v2"
)

TOTAL=${#PROJECTS[@]}
FAILED_PROJECTS=()
INDEX=0

for PROJECT_NAME in "${PROJECTS[@]}"; do
    INDEX=$((INDEX + 1))
    PROJECT_PATH="$PROJECTS_DIR/$PROJECT_NAME"

    echo "========================================"
    echo "Experiment $INDEX/$TOTAL on $PROJECT_PATH"
    echo "========================================"

    if [[ ! -d "$PROJECT_PATH" ]]; then
        echo "Error: dir not found: $PROJECT_PATH"
        FAILED_PROJECTS+=("$PROJECT_NAME (not found)")
        echo
        continue
    fi

    "$SCRIPT" "$PROJECT_PATH"
    EXIT_CODE=$?

    echo
    echo "Exp $INDEX ($PROJECT_NAME) return code: $EXIT_CODE"
    echo

    if [[ $EXIT_CODE -ne 0 ]]; then
        FAILED_PROJECTS+=("$PROJECT_NAME (exit code $EXIT_CODE)")
    fi
done

echo "========================================"
echo "Exps finished: $((TOTAL - ${#FAILED_PROJECTS[@]}))/$TOTAL succeeded"
if [[ ${#FAILED_PROJECTS[@]} -gt 0 ]]; then
    echo "Errors detected in projects:"
    for P in "${FAILED_PROJECTS[@]}"; do
        echo "  - $P"
    done
fi
echo "========================================"

exit 0
