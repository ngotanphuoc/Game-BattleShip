"""
Battle Statistics View - Display post-game statistics with charts
"""
import pygame
import math


class BattleStatsView:
    """Hiển thị thống kê sau trận đấu
    
    Màn hình so sánh kết quả giữa 2 người chơi:
    - Số tàu chìm
    - Tổng số phát trúng/trượt
    - Độ chính xác (%)
    - Chuỗi trúng dài nhất
    - Biểu đồ cột so sánh
    - Kết quả VICTORY/DEFEAT
    """
    
    def __init__(self):
        """Khởi tạo BattleStatsView
        
        Tạo các font chữ:
        - font_large: 32pt cho tiêu đề
        - font_medium: 24pt cho banner và biểu đồ
        - font_small: 18pt cho dữ liệu thống kê
        """
        self.font_large = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 32)
        self.font_medium = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 24)
        self.font_small = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 18)
        
        self.next_button = None
        
    def draw(self, window, stats):
        """Vẽ màn hình thống kê trận đấu
        
        Args:
            window: Cửa sổ Pygame
            stats: dict chứa:
                - winner_name: Tên người thắng (hoặc None)
                - my_username: Tên của tôi
                - enemy_username: Tên đối thủ
                - my_ships_sunk: Số tàu tôi đánh chìm
                - enemy_ships_sunk: Số tàu địch đánh chìm
                - my_hits, my_misses: Trúng/trượt của tôi
                - enemy_hits, enemy_misses: Trúng/trượt của địch
                - my_max_streak, enemy_max_streak: Chuỗi trúng dài nhất
        
        Layout:
        - Tiêu đề trên cùng: "BATTLE STATISTICS"
        - Bên trái: Bảng thống kê chi tiết
        - Bên phải: Biểu đồ cột so sánh
        - Phía dưới: Nút NEXT để tiếp tục
        """
        # Gradient background
        self.draw_gradient_background(window)
        
        # Title
        title_text = "BATTLE STATISTICS"
        title_surface = self.font_large.render(title_text, True, (0, 50, 100))
        title_rect = title_surface.get_rect(center=(400, 40))
        window.blit(title_surface, title_rect)
        
        # Left side - Stats table
        self.draw_stats_table(window, stats)
        
        # Right side - Chart
        self.draw_comparison_chart(window, stats)
        
        # Next button (bottom center)
        self.next_button = pygame.Rect(325, 545, 150, 45)
        
        mouse_pos = pygame.mouse.get_pos()
        button_color = (0, 150, 255) if self.next_button.collidepoint(mouse_pos) else (0, 120, 200)
        
        pygame.draw.rect(window, button_color, self.next_button, border_radius=10)
        pygame.draw.rect(window, (255, 255, 255), self.next_button, 3, border_radius=10)
        
        next_text = self.font_medium.render("NEXT", True, (255, 255, 255))
        next_rect = next_text.get_rect(center=self.next_button.center)
        window.blit(next_text, next_rect)
    
    def draw_stats_table(self, window, stats):
        """Vẽ bảng thống kê bên trái
        
        Args:
            window: Cửa sổ Pygame
            stats: Dữ liệu thống kê
        
        Bảng hiển thị:
        - Header: Tên 2 người chơi (my_username vs enemy_username)
        - 5 dòng dữ liệu:
          1. Ships Sunk: Số tàu đánh chìm
          2. Total Hits: Tổng số phát trúng
          3. Total Misses: Tổng số phát trượt
          4. Accuracy: Độ chính xác (%)
          5. Max Streak: Chuỗi trúng dài nhất
        - Footer: Banner VICTORY hoặc DEFEAT
        
        Màu sắc:
        - Cột trái (tôi): Xanh lá cây
        - Cột phải (địch): Đỏ
        """
        # Main stats card - left side
        card_rect = pygame.Rect(30, 80, 360, 420)
        pygame.draw.rect(window, (255, 255, 255), card_rect, border_radius=15)
        pygame.draw.rect(window, (100, 150, 200), card_rect, 3, border_radius=15)
        card_rect = pygame.Rect(30, 80, 360, 430)
        pygame.draw.rect(window, (255, 255, 255), card_rect, border_radius=15)
        pygame.draw.rect(window, (100, 150, 200), card_rect, 3, border_radius=15)
        
        # Player names header
        y_offset = 95
        
        # Column headers with backgrounds
        my_name_bg = pygame.Rect(50, y_offset, 120, 30)
        enemy_name_bg = pygame.Rect(240, y_offset, 120, 30)
        
        pygame.draw.rect(window, (200, 230, 255), my_name_bg, border_radius=8)
        pygame.draw.rect(window, (255, 200, 200), enemy_name_bg, border_radius=8)
        
        my_name_surface = self.font_small.render(stats['my_username'][:10], True, (0, 100, 200))
        enemy_name_surface = self.font_small.render(stats['enemy_username'][:10], True, (200, 0, 0))
        
        my_name_rect = my_name_surface.get_rect(center=(110, y_offset + 15))
        enemy_name_rect = enemy_name_surface.get_rect(center=(300, y_offset + 15))
        
        window.blit(my_name_surface, my_name_rect)
        window.blit(enemy_name_surface, enemy_name_rect)
        
        # Separator line
        y_offset += 40
        pygame.draw.line(window, (150, 180, 220), (45, y_offset), (375, y_offset), 2)
        
        # Statistics rows
        y_offset += 15
        
        # Calculate accuracy
        my_total_shots = stats['my_hits'] + stats['my_misses']
        enemy_total_shots = stats['enemy_hits'] + stats['enemy_misses']
        
        my_accuracy = (stats['my_hits'] / my_total_shots * 100) if my_total_shots > 0 else 0
        enemy_accuracy = (stats['enemy_hits'] / enemy_total_shots * 100) if enemy_total_shots > 0 else 0
        
        # Stats data
        stats_data = [
            ("Ships Sunk", stats['my_ships_sunk'], stats['enemy_ships_sunk']),
            ("Total Hits", stats['my_hits'], stats['enemy_hits']),
            ("Total Misses", stats['my_misses'], stats['enemy_misses']),
            ("Accuracy", f"{my_accuracy:.1f}%", f"{enemy_accuracy:.1f}%"),
            ("Max Streak", stats['my_max_streak'], stats['enemy_max_streak'])
        ]
        
        for i, (label, my_value, enemy_value) in enumerate(stats_data):
            # Alternating row background
            if i % 2 == 0:
                row_bg = pygame.Rect(40, y_offset - 3, 340, 35)
                pygame.draw.rect(window, (245, 250, 255), row_bg, border_radius=5)
            
            # Label (centered)
            label_surface = self.font_small.render(label, True, (40, 60, 80))
            label_rect = label_surface.get_rect(center=(210, y_offset + 10))
            window.blit(label_surface, label_rect)
            
            # My value (left side)
            my_color = (0, 130, 0)
            my_value_surface = self.font_small.render(str(my_value), True, my_color)
            my_value_rect = my_value_surface.get_rect(center=(110, y_offset + 10))
            window.blit(my_value_surface, my_value_rect)
            
            # Enemy value (right side)
            enemy_color = (180, 0, 0)
            enemy_value_surface = self.font_small.render(str(enemy_value), True, enemy_color)
            enemy_value_rect = enemy_value_surface.get_rect(center=(300, y_offset + 10))
            window.blit(enemy_value_surface, enemy_value_rect)
            
            y_offset += 40
        
        # Winner banner
        y_offset += 15
        if stats.get('winner_name'):
            is_winner = stats['winner_name'] == stats['my_username']
            
            if is_winner:
                banner_text = "VICTORY!"
                banner_color = (0, 180, 0)
                banner_bg = (220, 255, 220)
            else:
                banner_text = "DEFEAT"
                banner_color = (200, 0, 0)
                banner_bg = (255, 220, 220)
            
            # Banner background
            banner_bg_rect = pygame.Rect(60, y_offset - 5, 280, 40)
            pygame.draw.rect(window, banner_bg, banner_bg_rect, border_radius=10)
            pygame.draw.rect(window, banner_color, banner_bg_rect, 3, border_radius=10)
            
            banner_surface = self.font_medium.render(banner_text, True, banner_color)
            banner_rect = banner_surface.get_rect(center=(200, y_offset + 15))
            window.blit(banner_surface, banner_rect)
    
    def draw_comparison_chart(self, window, stats):
        """Vẽ biểu đồ cột so sánh bên phải
        
        Args:
            window: Cửa sổ Pygame
            stats: Dữ liệu thống kê
        
        Biểu đồ cột ngang so sánh 4 chỉ số:
        1. Ships Sunk (max = 5)
        2. Total Hits (max = tổng số phát lớn hơn)
        3. Total Misses (max = tổng số phát lớn hơn)
        4. Max Streak (max = chuỗi dài hơn)
        
        Mỗi chỉ số có 2 cột:
        - Cột trên: Xanh lá (my_value)
        - Cột dưới: Hồng (enemy_value)
        
        Chiều dài cột tỉ lệ với giá trị (max_bar_width = 290px)
        Hiển thị số trên cột hoặc bên cạnh nếu cột quá ngắn
        """
        # Chart card - wider to prevent overflow (increased height)
        card_rect = pygame.Rect(410, 80, 370, 450)
        pygame.draw.rect(window, (255, 255, 255), card_rect, border_radius=15)
        pygame.draw.rect(window, (100, 150, 200), card_rect, 3, border_radius=15)
        
        # Chart title
        title = self.font_medium.render("Comparison Chart", True, (0, 50, 100))
        title_rect = title.get_rect(center=(590, 100))
        window.blit(title, title_rect)
        
        # Legend at top
        legend_y = 130
        
        # My legend
        my_legend_rect = pygame.Rect(450, legend_y, 25, 20)
        pygame.draw.rect(window, (100, 200, 100), my_legend_rect, border_radius=3)
        pygame.draw.rect(window, (0, 130, 0), my_legend_rect, 2, border_radius=3)
        legend_text = self.font_small.render(stats['my_username'][:8], True, (0, 100, 0))
        window.blit(legend_text, (485, legend_y + 2))
        
        # Enemy legend  
        enemy_legend_rect = pygame.Rect(610, legend_y, 25, 20)
        pygame.draw.rect(window, (255, 150, 150), enemy_legend_rect, border_radius=3)
        pygame.draw.rect(window, (180, 0, 0), enemy_legend_rect, 2, border_radius=3)
        legend_text = self.font_small.render(stats['enemy_username'][:8], True, (180, 0, 0))
        window.blit(legend_text, (645, legend_y + 2))
        
        # Calculate values
        my_total_shots = stats['my_hits'] + stats['my_misses']
        enemy_total_shots = stats['enemy_hits'] + stats['enemy_misses']
        
        # Chart data
        chart_data = [
            ("Ships Sunk", stats['my_ships_sunk'], stats['enemy_ships_sunk'], 5),
            ("Total Hits", stats['my_hits'], stats['enemy_hits'], max(my_total_shots, enemy_total_shots, 1)),
            ("Total Misses", stats['my_misses'], stats['enemy_misses'], max(my_total_shots, enemy_total_shots, 1)),
            ("Max Streak", stats['my_max_streak'], stats['enemy_max_streak'], max(stats['my_max_streak'], stats['enemy_max_streak'], 1))
        ]
        
        # Draw bars
        y_offset = 175
        bar_height = 28
        spacing = 85  # Increased spacing between categories
        max_bar_width = 290  # Wider bars
        
        for label, my_val, enemy_val, max_val in chart_data:
            # Category label
            label_surface = self.font_small.render(label, True, (40, 60, 80))
            window.blit(label_surface, (430, y_offset))
            
            # My bar (top) - only draw if value > 0
            if max_val > 0 and my_val > 0:
                my_width = max(int((my_val / max_val) * max_bar_width), 3)
                my_bar = pygame.Rect(430, y_offset + 22, my_width, bar_height)
                pygame.draw.rect(window, (100, 200, 100), my_bar, border_radius=5)
                pygame.draw.rect(window, (0, 130, 0), my_bar, 2, border_radius=5)
                
                # Value label
                val_text = self.font_small.render(str(my_val), True, (255, 255, 255) if my_width > 35 else (0, 100, 0))
                if my_width > 35:
                    window.blit(val_text, (438, y_offset + 27))
                else:
                    window.blit(val_text, (435 + my_width, y_offset + 27))
            elif my_val == 0:
                # Show "0" text without bar
                zero_text = self.font_small.render("0", True, (150, 150, 150))
                window.blit(zero_text, (430, y_offset + 27))
            
            # Enemy bar (bottom) - only draw if value > 0
            if max_val > 0 and enemy_val > 0:
                enemy_width = max(int((enemy_val / max_val) * max_bar_width), 3)
                enemy_bar = pygame.Rect(430, y_offset + 22 + bar_height + 5, enemy_width, bar_height)
                pygame.draw.rect(window, (255, 150, 150), enemy_bar, border_radius=5)
                pygame.draw.rect(window, (180, 0, 0), enemy_bar, 2, border_radius=5)
                
                # Value label
                val_text = self.font_small.render(str(enemy_val), True, (255, 255, 255) if enemy_width > 35 else (180, 0, 0))
                if enemy_width > 35:
                    window.blit(val_text, (438, y_offset + 32 + bar_height))
                else:
                    window.blit(val_text, (435 + enemy_width, y_offset + 32 + bar_height))
            elif enemy_val == 0:
                # Show "0" text without bar
                zero_text = self.font_small.render("0", True, (150, 150, 150))
                window.blit(zero_text, (430, y_offset + 32 + bar_height))
            
            y_offset += spacing
    
    def draw_gradient_background(self, window):
        """Vẽ nền gradient cho màn hình thống kê
        
        Args:
            window: Cửa sổ Pygame
        
        Gradient từ trên xuống:
        - Trên cùng: Xanh nhạt (240, 248, 255)
        - Giữa: Xanh trung bình (224, 242, 254)
        - Dưới cùng: Xanh đậm hơn (186, 230, 253)
        
        Tạo hiệu ứng bầu trời mướt mà, thanh thoáng
        """
        color_top = (240, 248, 255)
        color_mid = (224, 242, 254)
        color_bottom = (186, 230, 253)
        
        height = window.get_height()
        
        for y in range(height):
            if y < height // 2:
                ratio = y / (height // 2)
                r = int(color_top[0] + (color_mid[0] - color_top[0]) * ratio)
                g = int(color_top[1] + (color_mid[1] - color_top[1]) * ratio)
                b = int(color_top[2] + (color_mid[2] - color_top[2]) * ratio)
            else:
                ratio = (y - height // 2) / (height // 2)
                r = int(color_mid[0] + (color_bottom[0] - color_mid[0]) * ratio)
                g = int(color_mid[1] + (color_bottom[1] - color_mid[1]) * ratio)
                b = int(color_mid[2] + (color_bottom[2] - color_mid[2]) * ratio)
            
            pygame.draw.line(window, (r, g, b), (0, y), (window.get_width(), y))
    
    def handle_click(self, mouse_pos):
        """Xử lý click chuột
        
        Args:
            mouse_pos: (x, y) vị trí chuột
        
        Returns:
            str: 'next' nếu click vào nút Next
                 None nếu click chỗ khác
        
        Khi click Next: Chuyển về màn hình chủ
        """
        if self.next_button and self.next_button.collidepoint(mouse_pos):
            return 'next'
        
        return None
