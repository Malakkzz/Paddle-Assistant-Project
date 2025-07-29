import requests

# manages the editable prompt system for the AI assistant
# loads current prompt from file, allows admin to edit prompt
# enhance prompt using gemini api
# ask for confirmation to replace current prompt


class PromptManager:
    def __init__(self):
        self.current_prompt_file = "current_prompt.txt"
        self.edited_prompt_file = "edited_prompt.txt"
        self.pending_prompt_file = "pending_prompt.txt"
        self.api_key = "AIzaSyDF55zA3b2dK8XSKU7Ux6y7zZcc6Xsospw"
        self.model_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def get_current_prompt(self):
        try:
            with open(self.current_prompt_file, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "No current prompt found."

    def save_edited_prompt(self, edited_text):
        with open(self.edited_prompt_file, 'w', encoding='utf-8') as file:
            file.write(edited_text)
        print("✅ Edited prompt saved and ready for enhancement.")

    def call_llm_to_refine(self, prompt_text):
        headers = {"Content-Type": "application/json"}
        instruction = (
            "You're a smart assistant. The following text is a system prompt for a paddle game assistant. "
            "Please clean it up, improve clarity, remove redundancy, and enhance tone while keeping the meaning. "
            "Keep bullet points short and clear.\n\nPrompt:\n"
        )
        full_prompt = instruction + prompt_text

        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }

        try:
            response = requests.post(
                f"{self.model_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return None

    def confirm_prompt_update(self):
        """Once refined, ask user whether to accept it."""
        try:
            with open(self.pending_prompt_file, 'r', encoding='utf-8') as file:
                new_prompt = file.read()
        except FileNotFoundError:
            print("No refined prompt pending confirmation.")
            return

        print("\n📌 Finetuned Prompt Preview:\n")
        print(new_prompt)
        choice = input("\nDo you want to use this version as your new prompt? (y/n): ").strip().lower()
        if choice == 'y':
            with open(self.current_prompt_file, 'w', encoding='utf-8') as file:
                file.write(new_prompt)
            print("✅ Prompt updated successfully.")
        else:
            print("❌ Finetuned prompt discarded. Keeping the original.")

    def show_prompt_menu(self):
        print("\n📄 Current Prompt:\n")
        print(self.get_current_prompt())
        choice = input("\nDo you want to edit the prompt? (y/n): ").strip().lower()
        if choice == 'y':
            print("\nEnter the updated prompt (type 'END' on a new line to finish):")
            new_prompt_lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                new_prompt_lines.append(line)
            updated_prompt = "\n".join(new_prompt_lines)
            self.save_edited_prompt(updated_prompt)

            # Step 2: Enhance using LLM
            print("\n🧠 Enhancing your prompt using Gemini AI...")
            improved = self.call_llm_to_refine(updated_prompt)
            if improved:
                with open(self.pending_prompt_file, 'w', encoding='utf-8') as file:
                    file.write(improved)
                print("✅ Finetuned prompt generated and saved.")
                self.confirm_prompt_update()
            else:
                print("❌ Failed to enhance the prompt.")

        else:
            print("No changes made to the prompt.")
