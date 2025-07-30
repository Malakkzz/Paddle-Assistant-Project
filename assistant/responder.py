import requests
from assistant.config import BUSINESS_HOURS, AVAILABLE_TIMES, PRICING
import time


# handles conversation with the user ( sending messages to gemini AI API, responding to offline questions when api fails)

class Responder:
    def __init__(self, prompt_manager):
        self.prompt_manager = prompt_manager
        self.api_key = prompt_manager.api_key
        self.base_url = prompt_manager.model_url
        self.conversation_history = []

    # dynamic prompt
    def get_business_context(self):
        """Load current prompt from file, fallback to static if empty"""
        try:
            prompt = self.prompt_manager.get_current_prompt()
            
            # Debug print to see what we're getting
            print(f"[DEBUG] Loaded prompt: {len(prompt)} chars, starts with: {repr(prompt[:50])}")
            
            # Check if prompt is valid and not empty
            if prompt and prompt.strip() and len(prompt.strip()) > 50:  # At least 50 chars for a real prompt
                print("[DEBUG] ✅ Using CUSTOM prompt from current_prompt.txt")
                return prompt
            else:
                print("[DEBUG] ⚠️ Using STATIC fallback prompt")
                return self.get_static_prompt()
                
        except Exception as e:
            print(f"[ERROR] Failed to load prompt: {e}")
            return self.get_static_prompt()

    def get_static_prompt(self):
        """Static fallback prompt"""
        return f"""
        You are a virtual assistant for a paddle center.

        Services:
        - Court rental: ${PRICING['singles']}/hour (singles), ${PRICING['doubles']}/hour (doubles)
        - Equipment rental: ${PRICING['equipment']}/person
        - Coaching: ${PRICING['coaching']}/hour
        - Hours: {BUSINESS_HOURS}
        - 6 courts available

        Available time slots: {', '.join(AVAILABLE_TIMES)}

        Answer questions about pricing, availability, equipment, and booking.
        Be helpful and concise.
        """

    def send_to_gemini(self, user_message, max_retries=2):
        headers = {"Content-Type": "application/json"}
        context = self.get_business_context()

        if self.conversation_history:
            context += "\n\nRecent conversation:\n"
            for entry in self.conversation_history[-6:]:
                context += f"{entry}\n"

        prompt = f"{context}\n\nCustomer: {user_message}\nAssistant:"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    headers=headers,
                    json=data,
                    timeout=20
                )
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    self.conversation_history.append(f"Customer: {user_message}")
                    self.conversation_history.append(f"Assistant: {ai_response}")
                    return ai_response
                else:
                    print(f"[API Error {response.status_code}] Attempt {attempt}/{max_retries}")
                    if attempt < max_retries:
                        time.sleep(1)  # brief wait before retry
            except Exception as e:
                print(f"[Retry {attempt}] API exception: {e}")
                if attempt < max_retries:
                    time.sleep(1)

        # Final fallback after all retries fail
        return self.handle_offline_query(user_message)


    def handle_offline_query(self, message):
        msg = message.lower()
        if any(x in msg for x in ['court', 'available', 'time', 'slot', 'book']):
            return f"Available times: {', '.join(AVAILABLE_TIMES)}. Open: {BUSINESS_HOURS}"
        elif any(x in msg for x in ['price', 'cost']):
            return f"Singles: ${PRICING['singles']}, Doubles: ${PRICING['doubles']}, Equipment: ${PRICING['equipment']}, Coaching: ${PRICING['coaching']}"
        elif any(x in msg for x in ['hours', 'open', 'close']):
            pricing, hours, times, allowed_days = self.prompt_manager.get_dynamic_info()
            return f"Open days: {', '.join(allowed_days)}. Hours: {hours}. Time slots: {', '.join(times)}"
        elif any(x in msg for x in ['equipment', 'paddle']):
            return f"Yes, equipment rental available for ${PRICING['equipment']} per person."
        elif any(x in msg for x in ['coach', 'lesson']):
            return f"Coaching is ${PRICING['coaching']} per hour."
        elif any(x in msg for x in ['hello', 'hi']):
            return "Hi! I'm your paddle assistant. Ask anything or type 'schedule' to book!"
        return "I'm offline. Try asking about hours, pricing, or type 'schedule'."