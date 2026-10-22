import sqlite3
from agent_card import AgentCard
from MCP_Protocol import MCPMessageType


class SQLExecutionAgent:
    """Read-only SQLite query agent for the Cura Query demo."""

    def __init__(self, db_path="hospital_patients.db", check_same_thread=False):
        self.conn = sqlite3.connect(db_path, check_same_thread=check_same_thread)
        self.conn.row_factory = sqlite3.Row
        self.card = AgentCard(
            name="SQLExecutionAgent",
            supported_messages=[MCPMessageType.QUERY_REQUEST.name],
            capabilities=["execute_read_only_sql"],
            version="1.0",
        )
        # Defense in depth: SQLite itself denies writes and schema changes.
        denied_actions = {
            sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE,
            sqlite3.SQLITE_ALTER_TABLE, sqlite3.SQLITE_DROP_TABLE,
            sqlite3.SQLITE_DROP_INDEX, sqlite3.SQLITE_CREATE_TABLE,
            sqlite3.SQLITE_CREATE_INDEX, sqlite3.SQLITE_ATTACH,
            sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA,
        }
        def authorizer(action, arg1, arg2, database, trigger):
            if action in denied_actions:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        self.conn.set_authorizer(authorizer)

    @staticmethod
    def _validate_query(sql_query):
        query = sql_query.strip()
        if not query:
            raise ValueError("The generated SQL query is empty.")
        # Permit one SELECT statement only. Semicolons inside quoted strings
        # are not expected from this demo's model output, so reject multiple statements.
        if not query[:6].lower() == "select":
            raise ValueError("Only SELECT queries are allowed.")
        trimmed = query.rstrip(";").strip()
        if ";" in trimmed:
            raise ValueError("Only one SQL statement is allowed.")
        return trimmed

    def execute_sql(self, sql_query):
        try:
            query = self._validate_query(sql_query)
            cursor = self.conn.execute(query)
            rows = cursor.fetchmany(100)
            columns = [item[0] for item in cursor.description or []]
            return [dict(zip(columns, tuple(row))) for row in rows]
        except Exception as exc:
            return str(exc)

    def handle_message(self, message):
        if message.get("type") != MCPMessageType.QUERY_REQUEST.name:
            raise ValueError("Unsupported message type")
        content = message.get("content", {})
        raw_query = content.get("sql_query", "")
        result = self.execute_sql(raw_query)
        response_content = {
            "original_query": content.get("original_query"),
            "sql_query": raw_query,
        }
        if isinstance(result, str):
            response_content["error"] = result
        else:
            response_content["result"] = result
        return {
            "sender": self.card.name,
            "receiver": message.get("sender"),
            "type": MCPMessageType.QUERY_RESULT.name,
            "content": response_content,
        }

    def close(self):
        self.conn.close()
