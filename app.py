from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, emit, join_room
import sqlite3
import csv
import io
import os
from datetime import datetime
from models import db, User, GridSquare
from forms import LoginForm, UserCreateForm, UserEditForm
from config import Config


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)



# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Socket.IO with simpler configuration
# Remove eventlet dependency and use Flask's built-in server capabilities
# In app.py
# Database connection pooling (add to Config class in config.py)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'max_overflow': 10,
    'pool_timeout': 30
}

# In app.py (replace existing SocketIO init)
socketio = SocketIO(
    app,
    async_mode='eventlet',
    cors_allowed_origins="*",
    engineio_logger=True,  # Enable to see connection attempts
    max_http_buffer_size=10_000_000,  # Larger WebSocket packets
    ping_timeout=120,
    ping_interval=60,
    websocket=True,
    monkey_patch=True  # Critical for eventlet
)
socketio.SO_REUSEADDR = 1  # Allow address   
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    # Join a room based on user role if authenticated
    if current_user.is_authenticated:
        room = 'admin_room' if current_user.role == 'admin' else 'user_room'
        join_room(room)
        print(f'User {current_user.username} joined {room}')
    emit('connection_response', {'data': 'Connected successfully'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

# Socket.IO event for status updates
@socketio.on('status_change')
def handle_status_change(data):
    if current_user.is_authenticated:
        print(f'Status change from {current_user.username}: {data}')
        # Process the status change here
        grid_square = GridSquare.query.filter_by(id=current_user.grid_square_id).first()
        if grid_square:
            grid_square.status = data['status']
            db.session.commit()
            
            # Broadcast the update to all clients
            socketio.emit('status_update', {
                'square_id': grid_square.id,
                'status': grid_square.status,
                'user_id': current_user.id,
                'username': current_user.username,
                'square_name': grid_square.name
            })
            return {'success': True}
    return {'success': False}

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    grid_squares = GridSquare.query.all()
    user_square = GridSquare.query.filter_by(id=current_user.grid_square_id).first()
    
    if current_user.role == 'admin':
        return render_template('admin.html', grid_squares=grid_squares, user_square=user_square)
    else:
        return render_template('dashboard.html', grid_squares=grid_squares, user_square=user_square)

# API Endpoints
@app.route('/api/update_status', methods=['POST'])
@login_required
def update_status():
    data = request.get_json()
    status = data.get('status')
    
    if status not in [0, 1, 2]:
        return jsonify({'success': False, 'message': 'Invalid status value'}), 400
    
    grid_square = GridSquare.query.filter_by(id=current_user.grid_square_id).first()
    if grid_square:
        grid_square.status = status
        db.session.commit()
        
        # Broadcast the update to all clients
        socketio.emit('status_update', {
            'square_id': grid_square.id,
            'status': status,
            'user_id': current_user.id,
            'username': current_user.username,
            'square_name': grid_square.name
        })
        
        return jsonify({'success': True, 'message': 'Status updated'})
    
    return jsonify({'success': False, 'message': 'Grid square not found'}), 404

@app.route('/api/grid_data')
@login_required
def grid_data():
    grid_squares = GridSquare.query.all()
    result = []
    
    for square in grid_squares:
        result.append({
            'id': square.id,
            'name': square.name,
            'status': square.status,
            'user_id': square.user_id
        })
    
    return jsonify(result)

@app.route('/api/filter_status', methods=['POST'])
@login_required
def filter_status():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    status_filter = data.get('status')
    
    if status_filter is None:
        grid_squares = GridSquare.query.all()
    else:
        grid_squares = GridSquare.query.filter_by(status=status_filter).all()
    
    result = []
    for square in grid_squares:
        result.append({
            'id': square.id,
            'name': square.name,
            'status': square.status,
            'user_id': square.user_id
        })
    
    return jsonify(result)

@app.route('/api/export_csv')
@login_required
def export_csv():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['ID', 'Name', 'Status', 'User'])
    
    # Write data
    grid_squares = GridSquare.query.all()
    for square in grid_squares:
        user = User.query.filter_by(grid_square_id=square.id).first()
        username = user.username if user else 'Unassigned'
        status_text = ['Busy', 'Almost Ready', 'Available'][square.status]
        writer.writerow([square.id, square.name, status_text, username])
    
    # Create response
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'team_status_{timestamp}.csv'
    )

# Admin routes
@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    form = UserCreateForm()
    
    # Get available grid squares
    available_squares = GridSquare.query.filter(GridSquare.user_id.is_(None)).all()
    form.grid_square_id.choices = [(square.id, square.name) for square in available_squares]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            grid_square_id=form.grid_square_id.data
        )
        
        # Update the grid square with the user ID
        grid_square = GridSquare.query.get(form.grid_square_id.data)
        grid_square.user_id = user.id
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('user_form.html', form=form, title='Create User')

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    # Get available grid squares plus the user's current one
    available_squares = GridSquare.query.filter((GridSquare.user_id.is_(None)) | (GridSquare.id == user.grid_square_id)).all()
    form.grid_square_id.choices = [(square.id, square.name) for square in available_squares]
    
    if form.validate_on_submit():
        # Save old grid square ID to update it later
        old_grid_square_id = user.grid_square_id
        
        user.username = form.username.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        user.role = form.role.data
        user.grid_square_id = form.grid_square_id.data
        
        # Update grid squares
        if old_grid_square_id != form.grid_square_id.data:
            # Clear user_id from old grid square
            old_square = GridSquare.query.get(old_grid_square_id)
            if old_square:
                old_square.user_id = None
            
            # Set user_id on new grid square
            new_square = GridSquare.query.get(form.grid_square_id.data)
            if new_square:
                new_square.user_id = user.id
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('user_form.html', form=form, title='Edit User')

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Clear user_id from grid square
    grid_square = GridSquare.query.get(user.grid_square_id)
    if grid_square:
        grid_square.user_id = None
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin_users'))

# Handle when an admin updates someone else's status
@app.route('/api/admin_update_status', methods=['POST'])
@login_required
def admin_update_status():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    square_id = data.get('square_id')
    status = data.get('status')
    
    if status not in [0, 1, 2]:
        return jsonify({'success': False, 'message': 'Invalid status value'}), 400
    
    grid_square = GridSquare.query.filter_by(id=square_id).first()
    if grid_square:
        grid_square.status = status
        db.session.commit()
        
        # Get the username of the grid square owner
        user = User.query.filter_by(grid_square_id=square_id).first()
        username = user.username if user else 'Unassigned'
        
        # Broadcast the update to all clients
        socketio.emit('status_update', {
            'square_id': grid_square.id,
            'status': status,
            'user_id': user.id if user else None,
            'username': username,
            'square_name': grid_square.name,
            'updated_by_admin': True
        })
        
        return jsonify({'success': True, 'message': 'Status updated by admin'})
    
    return jsonify({'success': False, 'message': 'Grid square not found'}), 404
# Modify the __main__ block at the bottom to:
if __name__ == '__main__':
    def get_local_ip():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '0.0.0.0'  # Bind to all interfaces
        finally:
            s.close()
        return IP
    port = 94
    print(f"\nAccess the app at: http://{get_local_ip()}:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)