class AgentCard:
    def __init__(self, name, supported_messages, capabilities, version="1.0"):
        self.name = name
        self.supported_messages = supported_messages
        self.capabilities = capabilities
        self.version = version

    def to_dict(self):
        return {
            "name": self.name,
            "supported_messages": self.supported_messages,
            "capabilities": self.capabilities,
            "version": self.version
        }

    def can_handle(self, message_type: str) -> bool:
        return message_type in self.supported_messages