from datetime import datetime
from assistant.utils import get_upcoming_dates, safe_input


def remove_duplicate_lines(text):
    seen = set()
    result = []
    for line in text.splitlines():
        if line.strip() not in seen:
            seen.add(line.strip())
            result.append(line)
    return '\n'.join(result)


class BookingManager:
    def __init__(self, responder=None):
        self.bookings = []
        self.responder = responder

        if responder:
            self.pricing, self.hours, self.available_times = responder.prompt_manager.get_dynamic_info()
        else:
            from assistant.config import AVAILABLE_TIMES, PRICING, BUSINESS_HOURS
            self.pricing = PRICING
            self.available_times = AVAILABLE_TIMES
            self.hours = BUSINESS_HOURS

    def schedule_game(self):
        print("\nSCHEDULE A PADDLE GAME\n" + "="*30)
        name = safe_input("Your name: ", lambda x: len(x) > 0)
        email = safe_input("Your email: ", lambda x: "@" in x)
        phone = input("Your phone: ").strip()

        print(f"\nGame types:\n1. Singles (${self.pricing['singles']})\n2. Doubles (${self.pricing['doubles']})")
        game_choice = safe_input("Choose (1 or 2): ", lambda x: x in ['1', '2'])
        game_type = "Singles" if game_choice == '1' else "Doubles"
        price = self.pricing['singles'] if game_choice == '1' else self.pricing['doubles']

        print("\nAvailable dates:")
        date_options = get_upcoming_dates()
        for i, date in date_options:
            print(f"{i}. {date}")
        date_index = int(safe_input("Choose date (1-7): ", lambda x: x.isdigit() and 1 <= int(x) <= 7))
        selected_date = date_options[date_index - 1][1]

        print("\nAvailable times:")
        for i, t in enumerate(self.available_times):
            print(f"{i + 1}. {t}")
        time_index = int(safe_input(f"Choose time (1-{len(self.available_times)}): ", lambda x: x.isdigit() and 1 <= int(x) <= len(self.available_times)))
        selected_time = self.available_times[time_index - 1]

        equipment = safe_input("Need equipment? (y/n): ", lambda x: x in ['y', 'n']) == 'y'
        total = price + (self.pricing['equipment'] if equipment else 0)

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

        if self.responder:
            try:
                ai_message = f"Generate a friendly confirmation message for {name} who just booked a {game_type} game on {selected_date} at {selected_time} for ${total}. Include helpful tips."
                confirmation = self.responder.send_to_gemini(ai_message)
                confirmation = remove_duplicate_lines(confirmation)
                print(f"\n🤖 {confirmation}")
            except:
                print("\n📋 Important: Please arrive 15 minutes early and bring comfortable athletic wear!")

    def view_bookings(self):
        if not self.bookings:
            print("No bookings found.")
            return
        print(f"\nALL BOOKINGS ({len(self.bookings)} total):")
        for b in self.bookings:
            print(f"#{b['id']} | {b['date']} {b['time']} | {b['name']} | {b['game_type']} | ${b['price']}")

    def get_ai_booking_summary(self):
        if not self.responder or not self.bookings:
            return "No bookings to summarize."

        try:
            summary_request = f"Summarize these bookings in a friendly way: {len(self.bookings)} total bookings. Recent: {self.bookings[-3:] if len(self.bookings) >= 3 else self.bookings}"
            return self.responder.send_to_gemini(summary_request)
        except:
            return f"You have {len(self.bookings)} bookings total."
