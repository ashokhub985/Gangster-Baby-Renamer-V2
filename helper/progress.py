import math
import time


async def progress_for_pyrogram(
    current: int,
    total: int,
    ud_type: str,
    message,
    start: float
):
    """
    Update a Pyrogram message with a visual progress bar and download/upload statistics.

    Args:
        current (int): The current progress in bytes.
        total (int): The total size in bytes.
        ud_type (str): Type of operation (e.g., "Uploading", "Downloading").
        message: Pyrogram message object to update.
        start (float): Start time of the operation.
    """
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # Calculate percentage, speed, elapsed time, and estimated time to complete
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff * 1000)
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = elapsed_time + time_to_completion

        # Format times
        elapsed_time_str = TimeFormatter(elapsed_time)
        estimated_total_time_str = TimeFormatter(estimated_total_time)

        # Generate progress bar
        progress = "[{0}{1}] \n**Progress**: {2}%\n".format(
            ''.join(["●" for _ in range(math.floor(percentage / 5))]),
            ''.join(["○" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2)
        )

        # Compile message text
        tmp = (
            f"{progress}"
            f"{humanbytes(current)} of {humanbytes(total)}\n"
            f"**Speed**: {humanbytes(speed)}/s\n"
            f"**ETA**: {estimated_total_time_str if estimated_total_time_str else '0 s'}\n"
        )

        # Update the message
        try:
            await message.edit(
                text=f"{ud_type}\n{tmp}"
            )
        except Exception as e:
            print(f"Failed to update progress message: {e}")


def humanbytes(size: int) -> str:
    """
    Convert a size in bytes to a human-readable format.

    Args:
        size (int): Size in bytes.

    Returns:
        str: Human-readable size (e.g., 1.5 GiB).
    """
    if not size:
        return "0B"
    power = 2**10
    n = 0
    Dic_powerN = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"


def TimeFormatter(milliseconds: int) -> str:
    """
    Convert milliseconds to a human-readable time format.

    Args:
        milliseconds (int): Time in milliseconds.

    Returns:
        str: Formatted time (e.g., "1d, 3h, 5m, 10s").
    """
    if milliseconds <= 0:
        return "0s"
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    formatted_time = (
        (f"{days}d, " if days else "") +
        (f"{hours}h, " if hours else "") +
        (f"{minutes}m, " if minutes else "") +
        (f"{seconds}s, " if seconds else "") +
        (f"{milliseconds}ms, " if milliseconds else "")
    )
    return formatted_time.rstrip(', ')
