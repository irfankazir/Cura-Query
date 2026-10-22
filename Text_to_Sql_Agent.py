import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from agent_card import AgentCard
from MCP_Protocol import MCPMessageType  


class TextToSQLAgent:
    def __init__(self, model_name="tscholak/cxmefzzi", device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device).eval()

        self.card = AgentCard(
            name="TextToSQLAgent",
            supported_messages=[MCPMessageType.QUERY_REQUEST.name],
            capabilities=["generate_sql"],
            version="1.0"
        )

    def generate_sql(self, user_query):

        schema = (
    "You are a text-to-SQL assistant. Use only the table `patients`.\n"
    "The table has these columns: patient_id, name, age, gender, blood_group, city, email, "
    "admission_date, diagnosis, treatment, discharge_date, doctor_assigned, bill_amount, contact_number, medical_history.\n\n"
    "Rules:\n"
    "- Only write SQL SELECT queries.\n"
    "- Do NOT use JOINs.\n"
    "- Do NOT use table aliases (e.g., t1, p).\n"
    "- Do NOT invent or assume column names.\n"
    "- Match user terms directly to column names.\n"
    "- Use exact matching in WHERE clauses.\n"
    "- Use LIMIT 5 at the end of every query unless the user explicitly asks for more rows.\n"
    "- Example mappings:\n"
    "   • 'patients in Chennai' → city = 'Chennai'\n"
    "   • 'diagnosed with malaria' → diagnosis = 'malaria'\n"
    "   • 'treated by Dr. Kumar' → doctor_assigned = 'Dr. Kumar'\n"
    "   • 'all male patients' → gender = 'Male'\n"
    "   • 'patients aged 45' → age = 45\n"
    "- If no filter is given, use: SELECT * FROM patients LIMIT 5;\n"
    "- Always end the query with LIMIT 5 unless otherwise stated.\n"
    "- Output ONLY a valid SQLite SELECT query. No extra text, no aliases, no joins.\n"
    "- If no WHERE condition is needed, use: SELECT * FROM patients LIMIT 5;\n"
    "- Only match city if it is clearly stated. Do not substitute or guess city names.\n"
)

        prompt = f"{schema}\nUser request: {user_query}\nSQL query:"


        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self.device)

        outputs = self.model.generate(
            **inputs, max_length=128, num_beams=4, early_stopping=True
        )

        raw_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        lower_output = raw_output.lower()
        if "sql query:" in lower_output:
            start_idx = lower_output.index("sql query:") + len("sql query:")
            sql_query = raw_output[start_idx:].strip()
        elif "user request:" in lower_output:
            start_idx = lower_output.index("user request:") + len("user request:")
            sql_query = raw_output[start_idx:].strip()
        else:
            sql_query = raw_output.strip()
        
        if "join" in sql_query.lower() or "t1." in sql_query.lower() or " as " in sql_query.lower():
            sql_query = "SELECT * FROM patients WHERE 1=0 -- Invalid SQL generated (contained JOIN or alias)"


        sql_query = sql_query.strip(' "\'')

        if sql_query.count('"') % 2 != 0:
            sql_query += '"'
        if sql_query.count("'") % 2 != 0:
            sql_query += "'"
        sql_query = sql_query.replace("join table", "")
        sql_query = sql_query.replace("join SQL", "")
        sql_query = sql_query.replace("JOIN SQL", "")
        sql_query = sql_query.replace("JOIN Table", "")
        sql_query = sql_query.replace("JOIN table", "")
        sql_query = re.sub(r"= ['\"]?(\w+)%['\"]?", r"LIKE '%\1%'", sql_query)
        sql_query = sql_query.replace("user request:", "").strip()
        sql_query = sql_query.replace("create SQL query", "SELECT *").strip()

        return sql_query



    def explain_sql(self, user_query, sql_query):
        return f"Your query '{user_query}' is translated as: {sql_query}"

    def handle_message(self, message):
        if message["type"] != MCPMessageType.QUERY_REQUEST.name:
            raise Exception(f"Unsupported message type: {message['type']}")

        content = message["content"]
        original_query = content.get("original_query")
        if not original_query:
            raise Exception("No original_query found in message content")

        sql_query = self.generate_sql(original_query)
        explanation = self.explain_sql(original_query, sql_query)

        return {
            "sender": self.card.name,
            "receiver": message["sender"],
            "type": MCPMessageType.QUERY_REQUEST.name,
            "content": {
                "original_query": original_query,
                "sql_query": sql_query,
                "explanation": explanation
            }
        }