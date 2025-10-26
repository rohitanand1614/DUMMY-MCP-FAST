from pydantic import BaseModel, Field
from typing import Optional

class NavigateInput(BaseModel):
    url: str = Field(..., description="URL to open")

class NavigateOutput(BaseModel):
    message: str
    current_url: Optional[str]
