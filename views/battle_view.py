"""
Battle View - UI rendering for battle stage
"""
import pygame


class BattleView:
    """Xử lý tất cả việc vẽ giao diện cho màn hình chiến đấu
    
    Class này chỉ làm UI - vẽ lưới, vẽ tàu, vẽ hiệu ứng
    Không chứa logic game (logic ở BattleController)
    
    Hiển thị:
    - 2 lưới 10x10 (MY_GRID bên trái, ENEMY_GRID bên phải)
    - Panel thông tin 2 người chơi
    - Timer đếm ngược 30s/lượt
    - Thông báo lượt chơi
    - Hiệu ứng: explosion (nổ), fire (lửa), crosshair (dấu ngắm)
    """
    
    def __init__(self):
        """Khởi tạo BattleView
        
        Thiết lập:
        - Màu sắc (tàu, nước, trúng, trượt, etc.)
        - Kích thước lưới (10x10, mỗi ô 35x35 pixels)
        - Vị trí lưới (MY_GRID tại x=30, ENEMY_GRID tại x=430)
        - Tải hình ảnh tàu và hiệu ứng
        """
        # Colors - Modern palette
        self.ship_color = (100, 116, 139)  # Slate gray
        self.water_color = (14, 165, 233)  # Sky blue
        self.hit_color = (239, 68, 68)  # Red
        self.miss_color = (148, 163, 184)  # Slate
        self.grid_border_color = (30, 41, 59)  # Slate dark
        self.panel_color = (255, 255, 255)  # White
        self.title_bar_color = (30, 58, 138)  # Blue dark
        self.gradient_colors = [(15, 32, 39), (32, 58, 67), (44, 83, 100)]
        
        # Grid settings
        self.grid_size = 10
        self.cell_size = 35
        self.my_grid_offset = (30, 170)
        self.enemy_grid_offset = (430, 170)
        
        # Load images
        self.load_images()
    
    def load_images(self):
        """Tải tất cả hình ảnh game
        
        Load:
        - Hình ảnh 5 loại tàu (battleship, cruiser, destroyer, plane, submarine)
        - Hiệu ứng fire (lửa)
        - Crosshair (dấu ngắm đỏ khi hover chuột)
        
        Mỗi hình được scale về kích thước 35x35 (cell_size - 2)
        """
        try:
            # Tải hình ảnh tàu
            self.ship_images = {}
            ship_asset_map = {
                'battleship': 'battleship',  # Tàu chiến (5 ô)
                'cruiser': 'cruiser',        #順洋艦 (4 ô)
                'destroyer1': 'destroyer',   # Tàu khu trục 1 (3 ô)
                'destroyer2': 'destroyer',   # Tàu khu trục 2 (3 ô)
                'plane': 'plane'            # Máy bay (2 ô)
            }
            
            for ship_name, asset_name in ship_asset_map.items():
                try:
                    img_path = f'assets/ships/{asset_name}/{asset_name}.png'
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(img, (self.cell_size - 2, self.cell_size - 2))
                    self.ship_images[ship_name] = img
                except Exception as e:
                    print(f"[VIEW] Failed to load {ship_name}: {e}")
                    self.ship_images[ship_name] = None
                    print(f"[VIEW] Failed to load {ship_name}: {e}")
                    self.ship_images[ship_name] = None
            
            # Load fire animation
            self.fire_image = pygame.image.load('assets/fire/frame1.png')
            self.fire_image = pygame.transform.scale(self.fire_image, (self.cell_size - 2, self.cell_size - 2))
            
            # Load crosshair
            self.crosshair_image = pygame.image.load('assets/crosshair/crosshair_red_small.png')
            self.crosshair_image = pygame.transform.scale(self.crosshair_image, (self.cell_size, self.cell_size))
        except Exception as e:
            print(f"[VIEW] Error loading images: {e}")
            self.ship_images = {}
            self.fire_image = None
            self.crosshair_image = None
    
    def draw(self, window, state):
        """Vẽ toàn bộ màn hình trận đấu
        
        Args:
            window: Cửa sổ Pygame để vẽ
            state: Dict chứa trạng thái game (my_turn, time_remaining, grids, etc.)
        
        Thứ tự vẽ (từ dưới lên trên):
        1. Nền gradient
        2. Thanh tiêu đề trên cùng
        3. Panel thông tin 2 người chơi
        4. 2 lưới chơi
        5. Chỉ báo lượt
        6. Timer
        7. Crosshair (nếu hover)
        8. Các thông báo (quit, ship_sunk, timeout, game_over)
        """
        self.draw_gradient_background(window)  # Nền gradient
        self.draw_title_bar(window)  # Thanh tiêu đề trên cùng
        self.draw_player_panels(window, state)  # Bảng thông tin người chơi
        self.draw_grids(window, state)  # 2 lưới chơi
        self.draw_turn_indicator(window, state)  # Chỉ báo lượt chơi
        self.draw_timer(window, state)  # Đồng hồ đếm ngược
        self.draw_crosshair(window, state)  # Dấu ngắm
        
        if state.get('ship_sunk_message'):
            self.draw_ship_sunk_notification(window, state)
        
        if state.get('turn_transition_message'):
            self.draw_turn_transition(window, state)
        
        if state.get('timeout_warning'):
            self.draw_timeout_warning(window, state)
        
        if state.get('game_over_message'):
            self.draw_game_over(window, state)
        
        pygame.display.update()
    
    def draw_gradient_background(self, window):
        """Vẽ nền gradient (chuyển màu dần từ trên xuống dưới)
        
        Màu chuyển từ gradient_colors[0] → [1] → [2]
        Vẽ 600 đường ngang, mỗi đường 1 pixel cao
        Tạo hiệu ứng chuyển màu mượt mà từ tối (trên) đến sáng (dưới)
        """
        for i in range(600):
            ratio = i / 600
            if ratio < 0.5:
                color_ratio = ratio * 2
                r = int(self.gradient_colors[0][0] * (1 - color_ratio) + self.gradient_colors[1][0] * color_ratio)
                g = int(self.gradient_colors[0][1] * (1 - color_ratio) + self.gradient_colors[1][1] * color_ratio)
                b = int(self.gradient_colors[0][2] * (1 - color_ratio) + self.gradient_colors[1][2] * color_ratio)
            else:
                color_ratio = (ratio - 0.5) * 2
                r = int(self.gradient_colors[1][0] * (1 - color_ratio) + self.gradient_colors[2][0] * color_ratio)
                g = int(self.gradient_colors[1][1] * (1 - color_ratio) + self.gradient_colors[2][1] * color_ratio)
                b = int(self.gradient_colors[1][2] * (1 - color_ratio) + self.gradient_colors[2][2] * color_ratio)
            pygame.draw.line(window, (r, g, b), (0, i), (800, i))
    
    def draw_title_bar(self, window):
        """Vẽ thanh tiêu đề trên cùng
        
        Hiển thị: 🚢 BATTLESHIP BATTLE
        Vị trí: y=0, cao 65 pixels, full width
        Có bóng đổ phía dưới
        """
        shadow_rect = pygame.Rect(0, 5, 800, 65)
        pygame.draw.rect(window, (0, 0, 0, 50), shadow_rect)
        title_rect = pygame.Rect(0, 0, 800, 65)
        pygame.draw.rect(window, self.title_bar_color, title_rect)
        
        font_title = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 32)
        title_text = font_title.render('🚢 BATTLESHIP BATTLE', True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 32))
        window.blit(title_text, title_rect)
    
    def draw_player_panels(self, window, state):
        """Vẽ 2 bảng thông tin người chơi
        
        MY PANEL (trái, viền xanh):
        - Tên người chơi
        - 3 ô timeout (đỏ = đã timeout, xám = chưa)
        - Số tàu còn lại
        
        ENEMY PANEL (phải, viền đỏ):
        - Tên đối thủ
        - Timeout của đối thủ
        - Tàu đối thủ còn lại
        """
        font_name = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 18)
        font_label = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 13)
        
        # My panel - Nằm giữa title và tọa độ ABC
        shadow_panel = pygame.Rect(23, 73, 360, 65)
        pygame.draw.rect(window, (0, 0, 0, 30), shadow_panel)
        my_panel = pygame.Rect(20, 70, 360, 65)
        pygame.draw.rect(window, self.panel_color, my_panel)
        pygame.draw.rect(window, (59, 130, 246), my_panel, 3, border_radius=8)
        
        my_name = font_name.render(f'👤 {state.get("my_username", "")}', True, (30, 58, 138))
        window.blit(my_name, (30, 78))
        
        # My timeout boxes
        self.draw_timeout_boxes(window, 220, 82, state.get('my_timeout_count', 0))
        
        my_ships = state.get('total_ships', 5) - state.get('ships_sunk', 0)
        my_ships_text = font_label.render(f'⚓ Ships: {my_ships}/5', True, (34, 197, 94))
        window.blit(my_ships_text, (30, 105))
        
        # Enemy panel - Nằm giữa title và tọa độ ABC
        shadow_panel2 = pygame.Rect(423, 73, 360, 65)
        pygame.draw.rect(window, (0, 0, 0, 30), shadow_panel2)
        enemy_panel = pygame.Rect(420, 70, 360, 65)
        
        # Hover effect - sáng lên khi hover
        is_hover = state.get('enemy_panel_hover', False)
        if is_hover:
            # Màu nền sáng hơn khi hover
            pygame.draw.rect(window, (255, 240, 240), enemy_panel)  # Hồng nhạt
            pygame.draw.rect(window, (239, 68, 68), enemy_panel, 4, border_radius=8)  # Border dày hơn
        else:
            # Màu nền bình thường
            pygame.draw.rect(window, self.panel_color, enemy_panel)
            pygame.draw.rect(window, (239, 68, 68), enemy_panel, 3, border_radius=8)
        
        enemy_display = state.get('enemy_username', 'OPPONENT')
        enemy_name = font_name.render(f'🎯 {enemy_display}', True, (153, 27, 27))
        window.blit(enemy_name, (430, 78))
        
        # Hint text khi hover
        if is_hover:
            hint_font = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 10)
            hint_text = hint_font.render('📊 Click to view stats', True, (100, 100, 100))
            window.blit(hint_text, (645, 79))
        
        # Enemy timeout boxes
        self.draw_timeout_boxes(window, 620, 82, state.get('enemy_timeout_count', 0))
        
        enemy_ships = state.get('total_ships', 5) - state.get('enemy_ships_sunk', 0)
        enemy_ships_text = font_label.render(f'⚓ Ships: {enemy_ships}/5', True, (220, 38, 38))
        window.blit(enemy_ships_text, (430, 105))
    
    def draw_timeout_boxes(self, window, start_x, y, timeout_count):
        """Vẽ 3 ô chỉ báo timeout
        
        Args:
            start_x: Vị trí x bắt đầu
            y: Vị trí y
            timeout_count: Số lần đã timeout (0-3)
        
        Hiển thị:
        - Ô đỏ có dấu X trắng: Đã timeout
        - Ô xám rỗng: Chưa timeout
        """
        box_size = 16
        for i in range(3):
            box_x = start_x + i * 22
            box_rect = pygame.Rect(box_x, y, box_size, box_size)
            if i < timeout_count:
                # Filled red X for timeout
                pygame.draw.rect(window, (239, 68, 68), box_rect)
                pygame.draw.rect(window, (153, 27, 27), box_rect, 2)
                # Draw X
                pygame.draw.line(window, (255, 255, 255), (box_x + 3, y + 3), 
                               (box_x + box_size - 3, y + box_size - 3), 2)
                pygame.draw.line(window, (255, 255, 255), (box_x + box_size - 3, y + 3), 
                               (box_x + 3, y + box_size - 3), 2)
            else:
                # Empty gray box
                pygame.draw.rect(window, (203, 213, 225), box_rect)
                pygame.draw.rect(window, (100, 116, 139), box_rect, 2)
    
    def draw_grids(self, window, state):
        """Vẽ cả 2 lưới chơi
        
        Gọi draw_grid 2 lần:
        1. MY_GRID (trái): is_my_grid=True, offset=(30,170)
        2. ENEMY_GRID (phải): is_my_grid=False, offset=(430,170)
        """
        self.draw_grid(window, self.my_grid_offset, True, state)
        self.draw_grid(window, self.enemy_grid_offset, False, state)
    
    def draw_grid(self, window, offset, is_my_grid, state):
        """Vẽ 1 lưới chơi (10x10 ô)
        
        Args:
            window: Cửa sổ Pygame
            offset: Vị trí lưới (x, y)
            is_my_grid: True = MY_GRID (trái), False = ENEMY_GRID (phải)
            state: Trạng thái game
        
        Thứ tự vẽ:
        1. Bóng đổ (shadow)
        2. Viền lưới (border)
        3. Hình ảnh tàu (chỉ với MY_GRID)
        4. Các ô (cells) với màu tương ứng
        5. Tàu chìm với lửa và dấu X đỏ
        6. Tọa độ A-J và 1-10
        """
        grid_width = self.grid_size * self.cell_size
        grid_height = self.grid_size * self.cell_size
        
        # Shadow
        shadow_rect = pygame.Rect(offset[0] + 3, offset[1] + 3, grid_width, grid_height)
        pygame.draw.rect(window, (100, 100, 100), shadow_rect)
        
        # Border
        border_rect = pygame.Rect(offset[0] - 2, offset[1] - 2, grid_width + 4, grid_height + 4)
        pygame.draw.rect(window, self.grid_border_color, border_rect, 4)
        
        # Draw ship images first (my grid only)
        drawn_ship_cells = set()
        if is_my_grid:
            drawn_ship_cells = self.draw_ship_images(window, offset, state)
        
        # Draw cells
        self.draw_cells(window, offset, is_my_grid, state, drawn_ship_cells)
        
        # Draw sunk ships on both grids
        if not is_my_grid:
            self.draw_sunk_ships(window, offset, state, is_my_grid=False)
        else:
            self.draw_sunk_ships(window, offset, state, is_my_grid=True)
        
        # Draw coordinate labels
        self.draw_coordinates(window, offset)
    
    def draw_ship_images(self, window, offset, state):
        """Vẽ ảnh tàu trên MY_GRID (tàu nổi, chưa bị đánh)
        
        Args:
            window: Cửa sổ Pygame
            offset: Vị trí lưới
            state: Trạng thái game
            
        Returns:
            set: Tập hợp các ô (row, col) đã vẽ ảnh tàu
        
        Logic:
        - CHỈ vẽ tàu chưa bị đánh (không có hit nào)
        - Nếu có 1 ô bị hit → không vẽ ảnh (vẽ fire thay thế)
        - Tàu chìm: SKIP (để draw_sunk_ships xử lý)
        - Vẽ với alpha=200 (hơi trong suốt)
        """
        drawn_cells = set()  # Danh sách ô đã vẽ ảnh tàu
        my_ship_positions = state.get('my_ship_positions', {})
        my_hits = state.get('my_hits', [[False] * 10 for _ in range(10)])
        my_sunk_ships = state.get('my_sunk_ships', set())
        
        for ship_name, ship_list in my_ship_positions.items():
            # Bỏ qua tàu đã chìm - để draw_sunk_ships xử lý
            if ship_name in my_sunk_ships:
                continue
                
            for ship_data in ship_list:
                cells = ship_data['cells']  # Danh sách ô của tàu
                horizontal = ship_data['horizontal']  # Ngang hay dọc
                
                # KHÔNG vẽ ảnh nếu bất kỳ ô nào bị đánh
                any_hit = any(my_hits[r][c] for r, c in cells)
                
                if not any_hit and ship_name in self.ship_images and self.ship_images[ship_name]:
                    start_row, start_col = cells[0]
                    
                    # Draw water background for all ship cells first
                    for r, c in cells:
                        cell_x = offset[0] + c * self.cell_size
                        cell_y = offset[1] + r * self.cell_size
                        cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size - 1, self.cell_size - 1)
                        pygame.draw.rect(window, self.water_color, cell_rect)
                        pygame.draw.rect(window, (60, 60, 60), cell_rect, 1)
                    
                    x = offset[0] + start_col * self.cell_size + 1
                    y = offset[1] + start_row * self.cell_size + 1
                    
                    # Xoay ảnh 90 độ nếu nằm ngang
                    if horizontal:
                        ship_width = len(cells) * self.cell_size - 2
                        ship_height = self.cell_size - 2
                        # Scale ảnh với chiều dọc ban đầu, sau đó xoay 90 độ
                        ship_img = pygame.transform.scale(self.ship_images[ship_name], (ship_height, ship_width))
                        ship_img = pygame.transform.rotate(ship_img, -90)  # Xoay ngược chiều kim đồng hồ
                    else:
                        ship_width = self.cell_size - 2
                        ship_height = len(cells) * self.cell_size - 2
                        ship_img = pygame.transform.scale(self.ship_images[ship_name], (ship_width, ship_height))
                    
                    ship_img.set_alpha(200)  # Same alpha as sunk ships
                    window.blit(ship_img, (x, y))
                    
                    for r, c in cells:
                        drawn_cells.add((r, c))
        
        return drawn_cells
    
    def draw_cells(self, window, offset, is_my_grid, state, drawn_ship_cells):
        """Vẽ từng ô trên lưới (100 ô)
        
        Args:
            window: Cửa sổ Pygame
            offset: Vị trí lưới (x, y)
            is_my_grid: True = MY_GRID, False = ENEMY_GRID
            state: Trạng thái game
            drawn_ship_cells: Set các ô đã vẽ ảnh tàu (bỏ qua)
        
        Logic:
        - Ô tàu chìm: SKIP (draw_sunk_ships sẽ vẽ)
        - Ô tàu nổi có ảnh: SKIP (đã vẽ ở draw_ship_images)
        - Ô trúng: Vẽ đỏ + lửa
        - Ô trượt: Vẽ xám + dấu chấm
        - Ô nước: Vẽ xanh
        """
        my_grid = state.get('my_grid', [])
        enemy_grid = state.get('enemy_grid', [[None] * 10 for _ in range(10)])
        my_hits = state.get('my_hits', [[False] * 10 for _ in range(10)])
        enemy_hits = state.get('enemy_hits', [[False] * 10 for _ in range(10)])
        my_sunk_ships = state.get('my_sunk_ships', set())
        enemy_sunk_ships = state.get('enemy_sunk_ships', set())
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = offset[0] + col * self.cell_size
                y = offset[1] + row * self.cell_size
                
                # Kiểm tra ô này có thuộc tàu chìm không
                is_sunk_ship_cell = False
                if is_my_grid:
                    if my_grid and row < len(my_grid) and col < len(my_grid[row]):
                        ship_name = my_grid[row][col]
                        if ship_name in my_sunk_ships:  # Tàu đã chìm
                            is_sunk_ship_cell = True
                else:
                    ship_name = enemy_grid[row][col]
                    if ship_name in enemy_sunk_ships:
                        is_sunk_ship_cell = True
                
                # Bỏ qua ô tàu chìm - để draw_sunk_ships vẽ
                if is_sunk_ship_cell:
                    continue
                
                # Xác định màu ô
                if is_my_grid:  # Lưới của tôi
                    if my_grid and my_grid[row][col] is not None:  # Có tàu
                        if my_hits[row][col]:  # Bị đánh
                            color = self.hit_color  # Màu đỏ
                        else:  # Chưa bị đánh
                            # Bỏ qua ô có ảnh tàu - đã vẽ rồi
                            if (row, col) in drawn_ship_cells:
                                continue
                            # Không có ảnh, vẽ màu tàu
                            color = self.ship_color
                    else:  # Không có tàu
                        color = self.miss_color if my_hits[row][col] else self.water_color
                else:
                    if enemy_hits[row][col]:
                        if enemy_grid[row][col] is not None and enemy_grid[row][col] != '':
                            color = self.hit_color
                        else:
                            color = self.miss_color
                    else:
                        color = self.water_color
                
                # Draw cell
                cell_rect = pygame.Rect(x, y, self.cell_size - 1, self.cell_size - 1)
                pygame.draw.rect(window, color, cell_rect)
                pygame.draw.rect(window, (60, 60, 60), cell_rect, 1)
                
                # Draw fire for hits
                show_fire = False
                if is_my_grid:
                    if my_grid and my_hits[row][col] and my_grid[row][col] is not None:
                        show_fire = True
                else:
                    if enemy_hits[row][col] and color == self.hit_color:
                        show_fire = True
                
                if show_fire and self.fire_image:
                    window.blit(self.fire_image, (x + 1, y + 1))
                
                # Draw miss dots
                elif is_my_grid and my_hits[row][col] and (not my_grid or my_grid[row][col] is None):
                    pygame.draw.circle(window, (100, 100, 100), 
                                     (x + self.cell_size // 2, y + self.cell_size // 2), 4)
                elif not is_my_grid and enemy_hits[row][col] and (enemy_grid[row][col] is None or enemy_grid[row][col] == ''):
                    pygame.draw.circle(window, (100, 100, 100), 
                                     (x + self.cell_size // 2, y + self.cell_size // 2), 4)
    
    def draw_sunk_ships(self, window, offset, state, is_my_grid=False):
        """Vẽ tàu chìm với ảnh + lửa + dấu X đỏ (cả 2 lưới)
        
        Args:
            window: Cửa sổ Pygame
            offset: Vị trí lưới
            state: Trạng thái game
            is_my_grid: True = tàu của tôi chìm, False = tàu địch chìm
        
        Hiệu ứng vẽ:
        1. Nền nước (water_color) cho tất cả các ô của tàu
        2. Hình ảnh tàu (với alpha=200)
        3. Lửa (fire) trên mỗi ô
        4. Dấu X đỏ chéo qua toàn bộ tàu
        """
        if is_my_grid:
            sunk_ships = state.get('my_sunk_ships', set())  # Tàu của tôi chìm
            grid = state.get('my_grid', [])
        else:
            sunk_ships = state.get('enemy_sunk_ships', set())  # Tàu đối thủ chìm
            grid = state.get('enemy_grid', [[None] * 10 for _ in range(10)])
        
        for ship_name in sunk_ships:
            # Tìm tất cả ô của tàu này
            ship_cells = []
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if grid and row < len(grid) and col < len(grid[row]) and grid[row][col] == ship_name:
                        ship_cells.append((row, col))
            
            if ship_cells:
                ship_cells.sort()
                horizontal = len(set(r for r, c in ship_cells)) == 1
                
                if ship_name in self.ship_images and self.ship_images[ship_name]:
                    start_row, start_col = ship_cells[0]
                    
                    # Draw water background for all ship cells first
                    for r, c in ship_cells:
                        cell_x = offset[0] + c * self.cell_size
                        cell_y = offset[1] + r * self.cell_size
                        cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size - 1, self.cell_size - 1)
                        pygame.draw.rect(window, self.water_color, cell_rect)
                        pygame.draw.rect(window, (60, 60, 60), cell_rect, 1)
                    
                    x = offset[0] + start_col * self.cell_size + 1
                    y = offset[1] + start_row * self.cell_size + 1
                    
                    # Xoay ảnh 90 độ nếu nằm ngang
                    if horizontal:
                        ship_width = len(ship_cells) * self.cell_size - 2
                        ship_height = self.cell_size - 2
                        # Scale ảnh với chiều dọc ban đầu, sau đó xoay 90 độ
                        ship_img = pygame.transform.scale(self.ship_images[ship_name], (ship_height, ship_width))
                        ship_img = pygame.transform.rotate(ship_img, -90)  # Xoay ngược chiều kim đồng hồ
                    else:
                        ship_width = self.cell_size - 2
                        ship_height = len(ship_cells) * self.cell_size - 2
                        ship_img = pygame.transform.scale(self.ship_images[ship_name], (ship_width, ship_height))
                    
                    ship_img.set_alpha(200)
                    window.blit(ship_img, (x, y))
                    
                    # Draw fire on each cell of sunk ship
                    if self.fire_image:
                        for cell_row, cell_col in ship_cells:
                            fire_x = offset[0] + cell_col * self.cell_size + 1
                            fire_y = offset[1] + cell_row * self.cell_size + 1
                            window.blit(self.fire_image, (fire_x, fire_y))
                    
                    # Draw red X
                    end_row, end_col = ship_cells[-1]
                    x1 = offset[0] + start_col * self.cell_size + 2
                    y1 = offset[1] + start_row * self.cell_size + 2
                    x2 = offset[0] + end_col * self.cell_size + self.cell_size - 2
                    y2 = offset[1] + end_row * self.cell_size + self.cell_size - 2
                    
                    pygame.draw.line(window, (220, 38, 38), (x1, y1), (x2, y2), 4)
                    pygame.draw.line(window, (220, 38, 38), (x2, y1), (x1, y2), 4)
    
    def draw_coordinates(self, window, offset):
        """Vẽ nhãn tọa độ A-J và 1-10
        
        Args:
            window: Cửa sổ Pygame
            offset: Vị trí lưới
        
        Hiển thị:
        - Phía trên lưới: A B C D E F G H I J (cột)
        - Phía trái lười: 1 2 3 4 5 6 7 8 9 10 (hàng)
        - Màu vàng (255, 255, 100)
        - Căn giữa chính xác với mỗi ô
        """
        font_coord = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 14)
        
        # Căn giữa chính xác với ô (cell_size = 35, giữa ô = 17)
        for col in range(self.grid_size):
            label = chr(65 + col)
            text_surf = font_coord.render(label, True, (255, 255, 100))
            text_rect = text_surf.get_rect(center=(
                offset[0] + col * self.cell_size + 17, 
                offset[1] - 15
            ))
            window.blit(text_surf, text_rect)
        
        for row in range(self.grid_size):
            label = str(row + 1)
            text_surf = font_coord.render(label, True, (255, 255, 100))
            text_rect = text_surf.get_rect(center=(
                offset[0] - 18, 
                offset[1] + row * self.cell_size + 17
            ))
            window.blit(text_surf, text_rect)
    
    def draw_turn_indicator(self, window, state):
        """Vẽ chỉ báo lượt chơi - phía dưới lưới
        
        Args:
            window: Cửa sổ Pygame
            state: Trạng thái game
        
        Hiển thị:
        - Nếu my_turn = True: Panel xanh lá cây, "YOUR TURN - Click enemy grid!"
        - Nếu my_turn = False: Panel đỏ, "OPPONENT'S TURN - Please wait..."
        
        Vị trí: Giữa 2 lười, y=525, rộng 400px, cao 35px
        """
        turn_panel = pygame.Rect(200, 525, 400, 35)
        my_turn = state.get('my_turn', False)
        
        if my_turn:
            pygame.draw.rect(window, (209, 250, 229), turn_panel, border_radius=8)
            pygame.draw.rect(window, (34, 197, 94), turn_panel, 3, border_radius=8)
            turn_text = "🎯 YOUR TURN - Click enemy grid!"
            turn_color = (22, 101, 52)
        else:
            pygame.draw.rect(window, (254, 226, 226), turn_panel, border_radius=8)
            pygame.draw.rect(window, (239, 68, 68), turn_panel, 3, border_radius=8)
            turn_text = "⏳ OPPONENT'S TURN - Please wait..."
            turn_color = (153, 27, 27)
        
        font_turn = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 13)
        turn_surface = font_turn.render(turn_text, True, turn_color)
        text_rect = turn_surface.get_rect(center=turn_panel.center)
        window.blit(turn_surface, text_rect)
    
    def draw_timer(self, window, state):
        """Vẽ đồng hồ đếm ngược - phía dưới lưới, kích thước nhỏ hơn
        
        Args:
            window: Cửa sổ Pygame
            state: Trạng thái game (chứa time_remaining)
        
        Hiển thị:
        - Hình tròn bán kính 20 pixels
        - Màu xanh nếu thời gian > 10s
        - Màu đỏ nhấp nháy nếu thời gian <= 10s (cảnh báo)
        - Hiển thị số giây còn lại (ví dụ: "25s")
        
        Vị trí: Trung tâm màn hình (400, 580)
        """
        timer_x, timer_y = 400, 580
        timer_radius = 20
        time_remaining = state.get('time_remaining', 30)
        
        pygame.draw.circle(window, (0, 0, 0, 30), (timer_x + 2, timer_y + 2), timer_radius)
        
        if time_remaining <= 10:
            circle_color = (239, 68, 68)
            border_color = (185, 28, 28)
        else:
            circle_color = (59, 130, 246)
            border_color = (30, 64, 175)
        
        pygame.draw.circle(window, circle_color, (timer_x, timer_y), timer_radius)
        pygame.draw.circle(window, border_color, (timer_x, timer_y), timer_radius, 3)
        
        font_timer = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 12)
        timer_text = f"{time_remaining}s"
        timer_surface = font_timer.render(timer_text, True, (255, 255, 255))
        timer_rect = timer_surface.get_rect(center=(timer_x, timer_y))
        window.blit(timer_surface, timer_rect)
    
    def draw_crosshair(self, window, state):
        """Vẽ dấu ngắm khi hover chuột trên lưới địch
        
        Args:
            window: Cửa sổ Pygame
            state: Trạng thái game
        
        Điều kiện hiển thị:
        - Phải là lượt của tôi (my_turn = True)
        - Phải có hover_cell (chuột đang ở trên ô nào)
        - Ô đó chưa bị tấn công
        
        Hiểu ứng: Hiển thị hình crosshair đỏ giúp người chơi nhạc được chính xác
        """
        if not state.get('my_turn') or not self.crosshair_image:
            return
        
        hover_cell = state.get('hover_cell')
        if not hover_cell:
            return
        
        col, row = hover_cell
        enemy_hits = state.get('enemy_hits', [[False] * 10 for _ in range(10)])
        
        if not enemy_hits[row][col]:
            x = self.enemy_grid_offset[0] + col * self.cell_size
            y = self.enemy_grid_offset[1] + row * self.cell_size
            window.blit(self.crosshair_image, (x, y))
    
    def draw_turn_transition(self, window, state):
        """Vẽ hiệu ứng chuyển lượt (animation trượt từ phải sang trái)
        
        Args:
            window: Cửa sổ Pygame
            state: Chứa turn_transition_message và turn_transition_progress (0-1)
        
        Animation:
        - progress 0-0.5: Trượt vào từ phải
        - progress 0.5-1: Trượt ra sang trái
        
        Màu:
        - "YOUR TURN": Xanh lá cây
        - "OPPONENT'S TURN": Đỏ
        
        Hiệu ứng này chạy khoảng 1-2 giây khi chuyển lượt
        """
        transition_msg = state.get('turn_transition_message', '')
        transition_progress = state.get('turn_transition_progress', 0)  # 0-1
        
        # Sliding animation from side
        screen_width = 800
        panel_width = 400
        panel_height = 100
        
        # Slide in from right, then slide out to left
        if transition_progress < 0.5:
            # Slide in (0 to 0.5)
            progress = transition_progress * 2
            x_pos = screen_width - (panel_width * progress)
        else:
            # Slide out (0.5 to 1)
            progress = (transition_progress - 0.5) * 2
            x_pos = screen_width - panel_width - (screen_width * progress)
        
        # Position at top center, below title bar
        panel_rect = pygame.Rect(x_pos, 70, panel_width, panel_height)
        
        # Determine color based on message
        if "YOUR TURN" in transition_msg:
            bg_color = (34, 197, 94)  # Green
            text_color = (255, 255, 255)
            border_color = (22, 101, 52)
        else:
            bg_color = (239, 68, 68)  # Red
            text_color = (255, 255, 255)
            border_color = (153, 27, 27)
        
        # Draw panel
        pygame.draw.rect(window, bg_color, panel_rect, border_radius=15)
        pygame.draw.rect(window, border_color, panel_rect, 4, border_radius=15)
        
        # Draw text
        font = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 24)
        text_surf = font.render(transition_msg, True, text_color)
        text_rect = text_surf.get_rect(center=panel_rect.center)
        window.blit(text_surf, text_rect)
    
    def draw_timeout_warning(self, window, state):
        """Vẽ cảnh báo timeout nhấp nháy
        
        Args:
            window: Cửa sổ Pygame
            state: Chứa time_remaining
        
        Hiển thị khi time_remaining <= 10 giây
        
        Hiệu ứng:
        - Overlay đỏ nhạt nhấp nháy (alpha từ 50-150)
        - Chữ "⚠️ TIME RUNNING OUT: {time_remaining}s ⚠️" phía trên
        - Màu vàng nổi bật
        
        Mục đích: Cảnh báo người chơi tấn công nhanh tránh timeout
        """
        time_remaining = state.get('time_remaining', 30)
        
        # Only show when time is low
        if time_remaining > 10:
            return
        
        # Pulsing effect based on time
        pulse = abs((pygame.time.get_ticks() % 1000) / 1000 - 0.5) * 2  # 0 to 1 to 0
        alpha = int(50 + pulse * 100)  # 50 to 150
        
        # Red overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(alpha)
        overlay.fill((200, 0, 0))
        window.blit(overlay, (0, 0))
        
        # Warning text at top
        font = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 32)
        warning_text = f"⚠️ TIME RUNNING OUT: {time_remaining}s ⚠️"
        text_surf = font.render(warning_text, True, (255, 255, 100))
        text_rect = text_surf.get_rect(center=(400, 50))
        
        # Pulsing shadow
        shadow_surf = font.render(warning_text, True, (100, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(402, 52))
        window.blit(shadow_surf, shadow_rect)
        window.blit(text_surf, text_rect)
    
    def draw_ship_sunk_notification(self, window, state):
        """Vẽ thông báo tàu chìm - overlay bán trong suốt
        
        Args:
            window: Cửa sổ Pygame
            state: Chứa ship_sunk_message (ví dụ: "YOUR BATTLESHIP SUNK!")
        
        Hiệu ứng:
        - Overlay tối nhẹ (alpha=80) - vẫn thấy được game
        - Hộp thông báo ở giữa màn hình
        - Nền đỏ, viền hồng nhạt
        - Hiển thị 2 giây rồi tự động biến mất
        
        Ví dụ: "YOUR BATTLESHIP SUNK!" hoặc "ENEMY CRUISER SUNK!"
        """
        # Light semi-transparent overlay - can still see game
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(80)  # Very light, can see through
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))
        
        # Compact notification box at center
        msg_width, msg_height = 400, 100
        msg_rect = pygame.Rect(200, 250, msg_width, msg_height)
        
        # Semi-transparent background
        msg_bg = pygame.Surface((msg_width, msg_height))
        msg_bg.set_alpha(200)
        msg_bg.fill((200, 50, 50))
        window.blit(msg_bg, msg_rect.topleft)
        
        # Border
        pygame.draw.rect(window, (255, 100, 100), msg_rect, 3, border_radius=10)
        
        font_big = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 28)
        
        ship_sunk_message = state.get('ship_sunk_message', '')
        
        text = font_big.render(ship_sunk_message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 300))
        window.blit(text, text_rect)
        
        pygame.display.update()
    
    def draw_game_over(self, window, state):
        """Vẽ thông báo kết thúc game - overlay bán trong suốt
        
        Args:
            window: Cửa sổ Pygame
            state: Chứa game_over_message ("YOU WON!" hoặc "YOU LOST!")
        
        Hiệu ứng:
        - Overlay tối nhẹ (alpha=100)
        - Hộp lớn ở giữa màn hình
        - Nếu thắng: Nền xanh lá, viền xanh sáng
        - Nếu thua: Nền đỏ tối, viền đỏ sáng
        - Dòng 1: "YOU WON!" / "YOU LOST!" (chữ lớn)
        - Dòng 2: "Loading statistics..." (chữ nhỏ)
        
        Hiển thị 2 giây trước khi chuyển sang màn hình thống kê
        """
        # Light semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(100)  # Light overlay
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))
        
        # Notification box at center
        msg_width, msg_height = 500, 140
        msg_rect = pygame.Rect(150, 230, msg_width, msg_height)
        
        game_over_message = state.get('game_over_message', '')
        won = 'WON' in game_over_message
        
        # Semi-transparent background with color based on result
        msg_bg = pygame.Surface((msg_width, msg_height))
        msg_bg.set_alpha(220)
        if won:
            msg_bg.fill((30, 120, 80))
            border_color = (100, 255, 150)
        else:
            msg_bg.fill((120, 30, 30))
            border_color = (255, 100, 100)
        window.blit(msg_bg, msg_rect.topleft)
        
        # Border
        pygame.draw.rect(window, border_color, msg_rect, 4, border_radius=12)
        
        font_big = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 36)
        font_small = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 18)
        
        color = (0, 150, 0) if won else (255, 0, 0)
        
        # Main message
        text1 = font_big.render(game_over_message, True, (255, 255, 255))
        text1_rect = text1.get_rect(center=(400, 280))
        window.blit(text1, text1_rect)
        
        # Sub message
        text2 = font_small.render('Loading statistics...', True, (220, 220, 220))
        text2_rect = text2.get_rect(center=(400, 330))
        window.blit(text2, text2_rect)
        
        pygame.display.update()
    
    def get_clicked_cell(self, mouse_pos, grid_offset):
        """Chuyển vị trí chuột thành tọa độ ô lười
        
        Args:
            mouse_pos: (x, y) vị trí chuột trên màn hình
            grid_offset: (gx, gy) vị trí góc trên-trái của lười
        
        Returns:
            tuple: (col, row) từ 0-9, hoặc None nếu click ngoài lười
        
        Ví dụ:
        - Click ô A1 (góc trên-trái): trả về (0, 0)
        - Click ô J10 (góc dưới-phải): trả về (9, 9)
        - Click bên ngoài lười: trả về None
        """
        x, y = mouse_pos
        gx, gy = grid_offset
        
        if x < gx or y < gy:
            return None
        
        col = (x - gx) // self.cell_size
        row = (y - gy) // self.cell_size
        
        if 0 <= col < self.grid_size and 0 <= row < self.grid_size:
            return (col, row)
        
        return None
