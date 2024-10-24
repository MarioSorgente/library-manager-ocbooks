from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Book, UserBook, db
import requests
from recommender import get_recommendations
import logging
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('books', __name__, url_prefix='/books')

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
logger = logging.getLogger(__name__)

@bp.route('/library')
@login_required
def library():
    try:
        want_to_read = UserBook.query.filter_by(user_id=current_user.id, status='want_to_read').all()
        reading = UserBook.query.filter_by(user_id=current_user.id, status='reading').all()
        read = UserBook.query.filter_by(user_id=current_user.id, status='read').all()
        recommendations = get_recommendations(current_user.id)
        
        return render_template('books/library.html',
                          want_to_read=want_to_read,
                          reading=reading,
                          read=read,
                          recommendations=recommendations)
    except Exception as e:
        logger.error(f"Error in library route: {str(e)}")
        flash('An error occurred while loading your library', 'danger')
        return render_template('books/library.html', 
                          want_to_read=[], reading=[], read=[], 
                          recommendations=[])

@bp.route('/search')
@login_required
def search():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'items': []})
            
        response = requests.get(GOOGLE_BOOKS_API, 
                              params={'q': query},
                              timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.Timeout:
        logger.error("Google Books API request timed out")
        return jsonify({'error': 'Search request timed out'}), 504
    except requests.RequestException as e:
        logger.error(f"Google Books API error: {str(e)}")
        return jsonify({'error': 'Failed to fetch search results'}), 502
    except Exception as e:
        logger.error(f"Error in search route: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/add', methods=['POST'])
@login_required
def add_book():
    try:
        google_books_id = request.form.get('google_books_id')
        status = request.form.get('status')
        
        if not google_books_id or not status:
            flash('Invalid book information', 'danger')
            return redirect(url_for('books.library'))
        
        # Check if user already has this book
        existing_book = Book.query.filter_by(google_books_id=google_books_id).first()
        if existing_book:
            existing_user_book = UserBook.query.filter_by(
                user_id=current_user.id,
                book_id=existing_book.id
            ).first()
            
            if existing_user_book:
                flash('This book is already in your library', 'warning')
                return redirect(url_for('books.library'))
        
        # If book doesn't exist, fetch it from Google Books API
        if not existing_book:
            try:
                response = requests.get(f"{GOOGLE_BOOKS_API}/{google_books_id}", timeout=5)
                response.raise_for_status()
                book_data = response.json()
                
                existing_book = Book(
                    google_books_id=google_books_id,
                    title=book_data['volumeInfo'].get('title', ''),
                    authors=', '.join(book_data['volumeInfo'].get('authors', [])),
                    description=book_data['volumeInfo'].get('description', ''),
                    cover_url=book_data['volumeInfo'].get('imageLinks', {}).get('thumbnail', '')
                )
                db.session.add(existing_book)
                db.session.flush()
            except requests.RequestException as e:
                logger.error(f"Error fetching book details: {str(e)}")
                flash('Failed to fetch book details', 'danger')
                return redirect(url_for('books.library'))
        
        # Add book to user's library
        user_book = UserBook(
            user_id=current_user.id,
            book_id=existing_book.id,
            status=status
        )
        db.session.add(user_book)
        db.session.commit()
        
        flash('Book added to your library!', 'success')
    except SQLAlchemyError as e:
        logger.error(f"Database error adding book: {str(e)}")
        db.session.rollback()
        flash('Failed to add book to database', 'danger')
    except Exception as e:
        logger.error(f"Error adding book: {str(e)}")
        db.session.rollback()
        flash('An unexpected error occurred', 'danger')
    
    return redirect(url_for('books.library'))

@bp.route('/move', methods=['POST'])
@login_required
def move_book():
    try:
        book_id = request.form.get('book_id')
        new_status = request.form.get('status')
        
        if not book_id or not new_status:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_book = UserBook.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first_or_404()
        
        if user_book.status != new_status:
            user_book.status = new_status
            db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error moving book: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to move book'}), 500

@bp.route('/rate', methods=['POST'])
@login_required
def rate_book():
    try:
        book_id = request.form.get('book_id')
        rating = request.form.get('rating')
        
        if not book_id or not rating:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_book = UserBook.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first_or_404()
        
        user_book.rating = rating
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error rating book: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to rate book'}), 500

@bp.route('/remove', methods=['POST'])
@login_required
def remove_book():
    try:
        book_id = request.form.get('book_id')
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first_or_404()
        db.session.delete(user_book)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error removing book: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to remove book'}), 500
