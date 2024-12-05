import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

async def process_thumbnail(thumb_path, target_width=320):
    """
    Processes a thumbnail to ensure it's in RGB mode and resizes it to a target width.

    Args:
        thumb_path (str): Path to the thumbnail image.
        target_width (int): Desired width for the resized thumbnail.

    Returns:
        tuple: (width, height, processed_thumbnail_path or None)
    """
    try:
        if thumb_path and os.path.exists(thumb_path):
            metadata = extractMetadata(createParser(thumb_path))
            if metadata and metadata.has("width") and metadata.has("height"):
                width, height = metadata.get("width"), metadata.get("height")
                aspect_ratio = height / width if width else 1
                new_height = int(target_width * aspect_ratio)

                with Image.open(thumb_path) as img:
                    img = img.convert("RGB")
                    img = img.resize((target_width, new_height), Image.ANTIALIAS)
                    img.save(thumb_path, "JPEG", quality=85)

                return target_width, new_height, thumb_path
            else:
                print(f"Metadata for {thumb_path} not found.")
    except Exception as e:
        print(f"Error processing thumbnail {thumb_path}: {e}")
    return 0, 0, None

async def capture_screenshot(video_file, output_directory, timestamp, quality="2"):
    """
    Captures a screenshot from a video at the specified timestamp using ffmpeg.

    Args:
        video_file (str): Path to the video file.
        output_directory (str): Directory to save the screenshot.
        timestamp (int): Timestamp in seconds to capture the screenshot.
        quality (str): Quality of the output image (lower number means higher quality).

    Returns:
        str or None: Path to the generated screenshot or None if failed.
    """
    try:
        output_file_name = os.path.join(output_directory, f"{time.time()}.jpg")
        command = [
            "ffmpeg",
            "-ss", str(timestamp),
            "-i", video_file,
            "-vframes", "1",
            "-q:v", quality,  # High-quality image
            output_file_name
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0 and os.path.exists(output_file_name):
            return output_file_name
        else:
            print(f"Failed to capture screenshot: {stderr.decode().strip()}")
    except Exception as e:
        print(f"Error during screenshot generation: {e}")
    return None
