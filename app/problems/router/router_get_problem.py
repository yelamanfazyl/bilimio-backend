from fastapi import Depends, HTTPException, status, Response
from bson.objectid import ObjectId
from typing import List
from pydantic import BaseModel
from app.utils import AppModel
from ..service import Service, get_service
from . import router
from app.auth.router.dependencies import parse_jwt_user_data
from app.auth.repository.repository import AuthRepository
from app.config import database
from typing import Any, List
from pydantic import Field


class GetProblemResponse(AppModel):
    id: Any = Field(alias="_id")
    title: str
    description: str
    answer: List[dict[str, str]]
    difficulty: str
    topic: str = ""
    user_id: str


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=GetProblemResponse)
def get_problem(
    response: Response,
    id: str,
    jwt_data=Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    user_id = jwt_data.user_id
    auth_rep = AuthRepository(database=database)
    user = auth_rep.get_user_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist.",
        )

    result = svc.repository.get_problem_by_id(id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problem does not exist.",
        )

    return GetProblemResponse(**result)
