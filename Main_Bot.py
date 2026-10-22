import streamlit as st
from Text_to_Sql_Agent import TextToSQLAgent
from SQL_execution_agent import SQLExecutionAgent
from agent_registry import register_agent
from MCP_Protocol import MCProtocol, MCPMessageType

st.set_page_config(page_title="A2A Text-to-SQL", layout="centered")

@st.cache_resource
def init_agents():
    text_agent = TextToSQLAgent()
    sql_agent = SQLExecutionAgent(db_path="hospital_patients.db", check_same_thread=False)
    register_agent(text_agent)
    register_agent(sql_agent)
    agents = {
        text_agent.card.name: text_agent,
        sql_agent.card.name: sql_agent
    }
    return text_agent, sql_agent, agents

text_agent, sql_agent, agents = init_agents()

st.title("🩺📊Cura Query")
st.markdown("Enter the details you need to access from your Hospital")

user_query = st.text_input("💬 Ask a Hospital database question:", placeholder="")

if st.button("Run Query") and user_query.strip():
    with st.spinner("Generating SQL and fetching results..."):
        try:
            message_to_text_agent = MCProtocol.create_message(
                sender="StreamlitBot",
                receiver=text_agent.card.name,
                message_type=MCPMessageType.QUERY_REQUEST,
                content={"original_query": user_query}
            )

            reply_from_text_agent = MCProtocol.dispatch(message_to_text_agent, agents)
            sql_query = reply_from_text_agent["content"]["sql_query"]
            explanation = reply_from_text_agent["content"]["explanation"]

            message_to_sql_agent = MCProtocol.create_message(
                sender=text_agent.card.name,
                receiver=sql_agent.card.name,
                message_type=MCPMessageType.QUERY_REQUEST,
                content={
                    "original_query": user_query,
                    "sql_query": sql_query
                }
            )

            reply_from_sql_agent = MCProtocol.dispatch(message_to_sql_agent, agents)
            result_content = reply_from_sql_agent["content"]

            st.subheader("📖 Explanation")
            st.success(explanation)

            st.subheader("📝 SQL Query")
            st.code(sql_query, language="sql")

            st.subheader("📊 Query Results")
            if "error" in result_content:
                st.error(f"❌ Error: {result_content['error']}")
            else:
                results = result_content.get("result", [])
                if results:
                    st.dataframe(results)
                else:
                    st.warning("No records found.")

        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
