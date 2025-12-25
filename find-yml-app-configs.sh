if [ $# -eq 0 -o $# -eq 1 ]; then
    echo "Script should be called with project name and output dir\n\n"
fi

PROJECT_NAME=$1
OUTPUT_DIR=$2

echo "Creating .csv table"
csv_file="$OUTPUT_DIR/yml-app-configs-with-names.csv"
echo "service_app_name,service_folder" > $csv_file

echo "Scanning project to get spring .yml configs"

find "$PROJECT_NAME" -type f \( -name "*.yml" \) -path "*/src/main/resources/*" -exec grep -l "spring:" {} \; | while read config_file; do
    echo "Found config file: $config_file"

    # otherwise couldn't parse out .yml in genai service
    service_name=$(grep -A2 "spring:" "$config_file" | grep -A2 "application:" | grep "name:" | \
    awk '
        $1=="spring:" {inspring=1}
        inspring && $1=="application:" {inapp=1}
        inspring && inapp && $1=="name:" {print $2; exit}' "$config_file")
    # config server case
    if [ -z "$service_name" ]; then
        if cat "$config_file" | tr -d '[:space:]' | grep -qE "spring:cloud:config:server:"; then
            service_name="config-server"
        fi
    fi
    echo "Service name: $service_name"

    service_dir=$(dirname "$(dirname "$(dirname "$(dirname "$config_file")")")")
    echo "Service folder: $service_dir"

    echo "$service_name,$service_dir" >> $csv_file
done
