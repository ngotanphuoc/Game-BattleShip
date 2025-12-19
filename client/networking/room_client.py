"""
Room-based Client
Enhanced client for room-based multiplayer
"""
import socket
import logging
from typing import Union, List, Tuple

from networking.network import Network, BUFFER_SIZE


logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class RoomClient(Network):
    """Client kết nối với server, hỗ trợ phòng chơi
    
    Chức năng:
    - Kết nối tới server game
    - Gửi/nhận dữ liệu qua Socket
    - Gửi lưới tàu (đặt tàu xong)
    - Bắn vào ô đối thủ
    - Lấy dữ liệu game (mỗi frame)
    """

    def __init__(self, username: str, user_id: int, room_id: int, host_address: str, host_port: int):
        self.is_disconnected = False
        self.username = username  # Tên đăng nhập
        self.user_id = user_id    # ID người dùng
        self.room_id = room_id    # ID phòng
        
        self.server_socket = None  # Socket kết nối
        self.host_port = host_port        # Port server (7777)
        self.host_address = host_address  # IP server (localhost)

    def connect_to_server(self) -> bool:
        """Kết nối tới server game
        
        Luồng:
        1. Tạo socket TCP
        2. Connect tới (host_address, host_port)
        3. Gửi thông tin: username, room_id
        4. Nhận ACK từ server
        
        Returns:
            True: Kết nối thành công
            False: Kết nối thất bại
        """
        try:
            self.host_port = int(self.host_port)

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.host_address, self.host_port))

            # Send connection data with username and room_id
            connection_data = {
                'username': self.username,
                'room_id': self.room_id,
                'user_id': self.user_id  # Gửi user_id để server lưu vào game_data
            }
            
            ack = self.send_data_to_server(connection_data)
            logging.info(f'Server ACK: {ack}')

            if ack and 'status' in ack and ack['status'] == 'connected':
                return True
            
            return False
            
        except TypeError as error:
            logging.error(error)
        except ValueError as error:
            logging.error(error)
        except socket.error as error:
            logging.error(error)

        return False

    def disconnect(self) -> None:
        """Ngắt kết nối với server
        
        Gửi request 'disconnect' cho server biết
        Đóng socket
        Đánh dấu is_disconnected = True
        """
        self.is_disconnected = True
        try:
            self.send_data_to_server({'request': 'disconnect'})
            # Small delay to ensure message is sent
            import time
            time.sleep(0.05)
        except:
            pass
        logging.info('Client disconnected')
        
        if self.server_socket:
            try:
                # Shutdown to flush pending data before closing
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.server_socket.close()
            except:
                pass

    def send_data_to_server(self, data: object) -> Union[dict, None]:
        """Gửi dữ liệu lên server và nhận response
        
        Args:
            data: Dict chứa request, ví dụ:
                {'request': 'attack_tile', 'position': (5, 3)}
                {'request': 'ship_locked', 'grid': [[...]]}
                {'request': 'timeout'}
        
        Returns:
            Dict response từ server hoặc None nếu lỗi
        
        Luồng:
        1. Encode data thành JSON bytes
        2. Gửi qua socket
        3. Chờ nhận response
        4. Decode response
        """
        try:
            message = self.create_datagram(BUFFER_SIZE, data)
            self.server_socket.sendall(message)

            response = self.server_socket.recv(BUFFER_SIZE)
            if response:
                return self.decode_data(response)
        except socket.error as e:
            logging.error(f'Socket error: {e}')
            self.is_disconnected = True

        return None

    def get_opponent_stats(self, opponent_username: str) -> Union[dict, None]:
        """Lấy thông tin thống kê của đối thủ từ server
        
        Args:
            opponent_username: Tên đối thủ cần lấy thông tin
        
        Returns:
            Dict chứa stats của đối thủ:
            {
                'total_games': int,
                'total_wins': int,
                'total_losses': int,
                'win_rate': float,
                'avg_accuracy': float,
                'total_ships_sunk': int,
                'best_streak': int,
                'current_streak': int
            }
            Hoặc None nếu lỗi
        
        Ví dụ:
            stats = client.get_opponent_stats("Player2")
            if stats:
                print(f"Win rate: {stats['win_rate']}%")
        """
        try:
            request = {
                'request': 'get_opponent_stats',
                'opponent_username': opponent_username
            }
            response = self.send_data_to_server(request)
            
            if response and response.get('success'):
                return response.get('stats')
            else:
                logging.error(f"Failed to get opponent stats: {response}")
                return None
        except Exception as e:
            logging.error(f"Error getting opponent stats: {e}")
            return None
    
    def lock_ships(self, game_grid: List[list]) -> None:
        """Gửi lưới tàu lên server (sau khi đặt tàu xong)
        
        Args:
            game_grid: Lười 10x10, mỗi ô là:
                - None: Nước
                - 'battleship', 'cruiser', ...: Tên tàu
        
        Ví dụ:
            [['battleship', 'battleship', None, ...],
             [None, 'cruiser', None, ...],
             ...]
        """
        self.send_data_to_server({'request': 'ship_locked', 'grid': game_grid})

    def attack_enemy_tile(self, position: Tuple[int, int]) -> str:
        """Bắn vào ô đối thủ
        
        Args:
            position: (col, row) - Tọa độ ô bắn
                Ví dụ: (5, 3) = cột F, hàng 4
        
        Returns:
            - ship_name: 'battleship', 'cruiser', ... nếu TRÚNG
            - None hoặc '': Nếu TRƯỢT
        
        Luồng:
        1. Gửi request 'attack_tile' + position
        2. Server kiểm tra lưới đối thủ
        3. Trả về kết quả
        4. Chuyển lượt
        """
        response = self.send_data_to_server({'request': 'attack_tile', 'position': position})
        if response:
            return response.get('attacked')
        return None

    def is_my_turn(self) -> bool:
        """Check if it is client turn"""
        game_data = self.get_game_data()
        if game_data and self.username in game_data:
            return game_data[self.username]['my_turn']
        return False

    def ship_sinked(self) -> None:
        """Notify that a ship is sinked"""
        self.send_data_to_server({'request': 'ship_sinked'})

    def get_game_data(self) -> Union[dict, None]:
        """Request current game data from server"""
        response = self.send_data_to_server({'request': 'game_data'})
        return response

    def get_game_status(self) -> Union[dict, None]:
        """Request game status from server"""
        response = self.send_data_to_server({'request': 'game_status'})
        return response

    def get_winner(self) -> Union[str, None]:
        """Request winner username from server"""
        response = self.send_data_to_server({'request': 'winner'})
        if response:
            return response.get('winner')
        return None
