from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")

prompt = PromptTemplate(
    input_variables=["message"],
    template=(
        "You are a helpful assistant that generates short, catchy titles for chat conversations.\n"
        "Generate a 3-5 word title based on this first message:\n\n"
        "{message}\n\n"
        "Guidelines:\n"
        "- DO NOT use any quotation marks.\n"
        "- Be specific to the unique details of the message (avoid generic titles like 'Retrieve Email' if there's a specific person or topic).\n"
        "- Return ONLY the title text."
    )
)

def generate_title(message: str) -> str:
    chain = prompt | llm
    response = chain.invoke({"message": message})
    title = response.content.strip()
    # Post-process to remove any unwanted quotes just in case
    title = title.replace('"', '').replace("'", "")
    return title


