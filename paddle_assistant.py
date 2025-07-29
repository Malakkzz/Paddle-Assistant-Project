import json
import requests  # Added missing import
from datetime import datetime, timedelta
from prompt_manager import PromptManager


class PaddleGameAssistant:
    def __init__(self):
        self.api_key = "AIzaSyDF55zA3b2dK8XSKU7Ux6y7zZcc6Xsospw"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.bookings = []
        self.conversation_history = []
        #calling prompt manager class from prompt_manager.py
        self.prompt_manager = PromptManager()

        
        # Business data for offline responses
        self.business_hours = "9 AM - 9 PM daily"
        self.available_times = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM", "7:00 PM"]
        self.pricing = {
            "singles": 30,
            "doubles": 50,
            "equipment": 10,
            "coaching": 60
        }
    
    #dynamic prompts edited by the admin    
    def get_business_context(self):
        prompt = self.prompt_manager.get_current_prompt()
        if "No current prompt found." in prompt or not prompt.strip():
            # Fallback prompt if no valid prompt is found
            return """
            You are a virtual assistant for a paddle center.

            Services:
            - Court rental: $30/hour (singles), $50/hour (doubles)
            - Equipment rental: $10/person
            - Coaching: $60/hour
            - Hours: 9 AM to 9 PM daily
            - 6 courts available

            Available time slots: 9 AM, 11 AM, 1 PM, 3 PM, 5 PM, 7 PM

            Answer questions about pricing, availability, equipment, and booking.
            Be helpful and concise.
            """
        return prompt

    # Handle common queries when API is unavailable
    def handle_offline_query(self, user_message):
        message_lower = user_message.lower()
        
        # Court availability questions
        if any(word in message_lower for word in ['court', 'available', 'time', 'slot', 'book']):
            if '8' in message_lower:
                return "I see you're asking about 8 PM. Unfortunately, our courts close at 9 PM, so 8 PM isn't one of our standard time slots. Our available times are: 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM, 5:00 PM, and 7:00 PM. Would you like to book the 7:00 PM slot instead?"
            
            return f"Our courts are available during these time slots: {', '.join(self.available_times)}. We operate from {self.business_hours} with 6 courts available. Type 'schedule' to book a game!"
        
        # Pricing questions
        if any(word in message_lower for word in ['price', 'cost', 'fee', 'charge', 'expensive']):
            return f"Our pricing: Singles court rental: ${self.pricing['singles']}/hour, Doubles: ${self.pricing['doubles']}/hour, Equipment rental: ${self.pricing['equipment']}/person, Coaching: ${self.pricing['coaching']}/hour. Type 'schedule' to book!"
        
        # Hours questions
        if any(word in message_lower for word in ['hours', 'open', 'close', 'when']):
            return f"We're open {self.business_hours}. Our time slots are: {', '.join(self.available_times)}."
        
        # Equipment questions
        if any(word in message_lower for word in ['equipment', 'paddle', 'ball', 'gear']):
            return f"Yes! We rent equipment for ${self.pricing['equipment']}/person (includes paddle and balls). You can add this when booking your court time."
        
        # Coaching questions
        if any(word in message_lower for word in ['coach', 'lesson', 'teach', 'learn']):
            return f"We offer coaching sessions for ${self.pricing['coaching']}/hour. Our coaches can help with technique, strategy, and game improvement!"
        
        # General greeting/help
        if any(word in message_lower for word in ['hello', 'hi', 'help', 'info', 'about']):
            return "Hi! I'm here to help with your paddle game needs. We have 6 courts available from 9 AM-9 PM daily. Ask about pricing, availability, or type 'schedule' to book a game!"
        
        return "I'm currently having connectivity issues, but I can still help! Try asking about court availability, pricing, hours, or type 'schedule' to book a game directly."
    
    def send_to_gemini(self, user_message):
        headers = {"Content-Type": "application/json"}
        
        # Include recent conversation history for context
        context = self.get_business_context()
        if self.conversation_history:
            context += "\n\nRecent conversation:\n"
            for entry in self.conversation_history[-6:]:  # Last 3 exchanges
                context += f"{entry}\n"
        
        prompt = f"{context}\n\nCustomer: {user_message}\nAssistant:"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Store conversation history
                self.conversation_history.append(f"Customer: {user_message}")
                self.conversation_history.append(f"Assistant: {ai_response}")
                
                return ai_response
            else:
                # Fallback to offline handling
                print(f"[API Error {response.status_code}] ", end="")
                return self.handle_offline_query(user_message)
                
        except requests.exceptions.Timeout:
            print("[Timeout] ", end="")
            return self.handle_offline_query(user_message)
        except requests.exceptions.RequestException as e:
            print("[Connection Error] ", end="")
            return self.handle_offline_query(user_message)
        except Exception as e:
            print("[Error] ", end="")
            return self.handle_offline_query(user_message)
    
    def show_help(self):
        print("\n" + "="*50)
        print("AVAILABLE COMMANDS & FEATURES")
        print("="*50)
        print("Commands:")
        print("• 'schedule' - Book a paddle game")
        print("• 'bookings' - View all current bookings")
        print("• 'help' - Show this help menu")
        print("• 'quit' or 'exit' - End the session")
        print("\nConversation:")
        print("• Ask about paddle game rules and techniques")
        print("• Inquire about pricing and services")
        print("• Get information about court availability")
        print("• Ask about equipment and coaching")
        print("• General paddle game questions")
        print("="*50)
    
    def schedule_game(self):
        print("\n" + "="*50)
        print("SCHEDULE A PADDLE GAME")
        print("="*50)
        
        try:
            # Get customer details
            name = input("Your name: ").strip()
            if not name:
                print("Name is required. Booking cancelled.")
                return
                
            email = input("Your email: ").strip()
            if not email:
                print("Email is required. Booking cancelled.")
                return
                
            phone = input("Your phone: ").strip()
            
            # Game type
            print("\nGame types:")
            print("1. Singles ($30/hour)")
            print("2. Doubles ($50/hour)")
            
            while True:
                game_choice = input("Choose (1 or 2): ").strip()
                if game_choice in ['1', '2']:
                    break
                print("Please enter 1 or 2.")
            
            game_type = "Singles" if game_choice == "1" else "Doubles"
            price = 30 if game_choice == "1" else 50
            
            # Available dates
            print("\nAvailable dates:")
            for i in range(1, 8):
                date = datetime.now() + timedelta(days=i)
                print(f"{i}. {date.strftime('%A, %B %d, %Y')}")
            
            while True:
                try:
                    date_choice = int(input("Choose date (1-7): "))
                    if 1 <= date_choice <= 7:
                        break
                    print("Please enter a number between 1 and 7.")
                except ValueError:
                    print("Please enter a valid number.")
            
            selected_date = datetime.now() + timedelta(days=date_choice)
            
            # Available times
            times = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM", "7:00 PM"]
            print("\nAvailable times:")
            for i, time in enumerate(times, 1):
                print(f"{i}. {time}")
            
            while True:
                try:
                    time_choice = int(input("Choose time (1-6): "))
                    if 1 <= time_choice <= 6:
                        break
                    print("Please enter a number between 1 and 6.")
                except ValueError:
                    print("Please enter a valid number.")
            
            selected_time = times[time_choice - 1]
            
            # Equipment rental
            while True:
                equipment_choice = input("Need equipment rental? (+$10/person) (y/n): ").lower().strip()
                if equipment_choice in ['y', 'yes', 'n', 'no']:
                    equipment = equipment_choice in ['y', 'yes']
                    break
                print("Please enter 'y' for yes or 'n' for no.")
            
            # Create booking
            booking = {
                "id": len(self.bookings) + 1,
                "name": name,
                "email": email,
                "phone": phone,
                "game_type": game_type,
                "date": selected_date.strftime('%A, %B %d, %Y'),
                "time": selected_time,
                "equipment": equipment,
                "price": price + (10 if equipment else 0),
                "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.bookings.append(booking)
            
            # Confirmation
            print("\n" + "="*50)
            print("🎉 BOOKING CONFIRMED!")
            print("="*50)
            print(f"Booking ID: #{booking['id']}")
            print(f"Name: {booking['name']}")
            print(f"Email: {booking['email']}")
            print(f"Game: {booking['game_type']}")
            print(f"Date: {booking['date']}")
            print(f"Time: {booking['time']}")
            print(f"Equipment: {'Yes' if booking['equipment'] else 'No'}")
            print(f"Total Cost: ${booking['price']}")
            print("\n📋 Important Notes:")
            print("• Please arrive 15 minutes early")
            print("• Bring comfortable athletic wear")
            print("• Courts are located at the main entrance")
            print("="*50)
            
        except KeyboardInterrupt:
            print("\nBooking cancelled.")
        except Exception as e:
            print(f"An error occurred during booking: {str(e)}")
    
    def view_bookings(self):
        if not self.bookings:
            print("\n📅 No bookings found.")
            return
        
        print("\n" + "="*50)
        print(f"ALL BOOKINGS ({len(self.bookings)} total)")
        print("="*50)
        for booking in self.bookings:
            print(f"🎾 Booking #{booking['id']}")
            print(f"   Name: {booking['name']}")
            print(f"   Game: {booking['game_type']}")
            print(f"   Date: {booking['date']} at {booking['time']}")
            print(f"   Equipment: {'Yes' if booking['equipment'] else 'No'}")
            print(f"   Cost: ${booking['price']}")
            print(f"   Booked: {booking.get('created', 'N/A')}")
            print("-" * 30)
    
    def run(self):
        print("🏓 Welcome to Paddle Game Assistant!")
        print("I can help you with questions about paddle games and schedule court time.")
        print("\n💬 You can:")
        print("• Ask me anything about paddle games, rules, or techniques")
        print("• Inquire about our services and pricing")
        print("• Type 'schedule' to book a game")
        print("• Type 'bookings' to view your bookings")
        print("• Type 'edit prompt' to view or update assistant instructions")
        print("• Type 'help' for more options")
        print("• Type 'quit' to exit")
        print("-" * 60)

        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    print("Please enter a message or command.")
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("Thanks for using Paddle Game Assistant! Have a great game! 🏓")
                    break

                elif user_input.lower() in ['schedule', 'book', 'booking']:
                    self.schedule_game()

                elif user_input.lower() in ['bookings', 'view bookings', 'my bookings']:
                    self.view_bookings()

                elif user_input.lower() in ['edit prompt', 'update prompt']:
                    self.prompt_manager.show_prompt_menu()  # ✅ Step 3 here

                elif user_input.lower() in ['help', 'commands', '?']:
                    self.show_help()

                else:
                    # Handle general conversation
                    print("\n🤖 Assistant: ", end="")
                    response = self.send_to_gemini(user_input)
                    print(response)

                    # Suggest actions if appropriate
                    if any(word in user_input.lower() for word in ['book', 'schedule', 'reserve', 'appointment']):
                        print("\n💡 Tip: Type 'schedule' to book a game right now!")

            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for using Paddle Game Assistant! 🏓")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                print("Please try again.")


if __name__ == "__main__":
    assistant = PaddleGameAssistant()
    assistant.run()
    