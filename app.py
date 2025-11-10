import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st
import matplotlib.pyplot as plt

# -----------------------------
# 1. CONFIGURATION
# -----------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found! Set OPENAI_API_KEY as environment variable.")
    st.stop()

llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o-mini", temperature=0)

# Database connection (use %20 for spaces in DB name)
db_url = "postgresql://postgres:MyPass123@localhost:5432/AI Agent"
engine = create_engine(db_url)

# -----------------------------
# 2. PROMPTS
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
# 3. HELPER FUNCTIONS
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

    # Remove markdown code block if present
    if raw_sql.startswith("```"):
        lines = raw_sql.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_sql = "\n".join(lines)

    # Remove empty lines and comments
    sql_query = "\n".join(
        line for line in raw_sql.splitlines() if line.strip() and not line.strip().startswith("--")
    ).strip()

    # Safety check: allow SELECT or WITH
    if not sql_query:
        raise ValueError("AI returned an empty query.")
    first_word = sql_query.split()[0].lower()
    if first_word not in ("select", "with"):
        raise ValueError(f"Only SELECT queries are allowed for safety! Generated query starts with '{first_word}'")

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
    return explanation

def display_chart(df, question):
    numeric_cols = df.select_dtypes(include='number').columns
    if len(numeric_cols) >= 1:
        x_col = df.columns[0]
        y_col = numeric_cols[0]
        st.write("### 📈 Chart")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(df[x_col].astype(str), df[y_col])
        ax.set_title(question)
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

# -----------------------------
# 4. STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="AI SQL Agent", layout="wide")
st.title("🤖 AI SQL Agent for Your Database")

user_question = st.text_input("Ask a question about your database:")

if st.button("Run Query") and user_question:
    with st.spinner("Generating SQL and fetching results..."):
        try:
            sql_query = generate_sql(user_question)

            # Show raw AI SQL
            st.write("### Raw AI-generated SQL")
            st.code(sql_query, language="sql")

            df_or_error = run_sql(sql_query)
            if isinstance(df_or_error, tuple):
                st.error(f"SQL Execution Error: {df_or_error[1]}")
            else:
                df = df_or_error
                explanation = explain_result(user_question, df)
                st.write("### 🤖 Explanation")
                st.success(explanation)

                if not df.empty:
                    st.write("### 📊 Data Preview")
                    st.dataframe(df)
                    display_chart(df, user_question)

        except Exception as e:
            st.error(f"Error: {str(e)}")
