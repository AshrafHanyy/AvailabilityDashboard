document.addEventListener('DOMContentLoaded', function() {
    const statusButtons = document.querySelectorAll('.status-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            updateStatus(status);
            
            // Highlight the active button
            statusButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Ensure full opacity for all squares
            document.querySelectorAll('.grid-square').forEach(square => {
                square.style.opacity = '1';
            });
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
                    // Ensure full opacity
                    userSquare.style.opacity = '1';
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
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