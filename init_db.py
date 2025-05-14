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
        
        # Create 7 grid squares for U-shaped layout
        grid_squares = []
        
        # Create 7 named squares (for U-shape)
        square_names = [
            "Slot 4", "Slot 3", "Slot 2", "Slot 1", "Slot 5", "Slot 6", "Slot 7"
        ]
        
        for i in range(7):
            square_id = i + 1
            square_name = square_names[i]
            grid_square = GridSquare(id=square_id, name=square_name, status=0)
            grid_squares.append(grid_square)
        
        db.session.add_all(grid_squares)
        db.session.commit()
        
        # Create users (7 regular, 3 admin)
        users = [
            # Admin users (not assigned to squares)
            User(
                username="admin1",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                grid_square_id=None
            ),
            User(
                username="admin2",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                grid_square_id=None
            ),
            User(
                username="admin3",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                grid_square_id=None
            ),
            # Regular users assigned to slots - user1 goes to Slot 1 (4th position)
            User(
                username="user1",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=4  # Slot 1
            ),
            User(
                username="user2",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=3  # Slot 2
            ),
            User(
                username="user3",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=2  # Slot 3
            ),
            User(
                username="user4",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=1  # Slot 4
            ),
            User(
                username="user5",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=5  # Slot 5
            ),
            User(
                username="user6",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=6  # Slot 6
            ),
            User(
                username="user7",
                password_hash=generate_password_hash("user123"),
                role="user",
                grid_square_id=7  # Slot 7
            )
        ]
        
        db.session.add_all(users)
        db.session.commit()
        
        # Update grid squares with user IDs
        # Mapping is now:
        # Slot 4 -> user4 (ID 7)
        # Slot 3 -> user3 (ID 6)
        # Slot 2 -> user2 (ID 5)
        # Slot 1 -> user1 (ID 4)
        # Slot 5 -> user5 (ID 8)
        # Slot 6 -> user6 (ID 9)
        # Slot 7 -> user7 (ID 10)
        grid_squares[0].user_id = 7  # Slot 4 -> user4
        grid_squares[1].user_id = 6  # Slot 3 -> user3
        grid_squares[2].user_id = 5  # Slot 2 -> user2
        grid_squares[3].user_id = 4  # Slot 1 -> user1
        grid_squares[4].user_id = 8  # Slot 5 -> user5
        grid_squares[5].user_id = 9  # Slot 6 -> user6
        grid_squares[6].user_id = 10 # Slot 7 -> user7
        
        db.session.commit()
        
        print("Database initialized successfully with:")
        print("- 3 admin users (not assigned to any slot)")
        print("- 7 regular users assigned to slots in U-shape:")
        print(f"  - Slot 1: user1 (ID: 4)")
        print(f"  - Slot 2: user2 (ID: 5)")
        print(f"  - Slot 3: user3 (ID: 6)")
        print(f"  - Slot 4: user4 (ID: 7)")
        print(f"  - Slot 5: user5 (ID: 8)")
        print(f"  - Slot 6: user6 (ID: 9)")
        print(f"  - Slot 7: user7 (ID: 10)")

if __name__ == "__main__":
    init_database()