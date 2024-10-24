// Define error boundary wrapper at the start
function wrapWithErrorBoundary(fn) {
    return function(...args) {
        try {
            return fn.apply(this, args);
        } catch (error) {
            console.error('Error in function:', error);
            showFeedback('An unexpected error occurred', 'danger');
            return null;
        }
    };
}

// UI feedback functions
function showFeedback(message, type) {
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
    feedbackDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(feedbackDiv);
    setTimeout(() => {
        feedbackDiv.remove();
    }, 3000);
}

function showLoading(show) {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}

// Define all handlers before DOM content loaded
function handleDrag(ev) {
    const bookId = ev.target.dataset.bookId;
    if (!bookId) {
        ev.preventDefault();
        return;
    }
    ev.target.classList.add('dragging');
    ev.dataTransfer.setData('bookId', bookId);
    ev.dataTransfer.effectAllowed = 'move';
}

function handleDrop(ev) {
    ev.preventDefault();
    const bookId = ev.dataTransfer.getData('bookId');
    const newStatus = ev.currentTarget.id;
    
    if (!bookId || !newStatus) {
        showFeedback('Error: Invalid drag and drop operation', 'danger');
        return;
    }
    
    ev.currentTarget.classList.remove('drag-over');
    const draggedElement = document.querySelector(`[data-book-id="${bookId}"]`);
    if (draggedElement) {
        draggedElement.classList.remove('dragging');
        // Move the element in the UI immediately
        const targetList = document.getElementById(newStatus);
        if (targetList) {
            targetList.appendChild(draggedElement);
            // Show book rating if moved to "read" status
            const ratingElement = draggedElement.querySelector('.rating');
            if (ratingElement) {
                ratingElement.classList.toggle('d-none', newStatus !== 'read');
            }
        }
    }
    
    handleMoveBook(bookId, newStatus);
}

function handleDragOver(ev) {
    ev.preventDefault();
    if (!ev.currentTarget.classList.contains('drag-over')) {
        ev.currentTarget.classList.add('drag-over');
    }
}

function handleDragLeave(ev) {
    ev.currentTarget.classList.remove('drag-over');
}

async function handleAddBook(googleBooksId, status) {
    if (!googleBooksId) {
        showFeedback('Error: Invalid book ID', 'danger');
        return;
    }

    const form = new FormData();
    form.append('google_books_id', googleBooksId);
    form.append('status', status);
    
    showLoading(true);
    try {
        const response = await fetch('/books/add', {
            method: 'POST',
            body: form
        });
        
        if (!response.ok) throw new Error('Failed to add book');
        showFeedback('Book added successfully!', 'success');
        window.location.reload();
    } catch (error) {
        console.error('Add book error:', error);
        showFeedback('Failed to add book', 'danger');
    } finally {
        showLoading(false);
    }
}

async function handleMoveBook(bookId, newStatus) {
    if (!bookId || !newStatus) {
        showFeedback('Error: Invalid book or status', 'danger');
        return;
    }

    const form = new FormData();
    form.append('book_id', bookId);
    form.append('status', newStatus);
    
    showLoading(true);
    try {
        const response = await fetch('/books/move', {
            method: 'POST',
            body: form
        });
        
        if (!response.ok) throw new Error('Failed to move book');
        showFeedback('Book moved successfully!', 'success');
        dispatchBookMoved();
    } catch (error) {
        console.error('Move book error:', error);
        showFeedback('Failed to move book', 'danger');
    } finally {
        showLoading(false);
    }
}

function handleConfirmDeleteBook(bookId) {
    if (!bookId) {
        showFeedback('Error: Invalid book ID', 'danger');
        return;
    }
    
    if (confirm('Are you sure you want to delete this book from your library?')) {
        handleRemoveBook(bookId);
    }
}

