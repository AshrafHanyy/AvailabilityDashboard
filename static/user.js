document.addEventListener('DOMContentLoaded', function() {
    const statusButtons = document.querySelectorAll('.status-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            updateStatus(status);
        });
    });

    function updateStatus(status) {
        fetch('/api/update_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ status: parseInt(status) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const userSquare = document.querySelector('.my-square');
                if (userSquare) {
                    userSquare.setAttribute('data-status', status);
                    // Force color update
                    userSquare.style.backgroundColor = '';
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
});