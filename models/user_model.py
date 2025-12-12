"""
User Model
Handles user authentication and user data management
"""
from datetime import datetime
from models.base_model import BaseModel
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class UserModel(BaseModel):
    """Model quản lý dữ liệu người dùng
    
    Kế thừa từ BaseModel để dùng execute_query()
    
    Chức năng:
    - Tạo tài khoản mới (create_user)
    - Xác thực đăng nhập (authenticate)
    - Lấy thông tin user theo ID/username
    - Cập nhật trạng thái online/offline
    
    Bảng database: users
    Cột: id, username, password, created_at, is_online
    """

    @staticmethod
    def create_user(username, password):
        """Tạo tài khoản mới
        
        Args:
            username: Tên đăng nhập (unique)
            password: Mật khẩu (plain text, chưa hash)
        
        Returns:
            user_id: ID người dùng vừa tạo
            None: Nếu thất bại (username tồn tại / lỗi DB)
        
        Lưu ý: Password nên hash trước khi lưu (bcrypt)
        Hiện tại lưu plain text - KHÔNG AN TOÀN cho production!
        
        Query: INSERT INTO users (username, password, is_online=0)
        """
        query = "INSERT INTO users (username, password, is_online) VALUES (%s, %s, 0)"
        try:
            user_id = BaseModel.execute_query(query, (username, password), commit=True)
            logging.info(f"User '{username}' created with ID: {user_id}")
            return user_id
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return None

    @staticmethod
    def authenticate(username, password):
        """Xác thực đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
        
        Returns:
            Dict user: {'id', 'username', 'created_at', 'is_online'}
            Dict error: {'error': 'already_online', 'username': ...}
            None: Sai tên/mật khẩu
        
        Kiểm tra:
        1. Username + password khớp trong DB
        2. User chưa online (tránh đa đăng nhập)
        
        Query: SELECT id, username, created_at, is_online 
               WHERE username=%s AND password=%s
        """
        query = "SELECT id, username, created_at, is_online FROM users WHERE username = %s AND password = %s"
        try:
            user = BaseModel.execute_query(query, (username, password), fetch_one=True)
            
            if user:
                # Kiểm tra đã online chưa
                if user.get('is_online') == 1:
                    logging.warning(f"User '{username}' is already online")
                    return {'error': 'already_online', 'username': username}
                
                logging.info(f"User '{username}' authenticated successfully")
            
            return user
        except Exception as e:
            logging.error(f"Error authenticating user: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """Lấy thông tin người dùng theo ID
        
        Args:
            user_id: ID người dùng
        
        Returns:
            Dict: {'id', 'username', 'created_at'}
            None: Không tìm thấy hoặc lỗi
        
        Query: SELECT id, username, created_at WHERE id=%s
        """
        query = "SELECT id, username, created_at FROM users WHERE id = %s"
        try:
            return BaseModel.execute_query(query, (user_id,), fetch_one=True)
        except Exception as e:
            logging.error(f"Error getting user by ID: {e}")
            return None

    @staticmethod
    def get_user_by_username(username):
        """Lấy thông tin người dùng theo tên đăng nhập
        
        Args:
            username: Tên đăng nhập
        
        Returns:
            Dict: {'id', 'username', 'created_at', 'is_online'}
            None: Không tìm thấy hoặc lỗi
        
        Dùng để kiểm tra username đã tồn tại chưa khi đăng ký
        
        Query: SELECT id, username, created_at, is_online WHERE username=%s
        """
        query = "SELECT id, username, created_at, is_online FROM users WHERE username = %s"
        try:
            return BaseModel.execute_query(query, (username,), fetch_one=True)
        except Exception as e:
            logging.error(f"Error getting user by username: {e}")
            return None
    
    @staticmethod
    def set_online_status(user_id, is_online):
        """Cập nhật trạng thái online/offline
        
        Args:
            user_id: ID người dùng
            is_online: True = online, False = offline
        
        Sử dụng:
        - Sau khi đăng nhập: set_online_status(user_id, True)
        - Khi thoát game: set_online_status(user_id, False)
        
        Tránh đa đăng nhập cùng 1 tài khoản
        """
        query = "UPDATE users SET is_online = %s WHERE id = %s"
        try:
            BaseModel.execute_query(query, (1 if is_online else 0, user_id), commit=True)
            logging.info(f"User {user_id} online status set to {is_online}")
            return True
        except Exception as e:
            logging.error(f"Error setting online status: {e}")
            return False