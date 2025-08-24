#!/bin/bash

echo "=== Media Content Analysis Across All Data Folders ==="
echo "Analysis Date: $(date)"
echo "=================================================="

# Initialize counters
total_images=0
total_yt_images=0
total_yt_videos=0
total_size_images=0
total_size_yt_images=0
total_size_yt_videos=0

echo ""
echo "📊 FOLDER-BY-FOLDER BREAKDOWN:"
echo "------------------------------"

# Analyze each data folder
for folder in data-*; do
    if [ -d "$folder" ]; then
        echo ""
        echo "📁 $folder:"
        
        # Count images
        if [ -d "$folder/images" ]; then
            images_count=$(find "$folder/images" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" \) 2>/dev/null | wc -l)
            images_size=$(du -sh "$folder/images" 2>/dev/null | cut -f1)
            echo "   📷 images: $images_count files ($images_size)"
            total_images=$((total_images + images_count))
            # Convert size to bytes for summation (simplified - just count directories)
            if [ "$images_count" -gt 0 ]; then
                total_size_images=$((total_size_images + 1))
            fi
        else
            echo "   📷 images: 0 files (no folder)"
        fi
        
        # Count yt_images
        if [ -d "$folder/yt_images" ]; then
            yt_images_count=$(find "$folder/yt_images" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" \) 2>/dev/null | wc -l)
            yt_images_size=$(du -sh "$folder/yt_images" 2>/dev/null | cut -f1)
            echo "   🎬 yt_images: $yt_images_count files ($yt_images_size)"
            total_yt_images=$((total_yt_images + yt_images_count))
            if [ "$yt_images_count" -gt 0 ]; then
                total_size_yt_images=$((total_size_yt_images + 1))
            fi
        else
            echo "   🎬 yt_images: 0 files (no folder)"
        fi
        
        # Count yt_videos
        if [ -d "$folder/yt_videos" ]; then
            yt_videos_count=$(find "$folder/yt_videos" -type f \( -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mov" -o -iname "*.mkv" -o -iname "*.webm" \) 2>/dev/null | wc -l)
            yt_videos_size=$(du -sh "$folder/yt_videos" 2>/dev/null | cut -f1)
            echo "   🎥 yt_videos: $yt_videos_count files ($yt_videos_size)"
            total_yt_videos=$((total_yt_videos + yt_videos_count))
            if [ "$yt_videos_count" -gt 0 ]; then
                total_size_yt_videos=$((total_size_yt_videos + 1))
            fi
        else
            echo "   🎥 yt_videos: 0 files (no folder)"
        fi
    fi
done

echo ""
echo "=================================================="
echo "🏆 GRAND TOTAL SUMMARY:"
echo "=================================================="
echo "📷 Total Images:    $(printf "%'d" $total_images) files"
echo "🎬 Total YT Images: $(printf "%'d" $total_yt_images) files" 
echo "🎥 Total YT Videos: $(printf "%'d" $total_yt_videos) files"
echo "---"
echo "📊 Combined Media:  $(printf "%'d" $((total_images + total_yt_images + total_yt_videos))) files total"
echo ""

# Calculate percentages
if [ $((total_images + total_yt_images + total_yt_videos)) -gt 0 ]; then
    total_media=$((total_images + total_yt_images + total_yt_videos))
    images_pct=$((total_images * 100 / total_media))
    yt_images_pct=$((total_yt_images * 100 / total_media))
    yt_videos_pct=$((total_yt_videos * 100 / total_media))
    
    echo "📈 DISTRIBUTION:"
    echo "   📷 Images:    ${images_pct}%"
    echo "   🎬 YT Images: ${yt_images_pct}%"
    echo "   🎥 YT Videos: ${yt_videos_pct}%"
fi

echo ""
echo "💾 STORAGE BREAKDOWN:"
echo "---------------------"
for folder in data-*; do
    if [ -d "$folder" ]; then
        echo -n "$folder: "
        
        # Get sizes for each media type
        if [ -d "$folder/images" ]; then
            img_size=$(du -sh "$folder/images" 2>/dev/null | cut -f1)
            echo -n "images($img_size) "
        fi
        
        if [ -d "$folder/yt_images" ]; then
            yt_img_size=$(du -sh "$folder/yt_images" 2>/dev/null | cut -f1)
            echo -n "yt_images($yt_img_size) "
        fi
        
        if [ -d "$folder/yt_videos" ]; then
            yt_vid_size=$(du -sh "$folder/yt_videos" 2>/dev/null | cut -f1)
            echo -n "yt_videos($yt_vid_size) "
        fi
        
        echo ""
    fi
done

echo ""
echo "✅ Analysis Complete!"
echo "Report generated: $(date)"