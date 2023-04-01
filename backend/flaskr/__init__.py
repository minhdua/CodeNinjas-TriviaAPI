import os
from random import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import exc

from .models import setup_db, Question, Category
from .config import ProductionConfig

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=ProductionConfig()):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app, test_config)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r'*': {'origins': '*'}})

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            if (len(categories) == 0):
                abort(404)

            formatted_categories = {
                category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_categories': len(Category.query.all())
            })

        except exc.SQLAlchemyError as e:
            print(str(e))
            abort(422)
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate(request, selection)

        print(len(current_questions))

        if (len(current_questions) == 0):
            abort(404)

        categories = {
            category.id: category.type for category in Category.query.all()}

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': [],
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            'success': True,
            'question': question_id,
            'total_questions': len(Question.query.all())
        })

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty,
                                category=new_category)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            questions = paginate(request, selection)
            return jsonify({
                'success': True,
                'questions': questions,
                'created': question.id,
                'total_questions': len(Question.query.all())
            })
        except Exception:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')

        if search_term:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            current_questions = paginate(request, selection)

            if (len(current_questions) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': []
            })

        abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if category is None:
            abort(404)

        selection = Question.query.filter(
            Question.category == str(category_id)).all()
        current_questions = paginate(request, selection)

        if (len(current_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    def get_random_question(category, previous_questions):
        if category == 0:
            questions = Question.query.filter(
                Question.id.notin_((previous_questions))).all()
        else:
            questions = Question.query.filter_by(
                category=category).filter(
                Question.id.notin_((previous_questions))).all()

        if len(questions) == 0:
            return None

        return questions[random.randrange(0, len(questions))]

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        question = get_random_question(quiz_category['id'], previous_questions)

        if question is None:
            return jsonify({
                'success': True
            })

        return jsonify({
            'success': True,
            'question': question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        })

    return app
