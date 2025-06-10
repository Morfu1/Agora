import json
import subprocess
import os

def fetch_video_data(channel_url):
    """
    Fetches video data from a YouTube channel using yt-dlp.
    Uses --flat-playlist for speed, which provides less detail per video.

    Args:
        channel_url (str): The URL of the YouTube channel.

    Returns:
        list: A list of dictionaries, where each dictionary represents a video.
              Returns an empty list if an error occurs.
    """
    videos_data = []
    yt_dlp_path = os.path.expanduser("~/.local/bin/yt-dlp")

    # Command to get video info as JSON objects (one per line)
    # --flat-playlist: Only list the videos, do not extract info for each video. Much faster.
    # This means we won't get detailed descriptions or all thumbnail sizes per video.
    command = [
        yt_dlp_path,
        "-j",  # Output JSON
        "--skip-download",  # We only want metadata
        "--flat-playlist", # Don't extract info for each video, just list them
        channel_url
    ]

    try:
        print(f"Fetching video data from: {channel_url} (using --flat-playlist)")
        # Increased timeout to 120 seconds
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)

        if process.returncode != 0:
            print(f"Error running yt-dlp: {process.stderr}")
            if "Unable to extract video data" in process.stderr or "No videos found" in process.stderr:
                print("No videos found or channel URL might be incorrect/private.")
            return []

        raw_json_data = process.stdout.strip().split('\n')

        if not raw_json_data or not raw_json_data[0]:
            print("No JSON data received from yt-dlp. The channel might have no videos or there's an issue.")
            return []

        for line in raw_json_data:
            if not line.strip():
                continue
            try:
                video_info = json.loads(line)
                # With --flat-playlist, typical fields are 'title', 'url' (direct video URL),
                # 'id', 'duration', 'channel', 'channel_url', 'thumbnails' (may be limited).
                # 'description' is usually not available with --flat-playlist.

                # Attempt to get a thumbnail. yt-dlp with --flat-playlist might still provide some.
                # It often provides a 'thumbnails' list. We'll try to get the last one (often best quality).
                thumbnail_url = None
                if "thumbnails" in video_info and isinstance(video_info["thumbnails"], list) and video_info["thumbnails"]:
                    # Try to find a thumbnail with a URL, preferring 'url' key
                    for thumb in reversed(video_info["thumbnails"]): # check better ones first
                        if isinstance(thumb, dict) and "url" in thumb:
                            thumbnail_url = thumb["url"]
                            break
                elif "thumbnail" in video_info: # Fallback if 'thumbnails' list is not as expected
                    thumbnail_url = video_info["thumbnail"]

                video_entry = {
                    "title": video_info.get("title"),
                    "url": video_info.get("url"), # 'url' is the direct video URL with --flat-playlist
                    "thumbnail_url": thumbnail_url,
                    "description": video_info.get("description") # Likely None with --flat-playlist
                }
                videos_data.append(video_entry)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for a video: {e}")
                print(f"Problematic line: '{line[:200]}...'")

        return videos_data

    except subprocess.TimeoutExpired:
        print("The command to fetch video data timed out. --flat-playlist was used, so this is unexpected. Check URL or network.")
        return []
    except FileNotFoundError:
        print(f"Error: yt-dlp not found at {yt_dlp_path}. Please ensure it is installed and in your PATH or the script is pointing to the correct location.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def save_to_json(data, filename="videos.json"):
    """
    Saves data to a JSON file.

    Args:
        data (list): The data to save.
        filename (str): The name of the JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved {len(data)} videos to {filename}")
    except IOError as e:
        print(f"Error saving data to JSON file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving to JSON: {e}")


if __name__ == "__main__":
    CHANNEL_URL = "https://www.youtube.com/@agorameditations/videos"

    video_details = fetch_video_data(CHANNEL_URL)

    if video_details:
        save_to_json(video_details, "videos.json")
    else:
        print("No video data fetched or an error occurred. 'videos.json' will not be created or will be empty.")

    # Final check if file was created, and how many entries it has
    try:
        with open("videos.json", 'r', encoding='utf-8') as f:
            final_data = json.load(f)
            print(f"Verification: 'videos.json' contains {len(final_data)} entries.")
    except FileNotFoundError:
        print("Verification: 'videos.json' was not created.")
    except json.JSONDecodeError:
        print("Verification: 'videos.json' exists but is not valid JSON (possibly empty or corrupted).")
    except Exception:
        print("Verification: Could not verify 'videos.json'.")
