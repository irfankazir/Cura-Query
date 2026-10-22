from enum import Enum

class MCPMessageType(Enum):
    QUERY_REQUEST = "QUERY_REQUEST"
    QUERY_RESULT = "QUERY_RESULT"
    EXECUTE_SQL = "EXECUTE_SQL"  

class MCProtocol:
    @staticmethod
    def create_message(sender, receiver, message_type, content):
        msg_type = message_type.value if isinstance(message_type, MCPMessageType) else message_type
        return {
            "sender": sender,
            "receiver": receiver,
            "type": msg_type,
            "content": content
        }

    @staticmethod
    def dispatch(message, agents):
        receiver = message["receiver"]
        if receiver not in agents:
            raise Exception(f"Agent '{receiver}' not found.")
        agent = agents[receiver]

        if not hasattr(agent, "card") or not agent.card.supported_messages:
            raise Exception(f"Agent '{receiver}' has no card or supported messages info.")

        if message["type"] not in agent.card.supported_messages:
            raise Exception(f"Agent '{receiver}' cannot handle message type '{message['type']}'.")

        return agent.handle_message(message)
