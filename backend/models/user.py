import bcrypt
from backend.database import get_db_connection

class User:
    @staticmethod
    def create(username, email, password):
        """Create a new user"""
        connection = get_db_connection()
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',  # Changed to 'password'
                    (username, email, password_hash)
                )
                user_id = cursor.lastrowid
                connection.commit()
                return user_id, None
                
        except Exception as e:
            connection.rollback()
            if "Duplicate entry" in str(e):
                return None, "Username or email already exists"
            return None, f"Error creating user: {str(e)}"
        finally:
            connection.close()

    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        user = User.get_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):  # Changed to 'password'
            return user
        return None

    @staticmethod
    def get_all(exclude_user_id=None):
        """Get all users"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if exclude_user_id:
                    cursor.execute(
                        'SELECT id, username, email, created_at FROM users WHERE id != %s ORDER BY username',
                        (exclude_user_id,)
                    )
                else:
                    cursor.execute('SELECT id, username, email, created_at FROM users ORDER BY username')
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = %s', (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            connection.close()