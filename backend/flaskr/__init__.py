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
        try:
            new_question = Question(question=new_question, answer=new_question_answer,
                                    category=new_question_category, difficulty=new_question_dificulty)
            new_question.insert()

            return jsonify({
                'success': True,
                'new_question': new_question.format()
            }), 200
        except:
            abort(422)


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

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()
        if body['quiz_category']['type'] == 'click':
            print('all categories')
            all_questions = Question.query.all()
            formated_questions = [question.format() for question in all_questions]
            unanswered_questions = [
            item for item in formated_questions if item['id'] not in body['previous_questions']]

        else:
            questions_in_category = Question.query.filter(Question.category == str(int(body['quiz_category']['id']) + 1)).all()
            formated_questions = [question.format() for question in questions_in_category]
            unanswered_questions = [item for item in formated_questions if item['id'] not in body['previous_questions']]
        
        if not unanswered_questions:
            return jsonify({
                'success': True,
                'question': False
            }), 200
        else:
            return jsonify({
                'success': True,
                'question': random.choice(unanswered_questions)
            }), 200


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
