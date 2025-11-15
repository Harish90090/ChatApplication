from backend.database import get_db_connection

class PrivateChat:
    @staticmethod
    def get_or_create(user1_id, user2_id):
        """Get existing private chat or create new one"""
        connection = get_db_connection()
        try:
            # Ensure consistent ordering
            sorted_users = sorted([user1_id, user2_id])
            user1_id, user2_id = sorted_users[0], sorted_users[1]
            
            with connection.cursor() as cursor:
                # Check if chat exists
                cursor.execute(
                    'SELECT * FROM private_chats WHERE user1_id = %s AND user2_id = %s',
                    (user1_id, user2_id)
                )
                chat = cursor.fetchone()
                
                if not chat:
                    # Create new chat
                    cursor.execute(
                        'INSERT INTO private_chats (user1_id, user2_id) VALUES (%s, %s)',
                        (user1_id, user2_id)
                    )
                    connection.commit()
                    chat_id = cursor.lastrowid
                    
                    # Get the created chat
                    cursor.execute('SELECT * FROM private_chats WHERE id = %s', (chat_id,))
                    chat = cursor.fetchone()
                
                return chat
        except Exception as e:
            print(f"Error in get_or_create private chat: {e}")
            connection.rollback()
            return None
        finally:
            connection.close()

    @staticmethod
    def send_message(sender_id, receiver_id, content):
        """Send private message"""
        connection = get_db_connection()
        try:
            # Ensure chat exists
            PrivateChat.get_or_create(sender_id, receiver_id)
            
            with connection.cursor() as cursor:
                cursor.execute(
                    '''INSERT INTO messages (sender_id, receiver_id, message_type, content) 
                       VALUES (%s, %s, 'private', %s)''',
                    (sender_id, receiver_id, content)
                )
                message_id = cursor.lastrowid
                connection.commit()
                
                # Get message with sender info
                cursor.execute('''
                    SELECT m.*, u.username as sender_username 
                    FROM messages m 
                    JOIN users u ON m.sender_id = u.id 
                    WHERE m.id = %s
                ''', (message_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error sending private message: {e}")
            connection.rollback()
            return None
        finally:
            connection.close()

    @staticmethod
    def get_messages(user1_id, user2_id):
        """Get all messages between two users"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT m.*, u.username as sender_username 
                    FROM messages m 
                    JOIN users u ON m.sender_id = u.id 
                    WHERE ((m.sender_id = %s AND m.receiver_id = %s) 
                           OR (m.sender_id = %s AND m.receiver_id = %s))
                    AND m.message_type = 'private'
                    ORDER BY m.created_at ASC
                ''', (user1_id, user2_id, user2_id, user1_id))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting private messages: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def get_user_chats(user_id):
        """Get all private chats for a user"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT pc.*, 
                           CASE 
                               WHEN pc.user1_id = %s THEN u2.username 
                               ELSE u1.username 
                           END as other_user_username,
                           CASE 
                               WHEN pc.user1_id = %s THEN u2.id 
                               ELSE u1.id 
                           END as other_user_id
                    FROM private_chats pc
                    JOIN users u1 ON pc.user1_id = u1.id
                    JOIN users u2 ON pc.user2_id = u2.id
                    WHERE pc.user1_id = %s OR pc.user2_id = %s
                ''', (user_id, user_id, user_id, user_id))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting user chats: {e}")
            return []
        finally:
            connection.close()