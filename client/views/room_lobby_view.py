"""
Room Lobby View - Tkinter UI Component (MVC View Layer)
"""

import tkinter as tk


class ModernButton(tk.Button):
    """Button tùy chỉnh với style hiện đại
    
    Tương tự như ModernButton trong các view khác
    """
    
    def __init__(self, parent, text, command, color='#3b82f6', **kwargs):
        """Khởi tạo button hiện đại"""
        super().__init__(
            parent, text=text, command=command,
            font=('Segoe UI', 11, 'bold'),
            bg=color, fg='white',
            activebackground=self._darken_color(color),
            activeforeground='white',
            relief=tk.FLAT, cursor='hand2',
            pady=10, padx=20, **kwargs
        )
    
    @staticmethod
    def _darken_color(hex_color):
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        darkened = tuple(max(0, c - 30) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'


class RoomLobbyView:
    """Giao diện phòng chờ (lobby)
    
    Màn hình chờ người chơi thứ 2 tham gia phòng
    Hiển thị:
    - Tên phòng
    - Số người chơi hiện tại (1/2 hoặc 2/2)
    - Trạng thái kết nối
    - Nút Leave để rời phòng
    """
    
    def __init__(self, parent, room_name):
        """Khởi tạo giao diện phòng chờ
        
        Args:
            parent: Cửa sổ Tkinter cha
            room_name: Tên phòng đã tạo/tham gia
        """
        self.parent = parent
        self.on_leave = None
        
        # Main frame
        self.frame = tk.Frame(parent, bg='#0f172a')
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Content
        content = tk.Frame(self.frame, bg='#1e293b', padx=60, pady=40)
        content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Room name
        tk.Label(
            content, text=f"🏠 {room_name}",
            font=('Segoe UI', 22, 'bold'),
            bg='#1e293b', fg='#60a5fa'
        ).grid(row=0, column=0, pady=(0, 20))
        
        # Players
        self.players_label = tk.Label(
            content, text="Waiting...",
            font=('Segoe UI', 14),
            bg='#1e293b', fg='#e2e8f0'
        )
        self.players_label.grid(row=1, column=0, pady=10)
        
        # Status
        self.status_label = tk.Label(
            content, text="✅ Connected",
            font=('Segoe UI', 12),
            bg='#1e293b', fg='#10b981'
        )
        self.status_label.grid(row=2, column=0, pady=10)
        
        # Info label
        tk.Label(
            content, text="Game will start automatically when 2 players join",
            font=('Segoe UI', 10),
            bg='#1e293b', fg='#94a3b8'
        ).grid(row=3, column=0, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(content, bg='#1e293b')
        btn_frame.grid(row=4, column=0, pady=30)
        
        ModernButton(
            btn_frame, "← LEAVE",
            lambda: self.on_leave() if self.on_leave else None,
            color='#ef4444', width=12
        ).pack(padx=5)
    
    def update_player_count(self, count):
        """Cập nhật số người chơi hiện thị
        
        Args:
            count: Số người chơi hiện tại (1 hoặc 2)
        
        Nếu count = 2: Hiển thị "Starting game..." và chuẩn bị bắt đầu game
        """
        self.players_label.config(text=f"👥 Players: {count}/2")
        
        if count == 2:
            self.status_label.config(text="🎮 Starting game...", fg='#10b981')
    
    def destroy(self):
        """Hủy giao diện
        
        Xóa frame khi bắt đầu game hoặc rời phòng
        """
        self.frame.destroy()
