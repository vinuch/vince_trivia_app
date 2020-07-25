import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    # '''
    # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    # '''

    # '''
    # @TODO: Use the after_request decorator to set Access-Control-Allow
    # '''

    # '''
    # @TODO:
    # Create an endpoint to handle GET requests
    # for all available categories.
    # '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories_selection = Category.query.all()
        categories = [category.type for category in categories_selection]

        return jsonify({
            'success': True,
            'categories': categories
        })


    @app.route('/questions')
    def get_questions():
        categories_selection = Category.query.all()
        categories = [category.type for category in categories_selection]
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if not current_questions:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'categories': categories,
                'total_questions': len(Question.query.all())
            })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        try:
            question.delete()
        except:
            abort(422)
        else:
            return jsonify({
                'success': True,
                'deleted': question_id
            }), 200

    @app.route('/questions', methods=['POST'])
    def add_question():
        res = request.get_json()
        new_question = res.get('question', None)
        new_question_answer = res.get('answer', None)
        new_question_category = res.get('category', None)
        new_question_dificulty = res.get('difficulty', None)
        search = res.get('search', None)
        try:
            new_question = Question(question=new_question, answer=new_question_answer,
                                    category=new_question_category, difficulty=new_question_dificulty)
            new_question.insert()
        except:
            abort(422)
        else:
            return jsonify({
                'success': True,
                'new_question': new_question.format()
            }), 200

    # '''
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search)))
            questions = paginate_questions(request, selection)
        except:
            abort(422)
        else:
            return jsonify({
                'success': True,
                'questions': questions,
                'totalQuestions': len(selection.all()),
            }), 200

    # '''
    # @TODO:
    # Create a GET endpoint to get questions based on category.

    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.
    # '''
    @app.route('/categories/<int:category_id>', methods=['GET'])
    def get_specific_category(category_id):
        categories_selection = Category.query.all()
        categories = [category.type for category in categories_selection]
        selection = Question.query.filter(Question.category == str(
            category_id)).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        if current_questions is None or not selection:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'categories': categories,
                'current_category': Category.query.get(category_id).type,
                'total_questions': len(current_questions)
            }), 200

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()
        questions_in_category = Question.query.filter(
            Question.category == str(int(body['quiz_category']['id']) + 1)).all()
        formated_questions = [question.format()
                              for question in questions_in_category]
        unanswered_questions = [
            item for item in formated_questions if item['id'] not in body['previous_questions']]
        # print(random.choice(unanswered_questions))
        if not unanswered_questions:
            return jsonify({
                'success': True,
                'question': False
            }), 404
        else:
            return jsonify({
                'success': True,
                'question': random.choice(unanswered_questions)
            }), 200

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Not found",
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "inaccessibe",
        }), 422

    return app
