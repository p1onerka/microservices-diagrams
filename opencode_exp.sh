#!/bin/bash

PROJECT_PATH="$1"

if [[ -z "$PROJECT_PATH" ]]; then
    echo "Usage: $0 <project_path>"
    exit 1
fi

PROJECT_NAME=$(basename -- "$PROJECT_PATH")
REPORT_PATH="report.json"
AGENT_NAME="reading-agent"
CODEQL_TIME_FILE="codeql_tool_time.txt"
OUTPUT_DIR="opencode-exp"
CSV_FILE="$OUTPUT_DIR/${PROJECT_NAME}-${AGENT_NAME}.csv"

get_metric() {
    local metric_name="$1"

    echo "$METRICS" | awk -v metric="$metric_name" '
        $1 == metric {
            print $2
            exit
        }
    '
}

if [[ ! -f "$CSV_FILE" ]]; then
    echo "run,project,agent,agent_wall_time_seconds,n_tokens_max,prompt_tokens_total,prompt_tokens_cached_total,total_input_tokens,tokens_predicted_total,total_tokens,prompt_seconds_total,tokens_predicted_seconds_total,prompt_tokens_seconds,predicted_tokens_seconds,n_decode_total,requests_processing,requests_deferred,n_busy_slots_per_decode,spec_decode_num_draft_tokens_total,spec_decode_num_accepted_tokens_total,spec_decode_num_drafts_total,spec_decode_acceptance_rate,spec_decode_num_accepted_tokens_per_pos_0,spec_decode_num_accepted_tokens_per_pos_1,spec_decode_num_accepted_tokens_per_pos_2,tool_calls,tool_time_seconds,tool_time_average_seconds,agent_output" > "$CSV_FILE"
fi

