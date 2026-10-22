AGENT_REGISTRY = {}

def register_agent(agent_instance):
    card = agent_instance.card
    AGENT_REGISTRY[card.name] = card.to_dict()

def get_agent_card(name):
    return AGENT_REGISTRY.get(name)