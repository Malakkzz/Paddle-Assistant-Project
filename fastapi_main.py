from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from assistant.core import PaddleGameAssistant
from assistant.bookings import BookingManager
from assistant.responder import Responder
from prompt_manager import PromptManager

app = FastAPI(title="Paddle Game Assistant API", version="1.0.0")

# Global instances
prompt_manager = PromptManager()
responder = Responder(prompt_manager)
booking_manager = BookingManager(responder)

# Pydantic models for request/response
class PromptUpdateRequest(BaseModel):
    prompt: str
    enhance: bool = False

class ChatRequest(BaseModel):
    message: str

class BookingRequest(BaseModel):
    name: str
    email: str
    phone: str
    game_type: str  # "singles" or "doubles"
    date: str
    time: str
    equipment: bool = False

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Main dashboard with prompt management interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paddle Game Assistant - Admin Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            .section { margin: 30px 0; }
            .section h3 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            textarea { width: 100%; min-height: 200px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
            button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #2980b9; }
            button.danger { background: #e74c3c; }
            button.danger:hover { background: #c0392b; }
            .current-prompt { background: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; margin: 15px 0; }
            .api-docs { background: #ecf0f1; padding: 15px; border-radius: 5px; }
            .endpoint { margin: 10px 0; padding: 10px; background: white; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏓 Paddle Game Assistant</h1>
                <p>Admin Dashboard & Prompt Management</p>
            </div>

            <div class="section">
                <h3>📝 Current Prompt</h3>
                <div class="current-prompt" id="currentPrompt">Loading...</div>
                <button onclick="loadCurrentPrompt()">Refresh Current Prompt</button>
            </div>

            <div class="section">
                <h3>✏️ Update Prompt</h3>
                <textarea id="newPrompt" placeholder="Enter your new prompt here..."></textarea>
                <br>
                <label>
                    <input type="checkbox" id="enhancePrompt"> Enhance with AI
                </label>
                <br><br>
                <button onclick="updatePrompt()">Update Prompt</button>
                <button onclick="resetPrompt()" class="danger">Reset to Default</button>
            </div>

            <div class="section">
                <h3>💬 Test Chat</h3>
                <input type="text" id="chatInput" placeholder="Ask me anything..." style="width: 70%; padding: 10px;">
                <button onclick="sendChat()">Send</button>
                <div id="chatResponse" style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px; min-height: 50px;"></div>
            </div>

            <div class="section">
                <h3>📊 Business Info</h3>
                <div id="businessInfo">Loading...</div>
                <button onclick="loadBusinessInfo()">Refresh Business Info</button>
            </div>

            
        </div>

        <script>
            async function loadCurrentPrompt() {
                try {
                    const response = await fetch('/prompt');
                    const data = await response.json();
                    document.getElementById('currentPrompt').innerHTML = '<pre>' + data.prompt + '</pre>';
                } catch (error) {
                    document.getElementById('currentPrompt').innerHTML = 'Error loading prompt: ' + error.message;
                }
            }

            async function updatePrompt() {
                const prompt = document.getElementById('newPrompt').value;
                const enhance = document.getElementById('enhancePrompt').checked;
                
                if (!prompt.trim()) {
                    alert('Please enter a prompt');
                    return;
                }

                try {
                    const response = await fetch('/prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt, enhance: enhance })
                    });
                    
                    const data = await response.json();
                    alert(data.message);
                    loadCurrentPrompt();
                    document.getElementById('newPrompt').value = '';
                } catch (error) {
                    alert('Error updating prompt: ' + error.message);
                }
            }

            async function resetPrompt() {
                if (!confirm('Are you sure you want to reset to the default prompt?')) return;
                
                try {
                    const response = await fetch('/prompt/reset', { method: 'POST' });
                    const data = await response.json();
                    alert(data.message);
                    loadCurrentPrompt();
                } catch (error) {
                    alert('Error resetting prompt: ' + error.message);
                }
            }

            async function sendChat() {
                const message = document.getElementById('chatInput').value;
                if (!message.trim()) return;

                document.getElementById('chatResponse').innerHTML = 'Thinking...';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    document.getElementById('chatResponse').innerHTML = '<strong>Assistant:</strong> ' + data.response;
                    document.getElementById('chatInput').value = '';
                } catch (error) {
                    document.getElementById('chatResponse').innerHTML = 'Error: ' + error.message;
                }
            }

            async function loadBusinessInfo() {
                try {
                    const response = await fetch('/business-info');
                    const data = await response.json();
                    const info = `
                        <p><strong>Pricing:</strong> Singles: $${data.pricing.singles}, Doubles: $${data.pricing.doubles}, Equipment: $${data.pricing.equipment}</p>
                        <p><strong>Hours:</strong> ${data.hours}</p>
                        <p><strong>Available Times:</strong> ${data.available_times.join(', ')}</p>
                    `;
                    document.getElementById('businessInfo').innerHTML = info;
                } catch (error) {
                    document.getElementById('businessInfo').innerHTML = 'Error loading business info: ' + error.message;
                }
            }

            // Load initial data
            window.onload = function() {
                loadCurrentPrompt();
                loadBusinessInfo();
            }

            // Enter key for chat
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('chatInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendChat();
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/prompt")
async def get_current_prompt():
    """Get the current prompt"""
    try:
        prompt = prompt_manager.get_current_prompt()
        return {"prompt": prompt, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prompt")
async def update_prompt(request: PromptUpdateRequest):
    """Update the prompt, optionally with AI enhancement"""
    try:
        if request.enhance:
            # Save the edited prompt first
            prompt_manager.save_edited_prompt(request.prompt)
            
            # Try to enhance it
            enhanced = prompt_manager.call_llm_to_refine(request.prompt)
            
            if enhanced:
                # Save the enhanced version
                with open(prompt_manager.current_prompt_file, 'w', encoding='utf-8') as file:
                    file.write(enhanced)
                return {"message": "Prompt updated and enhanced successfully!", "enhanced": True}
            else:
                # Fall back to original if enhancement fails
                with open(prompt_manager.current_prompt_file, 'w', encoding='utf-8') as file:
                    file.write(request.prompt)
                return {"message": "Prompt updated (enhancement failed, using original)", "enhanced": False}
        else:
            # Direct update without enhancement
            with open(prompt_manager.current_prompt_file, 'w', encoding='utf-8') as file:
                file.write(request.prompt)
            return {"message": "Prompt updated successfully!", "enhanced": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update prompt: {str(e)}")

@app.post("/prompt/reset")
async def reset_prompt():
    """Reset prompt to default"""
    try:
        default_prompt = prompt_manager.get_default_prompt()
        with open(prompt_manager.current_prompt_file, 'w', encoding='utf-8') as file:
            file.write(default_prompt)
        return {"message": "Prompt reset to default successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat with the assistant"""
    try:
        response = responder.send_to_gemini(request.message)
        return {"response": response, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/business-info")
async def get_business_info():
    """Get current business information"""
    try:
        pricing, hours, available_times = prompt_manager.get_dynamic_info()
        return {
            "pricing": pricing,
            "hours": hours,
            "available_times": available_times,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings")
async def get_bookings():
    """Get all bookings"""
    try:
        return {
            "bookings": booking_manager.bookings,
            "total": len(booking_manager.bookings),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bookings")
async def create_booking(request: BookingRequest):
    """Create a new booking"""
    try:
        from datetime import datetime
        
        # Get pricing
        pricing, _, _ = prompt_manager.get_dynamic_info()
        
        # Calculate price
        base_price = pricing.get('singles' if request.game_type.lower() == 'singles' else 'doubles', 30)
        equipment_price = pricing.get('equipment', 10) if request.equipment else 0
        total_price = base_price + equipment_price
        
        # Create booking
        booking = {
            "id": len(booking_manager.bookings) + 1,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "game_type": request.game_type.title(),
            "date": request.date,
            "time": request.time,
            "equipment": request.equipment,
            "price": total_price,
            "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        booking_manager.bookings.append(booking)
        
        return {
            "message": "Booking created successfully!",
            "booking": booking,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🏓 Starting Paddle Game Assistant API...")
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)