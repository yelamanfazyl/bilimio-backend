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


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_problem(
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

    if not user["admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not admin.",
        )

    result = svc.repository.delete_problem(id)

    if result is None or result == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problem does not exist.",
        )

    return Response(status_code=status.HTTP_200_OK)
