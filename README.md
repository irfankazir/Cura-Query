# Cura Query — A2A Text-to-SQL Demo

Cura Query is a Streamlit demonstration of a multi-agent workflow that turns a natural-language question into a SQL `SELECT` query and displays the result from a local SQLite database.

> **Demo and privacy note:** This repository intentionally excludes the original database files. The included generator creates a small database with fictional sample records. Do not use real patient information or connect this demo to a production healthcare database.

## Features

- Streamlit interface for natural-language questions
- Text-to-SQL generation using a Hugging Face Transformers sequence-to-sequence model
- Lightweight agent messaging and registry modules
- SQLite query execution with read-only restrictions and a 100-row result cap
- Synthetic database generator for local experimentation

## Architecture

1. `Main_Bot.py` receives a question from the user.
2. `Text_to_Sql_Agent.py` generates a SQL query and explanation.
3. `MCP_Protocol.py` dispatches messages to the registered agents.
4. `SQL_execution_agent.py` validates and executes a read-only query against SQLite.
5. Streamlit displays the generated query and result table.

## Requirements

- Python 3.10 or newer (a compatible PyTorch build is required for your platform)
- Internet access on first run to download the configured Hugging Face model, unless it is already cached

## Run locally

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and create the synthetic database:

```bash
python -m pip install -r requirements.txt
python create_sample_db.py
streamlit run Main_Bot.py
```

The first launch may take time while the model downloads. Model availability and generated SQL quality may vary. Review every generated query before using it for anything beyond this demo.

## Example questions

- How many patients are in Chennai?
- Show patients diagnosed with asthma.
- List patients aged 45.

The model may not generate a correct query for every question. This is a learning prototype, not a clinical tool.

## Safety limitations

- Only one `SELECT` statement is accepted by the SQL execution agent; SQLite write and schema-changing actions are denied.
- The demo uses fictional records and should not be connected to production or personal data.
- Generated SQL is not guaranteed to be semantically correct. Validate outputs before relying on them.
- The configured model is `tscholak/cxmefzzi`; change it in `Text_to_Sql_Agent.py` only after checking model compatibility and licensing.

## Project structure

```text
Cura-Query/
├── Main_Bot.py
├── Text_to_Sql_Agent.py
├── SQL_execution_agent.py
├── MCP_Protocol.py
├── agent_card.py
├── agent_registry.py
├── create_sample_db.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Credits and ownership

Add your internship/team acknowledgements here as appropriate. Publish this source only if you have permission from the relevant project owner and your internship agreement allows it.
