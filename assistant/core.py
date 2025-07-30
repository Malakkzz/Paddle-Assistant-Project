from prompt_manager import PromptManager
from assistant.bookings import BookingManager
from assistant.responder import Responder

# brain that ties everything together
# calls booking.schedule, booking.view, prompt.show
# sends all other text to AI via responder

class PaddleGameAssistant:
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.responder = Responder(self.prompt_manager)
        # Pass responder to booking manager for AI features
        self.booking_mgr = BookingManager(self.responder)

    def run(self):
        print("🏓 Welcome to Paddle Game Assistant!")
        print("Type 'schedule' to book, 'bookings' to view, 'edit prompt' to update, 'quit' to exit.")
        while True:
            try:
                user_input = input("\n💬 You: ").strip().lower()
                if not user_input:
                    continue
                elif user_input in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                elif user_input in ['schedule']:
                    self.booking_mgr.schedule_game()
                elif user_input in ['bookings']:
                    self.booking_mgr.view_bookings()
                    # Optional: Add AI summary
                    summary = self.booking_mgr.get_ai_booking_summary()
                    if summary and len(summary) > 10:
                        print(f"\n🤖 {summary}")
                elif user_input in ['edit prompt']:
                    self.prompt_manager.show_prompt_menu()
                else:
                    print("\n🤖 Assistant:", self.responder.send_to_gemini(user_input))
            except Exception as e:
                print(f"[Error] {e}")

if __name__ == "__main__":
    assistant = PaddleGameAssistant()
    assistant.run()