"""
Room List View - Tkinter UI Component (MVC View Layer)
"""

import tkinter as tk
from tkinter import ttk, messagebox


class ModernButton(tk.Button):
    """Button tùy chỉnh với style hiện đại
    
    Tương tự như ModernButton trong login_view
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
        """Làm tối màu hex để tạo hiệu ứng hover"""
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        darkened = tuple(max(0, c - 30) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'


class RoomListView:
    """Giao diện danh sách phòng chơi
    
    Hiển thị:
    - Bảng danh sách các phòng đang chờ người chơi
    - Thông tin: Room ID, Room Name, Host, Players (1/2 hoặc 2/2)
    - Nút: Refresh, Join, Back
    """
    
    def __init__(self, parent):
        """Khởi tạo giao diện danh sách phòng
        
        Args:
            parent: Cửa sổ Tkinter cha
        
        Tạo Treeview (bảng) để hiển thị danh sách phòng
        """
        self.parent = parent
        self.on_refresh = None
        self.on_join = None
        self.on_back = None
        
        # Main frame
        self.frame = tk.Frame(parent, bg='#0f172a')
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Content
        content = tk.Frame(self.frame, bg='#1e293b', padx=40, pady=30)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content, text="🔍 Available Rooms",
            font=('Segoe UI', 20, 'bold'),
            bg='#1e293b', fg='#60a5fa'
        ).pack(pady=(0, 20))
        
        # Table
        table_frame = tk.Frame(content, bg='#334155')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#334155', foreground='white', fieldbackground='#334155', borderwidth=0)
        style.configure('Treeview.Heading', background='#475569', foreground='white', borderwidth=0)
        style.map('Treeview', background=[('selected', '#3b82f6')])
        
        columns = ('Room ID', 'Room Name', 'Host', 'Players')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = tk.Frame(content, bg='#1e293b')
        btn_frame.pack()
        
        ModernButton(
            btn_frame, "🔄 REFRESH",
            lambda: self.on_refresh() if self.on_refresh else None,
            color='#8b5cf6', width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "✅ JOIN",
            self._on_join_click,
            color='#10b981', width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            btn_frame, "← BACK",
            lambda: self.on_back() if self.on_back else None,
            color='#6b7280', width=12
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_join_click(self):
        """Xử lý khi click nút Join
        
        1. Kiểm tra đã chọn phòng chưa
        2. Lấy thông tin phòng được chọn
        3. Gọi callback on_join với room_data
        """
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a room")
            return
        
        item = self.tree.item(selection[0])
        room_data = {
            'id': item['values'][0],
            'room_name': item['values'][1],
            'host_username': item['values'][2],
            'current_players': 1,
            'max_players': 2
        }
        
        if self.on_join:
            self.on_join(room_data)
    
    def update_rooms(self, rooms):
        """Cập nhật danh sách phòng hiển thị
        
        Args:
            rooms: List các dict chứa thông tin phòng
                   Mỗi dict có keys: id, room_name, host_username, 
                   current_players, max_players
        
        Xóa dữ liệu cũ và thêm dữ liệu mới vào Treeview
        """
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new
        for room in rooms:
            self.tree.insert('', tk.END, values=(
                room['id'],
                room['room_name'],
                room['host_username'],
                f"{room['current_players']}/{room['max_players']}"
            ))
    
    def destroy(self):
        self.frame.destroy()
