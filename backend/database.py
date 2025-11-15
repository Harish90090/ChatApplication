import pymysql
import pymysql.cursors
from backend.config import config

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            port=config.MYSQL_PORT,
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            autocommit=False
        )
        print("Database connection successful!")
        return connection
    except pymysql.err.OperationalError as e:
        print(f"Database connection failed: {e}")
        print("Please check your MySQL credentials in config.py")
        raise

def init_db():
    """Initialize database and create all tables"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            
            # First, check if tables exist and drop them if they do (for clean setup)
            cursor.execute("DROP TABLE IF EXISTS messages")
            cursor.execute("DROP TABLE IF EXISTS group_members")
            cursor.execute("DROP TABLE IF EXISTS private_chats")
            cursor.execute("DROP TABLE IF EXISTS group_chats")
            cursor.execute("DROP TABLE IF EXISTS users")
            
            # Users table - FIXED: Using password instead of password_hash
            cursor.execute('''
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,  -- Changed from password_hash to password
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print(" Users table created")
            
            # Group chats table
            cursor.execute('''
                CREATE TABLE group_chats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Group chats table created")
            
            # Group members table
            cursor.execute('''
                CREATE TABLE group_members (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    group_id INT,
                    user_id INT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_member (group_id, user_id)
                )
            ''')
            print("Group members table created")
            
           #privatechat table
            cursor.execute('''
                CREATE TABLE private_chats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user1_id INT,
                    user2_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_private_chat (user1_id, user2_id)
                )
            ''')
            print(" Private chats table created")
            
          #message table
            cursor.execute('''
                CREATE TABLE messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT,
                    receiver_id INT,
                    group_id INT,
                    message_type ENUM('private', 'group') NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Msg table created")
            
        connection.commit()
        print("database tables created successfully")
        
    except Exception as e:
        print(f" Error on creating database TABLE: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()