for i in {1..30}; do
    echo "=== Запуск $i ==="

    rm -f "$CODEQL_TIME_FILE"
    rm -f "$REPORT_PATH"

    # 1. Старт сервера llama.cpp
    llama serve \
    -hf ukisai/Swift-Qwen3.8-27B-GGUF:IQ4_XS \
    -c 28000 \
    -b 512 \
    -ub 512 \
    -np 1 \
    -fa on \
    -ctk q4_0 \
    -ctv q4_0 \
    -ctkd q4_0 \
    -ctvd q4_0 \
    --metrics \
    --jinja \
    --alias qwen3.8-q4ks \
    --reasoning-effort low \
    --temp 0.1 \
    --kv-unified \
    --cache-ram 12288 \
    --no-mmproj-offload \
    --spec-type draft-mtp \
    --spec-draft-n-max 3 \
    --ctx-checkpoints 4 \
    --spec-draft-p-min 0.8 \
    --predict 5000 \
    --n-gpu-layers all \
    > /tmp/llama_server.log 2>&1 &
    
    SERVER_PID=$!

    # 2. Ожидание загрузки модели (проверка эндпоинта /health)
    echo "Ожидание загрузки модели..."

    MODEL_READY=false

    for j in {1..120}; do
        if curl -s http://127.0.0.1:8080/health > /dev/null; then
            echo "Модель загружена."
            MODEL_READY=true
            break
        fi
        sleep 1
    done

    if [[ "$MODEL_READY" != true ]]; then
        echo "Ошибка: модель не загрузилась."

        kill "$SERVER_PID" 2>/dev/null
        wait "$SERVER_PID" 2>/dev/null
        continue
    fi

    # 3. Запуск агента и захват его JSON-вывода
    # (Возможно, потребуется дополнительная обработка, если вывод - NDJSON)
    #opencode run --agent reading-agent "analyze project $PROJECT_PATH"
    #opencode run --agent reading-agent "test query: write the phrase "pipi" in your report.json file"

    if [[ "$AGENT_NAME" == "codeql-agent" && -f "$CODEQL_TIME_FILE" ]]; then
        codeql database cleanup --cache-cleanup=clear -- {"codeql-dbs/$PROJECT_NAME-java"}
        codeql database cleanup --cache-cleanup=clear -- {"codeql-dbs/$PROJECT_NAME-js"}
    fi

    echo "Запуск агента: $AGENT_NAME"

    AGENT_START=$(python3 -c 'import time; print(time.perf_counter())')
    opencode run \
        --agent "$AGENT_NAME" \
        "analyze project $PROJECT_PATH"
    AGENT_EXIT_CODE=$?
    AGENT_END=$(python3 -c 'import time; print(time.perf_counter())')
    AGENT_WALL_TIME=$(python3 -c "print($AGENT_END - $AGENT_START)")

    echo "Агент завершён."
    echo "Agent wall time: ${AGENT_WALL_TIME}s"
    echo "Agent exit code: $AGENT_EXIT_CODE"

    # 4 codeql

    CODEQL_TIME=0
    CODEQL_CALLS=0
    CODEQL_AVG_TIME=0

    if [[ "$AGENT_NAME" == "codeql-agent" && -f "$CODEQL_TIME_FILE" ]]; then

        # Number of tool calls
        CODEQL_CALLS=$(wc -l < "$CODEQL_TIME_FILE" | tr -d ' ')

        # Sum of durations
        CODEQL_TIME=$(awk '
            {
                sum += $2
            }
            END {
                printf "%.6f", sum + 0
            }
        ' "$CODEQL_TIME_FILE")

        # Average duration
        if [[ "$CODEQL_CALLS" -gt 0 ]]; then
            CODEQL_AVG_TIME=$(awk -v total="$CODEQL_TIME" -v calls="$CODEQL_CALLS" '
                BEGIN {
                    printf "%.6f", total / calls
                }
            ')
        fi
        # Remove telemetry after reading it
        rm -f "$CODEQL_TIME_FILE"
    else
        # Standard agent does not use CodeQL
        CODEQL_TIME=0
        CODEQL_CALLS=0
        CODEQL_AVG_TIME=0
        # Just in case the file exists
        rm -f "$CODEQL_TIME_FILE"
    fi

    # 4. Снятие метрик

    METRICS=$(curl -s http://127.0.0.1:8080/metrics)

    N_TOKENS_MAX=$(get_metric "llamacpp:n_tokens_max")
    PROMPT_TOKENS=$(get_metric "llamacpp:prompt_tokens_total")
    PROMPT_TOKENS_CACHED=$(get_metric "llamacpp:prompt_tokens_cached_total")
    TOKENS_PREDICTED=$(get_metric "llamacpp:tokens_predicted_total")

    PROMPT_SECONDS=$(get_metric "llamacpp:prompt_seconds_total")
    PREDICTED_SECONDS=$(get_metric "llamacpp:tokens_predicted_seconds_total")

    N_DECODE=$(get_metric "llamacpp:n_decode_total")

    PROMPT_TOKENS_SECONDS=$(get_metric "llamacpp:prompt_tokens_seconds")
    PREDICTED_TOKENS_SECONDS=$(get_metric "llamacpp:predicted_tokens_seconds")

    REQUESTS_PROCESSING=$(get_metric "llamacpp:requests_processing")
    REQUESTS_DEFERRED=$(get_metric "llamacpp:requests_deferred")
    BUSY_SLOTS=$(get_metric "llamacpp:n_busy_slots_per_decode")

    SPEC_DRAFT_TOKENS=$(get_metric "llamacpp:spec_decode_num_draft_tokens_total")
    SPEC_ACCEPTED_TOKENS=$(get_metric "llamacpp:spec_decode_num_accepted_tokens_total")
    SPEC_DRAFTS=$(get_metric "llamacpp:spec_decode_num_drafts_total")

    SPEC_ACCEPTED_POS_0=$(echo "$METRICS" | awk '
        /^llamacpp:spec_decode_num_accepted_tokens_per_pos_total\{position="0"\}/ {
            print $2
            exit
        }
    ')
    SPEC_ACCEPTED_POS_1=$(echo "$METRICS" | awk '
        /^llamacpp:spec_decode_num_accepted_tokens_per_pos_total\{position="1"\}/ {
            print $2
            exit
        }
    ')
    SPEC_ACCEPTED_POS_2=$(echo "$METRICS" | awk '
        /^llamacpp:spec_decode_num_accepted_tokens_per_pos_total\{position="2"\}/ {
            print $2
            exit
        }
    ')

    # 5. Остановка сервера для чистого старта следующего запуска
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null

    # find json with result
    if [[ -f "$REPORT_PATH" ]]; then
        AGENT_OUTPUT=$(cat "$REPORT_PATH")
        rm -f "$REPORT_PATH"
    else
        AGENT_OUTPUT="<report.json not found>"
    fi

    python3 append_metrics.py \
    "$CSV_FILE" \
    "$i" \
    "$PROJECT_NAME" \
    "$AGENT_NAME" \
    "$AGENT_WALL_TIME" \
    "$N_TOKENS_MAX" \
    "$PROMPT_TOKENS" \
    "$PROMPT_TOKENS_CACHED" \
    "$TOKENS_PREDICTED" \
    "$PROMPT_SECONDS" \
    "$PREDICTED_SECONDS" \
    "$PROMPT_TOKENS_SECONDS" \
    "$PREDICTED_TOKENS_SECONDS" \
    "$N_DECODE" \
    "$REQUESTS_PROCESSING" \
    "$REQUESTS_DEFERRED" \
    "$BUSY_SLOTS" \
    "$SPEC_DRAFT_TOKENS" \
    "$SPEC_ACCEPTED_TOKENS" \
    "$SPEC_DRAFTS" \
    "$SPEC_ACCEPTED_POS_0" \
    "$SPEC_ACCEPTED_POS_1" \
    "$SPEC_ACCEPTED_POS_2" \
    "$CODEQL_CALLS" \
    "$CODEQL_TIME" \
    "$CODEQL_AVG_TIME" \
    "$AGENT_OUTPUT"


    echo "Результат сохранён в:"
    echo "$CSV_FILE"
    echo

done
