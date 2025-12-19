"""
Main Controller - MVC Architecture (Client Side)
Handles all business logic via networking - NO direct database access
"""
from networking.room_client import RoomClient
from controllers.auth_controller import AuthController
from data.user_session import UserSession


class MainController:
    """Controller chính quản lý toàn bộ luồng ứng dụng (Client Side)
    
    CLIENT-SIDE ONLY:
    - Không truy cập database trực tiếp
    - Tất cả request gửi qua networking tới server
    - Server xử lý database và trả về kết quả
    
    Chức năng:
    - Xác thực: login, register, logout (qua server)
    - Kết nối: lobby, room
    - Phòng: create, join, leave, get_status
    - Thống kê: user_stats, recent_games, win_streak (qua server)
    
    Quản lý:
    - self.user: UserSession object (lưu local)
    - self.lobby_client: Kết nối lobby server
    - self.room_client: Kết nối room server
    - self.room: Phòng hiện tại
    """
    
    def __init__(self):
        """Khởi tạo MainController (Client Side)
        
        Khởi tạo các thuộc tính:
        - user: None (chưa đăng nhập)
        - lobby_client: None (chưa kết nối)
        - room_client: None (chưa vào phòng)
        - room: None (chưa có phòng)
        - auth_controller: AuthController() (xử lý xác thực qua networking)
        """
        self.user = None
        self.lobby_client = None
        self.room_client = None
        self.room = None
        self.auth_controller = AuthController()
    
    # Authentication methods
    def login(self, username, password):
        """Xử lý đăng nhập (Client Side - via networking)
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
        
        Returns:
            Dict: {'success': True/False, 'message': ..., 'user': ...}
        
        Luồng:
        1. Gửi auth request trực tiếp qua AuthClient
        2. Nhận user data từ server
        3. Kết nối lobby với user info
        """
        if not username or not password:
            return {'success': False, 'message': 'Please fill all fields'}
        
        # Gửi login request qua AuthClient
        response = self.auth_controller.login(username, password)
        
        if response['success']:
            # Tạo UserSession từ data server trả về
            self.user = UserSession(response['user'])
            # Kết nối lobby với authenticated user
            if not self._connect_to_lobby():
                return {
                    'success': False,
                    'message': 'Login successful but failed to connect to lobby'
                }
        
        return response
    
    def register(self, username, password):
        """Xử lý đăng ký tài khoản (Client Side - via networking)
        
        Args:
            username: Tên đăng nhập mong muốn
            password: Mật khẩu
        
        Returns:
            Dict: {'success': True/False, 'message': ..., 'user': ...}
        """
        if not username or not password:
            return {'success': False, 'message': 'Please fill all fields'}
        
        # Gửi register request qua AuthClient
        return self.auth_controller.register(username, password)
    
    def logout(self):
        """Xử lý đăng xuất (Client Side)
        
        Luồng:
        1. Gửi logout request tới server (server sẽ set offline)
        2. Ngắt kết nối lobby_client
        3. Xóa tất cả session data
        """
        # Gửi logout request tới server
        if self.lobby_client and self.user:
            try:
                self.lobby_client.send_data_to_server({
                    'action': 'auth:logout',
                    'user_id': self.user.id if hasattr(self.user, 'id') else self.user['id']
                })
            except Exception as e:
                print(f"[CONTROLLER] Logout error: {e}")
        
        # Ngắt kết nối
        if self.lobby_client:
            try:
                self.lobby_client.disconnect()
            except:
                pass
        
        self.lobby_client = None
        self.user = None
        self.room = None
        self.room_client = None
    
    # Connection methods
    def _connect_to_lobby(self):
        """Kết nối tới lobby server với authenticated user
        
        Tạo RoomClient với:
        - username: Tên người dùng
        - user_id: ID người dùng
        - room_id: None (chưa vào phòng)
        - host: localhost:65432
        
        Returns:
            True: Kết nối thành công
            False: Thất bại
        
        Private method (_ prefix) - chỉ dùng nội bộ
        """
        try:
            self.lobby_client = RoomClient(
                username=self.user.username if isinstance(self.user, UserSession) else self.user['username'],
                user_id=self.user.id if isinstance(self.user, UserSession) else self.user['id'],
                room_id=None,
                host_address='localhost',
                host_port=65432
            )
            
            if self.lobby_client.connect_to_server():
                print(f"[CONTROLLER] Connected to lobby as {self.user['username']}")
                return True
        except Exception as e:
            print(f"[CONTROLLER] Failed to connect to lobby: {e}")
            self.lobby_client = None
        
        return False
    
    def _connect_to_room(self, room_id):
        """Kết nối tới một phòng cụ thể
        
        Args:
            room_id: ID của phòng muốn tham gia
        
        Tạo RoomClient mới với:
        - username, user_id: Từ self.user
        - room_id: ID phòng
        - host: localhost:65432
        
        Returns:
            True: Kết nối thành công
            False: Thất bại
        
        Private method - dùng trong create_room() và join_room()
        """
        try:
            self.room_client = RoomClient(
                username=self.user['username'],
                user_id=self.user['id'],
                room_id=room_id,
                host_address='localhost',
                host_port=65432
            )
            
            if self.room_client.connect_to_server():
                print(f"[CONTROLLER] Connected to room {room_id}")
                return True
        except Exception as e:
            print(f"[CONTROLLER] Failed to connect to room: {e}")
            self.room_client = None
        
        return False
    
    # Room methods
    def create_room(self, room_name=None):
        """Tạo phòng chơi mới
        
        Args:
            room_name: Tên phòng (tùy chọn)
        
        Returns:
            Dict: {'success': True/False, 'room': {...}, 'message': ...}
        
        Luồng:
        1. Kiểm tra đã kết nối lobby chưa
        2. Gửi request 'create_room' tới server
        3. Nhận room_id từ server
        4. Nếu không có room_name: Tự động đặt 'Room #{room_id}'
        5. Lưu thông tin phòng vào self.room
        6. Kết nối tới phòng (_connect_to_room)
        7. Trả về kết quả
        """
        if not self.lobby_client:
            return {'success': False, 'message': 'Not connected to server'}
        
        try:
            response = self.lobby_client.send_data_to_server({'request': 'create_room'})
            room_id = response.get('room_id')
            
            if room_id:
                if not room_name:
                    room_name = f'Room #{room_id}'
                
                self.room = {
                    'id': room_id,
                    'room_name': room_name,
                    'host_username': self.user['username'],
                    'current_players': 1,
                    'max_players': 2
                }
                
                if self._connect_to_room(room_id):
                    return {'success': True, 'room': self.room}
            
            return {'success': False, 'message': 'Failed to create room'}
        except Exception as e:
            print(f"[CONTROLLER] Error creating room: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_rooms(self):
        """Lấy danh sách các phòng đang chờ
        
        Returns:
            Dict: {'success': True/False, 'rooms': [...], 'message': ...}
        
        Gửi request 'get_rooms' tới lobby server
        Server trả về list các phòng status='waiting' và chưa đầy
        
        Mỗi room chứa:
        - id, room_name, host_username
        - current_players, max_players
        - status, created_at
        """
        if not self.lobby_client:
            return {'success': False, 'message': 'Not connected to server', 'rooms': []}
        
        try:
            response = self.lobby_client.send_data_to_server({'request': 'get_rooms'})
            rooms = response.get('rooms', [])
            return {'success': True, 'rooms': rooms}
        except Exception as e:
            print(f"[CONTROLLER] Error getting rooms: {e}")
            return {'success': False, 'message': str(e), 'rooms': []}
    
    def join_room(self, room_data):
        """Tham gia một phòng đã tồn tại
        
        Args:
            room_data: Dict thông tin phòng từ get_rooms()
                      Phải có key 'id'
        
        Returns:
            Dict: {'success': True/False, 'room': {...}, 'message': ...}
        
        Luồng:
        1. Lưu room_data vào self.room
        2. Kết nối tới phòng bằng room_id
        3. Trả về kết quả
        """
        self.room = room_data
        
        if self._connect_to_room(room_data['id']):
            return {'success': True, 'room': self.room}
        else:
            return {'success': False, 'message': 'Failed to connect to room'}
    
    def leave_room(self):
        """Rời khỏi phòng hiện tại
        
        Luồng:
        1. Ngắt kết nối room_client
        2. Xóa room_client và room khỏi session
        3. Luôn trả về success=True
        
        Dùng try-except để tránh lỗi khi disconnect
        """
        if self.room_client:
            try:
                self.room_client.disconnect()
            except:
                pass
        
        self.room_client = None
        self.room = None
        return {'success': True}
    
    def get_room_status(self):
        """Get current room status"""
        if not self.room_client:
            return {'success': False, 'message': 'Not in a room'}
        
        try:
            # Get player count
            response = self.room_client.send_data_to_server({'request': 'game_data'})
            player_count = len(response) if isinstance(response, dict) else 0
            
            # Get game status
            status_response = self.room_client.send_data_to_server({'request': 'game_status'})
            game_status = status_response.get('game_status', 'waiting')
            
            status = {
                'player_count': player_count,
                'game_status': game_status,
                'game_started': game_status == 'ship_lock'
            }
            
            return {'success': True, 'status': status}
        except Exception as e:
            print(f"[CONTROLLER] Error getting room status: {e}")
            return {'success': False, 'message': str(e)}
    
    # Statistics methods
    def get_user_stats(self):
        """Lấy thống kê tổng hợp của người dùng
        
        Returns:
            Dict chứa:
            - total_games: Tổng số trận
            - total_wins, total_losses: Số thắng/thua
            - win_rate: Tỉ lệ thắng (%)
            - total_ships_sunk: Tổng tàu đánh chìm
            - total_hits, total_misses: Tổng trúng/trượt
            - avg_accuracy: Độ chính xác trung bình
            - best_streak: Chuỗi trúng dài nhất
            
            None nếu chưa login hoặc lỗi
        
        Gửi request 'get_user_stats' với user_id tới server
        """
        if not self.lobby_client or not self.user:
            return None
        
        try:
            response = self.lobby_client.send_data_to_server({
                'request': 'get_user_stats',
                'user_id': self.user['id']
            })
            return response.get('stats')
        except Exception as e:
            print(f"[CONTROLLER] Error getting stats: {e}")
            return None
    
    def get_recent_games(self, limit=10):
        """Lấy lịch sử các trận gần đây
        
        Args:
            limit: Số trận muốn lấy (mặc định 10)
        
        Returns:
            List các trận, mỗi trận chứa:
            - opponent_username: Tên đối thủ
            - result: 'win' hoặc 'lose'
            - ships_sunk: Số tàu đánh chìm
            - hits, misses: Trúng/trượt
            - accuracy: Độ chính xác (%)
            - max_streak: Chuỗi trúng dài nhất
            - played_at: Thời gian chơi
            
            [] nếu chưa login hoặc lỗi
        
        Sắp xếp theo played_at giảm dần (mới nhất trên cùng)
        """
        if not self.lobby_client or not self.user:
            return []
        
        try:
            response = self.lobby_client.send_data_to_server({
                'request': 'get_recent_games',
                'user_id': self.user['id'],
                'limit': limit
            })
            return response.get('games', [])
        except Exception as e:
            print(f"[CONTROLLER] Error getting recent games: {e}")
            return []
    
    def get_win_streak(self):
        """Get win streak data"""
        if not self.lobby_client or not self.user:
            return None
        
        try:
            response = self.lobby_client.send_data_to_server({
                'request': 'get_win_streak',
                'user_id': self.user['id']
            })
            return response.get('streak')
        except Exception as e:
            print(f"[CONTROLLER] Error getting win streak: {e}")
            return None
    
    # Getters
    def get_user(self):
        """Get current user"""
        return self.user
    
    def get_room(self):
        """Get current room"""
        return self.room
    
    def is_connected_to_lobby(self):
        """Check if connected to lobby"""
        return self.lobby_client is not None
    
    def is_in_room(self):
        """Check if in a room"""
        return self.room is not None and self.room_client is not None
