"""
Base Database Model
Provides common database connection and query methods
"""
import mysql.connector
from mysql.connector import Error, pooling
from config.db_config import DB_CONFIG, POOL_CONFIG
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class Database:
    """Singleton database connection pool
    
    Quản lý connection pool MySQL:
    - Tạo pool khi lần đầu gọi get_pool()
    - Tái sử dụng connection (tránh tạo mới mỗi lần query)
    - Thread-safe cho server multi-threading
    
    Config: Lấy từ config/db_config.py
    """
    _connection_pool = None

    @classmethod
    def get_pool(cls):
        """Lấy hoặc tạo connection pool
        
        Returns:
            MySQLConnectionPool instance
        
        Singleton pattern: Chỉ tạo 1 pool duy nhất
        """
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pooling.MySQLConnectionPool(
                    **POOL_CONFIG,
                    **DB_CONFIG
                )
                logging.info("Database connection pool created successfully")
            except Error as e:
                logging.error(f"Error creating connection pool: {e}")
                raise
        return cls._connection_pool

    @classmethod
    def get_connection(cls):
        """Lấy 1 connection từ pool
        
        Returns:
            MySQL connection object
        
        Lưu ý: Nhớ close() connection sau khi dùng xong
        """
        try:
            return cls.get_pool().get_connection()
        except Error as e:
            logging.error(f"Error getting connection from pool: {e}")
            raise


class BaseModel:
    """Base model class với các database operations chung
    
    Cung cấp:
    - execute_query(): Thực thi query (SELECT/INSERT/UPDATE/DELETE)
    - execute_many(): Thực thi nhiều query cùng lúc (bulk insert)
    
    Kế thừa: UserModel, RoomModel, GameHistoryModel kế thừa class này
    """

    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Thực thi database query
        
        Args:
            query: SQL query string (có thể dùng %s placeholder)
            params: Query parameters (tuple hoặc dict)
            fetch_one: Trả về 1 row duy nhất (SELECT ... LIMIT 1)
            fetch_all: Trả về tất cả rows (SELECT ...)
            commit: Commit transaction (INSERT/UPDATE/DELETE)
            
        Returns:
            - Nếu commit: lastrowid (ID vừa insert)
            - Nếu fetch_one: Dict 1 row hoặc None
            - Nếu fetch_all: List[Dict] hoặc []
            - Mặc định: None
        
        Ví dụ:
            # INSERT
            user_id = execute_query(
                "INSERT INTO users (username) VALUES (%s)", 
                ("john",), 
                commit=True
            )
            
            # SELECT ONE
            user = execute_query(
                "SELECT * FROM users WHERE id=%s", 
                (1,), 
                fetch_one=True
            )
            
            # SELECT ALL
            users = execute_query(
                "SELECT * FROM users", 
                fetch_all=True
            )
        """
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(query, params or ())
            
            if commit:
                connection.commit()
                return cursor.lastrowid
            
            if fetch_one:
                return cursor.fetchone()
            
            if fetch_all:
                return cursor.fetchall()
            
            return None
            
        except Error as e:
            if connection:
                connection.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def execute_many(query, params_list):
        """Thực thi query với nhiều parameter sets (bulk operations)
        
        Args:
            query: SQL query string
            params_list: List of tuples, mỗi tuple là 1 set parameters
        
        Returns:
            rowcount: Số rows bị ảnh hưởng
        
        Ví dụ:
            # Bulk insert 3 users
            execute_many(
                "INSERT INTO users (username) VALUES (%s)",
                [("john",), ("jane",), ("bob",)]
            )
            # → INSERT 3 rows cùng lúc, nhanh hơn 3 lần execute_query()
        """
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()
            
            cursor.executemany(query, params_list)
            connection.commit()
            
            return cursor.rowcount
            
        except Error as e:
            if connection:
                connection.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
