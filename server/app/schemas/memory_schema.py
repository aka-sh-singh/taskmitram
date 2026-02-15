from pydantic import BaseModel, Field

class MemorySaveDecision(BaseModel):
    should_save: bool = Field(description="Whether the information is informative enough to be stored in long-term memory.")
    extracted_information: str = Field(description="The key information extracted from the conversation to be saved.")
    category: str = Field(description="Category of the information (e.g., preference, task, contact, project_detail).")
