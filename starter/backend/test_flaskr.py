import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format(
            "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertTrue(data["questions"])

    def test_fail_404_get_questions(self):
        res = self.client().get("/questions?page=100")
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)

    # def test_delete_question(self):
    #     res = self.client().delete("/questions/8")
    #     data = json.loads(res.data)
    #     self.assertEqual(data["success"], True)

    def test_fail_404_delete_question(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)

    def test_post_question(self):
        res = self.client().post(
            "/questions",
            json={
                "question": "What is my age ?",
                "category": 2,
                "difficulty": 3,
                "answer": 21,
            },
        )
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)

    def test_fail_post_question(self):
        res = self.client().post(
            "/questions/3",
            json={
                "question": "What is my age ?",
                "category": 2,
                "difficulty": 3,
                "answer": 21,
            },
        )
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)

    def test_get_questions_by_cat(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_fail_get_questions_by_cat(self):
        res = self.client().get("/categories/8/questions")
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)

    def test_play(self):
        res = self.client().post(
            "/quizzes",
            json={"previous_questions": [], "quiz_category": 0},
        )
        data = json.loads(res.data)
        self.assertTrue(data["question"])

    def test_play(self):
        res = self.client().post(
            "/quizzes/1",
            json={"previous_questions": [], "quiz_category": 0},
        )
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()