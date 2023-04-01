import unittest
import json

from sqlalchemy import desc
from flaskr.config import TestingConfig
from flaskr import create_app
from flaskr.models import Question, db, Category
from contextlib import contextmanager


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(TestingConfig())
        self.client = self.app.test_client
        # binds the app to the current context
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            # db.drop_all()
            pass

    @contextmanager
    def app_test_context(self, app):
        with app.app_context():
            # db = SQLAlchemy()
            # db.init_app(app)
            with db.engine.connect() as connection:
                # Begin transaction
                transaction = connection.begin()

                try:
                    yield db.session
                    # Rollback transaction after test is done
                    transaction.rollback()
                finally:
                    # Close session and dispose engine after rollback
                    db.session.close()
                    db.engine.dispose()
    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories_return_200(self):
        """
         Test getting all categories from / categories endpoint ( GET ). Expects 200
        """

        with self.app_test_context(self.app) as session:

            # Make request to endpoint
            res = self.client().get('/categories')
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['categories'])
            self.assertTrue(data['success'])
            categories = session.query(Category).all()
            self.assertEqual(data['total_categories'], len(categories))

    def test_get_all_categories_return_404(self):
        """
         Test getting all categories from / categories endpoint ( GET ). Expects 404
        """
        with self.app_test_context(self.app) as session:
            # delete all categories
            session.query(Category).delete()
            res = self.client().get('/categories')
            # test status code
            self.assertEqual(res.status_code, 404)

    def test_get_all_questions_return_200(self):
        """
         Test getting all questions from / questions endpoint ( GET ). Expects 200
        """
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().get('/questions')
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(data['categories'])
            self.assertTrue(data['total_questions'])
            self.assertFalse(data['current_category'])
            self.assertTrue(data['success'])
            questions = session.query(Question).all()
            self.assertEqual(data['total_questions'], len(questions))

    def test_get_all_questions_return_404(self):
        """
         Test getting all questions from / questions endpoint ( GET ). Expects 404
        """
        with self.app_test_context(self.app) as session:
            # delete all questions
            session.query(Question).delete()
            res = self.client().get('/questions')
            # test status code
            self.assertEqual(res.status_code, 404)

    def test_get_all_questions_paginated_return_200(self, page=1):
        """
         Test getting all questions from / questions endpoint ( GET ). Expects 200
        """
        NUMBER_OF_PAGE = 10
        CURRENT_PAGE = 1
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().get(f'/questions?page={CURRENT_PAGE}')
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(data['categories'])
            self.assertTrue(data['total_questions'])
            self.assertFalse(data['current_category'])
            self.assertTrue(data['success'])
            questions = session.query(Question).all()
            # get questions in current page
            questions_in_current_page = questions[(CURRENT_PAGE - 1) *
                                                  NUMBER_OF_PAGE:CURRENT_PAGE * NUMBER_OF_PAGE]
            self.assertEqual(data['total_questions'], len(questions))
            self.assertEqual(len(data['questions']),
                             len(questions_in_current_page))

    def test_get_all_questions_paginated_return_404(self):
        """
         Test getting all questions from / questions endpoint ( GET ). Expects 404
        """
        with self.app_test_context(self.app) as session:
            # delete all questions
            session.query(Question).delete()
            res = self.client().get('/questions?page=1')
            # test status code
            self.assertEqual(res.status_code, 404)

    def test_get_question_by_category_return_200(self):
        """
         Test getting all questions from / questions endpoint ( GET ). Expects 200
        """
        CURRENT_CATEGORY = 1
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().get(
                f'/categories/{CURRENT_CATEGORY}/questions')
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(data['total_questions'])
            self.assertEqual(data['current_category'], CURRENT_CATEGORY)
            self.assertTrue(data['success'])
            questions = session.query(Question).filter_by(
                category=CURRENT_CATEGORY).all()
            self.assertEqual(data['total_questions'], len(questions))

    def test_get_question_by_category_return_404(self):
        """
         Test getting all questions from / questions endpoint ( GET ). Expects 404
        """
        CURRENT_CATEGORY = 1
        with self.app_test_context(self.app) as session:
            # delete all questions
            session.query(Question).delete()
            res = self.client().get(
                f'/categories/{CURRENT_CATEGORY}/questions')
            # test status code
            self.assertEqual(res.status_code, 404)

    def test_delete_question_return_200(self):
        """
         Test deleting a question from / questions endpoint ( DELETE ). Expects 200
        """

        with self.app_test_context(self.app) as session:
            # Get random question
            question_last = session.query(
                Question).order_by(desc(Question.id)).first()
            # Make request to endpoint
            res = self.client().delete(f'/questions/{question_last.id}')
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertTrue(data['total_questions'])
            questions = session.query(Question).all()
            self.assertEqual(data['total_questions'], len(questions))

    def test_delete_question_return_404(self):
        """
         Test deleting a question from / questions endpoint ( DELETE ). Expects 404
        """
        QUESTION_NOT_EXIST = 1
        with self.app_test_context(self.app) as session:
            # delete all questions
            session.query(Question).delete()
            res = self.client().delete(f'/questions/{QUESTION_NOT_EXIST}')
            # test status code
            self.assertEqual(res.status_code, 404)

    def test_create_question_return_200(self):
        """
         Test creating a question from / questions endpoint ( POST ). Expects 200
        """
        self.new_question = {
            'question': 'What is the capital of France?',
            'answer': 'Paris',
            'difficulty': 1,
            'category': 1
        }
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().post('/questions', json=self.new_question)
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertTrue(data['total_questions'])
            questions = session.query(Question).all()
            self.assertEqual(data['total_questions'], len(questions))

    def test_search_question_return_200(self):
        """
         Test searching a question from / questions endpoint ( POST ). Expects 200
        """
        self.search_question = {
            'searchTerm': 'what'
        }
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().post('/questions/search', json=self.search_question)
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(data['total_questions'])
            self.assertFalse(data['current_category'])
            self.assertTrue(data['success'])
            questions = session.query(Question).filter(Question.question.ilike(
                '%' + self.search_question['searchTerm'] + '%')).all()
            self.assertEqual(data['total_questions'], len(questions))

    def test_search_question_when_searchTerm_is_empty_return_200(self):
        """
         Test searching a question from / questions endpoint ( POST ). Expects 200
        """
        self.search_question = {
            'searchTerm': ''
        }
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().post('/questions/search', json=self.search_question)
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            self.assertTrue(data['total_questions'])
            self.assertFalse(data['current_category'])
            self.assertTrue(data['success'])
            questions = session.query(Question).all()
            self.assertEqual(data['total_questions'], len(questions))

    def test_search_question_return_404(self):
        """
         Test searching a question from / questions endpoint ( POST ). Expects 404
        """
        self.search_question = {
            'searchTerm': 'abcdef'
        }
        with self.app_test_context(self.app) as session:
            res = self.client().post('/questions/search', json=self.search_question)
            # test status code
            self.assertEqual(res.status_code, 404)

    def test_create_quiz_question_return_200(self):
        """
         Test creating a quiz question from / quiz endpoint ( POST ). Expects 200
        """
        self.quiz_question = {
            'previous_questions': [1, 2, 3],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        with self.app_test_context(self.app) as session:
            # Make request to endpoint
            res = self.client().post('/quizzes', json=self.quiz_question)
            data = json.loads(res.data.decode('utf-8'))

            # Check response
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['question'])
            self.assertTrue(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
