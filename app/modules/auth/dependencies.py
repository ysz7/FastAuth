from typing import Annotated

from fastapi import Depends

from app.modules.auth import service
from app.modules.auth.schemas import UserResponse

CurrentUser = Annotated[UserResponse, Depends(service.get_current_user)]
