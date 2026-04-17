import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid  # to create dynamic threads

# ******************************** utility functions ******************************************#

def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    # initialize chat_threads if not present
    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = []

    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    # create new thread
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id

    # add to thread list
    add_thread(thread_id)

    # clear UI messages for new chat
    st.session_state['ui_messages'] = []

    # rerun to refresh UI
    st.rerun()


def load_chat(thread_id):
    # switch active thread
    st.session_state['thread_id'] = thread_id

    # load messages of that thread
    st.session_state['ui_messages'] = st.session_state['all_chats'].get(thread_id, [])

    st.rerun()

# *************************************************************************************** #

# Page config
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="centered"
)

# UI styling
st.markdown("""
<style>
    body { background-color: #0e1117; }

    .user-msg {
        background-color: #1f2937;
        color: white;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
    }

    .assistant-msg {
        background-color: #111827;
        color: #e5e7eb;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
    }

    .title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: white;
    }

    .subtitle {
        text-align: center;
        color: #9ca3af;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🤖 LangGraph AI Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">YOUR PERSONAL CHATBOT</div>', unsafe_allow_html=True)

# ******************************** session setup ********************************************** #

# store all chats (thread_id -> messages)
if "all_chats" not in st.session_state:
    st.session_state["all_chats"] = {}

# UI messages
if "ui_messages" not in st.session_state:
    st.session_state["ui_messages"] = []

# thread list
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

# initialize thread_id
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# ensure thread is tracked
add_thread(st.session_state['thread_id'])

# LangGraph config
config = {"configurable": {"thread_id": st.session_state['thread_id']}}

# *************************************************************************************** #

# sidebar UI
st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

# show all threads
for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(thread_id):
        load_chat(thread_id)

# *************************************************************************************** #

# display chat messages
for msg in st.session_state["ui_messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-msg'>{msg['content']}</div>", unsafe_allow_html=True)

# input box
user_input = st.chat_input("💬 Type your message...")

if user_input:

    # store user message
    st.session_state["ui_messages"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(f"<div class='user-msg'>{user_input}</div>", unsafe_allow_html=True)

    # streaming response
    with st.chat_message("assistant"):

        placeholder = st.empty()
        final_response = ""
        last_response = ""

        for chunk in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="values"
        ):
            if "messages" in chunk:
                msg = chunk["messages"][-1]

                if hasattr(msg, "content") and msg.content:

                    if msg.content.strip() == user_input.strip():
                        continue

                    if msg.content != last_response:
                        final_response = msg.content
                        last_response = msg.content

                        placeholder.markdown(
                            f"<div class='assistant-msg'>{final_response}▌</div>",
                            unsafe_allow_html=True
                        )

        # final render
        placeholder.markdown(
            f"<div class='assistant-msg'>{final_response}</div>",
            unsafe_allow_html=True
        )

    # store assistant message
    st.session_state["ui_messages"].append({
        "role": "assistant",
        "content": final_response
    })

    # save chat per thread
    st.session_state["all_chats"][st.session_state['thread_id']] = st.session_state["ui_messages"]