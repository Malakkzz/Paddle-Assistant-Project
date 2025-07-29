import requests
from assistant.config import BUSINESS_HOURS, AVAILABLE_TIMES, PRICING

# handles conversation with the user ( sending messages to gemini AI API, responding to offline questions when api fails)

class Responder:
    def __init__(self, prompt_manager):
        self.prompt_manager = prompt_manager
        self.api_key = prompt_manager.api_key
        self.base_url = prompt_manager.model_url
        self.conversation_history = []

    # dynamic prompt
    def get_business_context(self):
        prompt = self.prompt_manager.get_current_prompt()
        if "No current prompt found." in prompt or not prompt.strip():
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
        return prompt

    def send_to_gemini(self, user_message):
        headers = {"Content-Type": "application/json"}

        context = self.get_business_context()
        if self.conversation_history:
            context += "\n\nRecent conversation:\n"
            for entry in self.conversation_history[-6:]:
                context += f"{entry}\n"

        prompt = f"{context}\n\nCustomer: {user_message}\nAssistant:"

        data = {"contents": [{"parts": [{"text": prompt}]}]}

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
                self.conversation_history.append(f"Customer: {user_message}")
                self.conversation_history.append(f"Assistant: {ai_response}")
                return ai_response
            else:
                print(f"[API Error {response.status_code}] ", end="")
                return self.handle_offline_query(user_message)

        except Exception as e:
            print(f"[Error] {e}", end="")
            return self.handle_offline_query(user_message)

    def handle_offline_query(self, message):
        msg = message.lower()
        if any(x in msg for x in ['court', 'available', 'time', 'slot', 'book']):
            return f"Available times: {', '.join(AVAILABLE_TIMES)}. Open: {BUSINESS_HOURS}"
        elif any(x in msg for x in ['price', 'cost']):
            return f"Singles: ${PRICING['singles']}, Doubles: ${PRICING['doubles']}, Equipment: ${PRICING['equipment']}, Coaching: ${PRICING['coaching']}"
        elif any(x in msg for x in ['hours', 'open', 'close']):
            return f"Open from {BUSINESS_HOURS}. Time slots: {', '.join(AVAILABLE_TIMES)}"
        elif any(x in msg for x in ['equipment', 'paddle']):
            return f"Yes, equipment rental available for ${PRICING['equipment']} per person."
        elif any(x in msg for x in ['coach', 'lesson']):
            return f"Coaching is ${PRICING['coaching']} per hour."
        elif any(x in msg for x in ['hello', 'hi']):
            return "Hi! I'm your paddle assistant. Ask anything or type 'schedule' to book!"
        return "I'm offline. Try asking about hours, pricing, or type 'schedule'."