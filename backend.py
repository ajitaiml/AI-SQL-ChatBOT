import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OpenAI API key not found! Set OPENAI_API_KEY as environment variable.")

llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o-mini", temperature=0)

# Main DB (Postgres to query)
db_url = "postgresql://postgres:MyPass123@localhost:5432/AI Agent"
engine = create_engine(db_url)

# Chat history DB
CHAT_DB = "database.db"

# -----------------------------
# PROMPTS
# -----------------------------
sql_prompt = PromptTemplate.from_template("""
You are a helpful assistant that converts natural language into SQL queries.

Database dialect: {dialect}
Tables and columns available: {columns}

User Question: {question}

Return ONLY the SQL query, nothing else. Only generate SELECT queries. Do NOT generate INSERT, UPDATE, DELETE, DROP, or any destructive commands.
""")

explain_prompt = PromptTemplate.from_template("""
You are an assistant. The user asked: {question}
The SQL result is:

{result}

Explain this in plain English, short and clear.
""")

# -----------------------------
# CHAT STORAGE
# -----------------------------
def init_chat_db():
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT, -- 'user' or 'assistant'
        content TEXT,
        sql_query TEXT,
        result_preview TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)
    
    conn.commit()
    conn.close()

def create_session(title="New Chat"):
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (title) VALUES (?)", (title,))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def list_sessions():
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at FROM sessions ORDER BY created_at DESC")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def save_message(session_id, role, content, sql_query=None, result_preview=None):
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO messages (session_id, role, content, sql_query, result_preview)
    VALUES (?, ?, ?, ?, ?)
    """, (session_id, role, content, sql_query, result_preview))
    conn.commit()
    conn.close()

def load_messages(session_id):
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT role, content, sql_query, result_preview, timestamp
    FROM messages WHERE session_id=? ORDER BY id
    """, (session_id,))
    msgs = cursor.fetchall()
    conn.close()
    return msgs

# -----------------------------
# BACKEND FUNCTIONS
# -----------------------------
def get_tables_and_columns():
    inspector = inspect(engine)
    info = {}
    for table in inspector.get_table_names():
        info[table] = [col['name'] for col in inspector.get_columns(table)]
    return info

def generate_sql(question):
    tables_columns = get_tables_and_columns()
    dialect = engine.dialect.name
    raw_sql = llm.invoke(
        sql_prompt.format(dialect=dialect, columns=tables_columns, question=question)
    ).content

    if raw_sql.startswith("```"):
        lines = raw_sql.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_sql = "\n".join(lines)

    sql_query = "\n".join(
        line for line in raw_sql.splitlines() if line.strip() and not line.strip().startswith("--")
    ).strip()

    if not sql_query:
        raise ValueError("AI returned an empty query.")
    if sql_query.split()[0].lower() not in ("select", "with"):
        raise ValueError(f"Only SELECT queries allowed! Got: {sql_query[:20]}...")

    return sql_query

def run_sql(sql_query):
    try:
        df = pd.read_sql(text(sql_query), engine)
        return df
    except Exception as e:
        return None, str(e)

def explain_result(question, df):
    result_str = df.head(10).to_string(index=False) if not df.empty else "No rows returned."
    explanation = llm.invoke(
        explain_prompt.format(question=question, result=result_str)
    ).content
    return explanation, result_str

def rename_session(session_id, new_title):
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET title=? WHERE id=?", (new_title, session_id))
    conn.commit()
    conn.close()
    
def delete_session(session_id):
    conn = sqlite3.connect(CHAT_DB)
    cursor = conn.cursor()
    # Delete messages first
    cursor.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    # Delete session
    cursor.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()
 
 
