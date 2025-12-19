"""
User Model
Handles user authentication and management
"""
import hashlib
from datetime import datetime
from decimal import Decimal
from models.base_model import BaseModel


class UserModel(BaseModel):
    """Model quản lý users
    
    Bảng users:
    - id: INT PRIMARY KEY AUTO_INCREMENT
    - username: VARCHAR(50) UNIQUE
    - password: VARCHAR(255) (hashed)
    - wins: INT DEFAULT 0
    - losses: INT DEFAULT 0
    - draws: INT DEFAULT 0
    - total_games: INT DEFAULT 0
    - is_online: BOOLEAN DEFAULT 0
    - created_at: TIMESTAMP
    
    Methods:
    - authenticate(): Đăng nhập
    - create_user(): Đăng ký
    - get_user_by_id(): Lấy thông tin user
    - get_user_by_username(): Tìm user theo username
    - set_online_status(): Set online/offline
    - get_user_stats(): Lấy thống kê
    """
    
    @staticmethod
    def _convert_datetime_to_string(data):
        """Chuyển đổi datetime, Decimal và các types khác thành JSON serializable
        
        Args:
            data: Dict có thể chứa datetime, Decimal objects
            
        Returns:
            Dict với tất cả values đã được chuyển sang JSON-safe types
        """
        if not data:
            return data
            
        result = data.copy()
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, bytes):
                result[key] = value.decode('utf-8', errors='ignore')
        return result
    
    @staticmethod
    def hash_password(password):
        """Hash password bằng SHA-256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @classmethod
    def authenticate(cls, username, password):
        """Xác thực đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu plain text
            
        Returns:
            Dict user info nếu đúng, None nếu sai
            Dict với 'error' nếu đã online
        """
        # TẠM THỜI: Database đang lưu plain text password, không hash
        # TODO: Sau này nên hash tất cả passwords trong DB
        
        query = """
            SELECT id, username, is_online, created_at
            FROM users 
            WHERE username = %s AND password = %s
        """
        
        result = cls.execute_query(query, (username, password), fetch_one=True)
        
        if result:
            # Check if already online
            if result.get('is_online'):
                return {
                    'error': 'already_online',
                    'username': result.get('username')
                }
            
            # Thêm stats tính từ game_history
            stats = cls._calculate_user_stats(result['id'])
            result.update(stats)
            
            # Chuyển datetime thành string để JSON serialize
            return cls._convert_datetime_to_string(result)
        return None
    
    @classmethod
    def create_user(cls, username, password):
        """Tạo user mới
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu plain text
            
        Returns:
            user_id nếu thành công, None nếu thất bại
        """
        # TẠM THỜI: Lưu plain text để tương thích với users hiện có
        # TODO: Sau này nên hash passwords
        
        query = """
            INSERT INTO users (username, password, is_online)
            VALUES (%s, %s, 0)
        """
        
        return cls.execute_query(query, (username, password), commit=True)
    
    @classmethod
    def get_user_by_id(cls, user_id):
        """Lấy thông tin user theo ID
        
        Args:
            user_id: ID của user
            
        Returns:
            Dict user info hoặc None
        """
        query = """
            SELECT id, username, is_online, created_at
            FROM users 
            WHERE id = %s
        """
        
        result = cls.execute_query(query, (user_id,), fetch_one=True)
        if result:
            stats = cls._calculate_user_stats(user_id)
            result.update(stats)
            result = cls._convert_datetime_to_string(result)
        return result
    
    @classmethod
    def get_user_by_username(cls, username):
        """Lấy thông tin user theo username
        
        Args:
            username: Tên người dùng
            
        Returns:
            Dict user info hoặc None
        """
        query = """
            SELECT id, username, is_online, created_at
            FROM users 
            WHERE username = %s
        """
        
        result = cls.execute_query(query, (username,), fetch_one=True)
        if result:
            stats = cls._calculate_user_stats(result['id'])
            result.update(stats)
            result = cls._convert_datetime_to_string(result)
        return result
        
        result = cls.execute_query(query, (username,), fetch_one=True)
        if result:
            stats = cls._calculate_user_stats(result['id'])
            result.update(stats)
        return result
    
    @classmethod
    def _calculate_user_stats(cls, user_id):
        """Tính toán stats từ game_history
        
        Args:
            user_id: ID của user
            
        Returns:
            Dict với wins, losses, draws, total_games
        """
        query = """
            SELECT 
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'lose' THEN 1 ELSE 0 END) as losses,
                0 as draws,
                COUNT(*) as total_games
            FROM game_history
            WHERE user_id = %s
        """
        
        result = cls.execute_query(query, (user_id,), fetch_one=True)
        return result if result else {'wins': 0, 'losses': 0, 'draws': 0, 'total_games': 0}
    
    @classmethod
    def set_online_status(cls, user_id, is_online):
        """Set trạng thái online/offline
        
        Args:
            user_id: ID của user
            is_online: True (online) hoặc False (offline)
            
        Returns:
            True nếu thành công
        """
        query = """
            UPDATE users 
            SET is_online = %s
            WHERE id = %s
        """
        
        result = cls.execute_query(query, (1 if is_online else 0, user_id), commit=True)
        return result is not None
    
    @classmethod
    def get_user_stats(cls, user_id):
        """Lấy thống kê của user
        
        Args:
            user_id: ID của user
            
        Returns:
            Dict chứa stats hoặc None
        """
        query = """
            SELECT 
                u.username,
                u.wins as total_wins,
                u.losses as total_losses,
                u.draws as total_draws,
                u.total_games,
                CASE 
                    WHEN u.total_games > 0 THEN ROUND((u.wins * 100.0 / u.total_games), 2)
                    ELSE 0 
                END as win_rate,
                COALESCE(SUM(gh.ships_sunk), 0) as total_ships_sunk,
                COALESCE(SUM(gh.hits), 0) as total_hits,
                COALESCE(SUM(gh.misses), 0) as total_misses,
                CASE 
                    WHEN SUM(gh.hits + gh.misses) > 0 
                    THEN ROUND((SUM(gh.hits) * 100.0 / SUM(gh.hits + gh.misses)), 2)
                    ELSE 0 
                END as avg_accuracy,
                COALESCE(MAX(gh.max_streak), 0) as best_streak
            FROM users u
            LEFT JOIN game_history gh ON u.id = gh.user_id
            WHERE u.id = %s
            GROUP BY u.id
        """
        
        return cls.execute_query(query, (user_id,), fetch_one=True)
