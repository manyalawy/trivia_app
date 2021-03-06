import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # cors
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # get categories
    @app.route("/categories", methods=["GET"])
    def get_categories():
        cats = Category.query.all()
        formated = [cat.format() for cat in cats]
        return jsonify({"categories": formated})

    # get all questions
    @app.route("/questions", methods=["GET"])
    def get_questions():
        page = request.args.get("page", 1, type=int)
        first = (page - 1) * QUESTIONS_PER_PAGE
        last = first + QUESTIONS_PER_PAGE
        cats = Category.query.all()
        cats = [cat.format() for cat in cats]

        questions = Question.query.all()
        formated = [question.format() for question in questions]
        questions = formated[first:last]
        if len(questions) == 0:
            return abort(404)
        return jsonify(
            {
                "questions": questions,
                "categories": cats,
                "totalQuestions": len(formated),
            }
        )

    # delete question by id
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(id == question_id).one_or_none()
            if question is None:
                abort(404)
            else:
                question.delete()
                db.session.commit()
            return jsonify({"success": True, "msg": "question is deleted"})
        except Exception as e:
            print(e)
            abort(500)

    # add question to the database
    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()

        question = body.get("question")
        answer = body.get("answer")
        category = body.get("category")
        difficulty = body.get("difficulty")

        new_question = Question(
            question=question, answer=answer,
            difficulty=difficulty, category=category
        )
        try:
            db.session.add(new_question)
            db.session.commit()
            return jsonify({"msg": "Item added", "success": True})
        except Exception as e:
            print(e)
            abort(500)

    # search for specific question
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        search_string = body.get("search_string")
        try:
            allqs = Question.query.all()
            questions = Question.query.filter(
                Question.question.ilike("%" + search_string + "%")
            ).all()
            formated = [question.format() for question in questions]
            return jsonify(
                {"success": True, "questions": formated,
                    "totalQuestions": len(allqs)}
            )
        except Exception as e:
            print(e)
            abort(500)

    # get questions by category ids
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_cat(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            if len(questions) == 0:
                abort(404)
            formated = [question.format() for question in questions]
            return jsonify(
                {
                    "success": True,
                    "questions": formated,
                    "totalQuestions": len(formated),
                    "currentCategory": category_id,
                }
            )
        except Exception as e:
            print(e)
            abort(500)

    # play the game which gets next question
    @app.route("/quizzes", methods=["POST"])
    def play_trivia():
        body = request.get_json()
        try:
            prev_questions = body.get("previous_questions")
            questions = []

            categoryid = body.get("quiz_category")
            if categoryid == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=categoryid).all()
            formated = [question.format() for question in questions]
            print(prev_questions)

            formated = remove_qs(prev_questions, formated)
            nextq = random.choice(formated)
            return jsonify({"question": nextq, "success": True})

        except Exception as e:
            print(e)
            abort(500)

    # not found error handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404,
                        "message": "Not found"}), 404

    # server error handler
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"success": False, "error": 500,
                        "message": "Server error"}), 500

    # method not found error handler
    @app.errorhandler(405)
    def method_not_found(error):
        return (
            jsonify({"success": False, "error": 405,
                    "message": "Method not found"}), 405
        )

    return app


def remove_qs(askedqs, allqs):
    for askedq in askedqs:
        for question in allqs:
            if int(question["id"]) == int(askedq):
                allqs.remove(question)
                break
    return allqs
