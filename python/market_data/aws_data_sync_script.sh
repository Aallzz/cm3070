#!/bin/bash

export S3_BUCKET="s3://cm3070/"
export DATA_SYNC_DATA_DIR="./data/"
export DATA_SYNC_SYNCED_DIR="./synced_data/"
export DATA_SYNC_LOG_FILE="./aws_sync_log.txt"

upload_and_move() {
    # Find files matching the pattern and execute the following
    find "$DATA_SYNC_DATA_DIR" -type f -name "$(date -d "today" '+%-d').csv" -exec bash -c '{
        file="$1"
        
        # Get relative path from DATA_SYNC_DATA_DIR
        rel_path="${file#./data/}"
        
        # Create directory structure in DATA_SYNC_SYNCED_DIR
        mkdir -p "$(dirname "$DATA_SYNC_SYNCED_DIR/$rel_path")"
        
        # Upload to S3, maintaining folder structure
        aws s3 cp "$file" "$S3_BUCKET/${rel_path}"  && echo "$(date "+%Y-%m-%d %H:%M:%S") - Uploaded: $file" >> "$DATA_SYNC_LOG_FILE"
        
        # Move file to synced_data, maintaining folder structure
        mv "$file" "$DATA_SYNC_SYNCED_DIR/$rel_path" && echo "$(date "+%Y-%m-%d %H:%M:%S") - Moved: $file to $DATA_SYNC_SYNCED_DIR/$rel_path" >> "$DATA_SYNC_LOG_FILE"
        
        # Schedule deletion from synced_data after 3 hours
        echo "rm \"$DATA_SYNC_SYNCED_DIR/$rel_path\"" | at now + 3 hours
    }' _ '{}' \;
}

# Get the full path of the current script
SCRIPT_PATH=$(readlink -f "$0")

# Check if the script is already scheduled, if not add it to crontab
if ! sudo crontab -l | grep -Fq "$SCRIPT_PATH"; then
  # Append the new cron job to the existing crontab with the full script path
  (crontab -l 2>/dev/null; echo "0 3 * * * sudo $SCRIPT_PATH") | crontab -
fi

# Run the upload and move function
upload_and_move