from datetime import datetime
from assistant.config import AVAILABLE_TIMES, PRICING
from assistant.utils import get_upcoming_dates, safe_input

# handles booking scheduling and viewing
# did the isolation here for clarity to avoid cluttering core.py

class BookingManager:
    def __init__(self):
        self.bookings = []

    def schedule_game(self):
        print("\nSCHEDULE A PADDLE GAME\n" + "="*30)
        name = safe_input("Your name: ", lambda x: len(x) > 0)
        email = safe_input("Your email: ", lambda x: "@" in x)
        phone = input("Your phone: ").strip()

        print("\nGame types:\n1. Singles ($30)\n2. Doubles ($50)")
        game_choice = safe_input("Choose (1 or 2): ", lambda x: x in ['1', '2'])
        game_type = "Singles" if game_choice == '1' else "Doubles"
        price = PRICING['singles'] if game_choice == '1' else PRICING['doubles']

        print("\nAvailable dates:")
        date_options = get_upcoming_dates()
        for i, date in date_options:
            print(f"{i}. {date}")
        date_index = int(safe_input("Choose date (1-7): ", lambda x: x.isdigit() and 1 <= int(x) <= 7))
        selected_date = date_options[date_index - 1][1]

        print("\nAvailable times:")
        for i, t in enumerate(AVAILABLE_TIMES):
            print(f"{i + 1}. {t}")
        time_index = int(safe_input("Choose time (1-6): ", lambda x: x.isdigit() and 1 <= int(x) <= 6))
        selected_time = AVAILABLE_TIMES[time_index - 1]

        equipment = safe_input("Need equipment? (y/n): ", lambda x: x in ['y', 'n']) == 'y'
        total = price + (PRICING['equipment'] if equipment else 0)

        booking = {
            "id": len(self.bookings) + 1,
            "name": name,
            "email": email,
            "phone": phone,
            "game_type": game_type,
            "date": selected_date,
            "time": selected_time,
            "equipment": equipment,
            "price": total,
            "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.bookings.append(booking)

        print("\nBOOKING CONFIRMED! 🎉")
        print(f"Name: {name}, Game: {game_type}, Time: {selected_time}, Total: ${total}")

    def view_bookings(self):
        if not self.bookings:
            print("No bookings found.")
            return
        print(f"\nALL BOOKINGS ({len(self.bookings)} total):")
        for b in self.bookings:
            print(f"#{b['id']} | {b['date']} {b['time']} | {b['name']} | {b['game_type']} | ${b['price']}")