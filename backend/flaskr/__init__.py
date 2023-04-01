import random
from flask import Flask, request, abort, jsonify
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
    Set up CORS. Allow '*' for origins.
    """
    CORS(app, resources={r'*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        """
        Set Access-Control-Allow
        """
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        """
        Create an endpoint to handle GET requests for all available categories.
        """
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

    @app.route('/questions', methods=['GET'])
    def get_questions():
        """
        Create an endpoint to handle GET requests for questions,
        """
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
            'current_category': None,
            'categories': categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Delete a question
        """
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            'success': True,
            'question': question_id,
            'total_questions': len(Question.query.all()),
            'current_category': question.category
        })

    @app.route('/questions', methods=['POST'])
    def create_question():
        """
        Create a new question
        """
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
                'current_category': None,
                'total_questions': len(Question.query.all())
            })
        except Exception:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """
        Search questions
        """
        body = request.get_json()
        search_term = body.get('searchTerm')

        if search_term is not None:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            current_questions = paginate(request, selection)

            if (len(current_questions) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category': None,
                'total_questions': len(selection)
            })

        abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        """
        Get questions by category
        """
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
            'current_category': category_id
        })

    def get_random_question(category, previous_questions):
        """
        Get random question
        """
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
        """
        Play quiz
        """
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

    @app.errorhandler(404)
    def not_found(error):
        """
        Error handler for 404
        """
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        """
        Error handler for 422
        """
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        })

    return app
