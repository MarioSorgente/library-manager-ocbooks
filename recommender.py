from models import UserBook, Book
import re
import logging

logger = logging.getLogger(__name__)


def _tokens(book):
    text = f"{book.title or ''} {book.authors or ''} {book.description or ''}"
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def get_recommendations(user_id, n_recommendations=5):
    try:
        # Get user's rated books
        user_books = UserBook.query.filter_by(user_id=user_id).all()
        rated_books = [ub for ub in user_books if ub.rating is not None]
        
        if not rated_books:
            return []
        
        # Get all books except user's books
        user_book_ids = [ub.book_id for ub in user_books]
        all_books = Book.query.filter(Book.id.notin_(user_book_ids)).all()
        
        if not all_books:
            return []
        
        candidates = [(book, _tokens(book)) for book in all_books if book.title]
        if not candidates:
            return []

        # Rank candidates by token overlap with books the user rated highly.
        preferences = [
            (_tokens(user_book.book), user_book.rating or 0)
            for user_book in rated_books
        ]

        def score(candidate_tokens):
            return sum(
                rating * len(candidate_tokens & liked_tokens)
                for liked_tokens, rating in preferences
            )

        ranked = sorted(candidates, key=lambda item: score(item[1]), reverse=True)
        return [book for book, _ in ranked[:n_recommendations]]
    except Exception as e:
        logger.error(f"Error in recommendations: {str(e)}")
        return []
