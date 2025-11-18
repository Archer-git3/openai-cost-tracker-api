import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Cost Tracker", page_icon="💰")
st.title("💰 AI Cost Tracker Chat")

if "session_id" not in st.session_state:
    st.session_state["session_id"] = None

with st.sidebar:
    st.header("Controls")
    if st.button("New Chat"):
        with st.spinner("Creating new session..."):
            try:
                resp = requests.post(f"{API_URL}/sessions", timeout=15)  # <- збільшено timeout
                resp.raise_for_status()
                data = resp.json()
                st.session_state["session_id"] = data["session_id"]
                st.success(f"Created: {data['session_id']}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

session_id = st.session_state["session_id"]

if session_id:
    # --- Завантажуємо історію ---
    try:
        resp = requests.get(f"{API_URL}/sessions/{session_id}/history", timeout=15)
        resp.raise_for_status()
        data = resp.json()

        st.metric("Total Session Cost", f"${data['total_cost_usd']:.5f}")
        st.divider()

        for msg in data["messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg["role"] == "assistant":
                    st.caption(f"💸 Cost: ${msg['cost_usd']:.6f} | Tokens: {msg['completion_tokens']}")

    except Exception as e:
        st.error(f"Connection error: {e}")

    # --- Ввід повідомлення ---
    if prompt := st.chat_input("Type your message..."):
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("AI is thinking..."):
            try:
                # Відправка через query параметр, як очікує FastAPI
                resp = requests.post(
                    f"{API_URL}/sessions/{session_id}/chat",
                    params={"user_input": prompt},
                    timeout=60
                )
                resp.raise_for_status()
                st.rerun()
            except Exception as e:
                st.error(f"Request failed: {e}")
else:
    st.info("👈 Please click 'New Chat' in the sidebar to start.")
