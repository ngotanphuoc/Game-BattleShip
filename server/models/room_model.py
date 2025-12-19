"""
Room Model
Handles game room creation and management
"""
from datetime import datetime
from models.base_model import BaseModel
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class RoomModel(BaseModel):
    """Model quản lý phòng game
    
    Chức năng:
    - Tạo phòng mới (create_room)
    - Lấy danh sách phòng có sẵn (get_available_rooms)
    - Tham gia/rời phòng (join_room, leave_room)
    - Cập nhật trạng thái phòng (update_room_status)
    - Đặt người thắng (set_room_winner)
    
    Bảng database: rooms, room_players
    Lưu ý: Hiện tại chưa dùng (phòng quản lý in-memory trên server)
    """

    @staticmethod
    def create_room(room_name, host_user_id, max_players=2):
        """Tạo phòng game mới
        
        Args:
            room_name: Tên phòng
            host_user_id: ID người tạo phòng
            max_players: Số người chơi tối đa (mặc định 2)
            
        Returns:
            room_id nếu thành công, None nếu thất bại
        
        Luồng:
        1. INSERT vào bảng rooms (status='waiting', current_players=1)
        2. INSERT host vào bảng room_players
        3. Trả về room_id
        """
        query = """
            INSERT INTO rooms (room_name, host_user_id, max_players, current_players, status) 
            VALUES (%s, %s, %s, 1, 'waiting')
        """
        try:
            room_id = BaseModel.execute_query(
                query, (room_name, host_user_id, max_players), commit=True
            )
            
            # Add host to room_players
            player_query = "INSERT INTO room_players (room_id, user_id) VALUES (%s, %s)"
            BaseModel.execute_query(player_query, (room_id, host_user_id), commit=True)
            
            logging.info(f"Room '{room_name}' created with ID: {room_id}")
            return room_id
        except Exception as e:
            logging.error(f"Error creating room: {e}")
            return None

    @staticmethod
    def get_available_rooms():
        """Lấy tất cả phòng có sẵn (trạng thái waiting)
        
        Returns:
            List[Dict] phòng với thông tin:
            - id, room_name, host_user_id, host_username
            - current_players, max_players
            - status, created_at
        
        Điều kiện: status='waiting' và còn chỗ trống
        Sắp xếp: Phòng mới nhất trước (ORDER BY created_at DESC)
        """
        query = """
            SELECT r.*, u.username as host_username 
            FROM rooms r
            JOIN users u ON r.host_user_id = u.id
            WHERE r.status = 'waiting' AND r.current_players < r.max_players
            ORDER BY r.created_at DESC
        """
        try:
            return BaseModel.execute_query(query, fetch_all=True)
        except Exception as e:
            logging.error(f"Error getting available rooms: {e}")
            return []

    @staticmethod
    def get_room_by_id(room_id):
        """Lấy thông tin phòng theo ID
        
        Args:
            room_id: ID phòng
        
        Returns:
            Dict thông tin phòng hoặc None nếu không tìm thấy
        
        JOIN với bảng users để lấy host_username
        """
        query = """
            SELECT r.*, u.username as host_username 
            FROM rooms r
            JOIN users u ON r.host_user_id = u.id
            WHERE r.id = %s
        """
        try:
            return BaseModel.execute_query(query, (room_id,), fetch_one=True)
        except Exception as e:
            logging.error(f"Error getting room by ID: {e}")
            return None

    @staticmethod
    def join_room(room_id, user_id):
        """Tham gia vào phòng
        
        Args:
            room_id: ID phòng muốn vào
            user_id: ID người chơi
            
        Returns:
            True nếu thành công, False nếu thất bại
        
        Validate:
        - Phòng phải ở trạng thái 'waiting'
        - Phòng chưa đầy (current_players < max_players)
        
        Luồng:
        1. Kiểm tra phòng hợp lệ
        2. INSERT vào room_players
        3. Tăng current_players trong rooms
        """
        try:
            # Check if room is available
            room = RoomModel.get_room_by_id(room_id)
            if not room or room['status'] != 'waiting':
                logging.warning(f"Room {room_id} not available")
                return False
            
            if room['current_players'] >= room['max_players']:
                logging.warning(f"Room {room_id} is full")
                return False
            
            # Add player to room
            player_query = "INSERT INTO room_players (room_id, user_id) VALUES (%s, %s)"
            BaseModel.execute_query(player_query, (room_id, user_id), commit=True)
            
            # Update room current_players count
            update_query = "UPDATE rooms SET current_players = current_players + 1 WHERE id = %s"
            BaseModel.execute_query(update_query, (room_id,), commit=True)
            
            logging.info(f"User {user_id} joined room {room_id}")
            return True
        except Exception as e:
            logging.error(f"Error joining room: {e}")
            return False

    @staticmethod
    def leave_room(room_id, user_id):
        """Rời khỏi phòng
        
        Args:
            room_id: ID phòng
            user_id: ID người chơi
        
        Returns:
            True nếu thành công, False nếu thất bại
        
        Luồng:
        1. DELETE khỏi room_players
        2. Giảm current_players trong rooms
        3. Nếu phòng rỗng (current_players <= 0) → DELETE phòng
        """
        try:
            # Remove player from room
            delete_query = "DELETE FROM room_players WHERE room_id = %s AND user_id = %s"
            BaseModel.execute_query(delete_query, (room_id, user_id), commit=True)
            
            # Update room current_players count
            update_query = "UPDATE rooms SET current_players = current_players - 1 WHERE id = %s"
            BaseModel.execute_query(update_query, (room_id,), commit=True)
            
            # Check if room is empty, delete it
            room = RoomModel.get_room_by_id(room_id)
            if room and room['current_players'] <= 0:
                delete_room_query = "DELETE FROM rooms WHERE id = %s"
                BaseModel.execute_query(delete_room_query, (room_id,), commit=True)
                logging.info(f"Room {room_id} deleted (empty)")
            
            logging.info(f"User {user_id} left room {room_id}")
            return True
        except Exception as e:
            logging.error(f"Error leaving room: {e}")
            return False

    @staticmethod
    def get_room_players(room_id):
        """Lấy danh sách người chơi trong phòng
        
        Args:
            room_id: ID phòng
        
        Returns:
            List[Dict] người chơi với thông tin:
            - user_id, username
            - joined_at
        
        Sắp xếp: Theo thứ tự vào phòng (ORDER BY joined_at)
        """
        query = """
            SELECT rp.*, u.username 
            FROM room_players rp
            JOIN users u ON rp.user_id = u.id
            WHERE rp.room_id = %s
            ORDER BY rp.joined_at
        """
        try:
            return BaseModel.execute_query(query, (room_id,), fetch_all=True)
        except Exception as e:
            logging.error(f"Error getting room players: {e}")
            return []

    @staticmethod
    def update_room_status(room_id, status):
        """Cập nhật trạng thái phòng
        
        Args:
            room_id: ID phòng
            status: Trạng thái mới ('waiting', 'in_progress', 'finished')
        
        Returns:
            True nếu thành công, False nếu thất bại
        
        Tự động cập nhật:
        - 'in_progress' → đặt started_at = NOW()
        - 'finished' → đặt finished_at = NOW()
        """
        query = "UPDATE rooms SET status = %s"
        params = [status]
        
        if status == 'in_progress':
            query += ", started_at = NOW()"
        elif status == 'finished':
            query += ", finished_at = NOW()"
        
        query += " WHERE id = %s"
        params.append(room_id)
        
        try:
            BaseModel.execute_query(query, tuple(params), commit=True)
            logging.info(f"Room {room_id} status updated to {status}")
            return True
        except Exception as e:
            logging.error(f"Error updating room status: {e}")
            return False

    @staticmethod
    def set_room_winner(room_id, winner_id):
        """Đặt người thắng của phòng
        
        Args:
            room_id: ID phòng
            winner_id: ID người thắng
        
        Returns:
            True nếu thành công, False nếu thất bại
        
        Tự động:
        - Đặt status = 'finished'
        - Đặt finished_at = NOW()
        """
        query = "UPDATE rooms SET winner_id = %s, status = 'finished', finished_at = NOW() WHERE id = %s"
        try:
            BaseModel.execute_query(query, (winner_id, room_id), commit=True)
            logging.info(f"Room {room_id} winner set to user {winner_id}")
            return True
        except Exception as e:
            logging.error(f"Error setting room winner: {e}")
            return False

    @staticmethod
    def delete_room(room_id):
        """Xóa phòng
        
        Args:
            room_id: ID phòng cần xóa
        
        Returns:
            True nếu thành công, False nếu thất bại
        
        Lưu ý: Cascade delete sẽ tự động xóa room_players nếu có thiết lập
        """
        query = "DELETE FROM rooms WHERE id = %s"
        try:
            BaseModel.execute_query(query, (room_id,), commit=True)
            logging.info(f"Room {room_id} deleted")
            return True
        except Exception as e:
            logging.error(f"Error deleting room: {e}")
            return False
