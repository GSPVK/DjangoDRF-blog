function toggleComments(element) {
    const comments = element.nextElementSibling;
    if (comments.style.display === 'none' || comments.style.display === '') {
        comments.style.display = 'block';
        element.innerHTML = 'Hide replies';
    } else {
        comments.style.display = 'none';
        element.innerHTML = 'Show replies';
    }
}

function showAllReplies(element) {
    const replies = element.nextElementSibling;
    if (replies.style.display === 'none' || replies.style.display === '') {
        replies.style.display = 'block';
        element.innerHTML = 'Hide thread';
    } else {
        replies.style.display = 'none';
        element.innerHTML = 'Expand entire thread';
    }
}
