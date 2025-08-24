#!/bin/bash

echo "=== S3 Transfer Status Monitor ==="
echo "Time: $(date)"
echo ""

# Check if transfer processes are running
echo "🔄 Active Processes:"
PROCESSES=$(ps aux | grep -E "(s3_transfer|caffeinate.*s3_transfer)" | grep -v grep)
if [ -n "$PROCESSES" ]; then
    echo "$PROCESSES"
    echo "✅ Transfer is RUNNING"
else
    echo "❌ No S3 transfer processes detected"
fi
echo ""

# Quick S3 bucket summary
echo "📊 S3 Bucket Summary:"
AWS_PROFILE=cli-algorec aws s3 ls s3://cid-mbs/cow-data/ --human-readable --summarize | tail -3
echo ""

# Check progress for each data folder
echo "📁 Folder Progress:"
for folder in data-2021 data-2022 data-2023 data-2024 data-2025; do
    echo -n "$folder: "
    count=$(AWS_PROFILE=cli-algorec aws s3 ls s3://cid-mbs/cow-data/$folder/ --recursive 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
        echo "✅ $count files uploaded"
    else
        echo "⏳ Not started"
    fi
done
echo ""

# Show most recent uploads
echo "📈 Latest Activity (last 10 files):"
AWS_PROFILE=cli-algorec aws s3 ls s3://cid-mbs/cow-data/ --recursive --human-readable | tail -10