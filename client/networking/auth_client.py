"""
Simple Authentication Client
Handles auth requests to server without full RoomClient connection
"""
import socket
import logging
from networking.network import Network, BUFFER_SIZE

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class AuthClient(Network):
    """Lightweight client cho authentication requests
    
    Kế thừa Network để dùng create_datagram và decode_data
    """
    
    def __init__(self, host_address='localhost', host_port=65432):
        self.host_address = host_address
        self.host_port = host_port
    
    def send_auth_request(self, action, username, password):
        """Gửi auth request tới server
        
        Args:
            action: 'login' hoặc 'register'
            username: Tên người dùng
            password: Mật khẩu
            
        Returns:
            Dict response từ server
        """
        try:
            # Tạo socket connection tạm thời
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host_address, self.host_port))
            
            # Gửi auth request với datagram format
            request = {
                'action': f'auth:{action}',
                'username': username,
                'password': password
            }
            
            datagram = self.create_datagram(BUFFER_SIZE, request)
            sock.sendall(datagram)
            
            # Nhận response
            response_data = sock.recv(BUFFER_SIZE)
            sock.close()
            
            if response_data:
                return self.decode_data(response_data)
            else:
                return {'success': False, 'message': 'No response from server'}
                
        except Exception as e:
            logging.error(f"Auth request error: {e}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }
