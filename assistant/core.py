from prompt_manager import PromptManager
from assistant.bookings import BookingManager
from assistant.responder import Responder

# Optional CLI version - now simplified since main functionality moved to FastAPI
# You can keep this for backwards compatibility or delete it

class PaddleGameAssistant:
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.responder = Responder(self.prompt_manager)
        self.booking_mgr = BookingManager(self.responder)

    def run(self):
        print("🏓 Paddle Game Assistant (CLI Mode)")
        print("💡 For full features, run: python fastapi_main.py")
        print("🌐 Then visit: http://localhost:8000")
        print("\nCLI Commands: 'schedule', 'bookings', 'chat <message>', 'quit'")
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                if not user_input:
                    continue
                elif user_input.lower() in ['quit', 'exit']:
                    print("👋 Goodbye! Consider using the web interface for more features.")
                    break
                elif user_input.lower() == 'schedule':
                    self.booking_mgr.schedule_game()
                elif user_input.lower() == 'bookings':
                    self.booking_mgr.view_bookings()
                    summary = self.booking_mgr.get_ai_booking_summary()
                    if summary and len(summary) > 10:
                        print(f"\n🤖 {summary}")
                elif user_input.lower().startswith('chat '):
                    message = user_input[5:]  # Remove 'chat ' prefix
                    print("\n🤖 Assistant:", self.responder.send_to_gemini(message))
                else:
                    print("\n🤖 Assistant:", self.responder.send_to_gemini(user_input))
            except Exception as e:
                print(f"[Error] {e}")

if __name__ == "__main__":
    assistant = PaddleGameAssistant()
    assistant.run()