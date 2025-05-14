document.addEventListener('DOMContentLoaded', function() {
    // Handle status button clicks
    const statusButtons = document.querySelectorAll('.status-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            
            // Update status via API
            updateUserStatus(status);
            
            // Highlight the active button
            statusButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Ensure full opacity for all squares
            document.querySelectorAll('.grid-square').forEach(square => {
                square.style.opacity = '1';
            });
        });

        // Add visual feedback for button presses
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
                // The socket update will handle the UI changes
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
    
    // Highlight current status button on load
    const userSquare = document.querySelector('.my-square');
    if (userSquare) {
        const currentStatus = userSquare.getAttribute('data-status');
        const activeButton = document.querySelector(`.status-btn[data-status="${currentStatus}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Ensure full opacity on load
        document.querySelectorAll('.grid-square').forEach(square => {
            square.style.opacity = '1';
        });
    }
});