"""
Authentication Controller - Client Side
Handles user authentication via server networking
NO direct database access - all auth goes through server
"""
import logging
from networking.auth_client import AuthClient

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class AuthController:
    """Controller xử lý xác thực người dùng (Client Side)
    
    Chức năng:
    - Đăng nhập (login): Gửi request tới server
    - Đăng ký (register): Gửi request tới server
    
    CLIENT KHÔNG truy cập database trực tiếp
    Tất cả auth được xử lý bởi server
    """

    def __init__(self, host_address='localhost', host_port=65432):
        """Khởi tạo với server info
        
        Args:
            host_address: Địa chỉ server
            host_port: Port server
        """
        self.auth_client = AuthClient(host_address, host_port)

    def login(self, username, password):
        """Xác thực đăng nhập qua server
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
            
        Returns:
            Dict chứa:
            - success: True/False
            - message: Thông báo lỗi hoặc thành công
            - user: Thông tin người dùng (nếu thành công)
        """
        if not username or not password:
            return {
                'success': False,
                'message': 'Username and password are required'
            }
        
        try:
            response = self.auth_client.send_auth_request('login', username, password)
            return response if response else {
                'success': False,
                'message': 'No response from server'
            }
        except Exception as e:
            logging.error(f"Login error: {e}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }

    def register(self, username, password):
        """Đăng ký tài khoản mới qua server
        
        Args:
            username: Tên đăng nhập mong muốn
            password: Mật khẩu
            
        Returns:
            Dict chứa:
            - success: True/False
            - message: Thông báo lỗi hoặc thành công
            - user: Thông tin người dùng (nếu thành công)
        
        Client-side validation trước khi gửi tới server
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
        
        try:
            response = self.auth_client.send_auth_request('register', username, password)
            return response if response else {
                'success': False,
                'message': 'No response from server'
            }
        except Exception as e:
            logging.error(f"Register error: {e}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }
