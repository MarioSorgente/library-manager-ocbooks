// Reading Progress Graph
function updateProgressGraph() {
    const canvas = document.getElementById('readingProgress');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Get book counts from each column
    const wantToRead = document.getElementById('want_to_read').children.length;
    const reading = document.getElementById('reading').children.length;
    const read = document.getElementById('read').children.length;
    
    const total = wantToRead + reading + read;
    if (total === 0) return;
    
    // Calculate percentages
    const readPercent = (read / total) * 100;
    const readingPercent = (reading / total) * 100;
    const wantToReadPercent = (wantToRead / total) * 100;
    
    // Draw bars
    const barHeight = height * 0.6;
    const startY = (height - barHeight) / 2;
    
    // Draw "Want to Read" section
    ctx.fillStyle = 'rgba(128, 0, 32, 0.3)';
    const wantToReadWidth = (wantToReadPercent / 100) * width;
    ctx.fillRect(0, startY, wantToReadWidth, barHeight);
    
    // Draw "Reading" section
    ctx.fillStyle = 'rgba(128, 0, 32, 0.6)';
    const readingWidth = (readingPercent / 100) * width;
    ctx.fillRect(wantToReadWidth, startY, readingWidth, barHeight);
    
    // Draw "Read" section
    ctx.fillStyle = 'rgba(128, 0, 32, 0.9)';
    const readWidth = (readPercent / 100) * width;
    ctx.fillRect(wantToReadWidth + readingWidth, startY, readWidth, barHeight);
    
    // Add labels
    ctx.fillStyle = '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    
    // Only show percentages if they're significant enough
    if (wantToReadPercent > 10) {
        ctx.fillText(`${Math.round(wantToReadPercent)}%`, wantToReadWidth / 2, height / 2);
    }
    if (readingPercent > 10) {
        ctx.fillText(`${Math.round(readingPercent)}%`, wantToReadWidth + readingWidth / 2, height / 2);
    }
    if (readPercent > 10) {
        ctx.fillText(`${Math.round(readPercent)}%`, wantToReadWidth + readingWidth + readWidth / 2, height / 2);
    }
}

// Update progress when DOM is loaded and after any drag operations
document.addEventListener('DOMContentLoaded', updateProgressGraph);
document.addEventListener('bookMoved', updateProgressGraph);
