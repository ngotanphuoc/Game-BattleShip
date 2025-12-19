"""
User Session - Client Side
Stores user information without database access
All authentication is done via networking with server
"""


class UserSession(dict):
    """Class lưu thông tin user ở client (kế thừa dict)
    
    CLIENT KHÔNG truy cập database trực tiếp
    Thông tin user được nhận từ server qua networking
    
    Kế thừa dict để có thể access cả user['id'] và user.id
    """
    
    def __init__(self, user_data=None):
        """Khởi tạo session với data từ server
        
        Args:
            user_data: Dict từ server chứa {id, username, wins, losses, etc}
        """
        # Khởi tạo dict với data
        if user_data:
            super().__init__(user_data)
            # Set attributes để có thể access bằng dot notation
            self.id = user_data.get('id')
            self.username = user_data.get('username')
            self.wins = user_data.get('wins', 0)
            self.losses = user_data.get('losses', 0)
            self.draws = user_data.get('draws', 0)
            self.total_games = user_data.get('total_games', 0)
            self.created_at = user_data.get('created_at')
        else:
            super().__init__()
            self.id = None
            self.username = None
            self.wins = 0
            self.losses = 0
            self.draws = 0
            self.total_games = 0
            self.created_at = None
    
    def to_dict(self):
        """Chuyển thành dict để dễ sử dụng"""
        return dict(self)
    
    def update_stats(self, stats_data):
        """Cập nhật stats từ server
        
        Args:
            stats_data: Dict chứa wins, losses, draws, etc
        """
        if stats_data:
            self.wins = stats_data.get('wins', self.wins)
            self.losses = stats_data.get('losses', self.losses)
            self.draws = stats_data.get('draws', self.draws)
            self.total_games = stats_data.get('total_games', self.total_games)
            # Update dict values
            self['wins'] = self.wins
            self['losses'] = self.losses
            self['draws'] = self.draws
            self['total_games'] = self.total_games
