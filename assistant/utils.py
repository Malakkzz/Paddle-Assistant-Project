from datetime import datetime, timedelta

def get_upcoming_dates():
    """Returns list of (index, formatted_date) for next 7 days"""
    dates = []
    for i in range(1, 8):
        date = datetime.now() + timedelta(days=i)
        formatted = date.strftime('%A, %B %d, %Y')
        dates.append((i, formatted))
    return dates

def safe_input(prompt, validator):
    """Get input with validation"""
    while True:
        value = input(prompt).strip()
        if validator(value):
            return value
        print("❌ Invalid input. Please try again.")