"""
Statistics View - Tkinter + Matplotlib version
Beautiful charts with professional UI
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from views.opponent_info_view import show_opponent_info
import matplotlib.patches as mpatches


class StatisticsViewTk:
    """Màn hình thống kê tổng quan - Dùng Tkinter + Matplotlib
    
    Hiển thị thống kê tất cả các trận của người chơi:
    - 6 thẻ thống kê tổng quan (Total Games, Wins, Losses, Win Rate, Ships Sunk, Best Streak)
    - Biểu đồ tròn Win/Loss
    - Biểu đồ radar 3 chỉ số (Accuracy, Win Rate, Efficiency)
    - Biểu đồ xu hướng độ chính xác theo thời gian
    - Biểu đồ cột Hits vs Misses
    - Biểu đồ hiệu suất trung bình
    - Bảng 20 trận gần nhất
    
    Có scrollbar để cuộn xem tất cả nội dung
    """
    
    def __init__(self, parent, user, lobby_client, on_back):
        """Khởi tạo màn hình thống kê
        
        Args:
            parent: Cửa sổ Tkinter cha
            user: Dict thông tin người dùng (có 'id' và 'username')
            lobby_client: Client kết nối server để lấy dữ liệu
            on_back: Callback khi nhấn nút Back to Home
        
        Flow:
        1. Setup background và canvas
        2. Tạo scrollbar và scroll frame
        3. Load dữ liệu thống kê từ server
        4. Xây dựng UI với các biểu đồ
        """
        self.parent = parent
        self.user = user
        self.lobby_client = lobby_client
        self.on_back = on_back
        
        self.stats = None
        self.recent_games = []
        self.win_streak = None
        
        # Store parent reference for resize
        self.parent_window = parent.winfo_toplevel()
        
        # Configure parent
        parent.configure(bg='#0f172a')
        
        # Configure scrollbar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Vertical.TScrollbar',
            background='#1e293b',
            darkcolor='#0f172a',
            lightcolor='#1e293b',
            troughcolor='#0f172a',
            bordercolor='#1e293b',
            arrowcolor='#60a5fa'
        )
        style.map('Vertical.TScrollbar',
            background=[('active', '#3b82f6'), ('!active', '#1e293b')]
        )
        
        # Create canvas with background
        self.canvas = tk.Canvas(parent, bg='#0f172a', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Store background image for resizing
        self.bg_image_id = None
        
        # Load and set background
        self.setup_background()
        
        # Create scrollable frame
        self.scroll_frame = tk.Frame(self.canvas, bg='#0f172a')
        self.canvas_window = self.canvas.create_window(0, 0, window=self.scroll_frame, anchor='nw')
        
        # Load data and build UI
        self.load_data()
        self.build_ui()
        
        # Configure scrolling
        self.scroll_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Mousewheel scroll
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind resize event
        self.parent_window.bind('<Configure>', self._on_window_resize)
    
    def setup_background(self):
        """Thiết lập hình nền
        
        Tải hình background.jpeg, resize theo kích thước canvas
        Thêm overlay tối (alpha=200) để làm nền mời cho nội dung
        Hiển thị lên canvas
        """
        try:
            # Get canvas size
            canvas_width = max(self.canvas.winfo_width(), 900)
            canvas_height = max(self.canvas.winfo_height(), 650)
            
            # Load and resize background
            bg = Image.open('assets/background/background.jpeg')
            bg = bg.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            # Dark overlay
            overlay = Image.new('RGBA', bg.size, (15, 23, 42, 200))
            bg = bg.convert('RGBA')
            bg = Image.alpha_composite(bg, overlay)
            
            self.bg_photo = ImageTk.PhotoImage(bg)
            
            # Delete old background if exists
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)
            
            # Create new background
            self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor='nw')
            
            # Lower background behind all other items
            self.canvas.tag_lower(self.bg_image_id)
        except Exception as e:
            print(f"[STATS] Error setting background: {e}")
    
    def load_data(self):
        """Lấy dữ liệu thống kê từ server
        
        Gửi 3 requests:
        1. get_user_stats: Thống kê tổng hợp
           (total_games, wins, losses, win_rate, accuracy, ships_sunk, hits, misses, streak)
        2. get_recent_games: 20 trận gần nhất
           (opponent, result, ships_sunk, hits, misses, accuracy, streak, played_at)
        3. get_win_streak: Chuỗi thắng hiện tại (không dùng, có thể bỏ)
        
        Lưu vào:
        - self.stats: Dict thống kê tổng
        - self.recent_games: List 20 trận
        - self.win_streak: Chuỗi thắng
        """
        if self.lobby_client:
            try:
                print(f"[STATS TK] Requesting user stats for user_id={self.user['id']}")
                
                # Get user stats
                stats_response = self.lobby_client.send_data_to_server({
                    'request': 'get_user_stats',
                    'user_id': self.user['id']
                })
                self.stats = stats_response.get('stats')
                print(f"[STATS TK] Stats: {self.stats}")
                
                # Get recent games
                games_response = self.lobby_client.send_data_to_server({
                    'request': 'get_recent_games',
                    'user_id': self.user['id'],
                    'limit': 20
                })
                self.recent_games = games_response.get('games', [])
                print(f"[STATS TK] Recent games: {len(self.recent_games)} games")
                
                # Get win streak
                streak_response = self.lobby_client.send_data_to_server({
                    'request': 'get_win_streak',
                    'user_id': self.user['id']
                })
                self.win_streak = streak_response.get('streak')
                print(f"[STATS TK] Win streak: {self.win_streak}")
                
            except Exception as e:
                print(f"[ERROR] Failed to load statistics: {e}")
                import traceback
                traceback.print_exc()
    
    
    def build_ui(self):
        """Xây dựng giao diện với thiết kế hiện đại
        
        Nếu không có dữ liệu (total_games = 0):
        - Hiển thị thông báo "No games played yet!"
        
        Nếu có dữ liệu:
        1. Header: Tiêu đề + tên người dùng
        2. Summary cards: 6 thẻ thống kê
        3. Charts row 1: Win/Loss Pie + Performance Radar
        4. Charts row 2: Accuracy Trend Over Time (nếu >= 3 trận)
        5. Charts row 3: Hits vs Misses + Performance Breakdown
        6. Recent games table: Bảng 20 trận gần nhất
        7. Back button: Quay về trang chủ
        """
        # Header with gradient background
        header_frame = tk.Frame(self.scroll_frame, bg='#1e293b', height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with anchor icon
        title_container = tk.Frame(header_frame, bg='#1e293b')
        title_container.pack(expand=True)
        
        title_label = tk.Label(
            title_container,
            text=f"⚓ PLAYER STATISTICS",
            font=('Segoe UI', 28, 'bold'),
            bg='#1e293b',
            fg='#60a5fa'
        )
        title_label.pack(pady=10)
        
        username_label = tk.Label(
            title_container,
            text=self.user['username'],
            font=('Segoe UI', 16),
            bg='#1e293b',
            fg='#94a3b8'
        )
        username_label.pack()
        
        if not self.stats or self.stats.get('total_games', 0) == 0:
            # No data message
            no_data_frame = tk.Frame(self.scroll_frame, bg='#1e293b', bd=2, relief=tk.RAISED)
            no_data_frame.pack(pady=50, padx=20)
            
            no_data_label = tk.Label(
                no_data_frame,
                text="⚔ No games played yet!\n\nPlay some battles to see your statistics.",
                font=('Segoe UI', 14),
                bg='#1e293b',
                fg='#cbd5e1',
                pady=40,
                padx=60
            )
            no_data_label.pack()
        else:
            # Summary cards with glass effect
            self.create_modern_summary_cards()
            
            # Charts row
            charts_container = tk.Frame(self.scroll_frame, bg='#0f172a')
            charts_container.pack(fill=tk.X, padx=20, pady=10)
            
            # Left: Win/Loss Pie + Accuracy Gauge
            left_charts = tk.Frame(charts_container, bg='#1e293b', bd=2, relief=tk.RAISED)
            left_charts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            # Right: Performance Trends
            right_charts = tk.Frame(charts_container, bg='#1e293b', bd=2, relief=tk.RAISED)
            right_charts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
            
            self.create_pie_chart(left_charts)
            self.create_performance_chart(right_charts)
            
            # New charts row - Accuracy Trend Over Time
            if len(self.recent_games) >= 3:  # Only show if we have enough data
                accuracy_trend_container = tk.Frame(self.scroll_frame, bg='#1e293b', bd=2, relief=tk.RAISED)
                accuracy_trend_container.pack(fill=tk.X, padx=20, pady=10)
                self.create_accuracy_trend_chart(accuracy_trend_container)
            
            # Performance Breakdown row
            breakdown_container = tk.Frame(self.scroll_frame, bg='#0f172a')
            breakdown_container.pack(fill=tk.X, padx=20, pady=10)
            
            # Left: Hits vs Misses
            hits_misses_frame = tk.Frame(breakdown_container, bg='#1e293b', bd=2, relief=tk.RAISED)
            hits_misses_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self.create_hits_misses_chart(hits_misses_frame)
            
            # Right: Ships Sunk & Avg Hits per Game
            ships_stats_frame = tk.Frame(breakdown_container, bg='#1e293b', bd=2, relief=tk.RAISED)
            ships_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
            self.create_ships_stats_chart(ships_stats_frame)
            
            # Recent games table
            self.create_modern_games_table()
        
        # Back button
        btn_frame = tk.Frame(self.scroll_frame, bg='#0f172a')
        btn_frame.pack(pady=20)
        
        back_btn = tk.Button(
            btn_frame,
            text="← BACK TO HOME",
            command=self.on_back,
            font=('Segoe UI', 12, 'bold'),
            bg='#475569',
            fg='white',
            activebackground='#64748b',
            activeforeground='white',
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        back_btn.pack()
    
    def create_modern_summary_cards(self):
        """Tạo 8 thẻ thống kê với icon
        
        8 thẻ (2 hàng x 4 cột):
        1. 🎮 Total Games (xanh dương)
        2. 🏆 Wins (xanh lá)
        3. 💀 Losses (đỏ)
        4. 📊TWin Rate (cam)
        5. 🎯 Accuracy (vàng) - MỚi
        6. 🔥 Current Streak (hồng) - MỚi
        7. ⚓ Ships Sunk (tím)
        8. ⭐ Longest Win Streak (vàng đậm) - MỚi
        
        Mỗi thẻ có:
        - Icon lớn phía trên
        - Giá trị (số) lớn với màu tương ứng
        - Nhãn (label) bên dưới
        
        Nền: #1e293b (tối), viền nổi
        """
        cards_frame = tk.Frame(self.scroll_frame, bg='#0f172a')
        cards_frame.pack(pady=20, padx=20)
        
        win_rate = self.stats['win_rate']
        avg_accuracy = float(self.stats.get('avg_accuracy', 0))
        
        # Lấy current streak và longest streak
        current_streak = 0
        longest_streak = int(self.stats.get('best_streak', 0))
        
        if self.win_streak:
            current_streak = int(self.win_streak.get('current_streak', 0))
            longest_from_api = int(self.win_streak.get('longest_streak', 0))
            longest_streak = max(longest_streak, longest_from_api)
        
        cards_data = [
            ("🎮", "Total Games", int(self.stats['total_games']), "#3b82f6"),
            ("🏆", "Wins", int(self.stats['total_wins']), "#10b981"),
            ("💀", "Losses", int(self.stats['total_losses']), "#ef4444"),
            ("📊", "Win Rate", f"{win_rate:.1f}%", "#f59e0b"),
            ("🎯", "Avg Accuracy", f"{avg_accuracy:.1f}%", "#eab308"),
            ("🔥", "Current Streak", f"{current_streak}W", "#ec4899"),
            ("⚓", "Ships Sunk", int(self.stats['total_ships_sunk']), "#8b5cf6"),
            ("⭐", "Best Win Streak", f"{longest_streak}W", "#facc15")
        ]
        
        for i, (icon, label, value, color) in enumerate(cards_data):
            card = tk.Frame(cards_frame, bg='#1e293b', bd=2, relief=tk.RAISED)
            card.grid(row=i//4, column=i%4, padx=10, pady=10, ipadx=20, ipady=15)
            
            # Icon
            icon_label = tk.Label(
                card,
                text=icon,
                font=('Segoe UI', 32),
                bg='#1e293b'
            )
            icon_label.pack()
            
            # Value
            value_label = tk.Label(
                card,
                text=str(value),
                font=('Segoe UI', 28, 'bold'),
                bg='#1e293b',
                fg=color
            )
            value_label.pack()
            
            # Label
            label_widget = tk.Label(
                card,
                text=label,
                font=('Segoe UI', 11),
                bg='#1e293b',
                fg='#94a3b8'
            )
            label_widget.pack()
    
    
    def create_pie_chart(self, parent):
        """Tạo biểu đồ tròn phân bố Win/Loss
        
        Args:
            parent: Frame cha chứa biểu đồ
        
        Biểu đồ tròn 2 phần:
        - Phần xanh lá: Số trận thắng (#10b981)
        - Phần đỏ: Số trận thua (#ef4444)
        
        Hiển thị:
        - Phần trăm mỗi phần trên biểu đồ
        - Tiêu đề: "{wins}W - {losses}L"
        - Có hiệu ứng bóng đổ (shadow)
        - Explode: Tách nhẹ ra khỏi tâm
        
        Dùng Matplotlib FigureCanvasTkAgg để nhúng vào Tkinter
        """
        # Title
        title_frame = tk.Frame(parent, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="📊 Win/Loss Distribution",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        ).pack()
        
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='#1e293b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1e293b')
        
        wins = int(self.stats['total_wins'])
        losses = int(self.stats['total_losses'])
        
        colors = ['#10b981', '#ef4444']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            [wins, losses],
            labels=['Wins', 'Losses'],
            autopct='%1.1f%%',
            colors=colors,
            explode=explode,
            shadow=True,
            startangle=90,
            textprops={'color': 'white', 'fontsize': 11, 'weight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')
        
        ax.set_title(f'{wins}W - {losses}L', fontsize=13, color='#cbd5e1', pad=15, weight='bold')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
    
    def create_performance_chart(self, parent):
        """Tạo biểu đồ radar cho các chỉ số hiệu suất
        
        Args:
            parent: Frame cha chứa biểu đồ
        
        Biểu đồ radar 3 trục (0-100%):
        1. Accuracy: Độ chính xác = hits / (hits + misses) * 100
        2. Win Rate: Tỉ lệ thắng = wins / total_games * 100
        3. Efficiency: Hiệu suất = ships_sunk / hits * 100 (scale x5)
           Perfect efficiency: 1 tàu/5 hits = 20% = 100% trên biểu đồ
        
        Hiệu ứng:
        - Vùng xanh dương (#3b82f6) biểu thị giá trị thực tế
        - Đường nét đứt 50% làm reference (trung bình)
        - Lưới tịa vào tâm
        
        Đây là 3 chỉ số quan trọng nhất để đánh giá người chơi
        """
        # Title
        title_frame = tk.Frame(parent, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="⚡ Performance Radar",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        ).pack()
        
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='#1e293b')
        ax = fig.add_subplot(111, projection='polar')
        ax.set_facecolor('#0f172a')
        
        # Calculate metrics
        total_games = max(float(self.stats['total_games']), 1)
        total_wins = float(self.stats['total_wins'])
        total_hits = float(self.stats.get('total_hits', 0))
        total_misses = float(self.stats.get('total_misses', 0))
        total_ships_sunk = float(self.stats['total_ships_sunk'])
        
        # Metrics for radar (3 dimensions) - ⭐⭐⭐⭐⭐
        categories = ['Accuracy', 'Win Rate', 'Efficiency']
        
        # 1. Accuracy: hits / (hits + misses) - Kỹ năng ngắm bắn
        accuracy = float(self.stats['avg_accuracy'])  # Already calculated as percentage
        
        # 2. Win Rate: wins / total_games - Mục tiêu cuối cùng
        win_rate = (total_wins / total_games) * 100
        
        # 3. Efficiency: ships_sunk / hits - Khả năng hoàn thiện công việc sau khi trúng
        # Scale to percentage: perfect efficiency = 1 ship per 5 hits (20%) = 100%
        if total_hits > 0:
            raw_efficiency = (total_ships_sunk / total_hits) * 100  # Convert to percentage
            efficiency = min(raw_efficiency * 5, 100)  # Scale so 20% = 100%
        else:
            efficiency = 0
        
        values = [accuracy, win_rate, efficiency]
        
        # Number of variables
        num_vars = len(categories)
        
        # Compute angle for each axis
        angles = [n / float(num_vars) * 2 * 3.14159 for n in range(num_vars)]
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        # Plot data
        ax.plot(angles, values, 'o-', linewidth=2.5, color='#3b82f6', label='Your Stats')
        ax.fill(angles, values, alpha=0.3, color='#3b82f6')
        
        # Add reference circle at 50%
        reference = [50] * (num_vars + 1)
        ax.plot(angles, reference, '--', linewidth=1, color='#64748b', alpha=0.5, label='Average')
        
        # Fix axis to go from 0 to 100
        ax.set_ylim(0, 100)
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color='#e2e8f0', fontsize=10, weight='bold')
        
        # Set radial labels
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25', '50', '75', '100'], color='#94a3b8', fontsize=8)
        
        # Grid styling
        ax.grid(color='#475569', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.spines['polar'].set_color('#475569')
        
        # Legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), 
                 frameon=True, facecolor='#1e293b', edgecolor='#475569',
                 labelcolor='#e2e8f0', fontsize=9)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
    
    def create_accuracy_trend_chart(self, parent):
        """Tạo biểu đồ xu hướng Thắng/Thua theo thời gian
        
        Args:
            parent: Frame cha chứa biểu đồ
        
        Biểu đồ line chart:
        - Trục X: Số thứ tự trận (1, 2, 3, ..., 20)
        - Trục Y: Kết quả (Win = 1, Loss = 0)
        - Đường xanh lá: Wins
        - Đường đỏ: Losses
        - Hiển thị rõ ràng xu hướng thắng thua gần đây
        
        Hiển thị 20 trận gần nhất theo thời gian
        Giúp người chơi thấy xu hướng tiến bộ hay thoi thoái bộ
        
        Chỉ hiển thị nếu có >= 3 trận
        """
        # Title
        title_frame = tk.Frame(parent, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="📈 Kết Quả Trận Đấu Gần Đây (20 trận cuối)",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        ).pack()
        
        fig = Figure(figsize=(10, 3.5), dpi=90, facecolor='#1e293b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0f172a')
        
        # Lấy dữ liệu từ recent games (reversed để hiển thị theo thời gian)
        games = list(reversed(self.recent_games[:20]))  # 20 trận cuối theo thời gian
        game_numbers = list(range(1, len(games) + 1))
        
        # Chuẩn bị dữ liệu: Win = 1, Loss = 0
        results = []
        win_positions = []
        loss_positions = []
        
        for i, game in enumerate(games, 1):
            if game['result'] == 'win':
                results.append(1)
                win_positions.append(i)
            else:
                results.append(0)
                loss_positions.append(i)
        
        # Vẽ điểm Wins (xanh lá)
        if win_positions:
            ax.scatter(win_positions, [1]*len(win_positions), 
                      s=150, marker='^', color='#10b981', 
                      label='Thắng ✓', edgecolors='white', linewidths=2, zorder=3)
        
        # Vẽ điểm Losses (đỏ)
        if loss_positions:
            ax.scatter(loss_positions, [0]*len(loss_positions), 
                      s=150, marker='v', color='#ef4444', 
                      label='Thua ✗', edgecolors='white', linewidths=2, zorder=3)
        
        # Vẽ đường nối để thấy xu hướng
        ax.plot(game_numbers, results, linewidth=2, color='#64748b', 
               alpha=0.5, linestyle='--', zorder=1)
        
        # Tính win rate trong 20 trận này
        win_count = sum(results)
        recent_win_rate = (win_count / len(results)) * 100 if results else 0
        
        # Thêm text hiển thị win rate
        ax.text(0.02, 0.98, f'Win Rate (20 trận gần nhất): {recent_win_rate:.1f}%',
               transform=ax.transAxes, fontsize=11, weight='bold',
               verticalalignment='top', color='#60a5fa',
               bbox=dict(boxstyle='round', facecolor='#1e293b', alpha=0.8, edgecolor='#475569'))
        
        # Styling
        ax.set_xlabel('Trận thứ (gần đây nhất)', color='#94a3b8', fontsize=11, weight='bold')
        ax.set_ylabel('Kết quả', color='#94a3b8', fontsize=11, weight='bold')
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Thua ✗', 'Thắng ✓'], fontsize=10, weight='bold')
        ax.tick_params(colors='#94a3b8', labelsize=9)
        ax.grid(color='#475569', linestyle='--', linewidth=0.5, alpha=0.5, axis='x')
        ax.set_ylim(-0.2, 1.2)
        
        # Spines styling
        for spine in ax.spines.values():
            spine.set_edgecolor('#475569')
        
        # Legend
        ax.legend(loc='upper right', frameon=True, facecolor='#1e293b', 
                 edgecolor='#475569', labelcolor='#e2e8f0', fontsize=10)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
    
    def create_hits_misses_chart(self, parent):
        """Tạo biểu đồ so sánh Hits vs Misses
        
        Args:
            parent: Frame cha chứa biểu đồ
        
        Biểu đồ cột dọc 2 cột:
        - Cột Hits: Xanh lá (#10b981) - Số phát trúng
        - Cột Misses: Đỏ (#ef4444) - Số phát trượt
        
        Hiển thị:
        - Số lượng phía trên mỗi cột
        - Phần trăm giữa cột
        - Lưới ngang (grid) giúp đọc giá trị
        
        Giúp người chơi thấy tỉ lệ trúng/trượt
        Nên có Hits cao hơn Misses nhiều lần
        """
        # Title
        title_frame = tk.Frame(parent, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="🎯 Hits vs Misses",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        ).pack()
        
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='#1e293b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0f172a')
        
        # Data
        total_hits = float(self.stats['total_hits'])
        total_misses = float(self.stats['total_misses'])
        
        # Bar chart
        categories = ['Hits', 'Misses']
        values = [total_hits, total_misses]
        colors = ['#10b981', '#ef4444']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='#1e293b', linewidth=2)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(value)}',
                   ha='center', va='bottom', color='#e2e8f0', 
                   fontsize=12, weight='bold')
        
        # Add percentage labels
        total_shots = total_hits + total_misses
        if total_shots > 0:
            hit_pct = (total_hits / total_shots) * 100
            miss_pct = (total_misses / total_shots) * 100
            ax.text(0, total_hits/2, f'{hit_pct:.1f}%',
                   ha='center', va='center', color='white', 
                   fontsize=10, weight='bold')
            ax.text(1, total_misses/2, f'{miss_pct:.1f}%',
                   ha='center', va='center', color='white', 
                   fontsize=10, weight='bold')
        
        # Styling
        ax.set_ylabel('Count', color='#94a3b8', fontsize=10, weight='bold')
        ax.tick_params(colors='#94a3b8', labelsize=10)
        ax.grid(axis='y', color='#475569', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Spines styling
        for spine in ax.spines.values():
            spine.set_edgecolor('#475569')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
    
    def create_ships_stats_chart(self, parent):
        """Tạo biểu đồ thống kê tàu chìm và trung bình hits/game
        
        Args:
            parent: Frame cha chứa biểu đồ
        
        Biểu đồ cột dọc 2 cột:
        1. Avg Ships per Game: Tím (#8b5cf6)
           = Total ships sunk / Total games
           Đánh giá số tàu trung bình đánh chìm mỗi trận
           (Lý tưởng: 5 = thắng mọi trận)
        
        2. Avg Hits per Game: Cam (#f59e0b)
           = Total hits / Total games
           Đánh giá độ chính xác tổng quát
           (Thấp hơn thì hiệu quả hơn)
        
        Hiển thị:
        - Giá trị trung bình trên cột (ví dụ: 3.5)
        - Tổng số bên dưới (ví dụ: Total: 175 ships, 850 hits)
        """
        # Title
        title_frame = tk.Frame(parent, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="⚓ Performance Breakdown",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        ).pack()
        
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='#1e293b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0f172a')
        
        # Calculate data
        total_games = float(self.stats['total_games'])
        total_ships_sunk = float(self.stats['total_ships_sunk'])
        total_hits = float(self.stats['total_hits'])
        
        avg_ships_per_game = total_ships_sunk / total_games if total_games > 0 else 0
        avg_hits_per_game = total_hits / total_games if total_games > 0 else 0
        
        # Bar chart with two metrics
        categories = ['Avg Ships\nper Game', 'Avg Hits\nper Game']
        values = [avg_ships_per_game, avg_hits_per_game]
        colors = ['#8b5cf6', '#f59e0b']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='#1e293b', linewidth=2)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}',
                   ha='center', va='bottom', color='#e2e8f0', 
                   fontsize=12, weight='bold')
        
        # Add total counts as text below
        info_text = f'Total Ships Sunk: {int(total_ships_sunk)} | Total Hits: {int(total_hits)}'
        ax.text(0.5, -0.15, info_text,
               ha='center', va='top', transform=ax.transAxes,
               color='#94a3b8', fontsize=9, weight='bold')
        
        # Styling
        ax.set_ylabel('Average Count', color='#94a3b8', fontsize=10, weight='bold')
        ax.tick_params(colors='#94a3b8', labelsize=10)
        ax.grid(axis='y', color='#475569', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Spines styling
        for spine in ax.spines.values():
            spine.set_edgecolor('#475569')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
    
    
    def create_modern_games_table(self):
        """Tạo bảng 20 trận đấu gần nhất với thiết kế hiện đại
        
        Treeview (bảng) với 6 cột:
        1. 📅 Date: Ngày giờ chơi (played_at) - Format: YYYY-MM-DD HH:MM
        2. ⚔ Opponent: Tên đối thủ (tối đa 12 ký tự)
        3. 🏆 Result: Kết quả (WIN/LOSS)
        4. ⚓ Ships Sunk: Số tàu đánh chìm
        5. 🎯 Accuracy: Độ chính xác (%)
        6. 🔥 Streak: Chuỗi trúng dài nhất trong trận
        
        Màu sắc:
        - WIN: Xanh lá đậm, dấu ✓
        - LOSS: Đỏ, dấu ✗
        
        Style:
        - Nền tối (#0f172a)
        - Header xanh dương (#60a5fa)
        - Hover highlight xanh (#3b82f6)
        - Scrollbar để xem tất cả 20 trận
        
        Hiển thị trận mới nhất ở trên cùng
        """
        table_container = tk.Frame(self.scroll_frame, bg='#1e293b', bd=2, relief=tk.RAISED)
        table_container.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = tk.Frame(table_container, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="🎯 Recent Battles",
            font=('Segoe UI', 14, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0'
        ).pack()
        
        # Create custom style for treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Dark.Treeview",
                       background="#0f172a",
                       foreground="#e2e8f0",
                       fieldbackground="#0f172a",
                       borderwidth=0)
        style.configure("Dark.Treeview.Heading",
                       background="#1e293b",
                       foreground="#60a5fa",
                       borderwidth=1,
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))
        style.map("Dark.Treeview",
                 background=[('selected', '#3b82f6')])
        
        # Create Treeview
        columns = ('Date', 'Opponent', 'Result', 'Ships', 'Accuracy', 'Streak')
        tree = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            height=10,
            style="Dark.Treeview"
        )
        
        # Define headings
        tree.heading('Date', text='📅 Date')
        tree.heading('Opponent', text='⚔ Opponent')
        tree.heading('Result', text='🏆 Result')
        tree.heading('Ships', text='⚓ Ships Sunk')
        tree.heading('Accuracy', text='🎯 Accuracy')
        tree.heading('Streak', text='🔥 Streak')
        
        # Column widths
        tree.column('Date', width=150, anchor=tk.CENTER)
        tree.column('Opponent', width=120, anchor=tk.CENTER)
        tree.column('Result', width=80, anchor=tk.CENTER)
        tree.column('Ships', width=100, anchor=tk.CENTER)
        tree.column('Accuracy', width=100, anchor=tk.CENTER)
        tree.column('Streak', width=80, anchor=tk.CENTER)
        
        # Add data
        for game in self.recent_games[:20]:  # Show 20 most recent
            result = game['result'].upper()
            result_display = f"{'✓ ' if result == 'WIN' else '✗ '}{result}"
            result_tag = 'win' if result == 'WIN' else 'loss'
            
            # Format date (played_at is datetime string from database)
            date_str = game.get('played_at', '')
            if date_str:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
                    date_display = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_display = str(date_str)[:16]
            else:
                date_display = 'N/A'
            
            tree.insert('', tk.END, values=(
                date_display,
                game['opponent_username'][:12],
                result_display,
                int(game['ships_sunk']),
                f"{game['accuracy']:.1f}%",
                int(game['max_streak'])
            ), tags=(result_tag,))
        
        # Configure tags
        tree.tag_configure('win', foreground='#10b981', font=('Segoe UI', 10, 'bold'))
        tree.tag_configure('loss', foreground='#ef4444', font=('Segoe UI', 10, 'bold'))
        
        # Bind double-click event to show opponent info
        def on_row_double_click(event):
            """Xử lý double-click vào row để hiển thị thông tin đối thủ"""
            item = tree.selection()
            if item:
                values = tree.item(item[0], 'values')
                if values and len(values) >= 2:
                    opponent_username = values[1]  # Column 1 is Opponent
                    print(f"[STATS VIEW] Double-clicked on opponent: {opponent_username}")
                    self.show_opponent_info(opponent_username)
        
        tree.bind('<Double-Button-1>', on_row_double_click)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def _on_window_resize(self, event):
        """Xử lý khi cửa sổ thay đổi kích thước
        
        Args:
            event: Configure event từ Tkinter
        
        Chỉ update background khi cửa sổ chính (toplevel) thay đổi kích thước
        """
        # Only handle toplevel window resize
        if event.widget == self.parent_window:
            # Schedule background update after a short delay to avoid too many updates
            if hasattr(self, '_resize_after_id'):
                self.parent_window.after_cancel(self._resize_after_id)
            self._resize_after_id = self.parent_window.after(100, self._update_on_resize)
    
    def _update_on_resize(self):
        """Update canvas và background sau khi resize"""
        try:
            # Force canvas to update its size
            self.canvas.update_idletasks()
            
            # Redraw background with new size
            self.setup_background()
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        except Exception as e:
            print(f"[STATS] Error updating on resize: {e}")
    
    def show_opponent_info(self, opponent_username):
        """Hiển thị popup thông tin đối thủ
        
        Args:
            opponent_username: Tên đối thủ cần hiển thị
        
        Gửi request tới server để lấy stats của đối thủ,
        sau đó hiển thị popup OpponentInfoView
        """
        try:
            print(f"[STATS VIEW] Fetching stats for opponent: {opponent_username}")
            
            # Lấy stats từ server qua lobby_client
            if hasattr(self, 'lobby_client') and self.lobby_client:
                opponent_stats = self.lobby_client.get_opponent_stats(opponent_username)
                
                if opponent_stats:
                    print(f"[STATS VIEW] Got stats for {opponent_username}")
                else:
                    print(f"[STATS VIEW] No stats found for {opponent_username}")
                    opponent_stats = None  # Will show default stats
            else:
                print("[STATS VIEW] No lobby_client available")
                opponent_stats = None
            
            # Hiển thị popup (sử dụng self.parent làm root window)
            print(f"[STATS VIEW] Creating popup for {opponent_username}")
            popup = show_opponent_info(self.parent, opponent_username, opponent_stats)
            
            # Chờ popup đóng (blocking - giữ popup mở)
            print("[STATS VIEW] Waiting for popup to close...")
            self.parent.wait_window(popup)
            print("[STATS VIEW] Popup closed")
            
        except Exception as e:
            print(f"[STATS VIEW] Error showing opponent info: {e}")
            import traceback
            traceback.print_exc()
    
    def destroy(self):
        """Dọn dẹp và hủy giao diện
        
        Xóa scroll_frame và canvas khi chuyển về trang chủ
        Giải phóng bộ nhớ từ các biểu đồ Matplotlib
        Unbind resize event
        """
        # Unbind resize event
        if hasattr(self, 'parent_window'):
            try:
                self.parent_window.unbind('<Configure>')
            except:
                pass
        
        # Cancel pending resize updates
        if hasattr(self, '_resize_after_id'):
            try:
                self.parent_window.after_cancel(self._resize_after_id)
            except:
                pass
        
        if hasattr(self, 'scroll_frame'):
            self.scroll_frame.destroy()
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
