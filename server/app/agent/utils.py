from langchain_core.messages import HumanMessage, AIMessage

def to_langchain_messages(db_messages):
    lc_messages = []
    for msg in db_messages:
        if msg.sender == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.sender == "agent":
            lc_messages.append(AIMessage(content=msg.content))
    return lc_messages
