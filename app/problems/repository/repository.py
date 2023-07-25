from datetime import datetime
from typing import List
from bson.objectid import ObjectId
from pymongo.database import Database
from app.utils import AppModel


class Answer(AppModel):
    answer: str
    correct: bool


class DiscussionRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_discussion(self, problem_id):
        result = self.database["discussions"].insert_one(
            {
                "problem_id": problem_id,
                "created_at": datetime.utcnow(),
            }
        )

        return result.inserted_id

    def get_all_discussions(self):
        result = self.database["discussions"].find()

        return result

    def get_discussion_by_id(self, discussion_id):
        discussion = self.database["discussions"].find_one(
            {
                "_id": ObjectId(discussion_id),
            }
        )

        return discussion

    def get_discussion_by_problem_id(self, problem_id):
        discussion = self.database["discussions"].find_one(
            {
                "problem_id": problem_id,
            }
        )

        return discussion

    def get_post_by_id(self, problem_id, post_id):
        discussion = self.database["discussions"].find_one(
            {
                "problem_id": problem_id,
                "posts": {
                    "$elemMatch": {
                        "id": ObjectId(post_id),
                    }
                },
            }
        )

        if discussion is None:
            return None

        for post in discussion["posts"]:
            if post["id"] == ObjectId(post_id):
                return post

        return None

    def create_post(self, discussion_id, title, content, user_id):
        result = self.database["discussions"].update_one(
            filter={"_id": ObjectId(discussion_id)},
            update={
                "$push": {
                    "posts": {
                        "id": ObjectId(),
                        "title": title,
                        "content": content,
                        "user_id": user_id,
                        "created_at": datetime.utcnow(),
                    }
                }
            },
        )

        return result.modified_count


class SolvedProblemRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_solved_problem(self, user_id, problem_id):
        # check if problem is already solved
        result = self.database["solved_problems"].find_one(
            {"user_id": user_id, "problem_id": str(problem_id)}
        )

        if result is not None:
            return True

        # check if user_id is already in solved_problems
        result = self.database["solved_problems"].find_one(
            {
                "user_id": user_id,
            }
        )

        if result is None:
            result = self.database["solved_problems"].insert_one(
                {"user_id": user_id, "problem_id": [str(problem_id)]}
            )

            if result.inserted_id is None:
                return False

            return True

        result = self.database["solved_problems"].update_one(
            {"user_id": user_id},
            {"$push": {"problem_id": str(problem_id)}},
        )

        if result.modified_count == 0:
            return False

        return True

    def get_solved_problems_by_user_id(self, user_id):
        result = self.database["solved_problems"].find_one({"user_id": user_id})

        if result is None:
            return []

        return result["problem_id"]


class SubmissionRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_submission(self, user_id, problem_id, correct):
        submission = self.get_submission_by_user_id(user_id=user_id)
        i = 1
        if submission is None:
            payload = {
                "user_id": user_id,
                "submissions": {str(datetime.utcnow().strftime("%Y-%m-%d")): i},
            }
            submission = self.database["submissions"].insert_one(payload)

            return submission.inserted_id

        if str(datetime.utcnow().strftime("%Y-%m-%d")) not in submission["submissions"]:
            i = 1
        else:
            i = (
                submission["submissions"][str(datetime.utcnow().strftime("%Y-%m-%d"))]
                + 1
            )

        result = self.database["submissions"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"submissions.{str(datetime.utcnow().strftime('%Y-%m-%d'))}": i,
                }
            },
        )

        return result.modified_count

    def get_submission_by_user_id(self, user_id):
        result = self.database["submissions"].find_one({"user_id": user_id})
        return result


class ProblemRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_problem(
        self,
        title: str,
        description: str,
        user_id: str,
        answer: List[Answer],
        difficulty: str = "easy",
        topic: str = "general",
    ):
        answers = []
        for ans in answer:
            answers.append({"answer": ans.answer, "correct": ans.correct})

        payload = {
            "title": title,
            "description": description,
            "answer": answers,
            "difficulty": difficulty,
            "topic": topic,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
        }

        result = self.database["problems"].insert_one(payload)

        return result.inserted_id

    def delete_problem(self, id):
        result = self.database["problems"].delete_one({"_id": ObjectId(id)})
        return result.deleted_count

    def get_problem_by_id(self, id):
        result = self.database["problems"].find_one({"_id": ObjectId(id)})
        return result

    def get_all_problems(self):
        result = self.database["problems"].find()
        return result

    def update_problem(
        self, id, title, description, user_id, answer, difficulty, topic
    ):
        result = self.database["problems"].update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "title": title,
                    "description": description,
                    "answer": answer,
                    "difficulty": difficulty,
                    "topic": topic,
                    "user_id": user_id,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return result.modified_count

    def get_problem_count_by_difficulty(self, difficulty):
        result = self.database["problems"].count_documents({"difficulty": difficulty})
        return result

    def get_problems_by_topic(self, topic):
        result = self.database["problems"].find({"topic": topic})
        return result
