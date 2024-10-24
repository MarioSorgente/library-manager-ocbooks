from models import UserBook, Book
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

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
        
        # Create text representation for each book
        book_texts = []
        book_ids = []
        for book in all_books:
            if book.title and book.authors:  # Only include books with valid data
                text = f"{book.title} {book.authors} {book.description or ''}"
                book_texts.append(text)
                book_ids.append(book.id)
        
        if not book_texts:  # If no valid books found
            return []
            
        # Convert to TF-IDF features
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(book_texts)
        
        # Calculate similarity between books
        similarities = cosine_similarity(tfidf_matrix)
        
        # Get recommendations based on highest rated books
        recommended_books = set()
        for user_book in sorted(rated_books, key=lambda x: x.rating or 0, reverse=True):
            try:
                book_idx = book_ids.index(user_book.book_id)
                similar_indices = similarities[book_idx].argsort()[::-1][1:6]
                
                for idx in similar_indices:
                    book_id = book_ids[idx]
                    if book_id not in user_book_ids:
                        recommended_books.add(Book.query.get(book_id))
                        if len(recommended_books) >= n_recommendations:
                            break
            except ValueError:
                continue
            
            if len(recommended_books) >= n_recommendations:
                break
        
        return list(recommended_books)
    except Exception as e:
        logger.error(f"Error in recommendations: {str(e)}")
        return []
