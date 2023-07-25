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


class Answer(AppModel):
    answer: str
    correct: bool = False


class UpdateProblemRequest(AppModel):
    title: str
    description: str
    answer: List[Answer]
    difficulty: str = "Easy"
    topic: str = "Math"


@router.patch("/{id}", status_code=status.HTTP_201_CREATED)
def update_problem(
    id: str,
    response: Response,
    input: UpdateProblemRequest,
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

    if not user["admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not admin.",
        )

    result = svc.repository.update_problem(
        id=id,
        title=input.title,
        description=input.description,
        user_id=user_id,
        answer=input.answer,
        difficulty=input.difficulty,
        topic=input.topic,
    )

    if result is None or result == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problem does not exist.",
        )

    return Response(status_code=status.HTTP_201_CREATED)
