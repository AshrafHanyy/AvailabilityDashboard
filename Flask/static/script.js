document.addEventListener('DOMContentLoaded', function() {
    // Handle status button clicks
    document.querySelectorAll('.status-btn').forEach(button => {
        button.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            updateUserStatus(status);
        });
    });

    // Function to update status via AJAX
    function updateUserStatus(status) {
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
                console.log('Status updated successfully');
                // Note: We don't need to update the UI manually here
                // since we'll receive a socket update from the server
            } else {
                console.error('Error updating status:', data.message);
                alert('Failed to update status: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating status');
        });
    }
    
    // Add visual feedback for status buttons
    const statusButtons = document.querySelectorAll('.status-btn');
    statusButtons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = '';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Highlight active status based on user's current status
    const userSquare = document.querySelector('.my-square');
    if (userSquare) {
        const currentStatus = userSquare.getAttribute('data-status');
        const activeButton = document.querySelector(`.status-btn[data-status="${currentStatus}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }
});