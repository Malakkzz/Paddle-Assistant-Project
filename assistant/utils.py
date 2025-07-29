from datetime import datetime, timedelta
# stores reusable helper functions

# generates the next 7 days for booking
def get_upcoming_dates(n=7):
    return [(i, (datetime.now() + timedelta(days=i)).strftime('%A, %B %d, %Y')) for i in range(1, n + 1)]

def safe_input(prompt, validator):
    while True:
        val = input(prompt).strip()
        if validator(val):
            return val
        print("Invalid input. Try again.")