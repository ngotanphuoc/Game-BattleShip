import socket
import logging
from typing import Union, List, Tuple

from networking.network import Network, BUFFER_SIZE


logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.NOTSET)


class Client(Network):
    """Class đại diện cho client instance (phiên bản cũ)
    
    Chức năng:
    - Kết nối đến server qua Socket TCP
    - Gửi/nhận dữ liệu (JSON qua socket)
    - Xử lý các request: attack_tile, ship_locked, game_data
    - Ngắt kết nối
    
    Lưu ý: Đây là phiên bản cũ, hiện tại dùng RoomClient
    """

    def __init__(self, client_name: str, host_address: str, host_port: int) -> None:
        self.is_disconnected = False
        self.client_name = client_name

        self.server_socket = None
        self.host_port = host_port
        self.host_address = host_address

    def connect_to_server(self) -> bool:
        """Tạo socket kết nối đến server game
        
        Luồng:
        1. Tạo socket TCP (AF_INET, SOCK_STREAM)
        2. Connect đến (host_address, host_port)
        3. Gửi client_name lên server
        4. Nhận ACK từ server
        
        Returns:
            True: Kết nối thành công
            False: Kết nối thất bại (TypeError, ValueError, socket.error)
        """

        try:
            self.host_port = int(self.host_port)

            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.host_address, self.host_port))

            ack = self.send_data_to_server(self.client_name)
            logging.info(f'Server ACK: {ack}')

            return True
        except TypeError as error:
            logging.error(error)
        except ValueError as error:
            logging.error(error)
        except socket.error as error:
            logging.error(error)

        return False

    def disconnect(self) -> None:
        """Gửi yêu cầu ngắt kết nối đến server
        
        - Đặt is_disconnected = True
        - Gửi {'request': 'disconnect'} cho server biết
        - Server sẽ dọn dẹp và đóng socket
        """

        self.is_disconnected = True
        self.send_data_to_server({'request': 'disconnect'})
        logging.info('Client disconnected')

    def send_data_to_server(self, data: object) -> Union[dict, None]:
        """Gửi dữ liệu và nhận response từ server
        
        Args:
            data: Dict chứa request, ví dụ:
                {'request': 'attack_tile', 'position': (5, 3)}
                {'request': 'game_data'}
        
        Returns:
            Dict response từ server hoặc None nếu lỗi
        
        Luồng:
        1. Encode data thành JSON bytes (create_datagram)
        2. Gửi qua socket (sendall)
        3. Chờ nhận response (recv)
        4. Decode response (decode_data)
        
        Nếu socket.error → đánh dấu is_disconnected = True
        """

        try:
            message = self.create_datagram(BUFFER_SIZE, data)
            self.server_socket.sendall(message)

            response = self.server_socket.recv(BUFFER_SIZE)
            if response:
                return self.decode_data(response)
        except socket.error:
            logging.info('Client disconnected by server')
            self.is_disconnected = True

        return None

    def lock_ships(self, game_grid: List[list]) -> None:
        """Thông báo server rằng client đã khóa tàu và gửi lưới game
        
        Args:
            game_grid: Lưới 10x10 với vị trí tàu
        
        Gửi request 'ship_locked' + grid lên server
        Server lưu lại và chờ người chơi khác
        """
        self.send_data_to_server({'request': 'ship_locked', 'grid': game_grid})

    def attack_enemy_tile(self, position: Tuple[float, float]) -> str:
        """Yêu cầu tấn công lưới địch
        
        Args:
            position: (col, row) - Tọa độ ô muốn bắn
        
        Returns:
            ship_name nếu TRÚNG, hoặc None/'' nếu TRƯỢT
        
        Gửi request 'attack_tile' + position
        Server kiểm tra và trả về kết quả
        """
        
        response = self.send_data_to_server({'request': 'attack_tile', 'position': position})
        return response.get('attacked')

    def is_my_turn(self) -> bool:
        """ This function checks if it is client turn. """

        game_data = self.get_game_data()
        return game_data[self.client_name]['my_turn']

    def ship_sinked(self) -> None:
        """Thông báo rằng một tàu đã chìm
        
        Gửi request 'ship_sinked' lên server
        Server kiểm tra xem đã chìm hết 5 tàu chưa → kết thúc game
        """
        self.send_data_to_server({'request': 'ship_sinked'})

    def get_game_data(self) -> Union[dict, None]:
        """Yêu cầu dữ liệu game hiện tại từ server
        
        Returns:
            Dict chứa:
            - my_turn: Lượt của tôi?
            - attacked_tile: Ô vừa bị tấn công
            - timeout_count: Số lần timeout
            - ship_sunk: Tên tàu vừa chìm
        
        Gọi mỗi frame để sync trạng thái với server
        """

        response = self.send_data_to_server({'request': 'game_data'})
        return response

    def get_game_status(self) -> Union[dict, None]:
        """ Request to server if game started. """

        response = self.send_data_to_server({'request': 'game_status'})
        return response.get('game_status')

    def get_winner(self) -> Union[dict, None]:
        """ Request to server winner username. """

        response = self.send_data_to_server({'request': 'winner'})
        return response.get('winner')

    def reset_game(self) -> None:
        """ Request to reset game. """
        self.send_data_to_server({'request': 'reset_game'})
    
    def get_opponent_stats(self, opponent_username: str) -> Union[dict, None]:
        """Lấy thống kê đối thủ từ server (lobby client)
        
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
        
        Sử dụng:
            stats = lobby_client.get_opponent_stats("Player2")
            if stats:
                print(f"Win rate: {stats['win_rate']}%")
        """
        try:
            response = self.send_data_to_server({
                'request': 'get_opponent_stats',
                'opponent_username': opponent_username
            })
            
            if response and response.get('success'):
                return response.get('stats')
            else:
                logging.error(f"Failed to get opponent stats: {response}")
                return None
        except Exception as e:
            logging.error(f"Error getting opponent stats: {e}")
            return None
