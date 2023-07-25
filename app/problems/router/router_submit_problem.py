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


class SubmitProblemRequest(AppModel):
    correct: bool


@router.post("/{id}/submit", status_code=status.HTTP_200_OK)
def submit_problem(
    response: Response,
    input: SubmitProblemRequest,
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

    result = svc.sub_repository.create_submission(
        user_id=user_id, problem_id=id, correct=input.correct
    )

    if result is None or result == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission failed.",
        )

    if input.correct:
        print('log')
        result = svc.solve_repository.create_solved_problem(
            user_id=user_id, problem_id=id
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solved problem failed.",
            )

    return Response(status_code=status.HTTP_200_OK)
