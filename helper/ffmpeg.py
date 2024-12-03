import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


async def fix_thumb(thumb_path):
    """
    Fixes a thumbnail image to ensure it's in RGB mode and resizes it to 320px width.
    
    Args:
        thumb_path (str): Path to the thumbnail image.
        
    Returns:
        tuple: (width, height, processed_thumbnail_path or None)
    """
    try:
        if thumb_path and os.path.exists(thumb_path):
            metadata = extractMetadata(createParser(thumb_path))
            width = metadata.get("width") if metadata and metadata.has("width") else 0
            height = metadata.get("height") if metadata and metadata.has("height") else 0
            
            with Image.open(thumb_path) as img:
                img = img.convert("RGB")
                aspect_ratio = height / width if width else 1
                new_height = int(320 * aspect_ratio)
                img = img.resize((320, new_height))
                img.save(thumb_path, "JPEG")
            return 320, new_height, thumb_path
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return 0, 0, None
    return 0, 0, None


async def take_screen_shot(video_file, output_directory, timestamp):
    """
    Takes a screenshot from a video at the specified timestamp using ffmpeg.
    
    Args:
        video_file (str): Path to the video file.
        output_directory (str): Directory to save the screenshot.
        timestamp (int): Timestamp in seconds to capture the screenshot.
        
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
            "-q:v", "2",  # High-quality image
            output_file_name
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode == 0 and os.path.exists(output_file_name):
            return output_file_name
        else:
            print(f"Failed to take screenshot: {stderr.decode().strip()}")
            return None
    except Exception as e:
        print(f"Error during screenshot generation: {e}")
        return None

import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


async def fix_thumb(thumb_path):
    """
    Fixes a thumbnail image to ensure it's in RGB mode and resizes it to 320px width.
    
    Args:
        thumb_path (str): Path to the thumbnail image.
        
    Returns:
        tuple: (width, height, processed_thumbnail_path or None)
    """
    try:
        if thumb_path and os.path.exists(thumb_path):
            metadata = extractMetadata(createParser(thumb_path))
            width = metadata.get("width") if metadata and metadata.has("width") else 0
            height = metadata.get("height") if metadata and metadata.has("height") else 0
            
            with Image.open(thumb_path) as img:
                img = img.convert("RGB")
                aspect_ratio = height / width if width else 1
                new_height = int(320 * aspect_ratio)
                img = img.resize((320, new_height))
                img.save(thumb_path, "JPEG")
            return 320, new_height, thumb_path
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return 0, 0, None
    return 0, 0, None


async def take_screen_shot(video_file, output_directory, timestamp):
    """
    Takes a screenshot from a video at the specified timestamp using ffmpeg.
    
    Args:
        video_file (str): Path to the video file.
        output_directory (str): Directory to save the screenshot.
        timestamp (int): Timestamp in seconds to capture the screenshot.
        
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
            "-q:v", "2",  # High-quality image
            output_file_name
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode == 0 and os.path.exists(output_file_name):
            return output_file_name
        else:
            print(f"Failed to take screenshot: {stderr.decode().strip()}")
            return None
    except Exception as e:
        print(f"Error during screenshot generation: {e}")
        return None
