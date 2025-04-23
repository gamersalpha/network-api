from pydantic import BaseModel
from typing import Optional, Union, Dict, List

class CommandResponse(BaseModel):
    success: bool
    output: Union[str, Dict, List]
    error: Optional[str] = None
