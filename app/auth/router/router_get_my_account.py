from typing import Any, List

from fastapi import Depends, HTTPException, Response
from pydantic import Field

from app.utils import AppModel

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router
from .dependencies import parse_jwt_user_data


class Problem(AppModel):
    id: Any = Field(alias="_id")
    title: str


class GetMyAccountResponse(AppModel):
    firstname: str
    lastname: str
    city: str
    country: str
    school: str
    date_of_birth: str
    problems: List[Problem]
    easy: int
    medium: int
    hard: int
    easy_total: int
    medium_total: int
    hard_total: int
    submissions: dict[str, int]


@router.get("/user/", summary="User Information", response_model=GetMyAccountResponse)
def get_my_account(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    print("LOH")
    user = svc.repository.get_user_by_id(jwt_data.user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    problems = svc.solved_repo.get_solved_problems_by_user_id(jwt_data.user_id)

    if problems is None:
        return Response(status_code=404)

    last_10_problems = problems[-10:]

    easy = 0
    medium = 0
    hard = 0

    for prob in problems:
        problem = svc.problem_repo.get_problem_by_id(prob)
        if problem is None:
            continue

        if problem["difficulty"] == "easy":
            easy += 1
        elif problem["difficulty"] == "medium":
            medium += 1
        elif problem["difficulty"] == "hard":
            hard += 1

    problems = []

    for problem in last_10_problems:
        pro = svc.problem_repo.get_problem_by_id(id=problem)
        if pro is None:
            continue
        prob = Problem(id=pro["_id"], title=pro["title"])
        problems.append(prob)

    easy_total = svc.problem_repo.get_problem_count_by_difficulty("easy")
    medium_total = svc.problem_repo.get_problem_count_by_difficulty("medium")
    hard_total = svc.problem_repo.get_problem_count_by_difficulty("hard")

    submissions = svc.sub_repo.get_submission_by_user_id(jwt_data.user_id)

    if submissions is None:
        submissions = {}
        submissions["submissions"] = []

    return GetMyAccountResponse(
        firstname=user["firstname"],
        lastname=user["lastname"],
        city=user["city"],
        country=user["country"],
        school=user["school"],
        date_of_birth=user["date_of_birth"],
        problems=problems,
        easy=easy,
        medium=medium,
        hard=hard,
        easy_total=easy_total,
        medium_total=medium_total,
        hard_total=hard_total,
        submissions=submissions["submissions"],
    )
