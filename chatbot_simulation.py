import streamlit as st
from openai import OpenAI
from datetime import datetime

# --- CONFIGURATION ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


st.set_page_config(page_title="Chatter Training Bot", layout="wide")
st.title("💬 OnlyFans Fan Simulation Chatbot")
st.write("Practice chatting with a simulated fan. Your goal: flirt, upsell, and build trust.")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- INITIAL FAN MESSAGE ---
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "fan",
        "content": "Hey you 😏 I was just staring at your pics… kinda obsessed lol. Whatchu up to?"
    })

# --- DISPLAY ALL MESSAGES ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# --- CHAT INPUT ---
user_input = st.chat_input("Type your response...")

if user_input:
    st.session_state.messages.append({"role": "chatter", "content": user_input})
    st.chat_message("chatter").markdown(user_input)

    # Prepare messages for API (convert custom 'fan' role to 'assistant')
    formatted_messages = [{"role": "system", "content":
        "You are a playful, flirty, American male fan chatting with an OnlyFans model. \
Sometimes you're sweet, sometimes you're pushy, sometimes you're cheap. \
Test the model’s responses using humor, slang, sexual curiosity, and emotional manipulation. \
Push her to upsell without being obvious."
    }]

    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "fan" else "user"
        formatted_messages.append({"role": role, "content": msg["content"]})

    # Get fan reply using GPT-4
    response = client.chat.completions.create(
        model="gpt-4",
        messages=formatted_messages,
        temperature=0.9
    )

    fan_reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "fan", "content": fan_reply})
    st.chat_message("fan").markdown(fan_reply)

# --- END SIMULATION AND EVALUATE ---
if st.button("📝 End Simulation & Get Feedback"):
    conversation = "\n".join([
        f"{m['role'].capitalize()}: {m['content']}"
        for m in st.session_state.messages
        if m["role"] != "system"
    ])

    evaluation_prompt = f"""You are a trainer at an OnlyFans agency. The following is a chat between a chatter and a fan.
Rate the chatter on the following out of 10:
- Natural tone & slang usage
- Progressive upselling
- Emotional connection
- Pricing confidence
- Handling objections

Then give 3 suggestions for improvement in a professional but helpful tone.

Conversation:
{conversation}
"""

    eval_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": evaluation_prompt}],
        temperature=0.6
    )

    feedback = eval_response.choices[0].message.content

    st.subheader("📊 Performance Feedback")
    st.write(feedback)

