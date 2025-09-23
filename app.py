import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(page_title="Heavenly DelusionZ", page_icon="💬", layout="wide")

from database import init_db, create_new_session, get_sessions, rename_session, delete_session, save_chat, load_chat_history
from auth import show_auth_page
from chatbot import get_response

# Initialize database
init_db()


st.sidebar.image("img/logo.png", width=200)  # Sidebar Logo
st.title("Heavenly DelusionZ - AI Mental Health Companion")

# Initialize chat message history in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# **Login/Register System**
show_auth_page()

# **Handle Chat Sessions**
if "authenticated" in st.session_state and st.session_state["authenticated"]:
    username = st.session_state["username"]  

    # **Page Navigation**
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📱 Navigation")
    page = st.sidebar.radio(
        "Select Page:",
        ["💬 Chat", "📊 Analytics"],
        key="page_navigation"
    )
    
    # Show appropriate page based on selection
    if page == "📊 Analytics":
        from analytics_page import show_analytics_page
        show_analytics_page()
    else:
        # Continue with chat interface if "💬 Chat" is selected

        # **Sidebar Section**
        st.sidebar.title(f"💬 {username}'s Chat Sessions")  

        # **Persona Selection**
        st.sidebar.markdown("### 🧠 Choose Your AI Persona")
        persona_options = {
            "Heavenly DelusionZ Counselor": "The balanced and supportive AI that provides empathetic yet structured mental health support.",
            "Compassionate Listener": "A deeply empathetic AI that focuses on active listening and validation.",
            "Motivational Coach": "A high-energy AI that encourages and empowers users to take action for self-improvement.",
            "CBT Guide": "A rational AI that helps reframe negative thoughts using cognitive behavioral techniques."
        }

        selected_persona = st.sidebar.selectbox("Select a Persona:", list(persona_options.keys()), key="persona_select")
        st.session_state["selected_persona"] = selected_persona  
        st.sidebar.markdown(f"📝 *{persona_options[selected_persona]}*")

        # Fetch user chat sessions
        user_sessions = get_sessions(username)

        # Clear selected session when changing sessions
        if "prev_session" not in st.session_state:
            st.session_state["prev_session"] = None
            st.session_state["selected_session"] = None

        # Display available chat sessions
        session_options = {session_name: session_id for session_id, session_name in user_sessions}
        selected_session_name = st.sidebar.radio("Select a chat:", list(session_options.keys()), key="session_select", index=None)

        # Update selected session when user clicks
        if selected_session_name:
            session_id = session_options[selected_session_name]
            if st.session_state["prev_session"] != session_id:
                st.session_state["selected_session"] = session_id
                st.session_state["prev_session"] = session_id
                st.session_state.messages = []  # Clear messages when switching chats
                st.rerun()

        # **New Chat Button**
        if st.sidebar.button("🆕 New Chat"):
            new_session_id, new_session_name = create_new_session(username)
            if new_session_id:
                st.session_state["selected_session"] = new_session_id
                st.session_state["prev_session"] = new_session_id
                st.session_state.messages = []  # Clear messages for new chat
                st.rerun()

        # Rename session
        new_name = st.sidebar.text_input("Rename chat:", selected_session_name if selected_session_name else "")
        if st.sidebar.button("Rename") and selected_session_name:
            rename_session(st.session_state["selected_session"], new_name)
            st.rerun()

        # Delete session
        if st.sidebar.button("🗑️ Delete Chat") and selected_session_name:
            delete_session(st.session_state["selected_session"])
            st.session_state["selected_session"] = None
            st.session_state["prev_session"] = None
            st.session_state.messages = []  # Clear messages after deletion
            st.rerun()

        # **Display Chat Interface OR Welcome Message**
        if st.session_state["selected_session"]:
            chat_container = st.container()
            
            with chat_container:
                st.write(f"💬 Chat Session: **{selected_session_name}**")
                st.write(f"🧠 AI Persona: **{st.session_state['selected_persona']}**")  # Show selected persona
                
                # Load chat history if messages list is empty
                if not st.session_state.messages:
                    chat_history = load_chat_history(st.session_state["selected_session"])
                    # Add chat history to session state
                    for message, response in chat_history:
                        st.session_state.messages.append({"role": "user", "content": message})
                        st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display all messages from session state
                messages_container = st.container()
                with messages_container:
                    for message in st.session_state.messages:
                        if message["role"] == "user":
                            st.chat_message("user", avatar="🌸").write(message["content"])
                        else:
                            st.chat_message("assistant", avatar="🤖").write(message["content"])
                
            # User input - place outside the container to prevent rerunning
            user_input = st.chat_input("Type your message here...")
            
            if user_input:
                # Add user message to session state immediately
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Display the updated messages including the new user message
                with messages_container:
                    for message in st.session_state.messages:
                        if message["role"] == "user":
                            st.chat_message("user", avatar="🌸").write(message["content"])
                        else:
                            st.chat_message("assistant", avatar="🤖").write(message["content"])
                
                # Show a spinner while waiting for the AI response
                with st.spinner("AI is thinking..."):
                    # Get AI response
                    response = get_response(username, user_input, st.session_state["selected_persona"])
                    
                    # Add AI response to session state
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Save conversation to database
                    save_chat(st.session_state["selected_session"], username, user_input, response)
                
                # Rerun to display the complete conversation including the new response
                st.rerun()

        else:
            welcome_container = st.container()
            with welcome_container:
                st.markdown(f"### 👋 Welcome, {username}!")
                st.markdown("Select an existing chat from the left panel or start a **new chat** to begin.")

        # **Logout Button at Bottom of Sidebar**
        st.sidebar.markdown("---")  
        if st.sidebar.button("🚪 Log Out", key="logout_button"):
            st.session_state.clear()  
            st.rerun()

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
        /* General responsive improvements */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Make sidebar logo responsive */
        [data-testid="stSidebar"] img {
            max-width: 80%;
            height: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

        /* Media query for mobile devices */
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            h1 {
                font-size: 1.8rem !important;
            }

            [data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
                padding-top: 1.5rem;
            }
        }
    </style>
""", unsafe_allow_html=True)
