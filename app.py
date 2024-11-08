import streamlit as st
import shelve
import google.generativeai as genai

# Configure the Gemini API with your API key

genai.configure(api_key="AIzaSyCTtah3iahaJ6-TirG8Zapn_KE6sqSwamc")

# Inject CSS into the app
st.markdown(
    """
    <style>
    /* Global styles */
    body {
        font-family: 'Arial', sans-serif;
    }

    /* Center align the title */
    .title {
        text-align: center;
        color: #6600cc; /* A nice purple color */
        font-size: 60px; /* Larger font size */
        margin-top: 20px;
        margin-bottom: 60px; /* Space below the title */
    }

    /* Style the sidebar */
    .css-1aumxhk {
        background-color: #f0f4f8 !important; /* Light sidebar background */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Style buttons */
    .stButton > button {
        background-color: #6600cc; /* purple background for buttons */
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .stButton > button:hover {
        color: white;
        background-color: green; /* light pruple on hover */
        border-style: solid;
        border-color: black;
    }

    /* Style the chat message bubbles */
    .user-message {
        background-color: #d1e7dd; /* Light green for user messages */
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }

    .assistant-message {
        background-color:  #e6ccff; /* Light purple for assistant messages */
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }

    /* Style the instructions in the sidebar */
    .sidebar-instructions {
        font-size: 14px;
        color: #555;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Apply the CSS class to the Title
st.markdown("<h1 class='title'>AI SideKick UI</h1>", unsafe_allow_html=True)

# Profession and Field selection below title
col1, col2 = st.columns(2)

# Dropdown to select a profession
with col1:
    profession = st.selectbox("Select your Profession", ["Student", "Teacher", "Engineer", "Entrepreneur", "Other"])
    st.session_state["profession"] = profession

# Dropdown to select a field
with col2:
    field = st.selectbox("Select your Field", ["Technology", "Finance", "Education", "Business", "Science", "Other"])
    st.session_state["field"] = field

# Button to reset profession and field
if st.button("Reset Profession and Field"):
    st.session_state["profession"] = "Select your Profession"
    st.session_state["field"] = "Select your Field"

# User and bot avatars
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    message_class = "user-message" if message["role"] == "user" else "assistant-message"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(f"<div class='{message_class}'>{message['content']}</div>", unsafe_allow_html=True)

# Create a custom chat input label based on selected profession and field
chat_label = f"Ask something related to {st.session_state.get('profession', 'your profession')} in {st.session_state.get('field', 'your field')}"

# Main chat interface
if prompt := st.chat_input(chat_label):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(f"<div class='user-message'>{prompt}</div>", unsafe_allow_html=True)

    # Generate response from the Gemini API based on profession and field
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""

        # Customize prompt with selected profession and field
        customized_prompt = f"As a {st.session_state['profession']} in {st.session_state['field']}, {prompt}"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(customized_prompt)  # Use user input to generate response
            full_response = response.text  # Extract the generated text from the response

        except Exception as e:
            full_response = f"Error: {e}"

        # Display the response
        message_placeholder.markdown(f"<div class='assistant-message'>{full_response}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)

# Sidebar instructions
st.sidebar.title("Welcome to AI SideKick!")
st.sidebar.markdown("AI SideKick is an online learning tool that provides personalized answers. Simply choose your profession and field, ask questions, and get instant help to your needs!")
st.sidebar.markdown("""
### Getting Started:
1. Select your profession and field below the main title.
2. Enter your question or message in the chat box below.
3. AI SideKick will respond based on your profession and field.
4. If your options are not available then choose other.
5. Clear chat history by clicking the button in the sidebar.
6. Reset profession and field by clicking 'Reset Profession and Field' below the title.
""", unsafe_allow_html=True)