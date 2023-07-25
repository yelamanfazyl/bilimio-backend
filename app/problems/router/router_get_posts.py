from fastapi import Depends, HTTPException, status, Response
from bson.objectid import ObjectId
import datetime
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


class Post(AppModel):
    id: Any = Field(alias="id")
    title: str
    content: str
    firstname: str
    lastname: str
    created_at: datetime.datetime


class GetDiscussionResponse(AppModel):
    posts: List[Post]


@router.get(
    "/{id}/discussions",
    status_code=status.HTTP_200_OK,
    response_model=GetDiscussionResponse,
)
def get_discussion(
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

    result = svc.discussion_repository.get_discussion_by_problem_id(id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problem does not exist.",
        )

    posts = []
    for post in result["posts"]:
        print(post)
        user = auth_rep.get_user_by_id(post["user_id"])
        firstname = ""
        lastname = ""
        if user is not None:
            firstname = user["firstname"]
            lastname = user["lastname"]

        posts.append(
            Post(
                id=post["id"],
                title=post["title"],
                content=post["content"],
                firstname=firstname,
                lastname=lastname,
                created_at=post["created_at"],
            )
        )

    return GetDiscussionResponse(posts=posts)
