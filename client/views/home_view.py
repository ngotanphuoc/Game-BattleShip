"""
Home View - Tkinter UI Component (MVC View Layer)
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFilter


class HomeView:
    """Giao diện trang chủ sau khi đăng nhập
    
    Hiển thị:
    - Tên người dùng
    - Trạng thái server (online/offline)
    - Các nút: Create Room, Browse Rooms, Statistics, Logout
    - Background blur với hiệu ứng glass morphism
    """
    
    def __init__(self, parent, username, is_server_online):
        """Khởi tạo giao diện trang chủ
        
        Args:
            parent: Cửa sổ Tkinter cha
            username: Tên người dùng đã đăng nhập
            is_server_online: True nếu server đang online, False nếu offline
        """
        self.parent = parent
        self.on_create_room = None
        self.on_browse_rooms = None
        self.on_statistics = None
        self.on_logout = None
        
        # Main frame
        self.frame = tk.Frame(parent, bg='#0a0f1e')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Main canvas for layered design
        self.canvas = tk.Canvas(self.frame, bg='#0a0f1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Load background image (full screen)
        try:
            bg_image = Image.open('assets/background/background.jpeg')
            bg_image = bg_image.resize((900, 650), Image.Resampling.LANCZOS)
            
            # Create blurred background for glass effect area
            glass_width = 420
            glass_height = 520
            glass_x = (900 - glass_width) // 2
            glass_y = (650 - glass_height) // 2
            
            # Crop the glass area and apply minimal blur for clear background visibility
            glass_area = bg_image.crop((glass_x, glass_y, glass_x + glass_width, glass_y + glass_height))
            glass_area = glass_area.filter(ImageFilter.GaussianBlur(radius=3))
            
            # Create extremely transparent overlay for maximum background visibility
            overlay = Image.new('RGBA', (glass_width, glass_height), (5, 10, 15, 3))  # Almost invisible overlay
            glass_area = glass_area.convert('RGBA')
            glass_blended = Image.alpha_composite(glass_area, overlay)
            
            # Paste back to main background
            bg_image = bg_image.convert('RGBA')
            bg_image.paste(glass_blended, (glass_x, glass_y))
            
            # Get average color of blurred area for frame background
            self.glass_bg_color = self._get_average_color(glass_blended)
            
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor='nw')
        except Exception as e:
            print(f"[HOME] Could not load background: {e}")
            self.glass_bg_color = '#2a3f5f'
        
        # Get average color from blurred area for widget backgrounds
        # Center position
        center_x = 450
        start_y = 100
        
        # Anchor icon - NO background
        self.canvas.create_text(
            center_x, start_y,
            text="⚓",
            font=('Segoe UI', 56),
            fill='#60a5fa'
        )
        
        # Title - NO background
        self.canvas.create_text(
            center_x, start_y + 80,
            text="BATTLESHIP",
            font=('Segoe UI', 28, 'bold'),
            fill='#ffffff'
        )
        
        # Welcome message - NO background
        self.canvas.create_text(
            center_x, start_y + 130,
            text=f"Welcome back, {username}!",
            font=('Segoe UI', 14),
            fill='#ffffff'
        )
        
        # Server status badge
        status_bg = '#10b981' if is_server_online else '#ef4444'
        status_text = "● SERVER ONLINE" if is_server_online else "● SERVER OFFLINE"
        status_label = tk.Label(
            self.canvas, text=status_text,
            font=('Segoe UI', 9, 'bold'),
            bg=status_bg, fg='white',
            padx=18, pady=5, bd=0
        )
        self.canvas.create_window(center_x, start_y + 170, window=status_label)
        
        # Menu buttons - smaller and rounded
        btn_y = start_y + 230
        
        # Create Room Button
        create_btn = tk.Button(
            self.canvas, text="🎮  CREATE NEW ROOM",
            command=lambda: self.on_create_room() if self.on_create_room else None,
            font=('Segoe UI', 11, 'bold'),
            bg='#3b82f6', fg='white',
            activebackground='#4f94ff', activeforeground='white',
            bd=0, cursor='hand2', width=26, pady=10,
            relief=tk.FLAT, highlightthickness=0
        )
        self.canvas.create_window(center_x, btn_y, window=create_btn)
        
        # Browse Rooms Button
        browse_btn = tk.Button(
            self.canvas, text="🔍  BROWSE ROOMS",
            command=lambda: self.on_browse_rooms() if self.on_browse_rooms else None,
            font=('Segoe UI', 11, 'bold'),
            bg='#8b5cf6', fg='white',
            activebackground='#9d71ff', activeforeground='white',
            bd=0, cursor='hand2', width=26, pady=10,
            relief=tk.FLAT, highlightthickness=0
        )
        self.canvas.create_window(center_x, btn_y + 55, window=browse_btn)
        
        # Statistics Button
        stats_btn = tk.Button(
            self.canvas, text="📊  VIEW STATISTICS",
            command=lambda: self.on_statistics() if self.on_statistics else None,
            font=('Segoe UI', 11, 'bold'),
            bg='#f59e0b', fg='white',
            activebackground='#ffb42e', activeforeground='white',
            bd=0, cursor='hand2', width=26, pady=10,
            relief=tk.FLAT, highlightthickness=0
        )
        self.canvas.create_window(center_x, btn_y + 110, window=stats_btn)
        
        # Logout Button
        logout_btn = tk.Button(
            self.canvas, text="⎋ LOGOUT",
            command=lambda: self.on_logout() if self.on_logout else None,
            font=('Segoe UI', 10, 'bold'),
            bg=self.glass_bg_color, fg='#ef4444',
            activebackground='#ef4444', activeforeground='white',
            bd=2, relief=tk.SOLID, cursor='hand2',
            width=26, pady=8, highlightthickness=0
        )
        self.canvas.create_window(center_x, btn_y + 175, window=logout_btn)
    
    def _get_average_color(self, image):
        """Lấy màu trung bình của hình ảnh
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Mã màu hex (ví dụ: '#2a3f5f')
        
        Dùng để tạo màu nền cho button Logout khớp với background
        """
        # Resize to 1x1 to get average color
        avg = image.resize((1, 1), Image.Resampling.LANCZOS)
        r, g, b, a = avg.getpixel((0, 0))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def destroy(self):
        """Hủy giao diện
        
        Xóa frame khi chuyển sang màn hình khác
        """
        self.frame.destroy()

