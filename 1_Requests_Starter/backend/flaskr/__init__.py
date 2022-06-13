from distutils.log import error
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)
    cors = CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    @app.route('/books', methods=['GET'])
    def home():
        books = Book.query.order_by(Book.id).all()
        formatted_books = [book.format() for book in books]
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        if len(formatted_books) <= 0:
            abort(404)

        if page > 500:
            return jsonify({
                'success': False,
                'status': 'Page number could not be found'
            })

        return jsonify({
            'success': True,
            'books': formatted_books[start:end],
            'total_books': len(Book.query.all())
        })

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_books(book_id):
        book_details = request.get_json()
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()

            if book is None:
                abort(404)

            if 'rating' in book_details:
                book.rating = int(book_details.get('rating'))

                if book.rating > 5:
                    return jsonify({
                        'success': False,
                        'content': 'Book rating cannot be more than 5',
                        'id': book.id,
                    })
            
            return jsonify({
                'success': True,
                'status': 'rating successfully updated',
                'id': book.id
            })

        except Exception as error:
            print(f'Error: {error}')
            
        finally:
            book.update()

    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def remove_book(book_id):
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()

            if book is None:
                abort(404)

            book.delete()

            formatted = [book.format() for book in book]
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * BOOKS_PER_SHELF
            end = start + BOOKS_PER_SHELF

            return jsonify({
                'success': True,
                'id': book_id,
                'books': formatted[start:end],
                'total_books': len(Book.query.all())
            })

        except Exception as error:
            print(f'Error: {error}')


    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route('/books/create', methods=['POST'])
    def create_book():
        new_book = request.get_json()

        title = new_book.get('title', None)
        author = new_book.get('author', None)
        rating = new_book.get('rating', None)

        try:
            book = Book(title=title, author=author, rating=rating)
            book.insert()

            books = Book.query.order_by(Book.id).all()
            formatted_books = [book.format() for book in books]
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * BOOKS_PER_SHELF
            end = start + BOOKS_PER_SHELF

            return jsonify({
            'success': True,
            'created book': book.id,
            'books': formatted_books[start:end],
            'total_books': len(Book.query.all())
        })

        except:
            abort(422)


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource nor found at the specified id',
        }), 404


    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': True,
            'error': 422,
            'message': 'request could not be processed at the moment. try later.'
        }), 422


    return app
