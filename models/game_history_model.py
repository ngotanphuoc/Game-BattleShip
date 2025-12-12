from config.db_config import get_db_connection
from datetime import datetime
from typing import List, Dict, Optional


class GameHistoryModel:
    """Model quản lý lịch sử trận đấu và thống kê
    
    Chức năng:
    - Lưu kết quả trận đấu (save_game)
    - Lấy thống kê tổng hợp (get_user_stats)
    - Lấy lịch sử các trận gần đây (get_recent_games)
    - Tính chuỗi thắng (get_win_streak)
    - Đếm tổng số trận (get_total_games_count)
    
    Bảng database: game_history
    Cột: id, user_id, opponent_id, result, ships_sunk, hits, misses, 
          accuracy, max_streak, played_at
    
    Lưu ý: Mỗi trận lưu 2 records (1 cho mỗi người chơi)
    """
    
    @staticmethod
    def save_game(user_id: int, username: str, opponent_username: str, 
                  result: str, ships_sunk: int, enemy_ships_sunk: int, hits: int, misses: int,
                  accuracy: float, max_streak: int,
                  enemy_hits: int = 0, enemy_misses: int = 0,
                  enemy_accuracy: float = 0, enemy_max_streak: int = 0) -> bool:
        """Lưu trận đấu vào lịch sử
        
        Args:
            user_id: ID người chơi
            username: Tên người chơi
            opponent_username: Tên đối thủ
            result: 'win' hoặc 'lose'
            ships_sunk: Số tàu địch bị chìm (tôi đánh)
            enemy_ships_sunk: Số tàu tôi bị chìm (địch đánh)
            hits: Tổng số phát trúng của tôi
            misses: Tổng số phát trượt của tôi
            accuracy: Độ chính xác (%) của tôi
            max_streak: Chuỗi trúng dài nhất của tôi
            enemy_*: Thống kê của địch (không lưu, dự phòng)
        
        Returns:
            True: Lưu thành công
            False: Thất bại
        
        Luồng:
        1. Tìm opponent_id từ opponent_username
        2. INSERT vào game_history
        3. Commit và close connection
        
        Lưu ý: Gọi hàm này 2 lần cho mỗi trận (1 lần/người)
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            print(f"[MODEL] Saving game for user_id={user_id}, opponent={opponent_username}, result={result}")
            
            # Get opponent_id from username
            cursor.execute("SELECT id FROM users WHERE username = %s", (opponent_username,))
            opponent_result = cursor.fetchone()
            opponent_id = opponent_result[0] if opponent_result else None
            
            if not opponent_id:
                print(f"[MODEL] Error: Could not find opponent_id for username {opponent_username}")
                cursor.close()
                connection.close()
                return False
            
            print(f"[MODEL] Found opponent_id={opponent_id}")
            
            query = """
                INSERT INTO game_history 
                (user_id, opponent_id, result, ships_sunk, hits, misses, accuracy, max_streak)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            print(f"[MODEL] Executing query with: user_id={user_id}, opponent_id={opponent_id}, result={result}, ships_sunk={ships_sunk}, hits={hits}, misses={misses}, accuracy={accuracy}, max_streak={max_streak}")
            
            cursor.execute(query, (
                user_id, opponent_id, result, ships_sunk, hits, misses, accuracy, max_streak
            ))
            
            connection.commit()
            print(f"[MODEL] ✓ Game history saved successfully! Insert ID: {cursor.lastrowid}")
            
            cursor.close()
            connection.close()
            
            return True
            
        except Exception as e:
            print(f"[MODEL] ✗ Error saving game history: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_user_stats(user_id: int) -> Optional[Dict]:
        """Lấy thống kê tổng hợp của người chơi
        
        Args:
            user_id: ID người chơi
        
        Returns:
            Dict chứa:
            - total_games: Tổng số trận
            - total_wins: Số trận thắng
            - total_losses: Số trận thua
            - win_rate: Tỉ lệ thắng (%)
            - total_ships_sunk: Tổng tàu đánh chìm
            - total_hits: Tổng số phát trúng
            - total_misses: Tổng số phát trượt
            - avg_accuracy: Độ chính xác trung bình
            - best_streak: Chuỗi trúng dài nhất
            
            None nếu chưa có trận nào
        
        Query: Dùng SUM, COUNT, AVG, MAX để tổng hợp từ game_history
        Chuyển Decimal thành float cho JSON serialization
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as total_wins,
                    SUM(CASE WHEN result = 'lose' THEN 1 ELSE 0 END) as total_losses,
                    ROUND(SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_rate,
                    SUM(ships_sunk) as total_ships_sunk,
                    SUM(hits) as total_hits,
                    SUM(misses) as total_misses,
                    ROUND(AVG(accuracy), 2) as avg_accuracy,
                    MAX(max_streak) as best_streak
                FROM game_history
                WHERE user_id = %s
            """
            
            cursor.execute(query, (user_id,))
            stats = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            # Handle case where no games exist
            if stats and stats['total_games'] == 0:
                return None
            
            # Convert Decimal to float for JSON serialization
            if stats:
                for key in stats:
                    if stats[key] is not None and hasattr(stats[key], '__float__'):
                        stats[key] = float(stats[key])
                
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return None
    
    @staticmethod
    def get_user_stats_by_username(username: str) -> Optional[Dict]:
        """Lấy thống kê tổng hợp của người chơi theo username
        
        Args:
            username: Tên người chơi
        
        Returns:
            Dict chứa:
            - total_games: Tổng số trận
            - total_wins: Số trận thắng
            - total_losses: Số trận thua
            - win_rate: Tỉ lệ thắng (%)
            - total_ships_sunk: Tổng tàu đánh chìm
            - total_hits: Tổng số phát trúng
            - total_misses: Tổng số phát trượt
            - avg_accuracy: Độ chính xác trung bình
            - best_streak: Chuỗi trúng dài nhất
            - current_streak: Chuỗi thắng hiện tại
            
            None nếu không tìm thấy user hoặc chưa có trận nào
        
        Sử dụng:
            stats = GameHistoryModel.get_user_stats_by_username("Player1")
            if stats:
                print(f"Win rate: {stats['win_rate']}%")
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Tìm user_id từ username
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_result = cursor.fetchone()
            
            if not user_result:
                cursor.close()
                connection.close()
                return None
            
            user_id = user_result['id']
            
            # Lấy stats từ get_user_stats
            cursor.close()
            connection.close()
            
            stats = GameHistoryModel.get_user_stats(user_id)
            
            if not stats:
                return None
            
            # Thêm current_streak từ get_win_streak
            streak_data = GameHistoryModel.get_win_streak(user_id)
            if streak_data:
                stats['current_streak'] = streak_data.get('current_streak', 0)
            else:
                stats['current_streak'] = 0
            
            return stats
            
        except Exception as e:
            print(f"Error getting user stats by username: {e}")
            return None
    
    @staticmethod
    def get_recent_games(user_id: int, limit: int = 10) -> List[Dict]:
        """Lấy danh sách các trận gần đây
        
        Args:
            user_id: ID người chơi
            limit: Số trận muốn lấy (mặc định 10)
        
        Returns:
            List các Dict, mỗi Dict chứa:
            - opponent_username: Tên đối thủ
            - result: 'win' / 'lose'
            - ships_sunk, hits, misses: Thống kê
            - accuracy: Độ chính xác (%)
            - max_streak: Chuỗi trúng dài nhất
            - played_at: Thời gian chơi (ISO format)
        
        Sắp xếp: ORDER BY played_at DESC (mới nhất trên cùng)
        JOIN với users để lấy tên đối thủ
        Chuyển datetime và Decimal thành JSON-serializable
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    u.username as opponent_username,
                    gh.result,
                    gh.ships_sunk,
                    gh.hits,
                    gh.misses,
                    gh.accuracy,
                    gh.max_streak,
                    gh.played_at
                FROM game_history gh
                JOIN users u ON gh.opponent_id = u.id
                WHERE gh.user_id = %s
                ORDER BY gh.played_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (user_id, limit))
            games = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Convert Decimal and datetime to JSON-serializable types
            for game in games:
                for key in game:
                    if game[key] is not None:
                        if hasattr(game[key], '__float__'):
                            game[key] = float(game[key])
                        elif hasattr(game[key], 'isoformat'):
                            game[key] = game[key].isoformat()
            
            return games
            
        except Exception as e:
            print(f"Error getting recent games: {e}")
            return []
    
    @staticmethod
    def get_win_streak(user_id: int) -> Dict:
        """Tính chuỗi thắng hiện tại và dài nhất
        
        Args:
            user_id: ID người chơi
        
        Returns:
            Dict chứa:
            - current_streak: Chuỗi thắng liên tiếp hiện tại
            - longest_streak: Chuỗi thắng dài nhất từ trước tới nay
        
        Logic:
        - Current: Đếm win liên tiếp từ trận mới nhất, dừng khi gặp lose
        - Longest: Duyệt tất cả trận, tìm chuỗi win dài nhất
        
        Ví dụ: W W W L W W W W W → current=5, longest=5
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Get all games ordered by date
            query = """
                SELECT result
                FROM game_history
                WHERE user_id = %s
                ORDER BY played_at DESC
            """
            
            cursor.execute(query, (user_id,))
            games = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            if not games:
                return {'current_streak': 0, 'longest_streak': 0}
            
            # Calculate current streak
            current_streak = 0
            for game in games:
                if game['result'] == 'win':
                    current_streak += 1
                else:
                    break
            
            # Calculate longest streak
            longest_streak = 0
            temp_streak = 0
            for game in reversed(games):
                if game['result'] == 'win':
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 0
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak
            }
            
        except Exception as e:
            print(f"Error calculating win streaks: {e}")
            return {'current_streak': 0, 'longest_streak': 0}
    
    @staticmethod
    def get_total_games_count(user_id: int) -> int:
        """Get total number of games played"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            query = "SELECT COUNT(*) FROM game_history WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return count
            
        except Exception as e:
            print(f"Error getting total games count: {e}")
            return 0

