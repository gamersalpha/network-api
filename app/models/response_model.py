from pydantic import BaseModel
from typing import Optional, Union, Dict, List

class CommandResponse(BaseModel):
    success: bool
    output: Optional[Union[str, Dict, List]] = None 
    error: Optional[str] = None
