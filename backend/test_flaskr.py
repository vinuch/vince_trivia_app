import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('mac@localhost:5432', self.database_name)
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
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_404_invalid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')


    def test_get_questions_by_category(self):
        res = self.client().get('/categories/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_category_404(self):
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        

    def test_create_question(self):
        res = self.client().post('/questions', json={
        "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
        "answer": "Apollo",
        "difficulty": 5,
        "category": 1,
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_delete_question(self):
        # Create test question to delete
        create_question = {
            'question' : 'This is a test question right?',
            'answer' : 'Correct!!!',
            'category' : '1',
            'difficulty' : 1
        } 

        res = self.client().post('/questions', json = create_question)
        data = json.loads(res.data)
        question_id = data['new_question']['id'] 

        # pass in the id of test question to query param of delete endpoint
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'title'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(len(data['questions']), 2)

    def test_search_question_not_found(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'applePineapple'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['totalQuestions'])
        self.assertEqual(len(data['questions']), 0)


    def test_play_quizz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 1, 'type': 'Science'}, 'previous_questions': []})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_quizz_questiion_not_found(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 1000, 'type': 'Science'}, 'previous_questions': []})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['question'])

        
  

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()