document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Define status colors
    const statusColors = {
        0: '#ff6b6b', // red
        1: '#ffd166', // yellow
        2: '#06d6a0'  // green
    };
    
    // Initialize grid squares
    const gridSquares = document.querySelectorAll('.grid-square');
    gridSquares.forEach(square => {
        const status = parseInt(square.getAttribute('data-status'));
        square.style.backgroundColor = statusColors[status];
    });
    
    // Function to update user status
    function updateStatus(status) {
        fetch('/api/update_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ status: status })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update my square
                const mySquare = document.querySelector('.my-square');
                if (mySquare) {
                    mySquare.setAttribute('data-status', status);
                    mySquare.style.backgroundColor = statusColors[status];
                }
                
                // Fetch updated grid data
                refreshGridData();
            } else {
                console.error('Failed to update status:', data.message);
            }
        })
        .catch(error => {
            console.error('Error updating status:', error);
        });
    }
    
    // Add event listeners to status buttons
    const statusButtons = document.querySelectorAll('.status-btn');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const status = parseInt(this.getAttribute('data-status'));
            updateStatus(status);
        });
    });
    
    // Function to filter grid by status
    function filterGrid(status) {
        if (status === 'all') {
            // Show all squares and fetch fresh data
            refreshGridData();
            return;
        }
        
        // Convert status to integer if it's not 'all'
        const statusInt = parseInt(status);
        
        fetch('/api/filter_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ status: statusInt })
        })
        .then(response => response.json())
        .then(data => {
            // First, hide all squares
            gridSquares.forEach(square => {
                square.style.opacity = '0.3';
            });
            
            // Then show only the squares with matching status
            data.forEach(square => {
                const gridSquare = document.querySelector(`.grid-square[data-id="${square.id}"]`);
                if (gridSquare) {
                    gridSquare.style.opacity = '1';
                }
            });
        })
        .catch(error => {
            console.error('Error filtering grid:', error);
        });
    }
    
    // Add event listeners to filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // First, remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            filterGrid(filter);
        });
    });
    
    // Function to refresh grid data
    function refreshGridData() {
        fetch('/api/grid_data')
        .then(response => response.json())
        .then(data => {
            data.forEach(square => {
                const gridSquare = document.querySelector(`.grid-square[data-id="${square.id}"]`);
                if (gridSquare) {
                    gridSquare.setAttribute('data-status', square.status);
                    gridSquare.style.backgroundColor = statusColors[square.status];
                    gridSquare.style.opacity = '1'; // Make sure all squares are visible
                }
            });
        })
        .catch(error => {
            console.error('Error fetching grid data:', error);
        });
    }
    
    // Export button functionality
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            window.location.href = '/api/export_csv';
        });
    }
    
    // Initial grid data refresh
    refreshGridData();
    
    // Set up periodic refresh every 10 seconds
    setInterval(refreshGridData, 10000);
});