from pydantic import BaseSettings

from app.config import database
from .repository.repository import (
    ProblemRepository,
    SubmissionRepository,
    SolvedProblemRepository,
    DiscussionRepository,
)

from .adapters.gpt_service import GPTService


class Service:
    def __init__(
        self,
        repository: ProblemRepository,
        sub_repository: SubmissionRepository,
        solve_repository: SolvedProblemRepository,
        discussion_repository: DiscussionRepository,
        gpt_service: GPTService,
    ):
        self.repository = repository
        self.sub_repository = sub_repository
        self.solve_repository = solve_repository
        self.discussion_repository = discussion_repository
        self.gpt_service = gpt_service


def get_service():
    repository = ProblemRepository(database)
    sub_repository = SubmissionRepository(database)
    solve_repository = SolvedProblemRepository(database)
    discussion_repository = DiscussionRepository(database)
    gpt_service = GPTService()
    svc = Service(
        repository, sub_repository, solve_repository, discussion_repository, gpt_service
    )
    return svc
