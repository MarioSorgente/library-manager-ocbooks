document.querySelectorAll('.rating').forEach(rating => {
    const bookId = rating.dataset.bookId;
    const stars = rating.querySelectorAll('.star');
    
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = star.dataset.rating;
            const form = new FormData();
            form.append('book_id', bookId);
            form.append('rating', rating);
            
            fetch('/books/rate', {
                method: 'POST',
                body: form
            }).then(response => response.json())
              .then(data => {
                  if (data.success) {
                      stars.forEach(s => {
                          s.classList.toggle('active', s.dataset.rating <= rating);
                      });
                  }
              });
        });
    });
});
