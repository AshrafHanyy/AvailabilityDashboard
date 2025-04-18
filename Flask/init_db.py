from app import app, db
from models import User, GridSquare
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have data
        if User.query.count() > 0:
            print("Database already initialized. Skipping.")
            return
        
        # Create grid squares
        grid_squares = []
        for row in range(1, 7):
            for col in range(1, 7):
                square_id = (row - 1) * 6 + col
                square_name = f"U-{square_id:03d}"
                grid_square = GridSquare(id=square_id, name=square_name, status=0)
                grid_squares.append(grid_square)
        
        db.session.add_all(grid_squares)
        db.session.commit()
        
        # Create test users (3 regular, 1 admin)
        users = [
            User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                grid_square_id=1  # U-001
            ),
            User(
                username="user1",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=2  # U-002
            ),
            User(
                username="user2",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=3  # U-003
            ),
            User(
                username="user3",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=4  # U-004
            )
        ]
        
        db.session.add_all(users)
        db.session.commit()
        
        # Update grid squares with user IDs
        grid_squares[0].user_id = 1  # admin
        grid_squares[1].user_id = 2  # user1
        grid_squares[2].user_id = 3  # user2
        grid_squares[3].user_id = 4  # user3
        
        db.session.commit()
        
        print("Database initialized successfully with test users and grid squares.")

if __name__ == "__main__":
    init_database()