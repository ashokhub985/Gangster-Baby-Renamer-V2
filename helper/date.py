from datetime import timedelta, date, datetime
import time
from typing import Tuple

def add_date(days: int = 30) -> Tuple[int, str]:
    """
    Calculate the expiration date and return it in both epoch and formatted date formats.
    
    Args:
        days (int): Number of days to add to the current date. Default is 30 days.
    
    Returns:
        tuple: (expiration_date_in_epoch, expiration_date_in_YYYY_MM_DD_format)
    """
    try:
        today = datetime.today()
        expiration_date = today + timedelta(days=days)
        expiration_epoch = int(expiration_date.timestamp())  # Use timestamp() for a more modern approach
        formatted_date = expiration_date.strftime('%Y-%m-%d')
        return expiration_epoch, formatted_date
    except Exception as e:
        print(f"Error calculating expiration date: {e}")
        return None, None

def check_expi(saved_epoch_date: int) -> bool:
    """
    Check if a saved epoch date has expired compared to the current date.
    
    Args:
        saved_epoch_date (int): Epoch date to check.
    
    Returns:
        bool: True if the date is still valid (not expired), False otherwise.
    """
    try:
        current_epoch = int(time.time())
        remaining_time = saved_epoch_date - current_epoch
        return remaining_time > 0
    except TypeError:
        print("Invalid epoch date provided.")
        return False
    except Exception as e:
        print(f"Error checking expiration: {e}")
        return False

# Add 30 days to today's date
epoch, formatted_date = add_date()
if epoch is not None and formatted_date is not None:
    print(f"Expiration Date (Epoch): {epoch}")
    print(f"Expiration Date (Formatted): {formatted_date}")

    # Check if a saved date is still valid
    is_valid = check_expi(epoch)
    print(f"Is the expiration date valid? {'Yes' if is_valid else 'No'}")
