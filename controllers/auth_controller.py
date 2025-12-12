"""
Authentication Controller
Handles user authentication logic
"""
from models.user_model import UserModel
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class AuthController:
    """Controller xử lý xác thực người dùng
    
    Chức năng:
    - Đăng nhập (login): Kiểm tra username + password
    - Đăng ký (register): Tạo tài khoản mới
    
    Không lưu trạng thái, chỉ xử lý logic
    Model (UserModel) làm việc với database
    """

    @staticmethod
    def login(username, password):
        """Xác thực đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
            
        Returns:
            Dict chứa:
            - success: True/False
            - message: Thông báo lỗi hoặc thành công
            - user: Thông tin người dùng (nếu thành công)
        
        Validate:
        1. Username và password không được rỗng
        2. Gọi UserModel.authenticate() để kiểm tra
        3. Kiểm tra tài khoản đã online chưa
        4. Set trạng thái online nếu đăng nhập thành công
        
        Lỗi có thể:
        - "Username and password are required"
        - "Account already logged in elsewhere"
        - "Invalid username or password"
        """
        if not username or not password:
            return {
                'success': False,
                'message': 'Username and password are required'
            }
        
        user = UserModel.authenticate(username, password)
        
        if user:
            # Check if already online
            if isinstance(user, dict) and user.get('error') == 'already_online':
                return {
                    'success': False,
                    'message': f'Account "{user.get("username")}" is already logged in elsewhere'
                }
            
            # Set user online
            UserModel.set_online_status(user['id'], True)
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user
            }
        else:
            return {
                'success': False,
                'message': 'Invalid username or password'
            }

    @staticmethod
    def register(username, password):
        """Đăng ký tài khoản mới
        
        Args:
            username: Tên đăng nhập mong muốn
            password: Mật khẩu
            
        Returns:
            Dict chứa:
            - success: True/False
            - message: Thông báo lỗi hoặc thành công
            - user: Thông tin người dùng (nếu thành công)
        
        Validate:
        1. Username và password không được rỗng
        2. Username phải từ 3-50 ký tự
        3. Password phải ít nhất 6 ký tự
        4. Username chưa tồn tại trong database
        
        Lỗi có thể:
        - "Username and password are required"
        - "Username must be between 3 and 50 characters"
        - "Password must be at least 6 characters"
        - "Username already exists"
        
        Nếu thành công: Tự động lấy thông tin user vừa tạo và trả về
        """
        if not username or not password:
            return {
                'success': False,
                'message': 'Username and password are required'
            }
        
        if len(username) < 3 or len(username) > 50:
            return {
                'success': False,
                'message': 'Username must be between 3 and 50 characters'
            }
        
        if len(password) < 6:
            return {
                'success': False,
                'message': 'Password must be at least 6 characters'
            }
        
        # Check if username already exists
        existing_user = UserModel.get_user_by_username(username)
        if existing_user:
            return {
                'success': False,
                'message': 'Username already exists'
            }
        
        user_id = UserModel.create_user(username, password)
        
        if user_id:
            user = UserModel.get_user_by_id(user_id)
            return {
                'success': True,
                'message': 'Registration successful',
                'user': user
            }
        else:
            return {
                'success': False,
                'message': 'Registration failed'
            }

    @staticmethod
    def get_user_info(user_id):
        """Get user information including stats"""
        user = UserModel.get_user_by_id(user_id)
        stats = UserModel.get_user_stats(user_id)
        
        if user and stats:
            return {
                'success': True,
                'user': user,
                'stats': stats
            }
        else:
            return {
                'success': False,
                'message': 'User not found'
            }
