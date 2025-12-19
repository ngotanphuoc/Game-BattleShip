"""
Refactored Game Server with Room Management
Supports multiple game rooms running simultaneously
"""
import enum
import socket
import logging
from typing import Dict, List, Tuple
from threading import Thread, Lock

from networking.network import Network, BUFFER_SIZE, SHIPS_NAMES
from models.game_history_model import GameHistoryModel


logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class GameStatus(enum.Enum):
    """Trạng thái của phòng game
    
    - waiting: Chờ người chơi thứ 2 tham gia
    - ship_lock: Đang đặt tàu (chờ cả 2 lock ships)
    - battle: Chiến đấu (2 người bắn luân phiên)
    - finished: Game kết thúc (có winner)
    """
    waiting = 1
    ship_lock = 2
    battle = 3
    finished = 4


class GameRoom:
    """Biểu diễn một phòng game
    
    Thuộc tính:
    - room_id: ID phòng (do server tạo)
    - room_name: Tên phòng (ví dụ: "Player1's Room")
    - host_username: Người tạo phòng
    - status: GameStatus (waiting/ship_lock/battle/finished)
    - is_first_player: Flag để phân biệt người vào trước (chơi trước)
    - lock: Thread lock cho thread-safe
    - game_data: Dict chứa:
        * winner: Tên người thắng
        * game_grid: {username: grid_10x10}
        * clients: {username: {attacked_tile, sinked_ships, my_turn, timeout_count, ...}}
        * sockets: {username: socket}
    
    Chức năng:
    - add_client(): Thêm người chơi vào phòng
    - remove_client(): Xóa người chơi (disconnect hoặc quit)
    - attack_enemy_tile(): Xử lý tấn công, trả về hit/miss
    - game_over(): Đặt winner và chuyển status thành finished
    - check_ships_locked(): Kiểm tra cả 2 người đã lock ships chưa
    
    Thread-safety: Dùng Lock() cho mọi thao tác thay đổi game_data
    """
    
    def __init__(self, room_id: int, room_name: str, host_username: str):
        """Khởi tạo phòng game mới
        
        Args:
            room_id: ID phòng (server assign)
            room_name: Tên phòng
            host_username: Người tạo phòng
        """
        self.room_id = room_id
        self.room_name = room_name
        self.host_username = host_username
        self.status = GameStatus.waiting
        self.is_first_player = True
        self.lock = Lock()
        
        self.game_data = {
            'winner': None,
            'game_grid': {},
            'clients': {},
            'sockets': {}
        }
    
    def add_client(self, username: str, client_socket: socket.socket, user_id: int = None):
        """Add a client to this room"""
        with self.lock:
            self.game_data['clients'][username] = {
                'user_id': user_id,  # Lưu user_id để save game history
                'attacked_tile': {
                    'ship_name': None,
                    'position': None
                },
                'sinked_ships': 0,
                'ship_locked': False,
                'my_turn': self.is_first_player,
                'timeout_count': 0
            }
            self.game_data['game_grid'][username] = None
            self.game_data['sockets'][username] = client_socket
            self.is_first_player = False
            
            # If we have 2 players, move to ship_lock stage
            if len(self.game_data['clients']) == 2:
                self.status = GameStatus.ship_lock
    
    def remove_client(self, username: str):
        """Remove a client from this room"""
        with self.lock:
            # If game is in progress and someone disconnects, other player wins
            if self.status == GameStatus.battle and not self.game_data['winner']:
                # Get the other player's username
                remaining_players = [u for u in self.game_data['clients'].keys() if u != username]
                if remaining_players:
                    winner = remaining_players[0]
                    self.game_data['winner'] = winner
                    logging.info(f'[ROOM] {username} disconnected during battle - {winner} wins!')
            
            self.game_data['clients'].pop(username, None)
            self.game_data['sockets'].pop(username, None)
            self.game_data['game_grid'].pop(username, None)
    
    def get_client_count(self):
        """Get number of clients in room"""
        with self.lock:
            return len(self.game_data['clients'])
    
    def check_all_ready(self):
        """Check if all players are ready"""
        with self.lock:
            if len(self.game_data['clients']) < 2:
                return False
            return all(client['ready'] for client in self.game_data['clients'].values())
    
    def set_ready(self, username: str, is_ready: bool):
        """Set player ready status"""
        with self.lock:
            if username in self.game_data['clients']:
                self.game_data['clients'][username]['ready'] = is_ready
                logging.info(f"[ROOM {self.room_id}] Player {username} ready: {is_ready}")
                
                # Check if all players ready and transition to ship_lock
                if self.check_all_ready() and self.status == GameStatus.waiting:
                    self.status = GameStatus.ship_lock
                    logging.info(f"[ROOM {self.room_id}] All players ready, starting game!")
    
    def is_empty(self):
        """Check if room is empty"""
        return self.get_client_count() == 0
    
    def check_ships_locked(self):
        """Check if all clients locked their ships"""
        with self.lock:
            return all(
                self.game_data['game_grid'][username] is not None
                for username in self.game_data['game_grid']
            )
    
    def attack_enemy_tile(self, attacker_name: str, position: Tuple[int, int]) -> str:
        """Process attack on enemy tile"""
        with self.lock:
            enemy_grid = None
            enemy_name = None
            for username in self.game_data['clients']:
                if username != attacker_name:
                    enemy_grid = self.game_data['game_grid'][username]
                    enemy_name = username
            
            print(f"[SERVER] Attack from {attacker_name} at position {position}")
            print(f"[SERVER] Enemy grid at [{position[1]}][{position[0]}]: '{enemy_grid[position[1]][position[0]]}'")
            print(f"[SERVER] SHIPS_NAMES: {SHIPS_NAMES}")
            print(f"[SERVER] Is in SHIPS_NAMES: {enemy_grid[position[1]][position[0]] in SHIPS_NAMES}")
            
            if enemy_grid and enemy_grid[position[1]][position[0]] in SHIPS_NAMES:
                # HIT - keep attacker's turn
                ship_name = enemy_grid[position[1]][position[0]]
                enemy_grid[position[1]][position[0]] = 'X'
                
                print(f"[SERVER] HIT! Ship: '{ship_name}'")
                
                # Check if this ship is completely sunk
                ship_still_alive = False
                for row in enemy_grid:
                    for cell in row:
                        if cell == ship_name:
                            ship_still_alive = True
                            break
                    if ship_still_alive:
                        break
                
                # If ship is sunk, notify the victim
                if not ship_still_alive:
                    print(f"[SERVER] {ship_name} is SUNK! Notifying {enemy_name}")
                    self.game_data['clients'][enemy_name]['ship_sunk'] = ship_name
                
                # Keep turn for attacker
                self.game_data['clients'][attacker_name]['my_turn'] = True
                self.game_data['clients'][enemy_name]['my_turn'] = False
                
                return ship_name
            else:
                # MISS - switch turns
                print(f"[SERVER] MISS!")
                self.game_data['clients'][attacker_name]['my_turn'] = False
                self.game_data['clients'][enemy_name]['my_turn'] = True
            
            return None
    
    def game_over(self, loser_name: str):
        """Set winner when game is over"""
        with self.lock:
            winner_name = next(
                (username for username in self.game_data['clients'] if username != loser_name),
                None
            )
            self.game_data['winner'] = winner_name
            self.status = GameStatus.finished
            print(f"[SERVER] Game over: {winner_name} wins, {loser_name} loses")


