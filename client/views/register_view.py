"""
Register View - Tkinter UI Component (MVC View Layer)
Giao diện đăng ký giống login
"""

import tkinter as tk
from PIL import Image, ImageTk


class RegisterView:
    """Giao diện màn hình đăng ký tài khoản
    
    Chỉ xử lý UI, không có logic nghiệp vụ (theo mô hình MVC)
    Tương tự LoginView nhưng có thêm ô Confirm Password
    """
    
    def __init__(self, parent):
        """Khởi tạo giao diện đăng ký
        
        Args:
            parent: Cửa sổ Tkinter cha
        
        Tạo giao diện gồm:
        - Phần trái (30%): Form đăng ký trên nền tối
        - Phần phải (70%): Hình nền background
        - Username, Password, Confirm Password entry
        - Nút Create Account và Back to Login
        """
        self.parent = parent
        self.on_register = None  # Callback set by controller
        self.on_back_to_login = None  # Callback to go back to login
        
        # Main frame
        self.frame = tk.Frame(parent, bg='#0f172a')
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load and display background image (right side 70%)
        try:
            bg_image = Image.open('assets/background/background.jpeg')
            bg_image = bg_image.resize((630, 650), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            bg_label = tk.Label(self.frame, image=self.bg_photo)
            bg_label.place(x=270, y=0, width=630, height=650)
        except Exception as e:
            print(f"[REGISTER] Could not load background image: {e}")
        
        # Left side - dark background
        left_bg = tk.Frame(self.frame, bg='#0a0f1e')
        left_bg.place(x=0, y=0, width=270, height=650)
        
        # Vertical divider
        divider = tk.Frame(self.frame, bg='#1e3a8a', width=2)
        divider.place(x=270, y=0, height=650)
        
        # Register form centered
        form_container = tk.Frame(left_bg, bg='#0a0f1e')
        form_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        content = tk.Frame(form_container, bg='#0a0f1e', padx=35, pady=20)
        content.pack()
        
        # Title with icon
        title_frame = tk.Frame(content, bg='#0a0f1e')
        title_frame.grid(row=0, column=0, pady=(0, 30))
        
        tk.Label(
            title_frame, text="⚓",
            font=('Segoe UI', 48),
            bg='#0a0f1e', fg='#10b981'
        ).pack()
        
        tk.Label(
            title_frame, text="CREATE ACCOUNT",
            font=('Segoe UI', 20, 'bold'),
            bg='#0a0f1e', fg='#f8fafc'
        ).pack(pady=(8, 0))
        
        tk.Label(
            title_frame, text="Join the Naval Battle",
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
        username_frame.grid(row=2, column=0, pady=(0, 18))
        
        self.username_entry = tk.Entry(
            username_frame, width=22, font=('Segoe UI', 12),
            bg='#1e293b', fg='white',
            insertbackground='#10b981', relief=tk.FLAT,
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
        password_frame.grid(row=4, column=0, pady=(0, 18))
        
        self.password_entry = tk.Entry(
            password_frame, width=22, show="●", font=('Segoe UI', 12),
            bg='#1e293b', fg='white',
            insertbackground='#10b981', relief=tk.FLAT,
            borderwidth=0
        )
        self.password_entry.pack(padx=12, pady=11, ipady=2)
        
        # Confirm Password field
        tk.Label(
            content, text="CONFIRM PASSWORD",
            font=('Segoe UI', 8, 'bold'),
            bg='#0a0f1e', fg='#64748b'
        ).grid(row=5, column=0, sticky=tk.W, pady=(0, 8))
        
        confirm_password_frame = tk.Frame(content, bg='#1e293b', highlightthickness=1, highlightbackground='#334155')
        confirm_password_frame.grid(row=6, column=0, pady=(0, 25))
        
        self.confirm_password_entry = tk.Entry(
            confirm_password_frame, width=22, show="●", font=('Segoe UI', 12),
            bg='#1e293b', fg='white',
            insertbackground='#10b981', relief=tk.FLAT,
            borderwidth=0
        )
        self.confirm_password_entry.pack(padx=12, pady=11, ipady=2)
        
        # Register Button (green)
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
        register_btn.grid(row=7, column=0, pady=(0, 12))
        
        # Back to Login button
        back_btn = tk.Button(
            content,
            text="← BACK TO LOGIN",
            command=self._on_back_click,
            font=('Segoe UI', 10),
            bg='#1e293b',
            fg='#94a3b8',
            activebackground='#334155',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            width=22,
            pady=10
        )
        back_btn.grid(row=8, column=0)
        
        # Message label
        self.message_label = tk.Label(
            content, text="",
            font=('Segoe UI', 9),
            bg='#0a0f1e',
            wraplength=200
        )
        self.message_label.grid(row=9, column=0, pady=(15, 0))
        
        # Bind Enter key
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind('<Return>', lambda e: self._on_register_click())
        
        # Focus on username
        self.username_entry.focus()
    
    def _on_register_click(self):
        """Xử lý khi click nút Create Account
        
        Validate:
        1. Kiểm tra username và password không rỗng
        2. Kiểm tra password và confirm password khớp nhau
        
        Nếu hợp lệ: Gọi callback on_register để tạo tài khoản
        Nếu không: Hiển thị thông báo lỗi
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validate
        if not username or not password:
            self.show_message("Please fill all fields", is_error=True)
            return
        
        if password != confirm_password:
            self.show_message("Passwords do not match", is_error=True)
            self.confirm_password_entry.delete(0, tk.END)
            return
        
        if self.on_register:
            self.on_register(username, password)
    
    def _on_back_click(self):
        """Xử lý khi click nút Back to Login
        
        Gọi callback on_back_to_login để quay về màn hình đăng nhập
        """
        if self.on_back_to_login:
            self.on_back_to_login()
    
    def show_message(self, message, is_error=False):
        """Hiển thị thông báo cho người dùng
        
        Args:
            message: Nội dung thông báo
            is_error: True = thông báo lỗi (đỏ), False = thông báo thành công (xanh)
        
        Thông báo tự động biến mất sau 4 giây
        
        Ví dụ:
        - "Passwords do not match" (lỗi)
        - "Account created successfully!" (thành công)
        """
        color = '#ef4444' if is_error else '#10b981'
        self.message_label.config(text=message, fg=color)
        
        # Clear message after 4 seconds
        self.parent.after(4000, lambda: self.message_label.config(text=""))
    
    def clear_password(self):
        """Xóa nội dung cả 2 ô password
        
        Xóa password và confirm_password sau khi đăng ký thất bại
        """
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
    
    def destroy(self):
        """Hủy giao diện
        
        Xóa frame và tất cả widgets con khi chuyển sang màn hình khác
        """
        self.frame.destroy()
