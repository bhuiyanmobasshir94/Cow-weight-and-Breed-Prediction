#!/bin/bash

# High-Performance S3 Transfer Script for data-**** folders
# Optimized for low latency and high throughput

set -e

S3_BUCKET=""
S3_PREFIX=""
EXCLUDE_PATTERNS="*.DS_Store,*.log,*.tmp"

usage() {
    echo "Usage: $0 -b BUCKET_NAME -p S3_PREFIX [options]"
    echo "Options:"
    echo "  -b BUCKET_NAME    S3 bucket name (required)"
    echo "  -p S3_PREFIX      S3 prefix/folder path (required)"
    echo "  -t THREADS        Number of parallel threads (default: 10)"
    echo "  -c                Enable compression for .pkl files"
    echo "  -d                Dry run - show what would be transferred"
    echo "  -h                Show this help message"
    echo ""
    echo "Example: $0 -b my-bucket -p cow-data/production -t 15 -c"
    exit 1
}

THREADS=10
COMPRESS=false
DRY_RUN=false

while getopts "b:p:t:cdh" opt; do
    case $opt in
        b) S3_BUCKET="$OPTARG";;
        p) S3_PREFIX="$OPTARG";;
        t) THREADS="$OPTARG";;
        c) COMPRESS=true;;
        d) DRY_RUN=true;;
        h) usage;;
        *) usage;;
    esac
done

if [ -z "$S3_BUCKET" ]; then
    echo "Error: Bucket name is required"
    usage
fi

# Handle empty prefix (root level)
if [ -z "$S3_PREFIX" ]; then
    S3_PATH="s3://$S3_BUCKET"
else
    S3_PATH="s3://$S3_BUCKET/$S3_PREFIX"
fi

echo "🚀 High-Performance S3 Transfer Configuration:"
echo "   S3 Path: $S3_PATH"
echo "   Threads: $THREADS"
echo "   Compression: $COMPRESS"
echo "   Dry Run: $DRY_RUN"
echo ""

# Configure AWS CLI for optimal performance
aws configure set default.max_concurrent_requests $THREADS
aws configure set default.max_bandwidth 1000MB/s
aws configure set default.multipart_threshold 64MB
aws configure set default.multipart_chunksize 16MB
aws configure set default.max_queue_size 10000

# Function to transfer a single folder
transfer_folder() {
    local folder="$1"
    local folder_name=$(basename "$folder")
    
    echo "📁 Starting transfer: $folder_name"
    echo "   Size: $(du -sh "$folder" | cut -f1)"
    echo "   Files: $(find "$folder" -type f | wc -l | xargs)"
    
    local start_time=$(date +%s)
    
    local target_path
    if [ -z "$S3_PREFIX" ]; then
        target_path="s3://$S3_BUCKET/$folder_name"
    else
        target_path="s3://$S3_BUCKET/$S3_PREFIX/$folder_name"
    fi
    
    if [ "$DRY_RUN" = true ]; then
        aws s3 sync "$folder" "$target_path" \
            --dryrun \
            --exclude "$EXCLUDE_PATTERNS" \
            --storage-class STANDARD_IA
    else
        if [ "$COMPRESS" = true ]; then
            # For compressed transfer, we'll use a different approach
            echo "   Using compression for .pkl files..."
            
            # First, sync non-pkl files normally
            aws s3 sync "$folder" "$target_path" \
                --exclude "*.pkl" \
                --exclude "$EXCLUDE_PATTERNS" \
                --storage-class STANDARD_IA
            
            # Then compress and upload .pkl files
            find "$folder" -name "*.pkl" | while read pkl_file; do
                relative_path=${pkl_file#$folder/}
                compressed_name="${pkl_file}.gz"
                
                echo "   Compressing: $relative_path"
                gzip -c "$pkl_file" > "$compressed_name"
                
                local pkl_target_path
                if [ -z "$S3_PREFIX" ]; then
                    pkl_target_path="s3://$S3_BUCKET/$folder_name/$relative_path.gz"
                else
                    pkl_target_path="s3://$S3_BUCKET/$S3_PREFIX/$folder_name/$relative_path.gz"
                fi
                
                aws s3 cp "$compressed_name" "$pkl_target_path" \
                    --storage-class STANDARD_IA \
                    --metadata "original-name=$relative_path"
                
                rm "$compressed_name"
            done
        else
            aws s3 sync "$folder" "$target_path" \
                --exclude "$EXCLUDE_PATTERNS" \
                --storage-class STANDARD_IA
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "✅ Completed: $folder_name (${duration}s)"
    echo ""
}

# Main transfer process
echo "🔍 Found data folders:"
data_folders=($(find . -maxdepth 1 -name "data-*" -type d | sort))

if [ ${#data_folders[@]} -eq 0 ]; then
    echo "❌ No data-* folders found in current directory"
    exit 1
fi

total_size=0
for folder in "${data_folders[@]}"; do
    folder_size=$(du -sm "$folder" | cut -f1)
    total_size=$((total_size + folder_size))
    echo "   $(basename "$folder"): $(du -sh "$folder" | cut -f1)"
done

echo "   Total size: ${total_size}MB (~$((total_size/1024))GB)"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "🧪 DRY RUN MODE - No files will be transferred"
else
    echo "⚡ Starting high-performance transfer..."
fi

transfer_start=$(date +%s)

# Transfer each folder
for folder in "${data_folders[@]}"; do
    transfer_folder "$folder"
done

transfer_end=$(date +%s)
total_duration=$((transfer_end - transfer_start))

echo "🎉 Transfer Summary:"
echo "   Total folders: ${#data_folders[@]}"
echo "   Total size: ${total_size}MB (~$((total_size/1024))GB)"
echo "   Total time: ${total_duration}s (~$((total_duration/60))min)"
if [ $total_duration -gt 0 ]; then
    echo "   Average speed: $((total_size/total_duration))MB/s"
fi
echo "   S3 Location: $S3_PATH"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo "🔍 Verifying upload..."
    if [ -z "$S3_PREFIX" ]; then
        aws s3 ls "s3://$S3_BUCKET" --recursive --human-readable --summarize
    else
        aws s3 ls "s3://$S3_BUCKET/$S3_PREFIX" --recursive --human-readable --summarize
    fi
fi

echo "✨ Transfer complete!"