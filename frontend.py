import streamlit as st
import matplotlib.pyplot as plt
from backend import init_chat_db, create_session, list_sessions, save_message, load_messages, rename_session,delete_session
from backend import generate_sql, run_sql, explain_result

# -----------------------------
# INIT
# -----------------------------
st.set_page_config(page_title="AI SQL Agent Chat", layout="wide")
init_chat_db()

if "active_session" not in st.session_state:
    st.session_state.active_session = None
if "rename_session_id" not in st.session_state:
    st.session_state.rename_session_id = None

st.title("💬 AI SQL Agent Chat")

# -----------------------------
# SIDEBAR: Session Manager
# -----------------------------
st.sidebar.header("💾 Conversations")

sessions = list_sessions()
if st.sidebar.button("➕ New Chat"):
    sid = create_session("New Chat")
    st.session_state.active_session = sid
    st.rerun()

for sid, title, created in sessions:
    # Rename mode
    if st.session_state.rename_session_id == sid:
        new_name = st.sidebar.text_input("Rename chat:", value=title, key=f"rename_{sid}")
        if st.sidebar.button("💾 Save", key=f"save_{sid}"):
            rename_session(sid, new_name)
            st.session_state.rename_session_id = None
            st.rerun()
        if st.sidebar.button("❌ Cancel", key=f"cancel_{sid}"):
            st.session_state.rename_session_id = None
            st.rerun()
    else:
        cols = st.sidebar.columns([0.7, 0.15, 0.15])
        if cols[0].button(title, key=f"session_{sid}"):
            st.session_state.active_session = sid
            st.rerun()
        if cols[1].button("✏️", key=f"rename_btn_{sid}"):
            st.session_state.rename_session_id = sid
            st.rerun()
        if cols[2].button("🗑️", key=f"delete_btn_{sid}"):
            delete_session(sid)
            # Clear active session if deleted
            if st.session_state.active_session == sid:
                st.session_state.active_session = None
            st.rerun()

# -----------------------------
# CHAT INTERFACE
# -----------------------------
if st.session_state.active_session:
    messages = load_messages(st.session_state.active_session)
    
    for role, content, sql, preview, ts in messages:
        if role == "user":
            st.chat_message("user").write(content)
        else:
            st.chat_message("assistant").write(content)
            if preview:
                st.text(preview)

    # Input box
    user_question = st.chat_input("Ask a question about your database:")
    if user_question:
        st.chat_message("user").write(user_question)
        save_message(st.session_state.active_session, "user", user_question)

        with st.spinner("🤖 Thinking..."):
            try:
                sql_query = generate_sql(user_question)
                df_or_error = run_sql(sql_query)

                if isinstance(df_or_error, tuple):  # Error
                    st.error(f"SQL Error: {df_or_error[1]}")
                else:
                    df = df_or_error
                    explanation, preview = explain_result(user_question, df)

                    st.chat_message("assistant").write(explanation)
                    st.write("### 📊 Data Preview")
                    st.dataframe(df)

                    save_message(st.session_state.active_session, "assistant", explanation, sql_query, preview)

                    # Chart
                    if not df.empty:
                        numeric_cols = df.select_dtypes(include='number').columns
                        if len(numeric_cols) >= 1:
                            x_col = df.columns[0]
                            y_col = numeric_cols[0]
                            fig, ax = plt.subplots(figsize=(8, 5))
                            ax.bar(df[x_col].astype(str), df[y_col])
                            ax.set_title(user_question)
                            ax.tick_params(axis='x', rotation=45)
                            st.pyplot(fig)

            except Exception as e:
                st.error(f"Error: {str(e)}")

else:
    st.info("👉 Select a chat session from the sidebar or create a new one.")
