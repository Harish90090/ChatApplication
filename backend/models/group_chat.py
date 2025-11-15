from backend.database import get_db_connection

class GroupChat:
    @staticmethod
    def create(name, description, created_by):
        """Create a new group chat"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO group_chats (name, description, created_by) VALUES (%s, %s, %s)',
                    (name, description, created_by)
                )
                group_id = cursor.lastrowid
                
                # Add creator as member
                GroupChat.add_member(group_id, created_by)
                
                connection.commit()
                return group_id
        except Exception as e:
            print(f"Error creating group: {e}")
            connection.rollback()
            return None
        finally:
            connection.close()

    @staticmethod
    def add_member(group_id, user_id):
        """Add user to group"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT IGNORE INTO group_members (group_id, user_id) VALUES (%s, %s)',
                    (group_id, user_id)
                )
                connection.commit()
                return True
        except Exception as e:
            print(f"Error adding member to group: {e}")
            connection.rollback()
            return False
        finally:
            connection.close()

    @staticmethod
    def send_message(group_id, sender_id, content):
        """Send message to group"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''INSERT INTO messages (sender_id, group_id, message_type, content) 
                       VALUES (%s, %s, 'group', %s)''',
                    (sender_id, group_id, content)
                )
                message_id = cursor.lastrowid
                connection.commit()
                
                # Get message with sender info
                cursor.execute('''
                    SELECT m.*, u.username as sender_username, g.name as group_name
                    FROM messages m 
                    JOIN users u ON m.sender_id = u.id 
                    JOIN group_chats g ON m.group_id = g.id
                    WHERE m.id = %s
                ''', (message_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error sending group message: {e}")
            connection.rollback()
            return None
        finally:
            connection.close()

    @staticmethod
    def get_messages(group_id):
        """Get all messages in a group"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT m.*, u.username as sender_username
                    FROM messages m 
                    JOIN users u ON m.sender_id = u.id 
                    WHERE m.group_id = %s 
                    ORDER BY m.created_at ASC
                ''', (group_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting group messages: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def get_all_groups():
        """Get all group chats"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT gc.*, u.username as created_by_username,
                           (SELECT COUNT(*) FROM group_members gm WHERE gm.group_id = gc.id) as member_count
                    FROM group_chats gc
                    JOIN users u ON gc.created_by = u.id
                    ORDER BY gc.created_at DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting all groups: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def get_user_groups(user_id):
        """Get all groups a user is member of"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT gc.*, u.username as created_by_username
                    FROM group_chats gc
                    JOIN group_members gm ON gc.id = gm.group_id
                    JOIN users u ON gc.created_by = u.id
                    WHERE gm.user_id = %s
                    ORDER BY gc.name
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting user groups: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def get_group_members(group_id):
        """Get all members of a group"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT u.id, u.username, u.email
                    FROM group_members gm
                    JOIN users u ON gm.user_id = u.id
                    WHERE gm.group_id = %s
                ''', (group_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting group members: {e}")
            return []
        finally:
            connection.close()