async function handleRemoveBook(bookId) {
    if (!bookId) {
        showFeedback('Error: Invalid book ID', 'danger');
        return;
    }

    showLoading(true);
    try {
        const response = await fetch('/books/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `book_id=${bookId}`
        });
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to remove book');
        }
        
        showFeedback('Book removed successfully!', 'success');
        window.location.reload();
    } catch (error) {
        console.error('Remove book error:', error);
        showFeedback('Failed to remove book', 'danger');
    } finally {
        showLoading(false);
    }
}

function handleShowBookDetails(bookId, title, authors, description, coverUrl, rating = null) {
    if (!title || !authors) {
        showFeedback('Error: Invalid book details', 'danger');
        return;
    }

    const modalTitle = document.getElementById('bookDetailsTitle');
    const modalAuthor = document.getElementById('bookDetailsAuthor');
    const modalDescription = document.getElementById('bookDetailsDescription');
    const modalCover = document.getElementById('bookDetailsCover');
    const ratingElement = document.getElementById('bookDetailsRating');
    
    if (!modalTitle || !modalAuthor || !modalDescription || !modalCover) {
        showFeedback('Error: Modal elements not found', 'danger');
        return;
    }
    
    modalTitle.textContent = title;
    modalAuthor.textContent = authors;
    modalDescription.textContent = description || 'No description available';
    modalCover.src = coverUrl;
    
    if (ratingElement) {
        const stars = ratingElement.querySelectorAll('.star');
        if (rating !== null && !isNaN(rating)) {
            ratingElement.classList.remove('d-none');
            stars.forEach((star, index) => {
                star.classList.toggle('active', index < rating);
            });
        } else {
            ratingElement.classList.add('d-none');
        }
    }
    
    const modal = new bootstrap.Modal(document.getElementById('bookDetailsModal'));
    modal.show();
}

// Event dispatchers
function dispatchBookMoved() {
    document.dispatchEvent(new CustomEvent('bookMoved'));
}

// Search functionality
function createSearchResultCard(googleBooksId, book, thumbnail) {
    const title = book.title?.replace(/'/g, "\\'") || 'Unknown Title';
    const authors = (book.authors || ['Unknown Author']).join(', ').replace(/'/g, "\\'");
    
    const element = document.createElement('div');
    element.className = 'col-md-4 mb-4';
    element.innerHTML = `
        <div class="card h-100 search-result-card">
            <img src="${thumbnail}" class="card-img-top" alt="${title}">
            <div class="card-body">
                <h5 class="card-title">${title}</h5>
                <p class="card-text">${authors}</p>
                <button class="btn btn-outline-secondary mt-2" onclick="handleAddBook('${googleBooksId}', 'want_to_read')">
                    Add to Library
                </button>
            </div>
        </div>
    `;
    return element;
}

// Initialize all event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add search functionality with debouncing
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async function() {
                const query = searchInput.value.trim();
                if (query.length < 2) return;
                
                showLoading(true);
                try {
                    const response = await fetch(`/books/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    const searchResults = document.getElementById('searchResults');
                    searchResults.innerHTML = '';
                    
                    if (data.items && data.items.length > 0) {
                        data.items.forEach(item => {
                            const thumbnail = item.volumeInfo.imageLinks?.thumbnail || '/static/img/no-cover.png';
                            const card = createSearchResultCard(item.id, item.volumeInfo, thumbnail);
                            searchResults.appendChild(card);
                        });
                    } else {
                        searchResults.innerHTML = '<p class="text-center w-100">No books found</p>';
                    }
                } catch (error) {
                    console.error('Search error:', error);
                    showFeedback('Error searching books', 'danger');
                } finally {
                    showLoading(false);
                }
            }, 300);
        });
    }
});

// Make handlers globally available
window.handleDrag = handleDrag;
window.handleDrop = handleDrop;
window.handleDragOver = handleDragOver;
window.handleDragLeave = handleDragLeave;
window.handleAddBook = handleAddBook;
window.handleMoveBook = handleMoveBook;
window.handleConfirmDeleteBook = handleConfirmDeleteBook;
window.handleRemoveBook = handleRemoveBook;
window.handleShowBookDetails = handleShowBookDetails;
