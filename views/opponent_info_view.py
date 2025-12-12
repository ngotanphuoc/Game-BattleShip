"""
Opponent Info View - Popup hiển thị thông tin thống kê đối thủ
"""
import tkinter as tk
from tkinter import ttk


class OpponentInfoView(tk.Toplevel):
    """Popup nhỏ hiển thị thống kê đối thủ
    
    Hiển thị khi người chơi click vào tên đối thủ trong battle view.
    Bao gồm các chỉ số:
    - Total Games (Tổng số trận)
    - Wins (Thắng)
    - Losses (Thua)
    - Win Rate (Tỷ lệ thắng %)
    - Avg Accuracy (Độ chính xác trung bình %)
    - Ships Sunk (Tàu đã đánh chìm)
    - Best Win Streak (Chuỗi thắng dài nhất)
    - Current Streak (Chuỗi hiện tại)
    
    Giao diện:
    - Popup size: 450x550 pixels
    - Dark theme: #0f172a background
    - 8 cards layout: 2 rows x 4 cols
    - Mỗi card có icon, value, label
    """
    
    def __init__(self, parent, opponent_username, opponent_stats):
        """Khởi tạo popup opponent info
        
        Args:
            parent: Cửa sổ cha (root window)
            opponent_username: Tên đối thủ (str)
            opponent_stats: Dict chứa thống kê đối thủ
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
        """
        super().__init__(parent)
        
        self.opponent_username = opponent_username
        self.stats = opponent_stats if opponent_stats else self._get_default_stats()
        
        # Window settings
        self.title(f"📊 Thông Tin Đối Thủ: {opponent_username}")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg='#0f172a')
        
        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (480 // 2)
        y = (self.winfo_screenheight() // 2) - (580 // 2)
        self.geometry(f"480x580+{x}+{y}")
        
        # Make popup transient (stay on top) but NOT modal
        # Removed grab_set() to allow non-blocking popup in battle
        self.transient(parent)
        # self.grab_set()  # REMOVED - causes popup to close immediately in thread
        
        # Build UI
        self.build_ui()
        
        # CRITICAL: Đảm bảo popup hiển thị lên trên và được focus
        self.update()  # Xử lý tất cả pending events
        self.lift()  # Đưa window lên trên cùng
        self.focus_force()  # Force focus vào popup
        self.attributes('-topmost', True)  # Luôn ở trên cùng
        self.after(100, lambda: self.attributes('-topmost', False))  # Sau 100ms thì bỏ topmost
    
    def _get_default_stats(self):
        """Trả về stats mặc định nếu không có dữ liệu"""
        return {
            'total_games': 0,
            'total_wins': 0,
            'total_losses': 0,
            'win_rate': 0.0,
            'avg_accuracy': 0.0,
            'total_ships_sunk': 0,
            'best_streak': 0,
            'current_streak': 0
        }
    
    def build_ui(self):
        """Xây dựng giao diện popup"""
        # Header
        header_frame = tk.Frame(self, bg='#1e293b', bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Avatar/Icon
        avatar_label = tk.Label(
            header_frame,
            text="🎯",
            font=('Segoe UI', 48),
            bg='#1e293b',
            fg='#ef4444'
        )
        avatar_label.pack(pady=10)
        
        # Username
        username_label = tk.Label(
            header_frame,
            text=self.opponent_username,
            font=('Segoe UI', 20, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        )
        username_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Thông Tin Đối Thủ",
            font=('Segoe UI', 11),
            bg='#1e293b',
            fg='#94a3b8'
        )
        subtitle_label.pack(pady=(5, 10))
        
        # Stats cards
        self.create_stats_cards()
        
        # Close button
        close_btn = tk.Button(
            self,
            text="✖ Đóng",
            font=('Segoe UI', 12, 'bold'),
            bg='#ef4444',
            fg='white',
            activebackground='#dc2626',
            activeforeground='white',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.destroy
        )
        close_btn.pack(pady=20)
    
    def create_stats_cards(self):
        """Tạo 8 thẻ thống kê (2 hàng x 4 cột)
        
        Cards:
        1. 🎮 Total Games (xanh dương)
        2. 🏆 Wins (xanh lá)
        3. 💀 Losses (đỏ)
        4. 📊 Win Rate (cam)
        5. 🎯 Accuracy (vàng)
        6. 🔥 Current Streak (hồng)
        7. ⚓ Ships Sunk (tím)
        8. ⭐ Best Streak (vàng đậm)
        """
        cards_frame = tk.Frame(self, bg='#0f172a')
        cards_frame.pack(pady=10, padx=20)
        
        win_rate = float(self.stats.get('win_rate', 0))
        avg_accuracy = float(self.stats.get('avg_accuracy', 0))
        current_streak = int(self.stats.get('current_streak', 0))
        best_streak = int(self.stats.get('best_streak', 0))
        
        cards_data = [
            ("🎮", "Total Games", int(self.stats.get('total_games', 0)), "#3b82f6"),
            ("🏆", "Wins", int(self.stats.get('total_wins', 0)), "#10b981"),
            ("💀", "Losses", int(self.stats.get('total_losses', 0)), "#ef4444"),
            ("📊", "Win Rate", f"{win_rate:.1f}%", "#f59e0b"),
            ("🎯", "Accuracy", f"{avg_accuracy:.1f}%", "#eab308"),
            ("🔥", "Streak", f"{current_streak}W", "#ec4899"),
            ("⚓", "Ships Sunk", int(self.stats.get('total_ships_sunk', 0)), "#8b5cf6"),
            ("⭐", "Best Streak", f"{best_streak}W", "#facc15")
        ]
        
        for i, (icon, label, value, color) in enumerate(cards_data):
            card = tk.Frame(cards_frame, bg='#1e293b', bd=2, relief=tk.RAISED)
            card.grid(row=i//4, column=i%4, padx=8, pady=8, ipadx=12, ipady=10)
            
            # Icon
            icon_label = tk.Label(
                card,
                text=icon,
                font=('Segoe UI', 24),
                bg='#1e293b'
            )
            icon_label.pack()
            
            # Value
            value_label = tk.Label(
                card,
                text=str(value),
                font=('Segoe UI', 20, 'bold'),
                bg='#1e293b',
                fg=color
            )
            value_label.pack()
            
            # Label
            label_widget = tk.Label(
                card,
                text=label,
                font=('Segoe UI', 9),
                bg='#1e293b',
                fg='#94a3b8'
            )
            label_widget.pack()


def show_opponent_info(parent, opponent_username, opponent_stats):
    """Helper function để hiển thị popup opponent info
    
    Args:
        parent: Cửa sổ cha (root window)
        opponent_username: Tên đối thủ
        opponent_stats: Dict thống kê đối thủ
    
    Returns:
        OpponentInfoView instance
    
    Usage:
        stats = {
            'total_games': 100,
            'total_wins': 55,
            'total_losses': 45,
            'win_rate': 55.0,
            'avg_accuracy': 68.5,
            'total_ships_sunk': 150,
            'best_streak': 8,
            'current_streak': 3
        }
        show_opponent_info(root, "PlayerX", stats)
    """
    popup = OpponentInfoView(parent, opponent_username, opponent_stats)
    return popup
