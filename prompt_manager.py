import requests
import time
import re

class PromptManager:
    def __init__(self):
        self.current_prompt_file = "current_prompt.txt"
        self.edited_prompt_file = "edited_prompt.txt"
        self.pending_prompt_file = "pending_prompt.txt"
        self.api_key = "AIzaSyDF55zA3b2dK8XSKU7Ux6y7zZcc6Xsospw"
        self.model_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.ensure_current_prompt_exists()

    def ensure_current_prompt_exists(self):
        try:
            with open(self.current_prompt_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    raise FileNotFoundError
        except FileNotFoundError:
            default_prompt = """You are a virtual assistant for a paddle game business.

SERVICES & PRICING:
- Court rental: $30/hour (singles), $50/hour (doubles)
- Equipment rental: $10/person (paddle + balls)
- Coaching: $60/hour
- Operating hours: 9 AM - 9 PM daily
- 6 courts available

AVAILABLE TIME SLOTS:
- 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM, 5:00 PM, 7:00 PM

Help customers with questions about paddle games, pricing, and scheduling.
Be friendly and helpful. Keep responses concise."""

            with open(self.current_prompt_file, 'w', encoding='utf-8') as file:
                file.write(default_prompt)
            print("✅ Default prompt created.")

    def get_current_prompt(self):
        try:
            with open(self.current_prompt_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                return content if content else self.get_default_prompt()
        except FileNotFoundError:
            return self.get_default_prompt()

    def get_default_prompt(self):
        return """You are a virtual assistant for a paddle game business.

SERVICES & PRICING:
- Court rental: $30/hour (singles), $50/hour (doubles)
- Equipment rental: $10/person (paddle + balls)
- Coaching: $60/hour
- Operating hours: 9 AM - 9 PM daily
- 6 courts available

AVAILABLE TIME SLOTS:
- 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM, 5:00 PM, 7:00 PM

Help customers with questions about paddle games, pricing, and scheduling.
Be friendly and helpful. Keep responses concise."""

    

    def get_dynamic_info(self):
        """Parse current_prompt.txt to extract pricing, hours, and available times"""
        prompt = self.get_current_prompt()

        pricing = {}
        hours = ""
        times = []

        if "Singles:" in prompt:
            singles_match = re.search(r"Singles: \$?(\d+)", prompt)
            if singles_match:
                pricing['singles'] = int(singles_match.group(1))

        if "Doubles:" in prompt:
            doubles_match = re.search(r"Doubles: \$?(\d+)", prompt)
            if doubles_match:
                pricing['doubles'] = int(doubles_match.group(1))

        if "equipment" in prompt.lower():
            equip_match = re.search(r"Equipment Rental:\s*\$?(\d+)", prompt, re.IGNORECASE)
            if equip_match:
                pricing['equipment'] = int(equip_match.group(1))

        if "Hours of Operation:" in prompt:
            hours_match = re.search(r"Hours of Operation:\s*(.+?)\n", prompt)
            if hours_match:
                hours = hours_match.group(1).strip()

        if "Available Court Times Today:" in prompt:
            times_match = re.findall(r"(\d{1,2}:\d{2} [AP]M)", prompt)
            if times_match:
                times = times_match
                
        pricing.setdefault('equipment', 10)

        return pricing, hours, times



    def save_edited_prompt(self, edited_text):
        with open(self.edited_prompt_file, 'w', encoding='utf-8') as file:
            file.write(edited_text)
        print("✅ Edited prompt saved and ready for enhancement.")

    def call_llm_to_refine(self, prompt_text, retries=2):
        headers = {"Content-Type": "application/json"}

        instruction = (
            "Improve this paddle game assistant prompt. Make it clearer and more professional while keeping the same information:\n\n"
        )
        full_prompt = instruction + prompt_text

        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": 1000,
                "temperature": 0.3
            }
        }

        for attempt in range(1, retries + 1):
            try:
                print(f"⏳ Attempt {attempt}/{retries} to enhance prompt...")

                response = requests.post(
                    f"{self.model_url}?key={self.api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    enhanced_text = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ Prompt enhanced successfully!")
                    return enhanced_text
                elif response.status_code == 429:
                    print("⚠️ Rate limited, waiting...")
                    time.sleep(5)
                else:
                    print(f"❌ API Error {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt}")
                if attempt < retries:
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"🌐 Connection error on attempt {attempt}: {e}")
                if attempt < retries:
                    time.sleep(3)
            except Exception as e:
                print(f"❌ Unexpected error on attempt {attempt}: {e}")
                if attempt < retries:
                    time.sleep(2)

        print("❌ All attempts failed. Skipping enhancement.")
        return None

    def confirm_prompt_update(self):
        try:
            with open(self.pending_prompt_file, 'r', encoding='utf-8') as file:
                new_prompt = file.read()
        except FileNotFoundError:
            print("❌ No refined prompt pending confirmation.")
            return

        print("\n" + "=" * 60)
        print("📌 ENHANCED PROMPT PREVIEW:")
        print("=" * 60)
        print(new_prompt)
        print("=" * 60)

        choice = input("\n✅ Accept this enhanced prompt? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            with open(self.current_prompt_file, 'w', encoding='utf-8') as file:
                file.write(new_prompt)
            print("✅ Prompt updated successfully!")

            try:
                import os
                os.remove(self.pending_prompt_file)
                os.remove(self.edited_prompt_file)
            except:
                pass
        else:
            print("❌ Enhanced prompt rejected. Keeping the original.")

    def show_prompt_menu(self):
        print("\n" + "=" * 60)
        print("📄 CURRENT PROMPT:")
        print("=" * 60)
        current = self.get_current_prompt()
        print(current)
        print("=" * 60)

        choice = input("\n✏️ Edit this prompt? (y/n): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("❌ No changes made.")
            return

        print("\n📝 Enter your updated prompt below.")
        print("💡 Type 'END' on a new line when finished:")
        print("-" * 40)

        new_prompt_lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                new_prompt_lines.append(line)
            except KeyboardInterrupt:
                print("\n❌ Editing cancelled.")
                return

        updated_prompt = "\n".join(new_prompt_lines).strip()

        if not updated_prompt:
            print("❌ Empty prompt. No changes made.")
            return

        self.save_edited_prompt(updated_prompt)

        enhance = input("\n🧠 Enhance with AI? (y/n): ").strip().lower()
        if enhance in ['y', 'yes']:
            print("\n🔄 Enhancing your prompt...")
            improved = self.call_llm_to_refine(updated_prompt)

            if improved:
                with open(self.pending_prompt_file, 'w', encoding='utf-8') as file:
                    file.write(improved)
                print("✅ Enhanced prompt generated!")
                self.confirm_prompt_update()
            else:
                print("❌ Enhancement failed. Using your original edit...")
                with open(self.current_prompt_file, 'w', encoding='utf-8') as file:
                    file.write(updated_prompt)
                print("✅ Your edited prompt saved successfully!")
        else:
            with open(self.current_prompt_file, 'w', encoding='utf-8') as file:
                file.write(updated_prompt)
            print("✅ Prompt updated successfully!")
