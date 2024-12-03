from datetime import timedelta, date, datetime
import time

def add_date(days=30):
    """
    Calculate the expiration date and return it in both epoch and formatted date formats.
    
    Args:
        days (int): Number of days to add to the current date. Default is 30 days.
    
    Returns:
        tuple: (expiration_date_in_epoch, expiration_date_in_YYYY_MM_DD_format)
    """
    today = date.today()
    expiration_date = today + timedelta(days=days)
    expiration_epoch = int(expiration_date.strftime('%s'))  # More modern approach for epoch
    formatted_date = expiration_date.strftime('%Y-%m-%d')
    return expiration_epoch, formatted_date

def check_expi(saved_epoch_date):
    """
    Check if a saved epoch date has expired compared to the current date.
    
    Args:
        saved_epoch_date (int): Epoch date to check.
    
    Returns:
        bool: True if the date is still valid (not expired), False otherwise.
    """
    current_epoch = int(time.time())
    remaining_time = saved_epoch_date - current_epoch
    return remaining_time > 0

# Add 30 days to today's date
epoch, formatted_date = add_date()
print(f"Expiration Date (Epoch): {epoch}")
print(f"Expiration Date (Formatted): {formatted_date}")

# Check if a saved date is still valid
is_valid = check_expi(epoch)
print(f"Is the expiration date valid? {'Yes' if is_valid else 'No'}")
