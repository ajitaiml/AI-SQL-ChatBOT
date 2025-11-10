💬 SQL ChatBot

🤖 SQL ChatBot is an intelligent assistant built with FastAPI and Streamlit, designed to interact with SQL databases using natural language queries.
It translates user prompts into SQL commands, executes them on the database, and returns human-readable responses — bridging the gap between non-technical users and databases.

🧾 Project Overview

This project implements an AI-powered SQL ChatBot that allows users to query and manage databases through plain English commands.
It combines Natural Language Processing (NLP) and database management for effortless data retrieval and interaction.
💡 Use Cases: Internal Data Query Tool, Business Insights Assistant, Database Query Automation.

🧠 Tech Stack
<table> <tr> <th>Category</th> <th>Tool</th> <th>Usage</th> </tr> <tr> <td><strong>Programming Language</strong></td> <td><img src="https://cdn.worldvectorlogo.com/logos/python-5.svg" alt="Python" width="30"/> <strong>Python</strong></td> <td>Core language for logic, database connectivity, and NLP processing</td> </tr> <tr> <td><strong>Backend Framework</strong></td> <td><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI" width="30"/> <strong>FastAPI</strong></td> <td>Used for handling API requests between frontend and database</td> </tr> <tr> <td><strong>Frontend Framework</strong></td> <td><img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="Streamlit" width="30"/> <strong>Streamlit</strong></td> <td>Provides an interactive UI for users to enter natural language queries</td> </tr> <tr> <td><strong>Database</strong></td> <td><img src="https://upload.wikimedia.org/wikipedia/commons/3/38/SQLite370.svg" alt="SQLite" width="30"/> <strong>SQLite</strong></td> <td>Local lightweight SQL database for executing queries</td> </tr> <tr> <td><strong>Environment Management</strong></td> <td><img src="https://seeklogo.com/images/D/dotenv-logo-04CB0E0DB5-seeklogo.com.png" alt="dotenv" width="30"/> <strong>dotenv</strong></td> <td>Used to manage API keys and environment variables securely</td> </tr> </table>

## 🗂️ Project Structure
├── app.py              # Streamlit frontend
├── backend.py          # FastAPI backend handling SQL operations
├── frontend.py         # Streamlit logic for user interface
├── test_db.py          # Database testing and connection validation
├── database.db         # SQLite database (ignored in .gitignore)
├── sql/                # Folder containing SQL templates
├── .env                # Environment variables (ignored in .gitignore)
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation



🚀 Running the Application

# Clone the repository
git clone https://github.com/ajitaiml/AI-SQL-ChatBot.git
cd AI-SQL-ChatBot

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
uvicorn backend:app --reload

# Start Streamlit frontend
streamlit run app.py

🎯 Key Features

💬 Natural Language to SQL — Query your database using plain English.

🧠 AI-Powered Query Generation — Converts user prompts into accurate SQL statements.

🗃️ SQLite Integration — Lightweight and portable local database management.

🧩 Seamless Frontend-Backend Communication — Built using FastAPI and Streamlit.

🔐 Secure Configuration — API keys and sensitive data handled via .env file.

📄 License

This project is licensed under the GPL-3.0 License.

👤 Author

Ajit Singh
🔗 GitHub Profile
