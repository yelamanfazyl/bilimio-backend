from fastapi import Depends, HTTPException, status, Response
from bson.objectid import ObjectId
import random
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


class GptProblemRequest(AppModel):
    topic: str


class GptProblemResponse(AppModel):
    description: str
    answer: List[dict[str, str]]


@router.post("gpt/", status_code=status.HTTP_200_OK, response_model=GptProblemResponse)
def get_problem_gpt(
    input: GptProblemRequest,
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

    problems = svc.repository.get_all_problems()
    topics = []
    for problem in problems:
        if problem["topic"] not in topics:
            topics.append(problem["topic"])

    if input.topic not in topics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic does not exist.",
        )

    problems = svc.repository.get_problems_by_topic(input.topic)
    problems = list(problems)
    three_random_problems = []
    for i in range(3):
        random_problem = problems[random.randint(0, len(problems) - 1)]
        three_random_problems.append(random_problem)

    result = svc.gpt_service.get_response(three_random_problems)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problem does not exist.",
        )

    return GptProblemResponse(**result)
