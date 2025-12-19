"""
Login View - Tkinter UI Component (MVC View Layer)
Only handles display and user input, no business logic
"""

import tkinter as tk
from PIL import Image, ImageTk


class ModernButton(tk.Button):
    """Button tùy chỉnh với style hiện đại
    
    Custom button với màu sắc và hiệu ứng đẹp mắt
    """
    
    def __init__(self, parent, text, command, color='#3b82f6', **kwargs):
        """Khởi tạo button
        
        Args:
            parent: Widget cha chứa button
            text: Văn bản hiển thị trên button
            command: Hàm được gọi khi click
            color: Màu nền button (hex color)
            **kwargs: Các tham số bổ sung cho tk.Button
        """
        super().__init__(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 11, 'bold'),
            bg=color,
            fg='white',
            activebackground=self._darken_color(color),
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=10,
            padx=20,
            **kwargs
        )
    
    @staticmethod
    def _darken_color(hex_color):
        """Làm tối màu hex đi 30 điểm
        
        Dùng để tạo màu khi hover button (activebackground)
        
        Args:
            hex_color: Mã màu hex (ví dụ: '#3b82f6')
            
        Returns:
            str: Mã màu hex đã làm tối
        """
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        darkened = tuple(max(0, c - 30) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'


class LoginView:
    """Giao diện màn hình đăng nhập
    
    Chỉ xử lý UI, không có logic nghiệp vụ (theo mô hình MVC)
    Controller sẽ xử lý logic đăng nhập thực tế
    """
    
    def __init__(self, parent):
        """Khởi tạo giao diện đăng nhập
        
        Args:
            parent: Cửa sổ Tkinter cha
        
        Tạo giao diện gồm:
        - Phần trái (30%): Form đăng nhập trên nền tối
        - Phần phải (70%): Hình nền background
        - Username và Password entry
        - Nút Login và Register
        """
        self.parent = parent
        self.on_login = None  # Callback set by controller
        self.on_register = None  # Callback set by controller
        
        # Main frame
        self.frame = tk.Frame(parent, bg='#0f172a')
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load and display background image (right side 70%)
        try:
            bg_image = Image.open('assets/background/background.jpeg')
            # Resize to fit right 70% of window (630x650)
            bg_image = bg_image.resize((630, 650), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # Background label on right side
            bg_label = tk.Label(self.frame, image=self.bg_photo)
            bg_label.place(x=270, y=0, width=630, height=650)
        except Exception as e:
            print(f"[LOGIN] Could not load background image: {e}")
        
        # Left side - gradient-like dark background (30%)
        left_bg = tk.Frame(self.frame, bg='#0a0f1e')
        left_bg.place(x=0, y=0, width=270, height=650)
        
        # Vertical divider line
        divider = tk.Frame(self.frame, bg='#1e3a8a', width=2)
        divider.place(x=270, y=0, height=650)
        
        # Login form on left side (centered vertically)
        form_container = tk.Frame(left_bg, bg='#0a0f1e')
        form_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Content inside form with better spacing
        content = tk.Frame(form_container, bg='#0a0f1e', padx=35, pady=20)
        content.pack()
        
        # Title with icon - centered
        title_frame = tk.Frame(content, bg='#0a0f1e')
        title_frame.grid(row=0, column=0, pady=(0, 35))
        
        tk.Label(
            title_frame, text="⚓",
            font=('Segoe UI', 48),
            bg='#0a0f1e', fg='#3b82f6'
        ).pack()
        
        tk.Label(
            title_frame, text="BATTLESHIP",
            font=('Segoe UI', 22, 'bold'),
            bg='#0a0f1e', fg='#f8fafc'
        ).pack(pady=(8, 0))
        
        tk.Label(
            title_frame, text="Naval Combat Game",
            font=('Segoe UI', 9),
            bg='#0a0f1e', fg='#64748b'
        ).pack(pady=(4, 0))
        
        # Username field
        tk.Label(
            content, text="USERNAME",
            font=('Segoe UI', 8, 'bold'),
            bg='#0a0f1e', fg='#64748b'
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
        
        username_frame = tk.Frame(content, bg='#1e293b', highlightthickness=1, highlightbackground='#334155')
        username_frame.grid(row=2, column=0, pady=(0, 20))
        
        self.username_entry = tk.Entry(
            username_frame, width=22, font=('Segoe UI', 12),
            bg='#1e293b', fg='white',
            insertbackground='#3b82f6', relief=tk.FLAT,
            borderwidth=0
        )
        self.username_entry.pack(padx=12, pady=11, ipady=2)
        
        # Password field
        tk.Label(
            content, text="PASSWORD",
            font=('Segoe UI', 8, 'bold'),
            bg='#0a0f1e', fg='#64748b'
        ).grid(row=3, column=0, sticky=tk.W, pady=(0, 8))
        
        password_frame = tk.Frame(content, bg='#1e293b', highlightthickness=1, highlightbackground='#334155')
        password_frame.grid(row=4, column=0, pady=(0, 30))
        
        self.password_entry = tk.Entry(
            password_frame, width=22, show="●", font=('Segoe UI', 12),
            bg='#1e293b', fg='white',
            insertbackground='#3b82f6', relief=tk.FLAT,
            borderwidth=0
        )
        self.password_entry.pack(padx=12, pady=11, ipady=2)
        
        # Login Button (primary) - full width
        login_btn = tk.Button(
            content,
            text="LOGIN",
            command=self._on_login_click,
            font=('Segoe UI', 11, 'bold'),
            bg='#3b82f6',
            fg='white',
            activebackground='#2563eb',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            width=22,
            pady=12
        )
        login_btn.grid(row=5, column=0, pady=(0, 12))
        
        # Register Button (secondary)
        register_btn = tk.Button(
            content,
            text="CREATE ACCOUNT",
            command=self._on_register_click,
            font=('Segoe UI', 11, 'bold'),
            bg='#10b981',
            fg='white',
            activebackground='#059669',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            width=22,
            pady=12
        )
        register_btn.grid(row=6, column=0)
        
        # Status message
        self.status_label = tk.Label(
            content, text="",
            font=('Segoe UI', 8),
            bg='#0a0f1e', wraplength=200,
            justify=tk.CENTER
        )
        self.status_label.grid(row=7, column=0, pady=(18, 0))
        
        # Bindings
        self.username_entry.bind('<Return>', lambda e: self._on_login_click())
        self.password_entry.bind('<Return>', lambda e: self._on_login_click())
    
    def _on_login_click(self):
        """Xử lý khi click nút Login
        
        Lấy username và password từ entry box
        Gọi callback on_login (do controller set) để xử lý đăng nhập
        """
        if self.on_login:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            self.on_login(username, password)
    
    def _on_register_click(self):
        """Xử lý khi click nút Create Account
        
        Gọi callback on_register để chuyển sang màn hình đăng ký
        """
        if self.on_register:
            self.on_register()
    
    def show_message(self, message, is_error=True):
        """Hiển thị thông báo cho người dùng
        
        Args:
            message: Nội dung thông báo
            is_error: True = thông báo lỗi (đỏ), False = thông báo thành công (xanh)
        
        Ví dụ:
        - is_error=True: "❌ Invalid username or password" (màu đỏ)
        - is_error=False: "✅ Login successful!" (màu xanh)
        """
        color = '#ef4444' if is_error else '#10b981'
        icon = '❌' if is_error else '✅'
        self.status_label.config(text=f"{icon} {message}", fg=color)
    
    def clear_password(self):
        """Xóa nội dung ô password
        
        Được gọi sau khi đăng nhập thất bại để người dùng nhập lại
        """
        self.password_entry.delete(0, tk.END)
    
    def destroy(self):
        """Hủy giao diện
        
        Xóa frame và tất cả widgets con khi chuyển sang màn hình khác
        """
        self.frame.destroy()