class RoomServer(Network):
    """Server game đa phòng
    
    Chức năng chính:
    - Lắng nghe kết nối từ client (localhost:65432)
    - Quản lý nhiều phòng game đồng thời (rooms dict)
    - Xử lý 2 loại kết nối:
      * Lobby client: Chưa vào phòng, browse rooms, tạo phòng
      * Room client: Đã vào phòng, chơi game
    - Assign room_id cho phòng mới (next_room_id)
    - Xử lý các request:
      * create_room, get_rooms, join_room
      * ship_locked, attack_tile, timeout
      * save_game_history, get_user_stats
      * player_quit, disconnect
    - Thread-safe operations với Lock()
    
    Thuộc tính:
    - server_socket: Socket lắng nghe chính
    - rooms: Dict {room_id: GameRoom}
    - client_rooms: Dict {username: room_id}
    - lobby_clients: Dict {username: socket}
    - next_room_id: Bộ đếm tự tăng cho room ID
    - lock: Thread lock
    
    Multi-threading:
    - Mỗi client có 1 thread riêng (handle_client)
    - Accept thread chạy liên tục (accept_connections)
    - GameRoom có lock riêng để đồng bộ
    """
    
    def __init__(self, host_address: str, host_port: int):
        self.server_socket = None
        self.host_address = host_address
        self.host_port = host_port
        self.rooms: Dict[int, GameRoom] = {}
        self.client_rooms: Dict[str, int] = {}  # username -> room_id mapping
        self.lobby_clients: Dict[str, socket.socket] = {}  # username -> socket for lobby users
        self.lock = Lock()
        self.next_room_id = 1  # Server-side room ID counter
    
    def handle_auth_request(self, client_socket: socket.socket, request_data: dict):
        """Xử lý auth requests (login/register)
        
        Args:
            client_socket: Socket của client
            request_data: Dict chứa action, username, password
        """
        from models.user_model import UserModel
        
        action = request_data.get('action')
        username = request_data.get('username')
        password = request_data.get('password')
        
        try:
            if action == 'auth:login':
                # Xử lý login
                user = UserModel.authenticate(username, password)
                
                if user:
                    # Check if already online
                    if isinstance(user, dict) and user.get('error') == 'already_online':
                        response = {
                            'success': False,
                            'message': f'Account "{user.get("username")}" is already logged in elsewhere'
                        }
                    else:
                        # Set user online
                        UserModel.set_online_status(user['id'], True)
                        response = {
                            'success': True,
                            'message': 'Login successful',
                            'user': user
                        }
                else:
                    response = {
                        'success': False,
                        'message': 'Invalid username or password'
                    }
            
            elif action == 'auth:register':
                # Kiểm tra username đã tồn tại
                existing_user = UserModel.get_user_by_username(username)
                if existing_user:
                    response = {
                        'success': False,
                        'message': 'Username already exists'
                    }
                else:
                    # Tạo user mới
                    user_id = UserModel.create_user(username, password)
                    
                    if user_id:
                        user = UserModel.get_user_by_id(user_id)
                        response = {
                            'success': True,
                            'message': 'Registration successful',
                            'user': user
                        }
                    else:
                        response = {
                            'success': False,
                            'message': 'Registration failed'
                        }
            
            elif action == 'auth:logout':
                # Xử lý logout
                user_id = request_data.get('user_id')
                if user_id:
                    UserModel.set_online_status(user_id, False)
                response = {
                    'success': True,
                    'message': 'Logged out'
                }
            
            else:
                response = {
                    'success': False,
                    'message': 'Unknown auth action'
                }
            
            # Gửi response
            self.send_data(client_socket, response)
            
        except Exception as e:
            logging.error(f'Auth error: {e}')
            self.send_data(client_socket, {
                'success': False,
                'message': f'Server error: {str(e)}'
            })
        finally:
            # Đóng socket sau khi xử lý auth (không giữ connection)
            try:
                client_socket.close()
            except:
                pass
    
    def start_server(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host_address, self.host_port))
        self.server_socket.listen(10)
        
        server_thread = Thread(target=self.accept_connections)
        server_thread.daemon = True
        server_thread.start()
        
        logging.info(f'Room Server started on {self.host_address}:{self.host_port}')
    
    def stop_server(self):
        """Stop the server"""
        with self.lock:
            # Close all client connections in rooms
            for room in self.rooms.values():
                for client_socket in room.game_data['sockets'].values():
                    try:
                        client_socket.shutdown(socket.SHUT_RDWR)
                        client_socket.close()
                    except:
                        pass
            
            # Close all lobby connections
            for client_socket in self.lobby_clients.values():
                try:
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                except:
                    pass
            
            self.rooms.clear()
            self.client_rooms.clear()
            self.lobby_clients.clear()
        
        if self.server_socket:
            self.server_socket.close()
        
        logging.info('Server stopped')
    
    def accept_connections(self):
        """Accept incoming client connections"""
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                client_thread = Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
        except socket.error as e:
            logging.error(f'Server accept error: {e}')
    
    def handle_client(self, client_socket: socket.socket, address):
        """Handle individual client connection"""
        username = None
        room_id = None
        in_lobby = False
        
        try:
            # Receive initial connection data (username and room_id)
            data = client_socket.recv(BUFFER_SIZE)
            connection_data = self.decode_data(data)
            
            # Check if this is an auth request
            action = connection_data.get('action')
            if action and action.startswith('auth:'):
                self.handle_auth_request(client_socket, connection_data)
                return
            
            username = connection_data.get('username')
            room_id = connection_data.get('room_id')
            user_id = connection_data.get('user_id')  # Lấy user_id từ connection data
            
            if not username:
                logging.warning(f'Invalid connection data from {address}')
                client_socket.close()
                return
            
            # Check if this is a lobby connection (no room_id)
            if room_id is None:
                in_lobby = True
                with self.lock:
                    self.lobby_clients[username] = client_socket
                
                logging.info(f'Client "{username}" connected to lobby from {address}')
                self.send_data(client_socket, {'status': 'connected', 'mode': 'lobby'})
                
                # Keep connection alive for lobby user
                self.lobby_listener(client_socket, username)
                return
            
            # Room connection (existing logic)
            # Get or create room
            room = self.get_or_create_room(room_id, username)
            
            if not room:
                self.send_data(client_socket, {'error': 'Room is full or invalid'})
                client_socket.close()
                return
            
            # Add client to room
            room.add_client(username, client_socket, user_id)
            self.client_rooms[username] = room_id
            
            logging.info(f'Client "{username}" joined room {room_id} from {address}')
            
            # Send connection acknowledgment
            self.send_data(client_socket, {'status': 'connected', 'room_id': room_id})
            
            # Handle client messages
            self.client_listener(client_socket, username, room)
            
        except Exception as e:
            logging.error(f'Error handling client {username}: {e}')
        finally:
            # Cleanup
            if in_lobby and username:
                with self.lock:
                    self.lobby_clients.pop(username, None)
                logging.info(f'Lobby client {username} disconnected')
            elif username and room_id is not None:
                room = self.rooms.get(room_id)
                if room:
                    room.remove_client(username)
                    if room.is_empty():
                        with self.lock:
                            self.rooms.pop(room_id, None)
                        logging.info(f'Room {room_id} deleted (empty)')
                
                self.client_rooms.pop(username, None)
            
            try:
                client_socket.close()
            except:
                pass
    
    def lobby_listener(self, client_socket: socket.socket, username: str):
        """Listen to lobby client (keeps connection alive)"""
        try:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                decoded_data = self.decode_data(data)
                
                # Handle action-based requests (như auth:logout)
                if 'action' in decoded_data:
                    action = decoded_data.get('action')
                    if action == 'auth:logout':
                        try:
                            from models.user_model import UserModel
                            user_id = decoded_data.get('user_id')
                            if user_id:
                                UserModel.set_online_status(user_id, False)
                                logging.info(f'User {user_id} logged out via lobby')
                            self.send_data(client_socket, {'success': True})
                        except Exception as e:
                            logging.error(f'Logout error: {e}')
                            self.send_data(client_socket, {'success': False, 'error': str(e)})
                    continue
                
                # Handle lobby requests
                if 'request' in decoded_data:
                    if decoded_data['request'] == 'disconnect':
                        break
                    elif decoded_data['request'] == 'ping':
                        self.send_data(client_socket, {'message': 'pong'})
                    elif decoded_data['request'] == 'get_rooms':
                        rooms_list = self._get_rooms_list()
                        self.send_data(client_socket, {'rooms': rooms_list})
                    elif decoded_data['request'] == 'create_room':
                        # Server assigns room ID
                        new_room_id = self.next_room_id
                        self.next_room_id += 1
                        self.send_data(client_socket, {'room_id': new_room_id})
                    elif decoded_data['request'] == 'get_user_stats':
                        # Get user statistics
                        try:
                            user_id = decoded_data.get('user_id')
                            stats = GameHistoryModel.get_user_stats(user_id)
                            self.send_data(client_socket, {'stats': stats})
                        except Exception as e:
                            logging.error(f'Error getting user stats: {e}')
                            self.send_data(client_socket, {'error': str(e)})
                    elif decoded_data['request'] == 'get_recent_games':
                        # Get recent games
                        try:
                            user_id = decoded_data.get('user_id')
                            limit = decoded_data.get('limit', 10)
                            games = GameHistoryModel.get_recent_games(user_id, limit)
                            self.send_data(client_socket, {'games': games})
                        except Exception as e:
                            logging.error(f'Error getting recent games: {e}')
                            self.send_data(client_socket, {'error': str(e)})
                    elif decoded_data['request'] == 'get_win_streak':
                        # Get win streak
                        try:
                            user_id = decoded_data.get('user_id')
                            streak_data = GameHistoryModel.get_win_streak(user_id)
                            self.send_data(client_socket, {'streak': streak_data})
                        except Exception as e:
                            logging.error(f'Error getting win streak: {e}')
                            self.send_data(client_socket, {'error': str(e)})
                    elif decoded_data['request'] == 'get_opponent_stats':
                        # Get opponent statistics by username
                        try:
                            opponent_username = decoded_data.get('opponent_username')
                            if opponent_username:
                                stats = GameHistoryModel.get_user_stats_by_username(opponent_username)
                                if stats:
                                    self.send_data(client_socket, {'success': True, 'stats': stats})
                                else:
                                    self.send_data(client_socket, {'success': False, 'error': 'User not found'})
                            else:
                                self.send_data(client_socket, {'success': False, 'error': 'Missing opponent_username'})
                        except Exception as e:
                            logging.error(f'Error getting opponent stats: {e}')
                            self.send_data(client_socket, {'success': False, 'error': str(e)})
                    elif decoded_data['request'] == 'save_game_history':
                        # Save game history to database
                        try:
                            game_data = decoded_data.get('game_data', {})
                            result = GameHistoryModel.save_game(
                                user_id=game_data.get('user_id'),
                                username=game_data.get('username'),
                                opponent_username=game_data.get('opponent_username'),
                                result=game_data.get('result'),
                                ships_sunk=game_data.get('ships_sunk'),
                                enemy_ships_sunk=game_data.get('enemy_ships_sunk'),
                                hits=game_data.get('hits'),
                                misses=game_data.get('misses'),
                                accuracy=game_data.get('accuracy'),
                                max_streak=game_data.get('max_streak'),
                                enemy_hits=game_data.get('enemy_hits'),
                                enemy_misses=game_data.get('enemy_misses'),
                                enemy_accuracy=game_data.get('enemy_accuracy'),
                                enemy_max_streak=game_data.get('enemy_max_streak')
                            )
                            self.send_data(client_socket, {'message': 'saved', 'success': result})
                        except Exception as e:
                            logging.error(f'Error saving game history: {e}')
                            self.send_data(client_socket, {'message': 'error', 'error': str(e)})
                else:
                    self.send_data(client_socket, {'message': 'ok'})
                    
        except socket.error:
            logging.info(f'Lobby client {username} disconnected')
    
    def client_listener(self, client_socket: socket.socket, username: str, room: GameRoom):
        """Listen to client messages"""
        # Set socket timeout to detect disconnections faster
        client_socket.settimeout(1.0)
        
        try:
            while True:
                try:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        logging.info(f'Client {username} connection closed (empty data)')
                        break
                    
                    decoded_data = self.decode_data(data)
                    
                    # Check game state transitions
                    if room.status == GameStatus.ship_lock and room.check_ships_locked():
                        room.status = GameStatus.battle
                    
                    if room.status == GameStatus.battle and room.game_data['winner']:
                        room.status = GameStatus.finished
                    
                    # Handle different request types
                    if 'request' in decoded_data:
                        response = self.process_request(decoded_data, username, room)
                        self.send_data(client_socket, response)
                        
                        # If disconnect request, break the loop immediately after sending response
                        if decoded_data.get('request') == 'disconnect':
                            logging.info(f'Client {username} requested disconnect - breaking loop')
                            break
                    else:
                        self.send_data(client_socket, {'message': 'ok'})
                
                except socket.timeout:
                    # Timeout is normal - just continue to check connection
                    continue
                    
        except socket.error as e:
            logging.info(f'Client {username} disconnected: {e}')
    
    def process_request(self, request_data: dict, username: str, room: GameRoom) -> dict:
        """Process client requests"""
        request_type = request_data.get('request')
        
        if request_type == 'ship_locked':
            room.game_data['clients'][username]['ship_locked'] = True
            room.game_data['game_grid'][username] = request_data['grid']
            return {'message': 'ok'}
        
        elif request_type == 'game_data':
            return room.game_data['clients']
        
        elif request_type == 'game_status':
            return {'game_status': room.status.name}
        
        elif request_type == 'winner':
            return {'winner': room.game_data['winner']}
        
        elif request_type == 'attack_tile':
            ship_name = room.attack_enemy_tile(username, request_data['position'])
            room.game_data['clients'][username]['attacked_tile'] = {
                'position': request_data['position'],
                'ship_name': ship_name
            }
            return {'attacked': ship_name}
        
        elif request_type == 'ship_sinked':
            # Player has sunk an enemy ship - increment their sunk count
            room.game_data['clients'][username]['sinked_ships'] += 1
            
            # Check if this player has won (sunk all 5 enemy ships)
            if room.game_data['clients'][username]['sinked_ships'] >= len(SHIPS_NAMES):
                # This player won - find opponent who lost
                for other_username in room.game_data['clients']:
                    if other_username != username:
                        room.game_over(other_username)  # Opponent is the loser
                        break
            return {'message': 'ok'}
        
        elif request_type == 'clear_ship_sunk':
            # Client acknowledged ship_sunk notification, clear it
            with room.lock:
                if 'ship_sunk' in room.game_data['clients'][username]:
                    ship_name = room.game_data['clients'][username]['ship_sunk']
                    del room.game_data['clients'][username]['ship_sunk']
                    print(f"[SERVER] Cleared ship_sunk notification '{ship_name}' for {username}")
            return {'message': 'ok'}
        
        elif request_type == 'timeout':
            # Time's up - increment timeout count and force turn switch
            with room.lock:
                room.game_data['clients'][username]['timeout_count'] += 1
                timeout_count = room.game_data['clients'][username]['timeout_count']
                print(f"[SERVER] {username} timeout #{timeout_count} - switching turn")
                
                # Always switch turn first
                room.game_data['clients'][username]['my_turn'] = False
                for other_username in room.game_data['clients']:
                    if other_username != username:
                        room.game_data['clients'][other_username]['my_turn'] = True
            
            # Check for game over OUTSIDE lock to prevent deadlock
            if timeout_count >= 3:
                print(f"[SERVER] {username} reached 3 timeouts - game over")
                room.game_over(username)
                return {'message': 'game_over_timeout', 'timeout_count': timeout_count}
            
            return {'message': 'turn_ended', 'timeout_count': timeout_count}
        
        elif request_type == 'player_quit':
            # Player quit - opponent wins immediately
            print(f"[SERVER] ==========================================")
            print(f"[SERVER] {username} QUIT THE GAME!")
            print(f"[SERVER] Setting opponent as winner...")
            with room.lock:
                if not room.game_data['winner']:
                    # Find opponent and set as winner
                    for other_username in room.game_data['clients']:
                        if other_username != username:
                            room.game_data['winner'] = other_username
                            print(f"[SERVER] ✓✓✓ {other_username} WINS because {username} quit!")
                            print(f"[SERVER] Winner is now: {room.game_data['winner']}")
                            print(f"[SERVER] ==========================================")
                            break
                else:
                    print(f"[SERVER] Winner already set: {room.game_data['winner']}")
                    print(f"[SERVER] ==========================================")
            return {'message': 'quit_acknowledged'}
        
        elif request_type == 'disconnect':
            return {'message': 'disconnecting'}
        
        elif request_type == 'save_game_history':
            # Save game history to database
            try:
                game_data = request_data.get('game_data', {})
                result = GameHistoryModel.save_game(
                    user_id=game_data.get('user_id'),
                    username=game_data.get('username'),
                    opponent_username=game_data.get('opponent_username'),
                    result=game_data.get('result'),
                    ships_sunk=game_data.get('ships_sunk'),
                    enemy_ships_sunk=game_data.get('enemy_ships_sunk'),
                    hits=game_data.get('hits'),
                    misses=game_data.get('misses'),
                    accuracy=game_data.get('accuracy'),
                    max_streak=game_data.get('max_streak'),
                    enemy_hits=game_data.get('enemy_hits'),
                    enemy_misses=game_data.get('enemy_misses'),
                    enemy_accuracy=game_data.get('enemy_accuracy'),
                    enemy_max_streak=game_data.get('enemy_max_streak')
                )
                return {'message': 'saved', 'success': result}
            except Exception as e:
                logging.error(f'Error saving game history: {e}')
                return {'message': 'error', 'error': str(e)}
        
        elif request_type == 'get_user_stats':
            # Get user statistics
            try:
                user_id = request_data.get('user_id')
                stats = GameHistoryModel.get_user_stats(user_id)
                return {'stats': stats}
            except Exception as e:
                logging.error(f'Error getting user stats: {e}')
                return {'error': str(e)}
        
        elif request_type == 'get_recent_games':
            # Get recent games
            try:
                user_id = request_data.get('user_id')
                limit = request_data.get('limit', 10)
                games = GameHistoryModel.get_recent_games(user_id, limit)
                return {'games': games}
            except Exception as e:
                logging.error(f'Error getting recent games: {e}')
                return {'error': str(e)}
        
        elif request_type == 'get_win_streak':
            # Get win streak
            try:
                user_id = request_data.get('user_id')
                streak_data = GameHistoryModel.get_win_streak(user_id)
                return {'streak': streak_data}
            except Exception as e:
                logging.error(f'Error getting win streak: {e}')
                return {'error': str(e)}
        
        elif request_type == 'get_opponent_stats':
            # Get opponent statistics by username (called during battle)
            try:
                opponent_username = request_data.get('opponent_username')
                if opponent_username:
                    stats = GameHistoryModel.get_user_stats_by_username(opponent_username)
                    if stats:
                        return {'success': True, 'stats': stats}
                    else:
                        return {'success': False, 'error': 'User not found or no games played'}
                else:
                    return {'success': False, 'error': 'Missing opponent_username'}
            except Exception as e:
                logging.error(f'Error getting opponent stats: {e}')
                return {'success': False, 'error': str(e)}
        
        return {'message': 'unknown request'}
    
    def get_or_create_room(self, room_id: int, username: str) -> GameRoom:
        """Get existing room or create new one"""
        with self.lock:
            if room_id in self.rooms:
                room = self.rooms[room_id]
                if room.get_client_count() >= 2:
                    return None
                return room
            else:
                room = GameRoom(room_id, f"Room {room_id}", username)
                self.rooms[room_id] = room
                logging.info(f'Created room {room_id}')
                return room
    
    def send_data(self, client_socket: socket.socket, data: dict):
        """Send data to client"""
        try:
            message = self.create_datagram(BUFFER_SIZE, data)
            client_socket.sendall(message)
        except socket.error as e:
            logging.error(f'Error sending data: {e}')
    
    def get_room_count(self):
        """Get number of active rooms"""
        with self.lock:
            return len(self.rooms)
    
    def get_client_count(self):
        """Get total number of connected clients (rooms + lobby)"""
        with self.lock:
            room_clients = sum(room.get_client_count() for room in self.rooms.values())
            lobby_count = len(self.lobby_clients)
            return room_clients + lobby_count
    
    def _get_rooms_list(self):
        """Get list of available rooms for browsing"""
        with self.lock:
            rooms_list = []
            for room_id, room in self.rooms.items():
                if room.get_client_count() < 2:  # Only show rooms with space
                    rooms_list.append({
                        'id': room_id,
                        'room_name': room.room_name,
                        'host_username': room.host_username,
                        'current_players': room.get_client_count(),
                        'max_players': 2
                    })
            return rooms_list

