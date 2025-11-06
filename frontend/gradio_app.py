import gradio as gr
import requests
import json
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Session management
if 'session_id' not in globals():
    session_id = str(uuid.uuid4())


def chat_with_agent(message, history):
    """Send message to the agent and get response"""
    global session_id
    
    if not message.strip():
        return history
    
    try:
        # Add user message to history
        history.append({"role": "user", "content": message})
        
        # Call API
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={
                "message": message,
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            assistant_message = data["response"]
            
            # Add assistant response to history
            history.append({"role": "assistant", "content": assistant_message})
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            history.append({"role": "assistant", "content": error_msg})
    
    except requests.exceptions.ConnectionError:
        history.append({
            "role": "assistant", 
            "content": "❌ Cannot connect to the server. Please make sure the backend is running at " + API_BASE_URL
        })
    except requests.exceptions.Timeout:
        history.append({
            "role": "assistant", 
            "content": "⏱️ Request timed out. Please try again."
        })
    except Exception as e:
        history.append({
            "role": "assistant", 
            "content": f"❌ Error: {str(e)}"
        })
    
    return history


def check_availability(date, appointment_type):
    """Check available slots"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/calendly/availability",
            params={
                "date": date,
                "appointment_type": appointment_type
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data["available_count"] == 0:
                return f"❌ No available slots on {data['day_of_week']}, {date}"
            
            slots_text = f"✅ **{data['available_count']} Available Slots** on {data['day_of_week']}, {date}:\n\n"
            
            for slot in data["available_slots"]:
                if slot["available"]:
                    slots_text += f"• {slot['start_time']} - {slot['end_time']}\n"
            
            return slots_text
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


def book_appointment(date, start_time, appointment_type, name, email, phone, reason):
    """Book an appointment"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/calendly/book",
            json={
                "appointment_type": appointment_type,
                "date": date,
                "start_time": start_time,
                "patient": {
                    "name": name,
                    "email": email,
                    "phone": phone
                },
                "reason": reason
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            result = "✅ **Appointment Confirmed!**\n\n"
            result += f"**Booking ID:** {data['booking_id']}\n"
            result += f"**Confirmation Code:** {data['confirmation_code']}\n\n"
            result += "**Details:**\n"
            result += f"• Date: {data['details']['date']} ({data['details']['day']})\n"
            result += f"• Time: {data['details']['time']}\n"
            result += f"• Duration: {data['details']['duration']}\n"
            result += f"• Type: {data['details']['appointment_type']}\n"
            result += f"• Doctor: {data['details']['doctor']}\n\n"
            result += f"• Clinic: {data['details']['clinic']}\n"
            result += f"• Address: {data['details']['address']}\n"
            result += f"• Phone: {data['details']['clinic_phone']}\n\n"
            result += f"📧 Confirmation email sent to {email}"
            
            return result
        else:
            return f"❌ Booking Failed: {response.json().get('detail', 'Unknown error')}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


def reset_chat():
    """Reset the chat session"""
    global session_id
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/reset-session/{session_id}",
            timeout=5
        )
        session_id = str(uuid.uuid4())
        return [], "✅ Chat session reset!"
    except:
        session_id = str(uuid.uuid4())
        return [], "✅ Chat session reset!"


def get_system_health():
    """Check system health"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            health = "✅ **System Status: Healthy**\n\n"
            for service, status in data["services"].items():
                health += f"• {service}: {status}\n"
            return health
        else:
            return "❌ System unavailable"
    except:
        return "❌ Cannot connect to backend server"


# Custom CSS
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.clinic-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
}
.feature-box {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 4px solid #667eea;
}
"""

# Build the Gradio interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="Sunrise Health Clinic") as demo:
    
    # Header
    gr.HTML("""
        <div class="clinic-header">
            <h1>Sunrise Health Clinic</h1>
            <h3>Dr. Aisha Mehta, M.B.B.S.</h3>
            <p>45 Gree View Road,Lake Side Colony Pune,Maharastra 411045 | +91 9893943223</p>
            <p><i>Appointment Scheduling App</i></p>
        </div>
    """)
    
    with gr.Tabs():
        
        # Tab 1: Chat Assistant
        with gr.Tab("Chat Assistant"):
            gr.Markdown("""
            ### Welcome! I'm your AI assistant.
            """)
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                type="messages",
                avatar_images=(None, "🏥")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Type your message here... (e.g., 'I need to book an appointment')",
                    scale=4
                )
                send_btn = gr.Button("Send", scale=1, variant="primary")
            
            with gr.Row():
                clear_btn = gr.Button("Reset Chat", size="sm")
                health_btn = gr.Button("System Status", size="sm")
            
            status_output = gr.Textbox(label="Status", interactive=False, visible=False)
            
            # Chat functionality
            msg.submit(chat_with_agent, [msg, chatbot], [chatbot]).then(
                lambda: "", None, [msg]
            )
            send_btn.click(chat_with_agent, [msg, chatbot], [chatbot]).then(
                lambda: "", None, [msg]
            )
            clear_btn.click(reset_chat, None, [chatbot, status_output]).then(
                lambda: gr.update(visible=True), None, [status_output]
            )
            
            def show_health():
                health = get_system_health()
                return health, gr.update(visible=True)
            
            health_btn.click(show_health, None, [status_output, status_output])
        
        # Tab 3: Check Availability
        with gr.Tab("Check Availability"):
            gr.Markdown("""
            ### Check Available Appointment Slots
            
            Select a date and appointment type to see available time slots.
            """)
            
            with gr.Row():
                avail_date = gr.Textbox(
                    label="Date (YYYY-MM-DD)",
                    placeholder=str((datetime.now() + timedelta(days=1)).date()),
                    value=str((datetime.now() + timedelta(days=1)).date())
                )
                avail_type = gr.Dropdown(
                    label="Appointment Type",
                    choices=[
                        ("General Consultation (30 min)", "consultation"),
                        ("Follow-up (15 min)", "followup"),
                        ("Physical Exam (45 min)", "physical"),
                        ("Specialist Consultation (60 min)", "specialist")
                    ],
                    value="consultation"
                )
            
            check_avail_btn = gr.Button("Check Availability 🔍", variant="primary")
            availability_output = gr.Markdown(label="Available Slots")
            
            check_avail_btn.click(
                check_availability,
                [avail_date, avail_type],
                [availability_output]
            )
        
        # Tab 4: Book Appointment
        with gr.Tab("Book Appointment"):
            gr.Markdown("""
            ### Direct Appointment Booking
            
            Fill in the form below to book an appointment directly.
            """)
            
            with gr.Row():
                book_date = gr.Textbox(
                    label="Date (YYYY-MM-DD)",
                    placeholder=str((datetime.now() + timedelta(days=1)).date())
                )
                book_time = gr.Textbox(
                    label="Time (HH:MM)",
                    placeholder="10:00"
                )
            
            book_type = gr.Dropdown(
                label="Appointment Type",
                choices=[
                    ("General Consultation (30 min)", "consultation"),
                    ("Follow-up (15 min)", "followup"),
                    ("Physical Exam (45 min)", "physical"),
                    ("Specialist Consultation (60 min)", "specialist")
                ],
                value="consultation"
            )
            
            gr.Markdown("### Patient Information")
            
            with gr.Row():
                book_name = gr.Textbox(label="Full Name", placeholder="Rajesh Kumar")
                book_email = gr.Textbox(label="Email", placeholder="rajesh@example.com")
            
            with gr.Row():
                book_phone = gr.Textbox(label="Phone", placeholder="+91-9876543210")
                book_reason = gr.Textbox(label="Reason for Visit", placeholder="Annual checkup")
            
            book_btn = gr.Button("Book Appointment 📅", variant="primary", size="lg")
            booking_output = gr.Markdown(label="Booking Confirmation")
            
            book_btn.click(
                book_appointment,
                [book_date, book_time, book_type, book_name, book_email, book_phone, book_reason],
                [booking_output]
            )
        
        # Tab 5: About
        with gr.Tab("About"):
            gr.Markdown("""
            ## 🏥 Sunrise Health Clinic
            
            ### 👨‍⚕️ Dr. Aisha Mehta
            **Specialization:** General Medicine  
            **Experience:** 10+ years
            
            ---
            
            ### 📍 Location
            **Address:** 45 Greenview Road , Lakeside Colony , Pune 411045  
            **Landmark:** Near Sayaji Hotel, opposite Central Mall
            
            ---
            
            ### 🕒 Working Hours
            **Monday - Friday:** 9:00 AM - 1:00 PM, 2:00 PM - 6:00 PM  
            **Saturday:** 9:00 AM - 2:00 PM  
            **Sunday:** Closed
            
            ---
            
            ### 📞 Contact
            **Phone:** +91-368-839-3829  
            **Email:** info@sunriseclinic.com  
            **WhatsApp:** +91-9876543210
            
            ---
            
            ### 💳 Accepted Insurance
            - Star Health Insurance
            - ICICI Lombard
            - HDFC ERGO
            - Bajaj Allianz
            - Religare Health Insurance
            - Care Health Insurance
            - Government schemes (CGHS, ESIC)
            - Ayushman Bharat (PMJAY)
            
            ---
            
            ### 🛠️ Technology
            This intelligent assistant uses:
            - **GPT-4** for natural conversation
            - **RAG** for accurate information retrieval
            - **Smart Scheduling** with conflict detection
            - **Context Switching** between FAQ and booking
            
            ---
            
            ### ⚡ Features
            - Natural conversational interface
            - FAQ knowledge base with 26+ topics
            - Real-time availability checking
            - Instant appointment booking
            - Multi-turn conversation memory
            - Empathetic healthcare-focused responses
            """)
    
    # Footer
    gr.HTML("""
        <div style="text-align: center; padding: 20px; margin-top: 30px; border-top: 2px solid #e0e0e0;">
            <p style="color: #999; font-size: 12px;">
                For emergencies, please call 108 or visit the nearest emergency room
            </p>
        </div>
    """)

# Launch configuration
if __name__ == "__main__":
    print("Starting- Gradio Interface")
    print("🌐 Opening browser...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )