import os
import unittest
import json
from sqlalchemy import text

from flaskr import create_app
from models import db, Question, Category

from settings import DB_USER, DB_PASSWORD


DATABASE_NAME = "trivia_test"
DATABASE_PATH = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DATABASE_NAME}"


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": DATABASE_PATH,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            with db.engine.connect() as conn:
                conn.execute(
                    text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
                conn.commit()

            db.create_all()

            category1 = Category(type="Science")
            category2 = Category(type="Art")
            category3 = Category(type="Geography")
            category4 = Category(type="History")
            category5 = Category(type="Entertainment")
            category6 = Category(type="Sports")

            db.session.add_all(
                [category1, category2, category3, category4, category5, category6])
            db.session.commit()

            question1 = Question(
                question="What is the chemical symbol for water?",
                answer="H2O",
                category=category1.id,
                difficulty=1)
            question2 = Question(
                question="Who painted the Mona Lisa?",
                answer="Leonardo da Vinci",
                category=category2.id,
                difficulty=2)
            question3 = Question(
                question="What is the capital of France?",
                answer="Paris",
                category=category3.id,
                difficulty=3)
            question4 = Question(
                question="What year did World War II end?",
                answer="1945",
                category=category4.id,
                difficulty=4)
            question5 = Question(
                question="What is the largest organ in the human body?",
                answer="Skin",
                category=category1.id,
                difficulty=1)
            question6 = Question(
                question="Which planet is known as the Red Planet?",
                answer="Mars",
                category=category1.id,
                difficulty=2)

            questions_for_pagination = []
            for i in range(15):
                q = Question(
                    question=f"Paginated Science Question {
                        i + 1}",
                    answer=f"Answer {
                        i + 1}",
                    category=category1.id,
                    difficulty=1)
                questions_for_pagination.append(q)

            db.session.add_all([question1,
                                question2,
                                question3,
                                question4,
                                question5,
                                question6] + questions_for_pagination)
            db.session.commit()

            self.question_to_delete_id = question1.id
            self.test_category_id = category1.id

            self.new_question = {
                'question': 'New Test Question?',
                'answer': 'New Test Answer!',
                'difficulty': 1,
                'category': category5.id
            }

            self.search_term = {'searchTerm': 'Red Planet'}

            self.quiz_round_all_categories = {
                'previous_questions': [question1.id, question2.id],
                'quiz_category': {'type': 'click', 'id': 0}
            }
            self.quiz_round_specific_category = {
                'previous_questions': [question5.id],
                'quiz_category': {'type': 'Science', 'id': category1.id}
            }

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()

    def test_get_categories(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']) > 0)

    def test_get_paginated_questions(self):
        """Test GET /questions with pagination"""
        res = self.client.get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['totalQuestions'] > 0)
        self.assertTrue(len(data['questions']) <= 10)
        self.assertTrue(data['categories'])

    def test_404_if_requesting_beyond_valid_page(self):
        """Test GET /questions for a non-existent page"""
        res = self.client.get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        """Test DELETE /questions/<id>"""
        res = self.client.delete(f'/questions/{self.question_to_delete_id}')
        data = json.loads(res.data)

        with self.app.app_context():
            question_check = Question.query.filter(
                Question.id == self.question_to_delete_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], self.question_to_delete_id)
        self.assertIsNone(question_check)

    def test_404_if_question_to_delete_does_not_exist(self):
        """Test DELETE /questions/<id> for a non-existent ID"""
        res = self.client.delete('/questions/999999')  # Non-existent ID
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_question(self):
        """Test POST /questions to add a new question"""
        res = self.client.post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

        with self.app.app_context():
            question_check = Question.query.filter(
                Question.id == data['created']).one_or_none()
            self.assertIsNotNone(question_check)
            self.assertEqual(
                question_check.question,
                self.new_question['question'])

    def test_400_if_create_question_fails_missing_data(self):
        """Test POST /questions with missing required fields"""
        bad_question = {
            'question': 'Bad Q?',
            'answer': 'Bad A!',
            'difficulty': 1
        }
        res = self.client.post('/questions', json=bad_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_search_questions_with_results(self):
        """Test POST /questions for search with results"""
        res = self.client.post('/questions', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['totalQuestions'] > 0)
        self.assertTrue(len(data['questions']) > 0)
        self.assertIn('Mars', data['questions'][0]['answer'])

    def test_search_questions_without_results(self):
        """Test POST /questions for search with no results"""
        no_results_term = {'searchTerm': 'nonexistentstringinanyquestion'}
        res = self.client.post('/questions', json=no_results_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_play_quiz_all_categories(self):
        """Test POST /quizzes for a question from all categories"""
        res = self.client.post('/quizzes', json=self.quiz_round_all_categories)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        self.assertNotIn(
            data['question']['id'],
            self.quiz_round_all_categories['previous_questions'])

    def test_play_quiz_specific_category(self):
        """Test POST /quizzes for a question from a specific category"""
        res = self.client.post('/quizzes',
                               json=self.quiz_round_specific_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        self.assertEqual(
            data['question']['category'],
            self.quiz_round_specific_category['quiz_category']['id'])
        self.assertNotIn(
            data['question']['id'],
            self.quiz_round_specific_category['previous_questions'])

    def test_play_quiz_no_questions_left(self):
        """Test POST /quizzes when no questions are left"""
        with self.app.app_context():
            all_q_ids = [q.id for q in Question.query.all()]

        quiz_round_no_questions = {
            'previous_questions': all_q_ids,
            'quiz_category': {'type': 'click', 'id': 0}
        }
        res = self.client.post('/quizzes', json=quiz_round_no_questions)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNone(data['question'])

    def test_400_if_quiz_parameters_missing(self):
        """Test POST /quizzes with missing parameters"""
        res = self.client.post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_get_questions_by_category(self):
        """Test GET /categories/<id>/questions"""
        res = self.client.get(f'/categories/{self.test_category_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['totalQuestions'] > 0)

        with self.app.app_context():
            self.assertEqual(
                data['currentCategory'], db.session.get(
                    Category, self.test_category_id).type)

        for q in data['questions']:
            self.assertEqual(q['category'], self.test_category_id)

    def test_404_if_category_for_questions_does_not_exist(self):
        """Test GET /categories/<id>/questions for non-existent category"""
        res = self.client.get('/categories/9999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category_no_questions(self):
        """Test GET /categories/<id>/questions for a category with no questions"""
        with self.app.app_context():
            category_no_questions_id = Category.query.filter_by(
                type='Sports').first().id

        res = self.client.get(
            f'/categories/{category_no_questions_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(data['currentCategory'], 'Sports')


if __name__ == "__main__":
    unittest.main()
