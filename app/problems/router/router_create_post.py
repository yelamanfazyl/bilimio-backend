from fastapi import Depends, HTTPException, status, Response
from bson.objectid import ObjectId
from typing import List
from pydantic import BaseModel
from app.utils import AppModel
from ..service import Service, get_service
from datetime import datetime
from . import router
from app.auth.router.dependencies import parse_jwt_user_data
from app.auth.repository.repository import AuthRepository
from app.config import database


class Answer(AppModel):
    answer: str
    correct: bool = False


class CreatePostRequest(AppModel):
    title: str
    content: str


@router.post("/{id}/discussions", status_code=status.HTTP_201_CREATED)
def create_post(
    id: str,
    response: Response,
    input: CreatePostRequest,
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

    discussion = svc.discussion_repository.get_discussion_by_problem_id(problem_id=id)

    if discussion is None:
        discussion_id = svc.discussion_repository.create_discussion(problem_id=id)
        discussion = svc.discussion_repository.get_discussion_by_id(
            discussion_id=discussion_id
        )
        if discussion is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create discussion.",
            )

    post_id = svc.discussion_repository.create_post(
        discussion_id=str(discussion["_id"]),
        title=input.title,
        content=input.content,
        user_id=user_id,
    )

    if post_id is None or post_id == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create post.",
        )

    return Response(status_code=status.HTTP_201_CREATED)
