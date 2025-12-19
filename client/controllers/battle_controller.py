"""
Battle Controller - Game logic for battle stage (MVC Pattern)
"""
import pygame
import tkinter as tk
from tkinter import messagebox
import threading
from networking.room_client import RoomClient
from views.battle_view import BattleView
from views.opponent_info_view import show_opponent_info


class BattleController:
    """Quản lý logic game chiến đấu (MVC Pattern)
    
    Chức năng chính:
    - Quản lý trạng thái 2 lưới (tàu của mình + tấn công địch)
    - Xử lý lượt chơi luân phiên (my_turn)
    - Đồng hồ đếm ngược 30s mỗi lượt (timeout sau 3 lần = thua)
    - Xử lý tấn công và nhận kết quả từ server
    - Kiểm tra tàu chìm (5 tàu): battleship, cruiser, destroyer1, destroyer2, plane
    - Hiệu ứng chuyển lượt, thông báo tàu chìm, game over
    - Thống kê: hits/misses, accuracy, streak dài nhất
    - Xử lý quit (hiển dialog xác nhận, thông báo server, đối thủ thắng)
    
    Luồng hoạt động:
    1. Load client + lưới tàu từ AutoShipLocation
    2. Vòng lặp game:
       - process_events() → handle_event() → update()
       - Nếu my_turn: click chuột → attack_cell() → gửi server
       - Server trả về hit/miss → update lưới
       - Sync game_data từ server mỗi frame
       - Kiểm tra winner → hiển game_over_message 2s → kết thúc
    3. Return states để chuyển sang BattleStatsView
    
    Thống kê tracking:
    - my_hits_count, my_misses_count: Số lần bắn
    - my_current_streak, my_max_streak: Chuỗi trúng liên tiếp
    - enemy_hits/misses/streak: Thống kê đối thủ
    - ships_sunk, enemy_ships_sunk: Tàu bị chìm
    
    Thread-safety: Đồng bộ qua server socket, không cần lock local
    """
    
    def __init__(self):
        """Khởi tạo controller và view
        
        Thiết lập:
        - view: BattleView để hiển thị giao diện
        - states: Dict chứa trạng thái game (game_finished, winner_name)
        - client: RoomClient (sẽ load sau)
        - my_grid, enemy_grid: Lưới 10x10
        - my_hits, enemy_hits: Ô bị bắn
        - my_turn: Lượt chơi
        - turn_start_time: Thời điểm bắt đầu lượt (milliseconds)
        - time_remaining: Thời gian còn lại (giây)
        - timeout_count: Số lần hết giờ (3 lần = thua)
        - ships_sunk, enemy_ships_sunk: Số tàu chìm
        - sunk_ships: Set tên tàu đã chìm (tránh xử lý trùng)
        - Thống kê: hits, misses, streak
        - Hiệu ứng: ship_sunk_message, turn_transition_message, game_over_message
        """
        # Khởi tạo view để hiển thị giao diện
        self.view = BattleView()
        
        # Trạng thái điều hướng (dùng để chuyển màn hình)
        self.states = {
            'game_finished': False,  # Game đã kết thúc chưa
            'winner_name': None,     # Tên người thắng
            'quit_requested': False  # Người chơi muốn thoát
        }
        
        self.client: RoomClient = None  # Kết nối mạng
        
        # Trạng thái bàn cờ
        self.my_grid = []  # Lưới tàu của tôi (10x10)
        self.enemy_grid = [[None for _ in range(10)] for _ in range(10)]  # Lưới đối thủ
        self.my_hits = [[False for _ in range(10)] for _ in range(10)]  # Ô tôi bị bắn
        self.enemy_hits = [[False for _ in range(10)] for _ in range(10)]  # Ô đối thủ bị bắn
        
        # Quản lý lượt chơi
        self.my_turn = False  # Có phải lượt tôi không
        self.turn_start_time = 0  # Thời điểm bắt đầu lượt (milliseconds)
        self.time_remaining = 30  # Thời gian còn lại (giây)
        self.my_timeout_count = 0  # Số lần tôi hết giờ
        self.enemy_timeout_count = 0  # Số lần đối thủ hết giờ
        
        # Đếm tàu bị chìm
        self.ships_sunk = 0  # Tàu tôi bị chìm (không dùng)
        self.enemy_ships_sunk = 0  # Tàu đối thủ bị chìm
        self.total_ships = 5  # Tổng số tàu
        
        # Danh sách tàu đã chìm hoàn toàn
        self.my_sunk_ships = set()  # Tên tàu của tôi đã chìm (battleship, cruiser, ...)
        self.enemy_sunk_ships = set()  # Tên tàu đối thủ đã chìm
        
        # Thông tin người chơi
        self.my_username = ""  # Tên đăng nhập của tôi
        self.my_user_id = None  # ID người dùng
        self.enemy_username = ""  # Tên đối thủ
        self.enemy_user_id = None  # ID đối thủ
        
        # Trạng thái giao diện
        self.hover_cell = None  # Ô đang rê chuột (col, row)
        # Removed show_quit_confirm - Using Tkinter messagebox instead
        self.game_over_message = None  # Thông báo kết thúc game ("YOU WON!" / "YOU LOST!")
        self.game_over_timer = 0  # Thời điểm hiện thông báo game over
        
        # Thông báo tàu chìm
        self.ship_sunk_message = None  # Tin nhắn tàu chìm ("BATTLESHIP SUNK!")
        self.ship_sunk_timer = 0  # Thời điểm hiện thông báo
        
        # Hiệu ứng chuyển lượt
        self.turn_transition_message = None  # Thông báo chuyển lượt ("YOUR TURN!" / "OPPONENT'S TURN")
        self.turn_transition_timer = 0  # Thời điểm bắt đầu animation
        self.turn_transition_duration = 2000  # Thời gian hiệu ứng (2 giây)
        
        # Cảnh báo timeout
        self.show_timeout_warning = False  # Hiện cảnh báo đỏ khi <= 10s
        
        # Vị trí tàu trên lưới
        self.my_ship_positions = {}  # Dict {tên_tàu: [{cells, horizontal}, ...]}
        
        # Enemy panel hover state
        self.enemy_panel_hover = False  # True khi hover vào enemy panel
        
        # Flag ngăn gọi ship_sinked nhiều lần
        self.game_ended = False
        
        # Thống kê trận đấu
        self.my_hits_count = 0  # Số lần tôi bắn trúng
        self.my_misses_count = 0  # Số lần tôi bắn trượt
        self.my_current_streak = 0  # Chuỗi bắn trúng hiện tại của tôi
        self.my_max_streak = 0  # Chuỗi bắn trúng dài nhất của tôi
        
        self.enemy_hits_count = 0  # Số lần đối thủ bắn trúng tôi
        self.enemy_misses_count = 0  # Số lần đối thủ bắn trượt
        self.enemy_current_streak = 0  # Chuỗi bắn trúng hiện tại của đối thủ
        self.enemy_max_streak = 0  # Chuỗi bắn trúng dài nhất của đối thủ
    
    def load_client(self, client: RoomClient):
        """Tải thông tin kết nối mạng
        
        Args:
            client: RoomClient instance đã kết nối với server
        
        Lưu thông tin:
        - client: Để gửi/nhận dữ liệu qua socket
        - my_username: Tên đăng nhập
        - my_user_id: ID người dùng (cho database)
        """
        self.client = client
        self.my_username = client.username
        self.my_user_id = client.user_id
    
    def load_my_grid(self, grid):
        """Tải lưới tàu của người chơi (10x10)
        
        Args:
            grid: List 10x10, mỗi ô là:
                - None: Nước
                - 'battleship', 'cruiser', 'destroyer1', 'destroyer2', 'plane': Tên tàu
        
        Xử lý:
        - Lưu grid vào self.my_grid
        - Gọi _find_ship_positions() để tìm vị trí tất cả tàu
        - Lưu kết quả vào self.my_ship_positions (dùng để kiểm tra tàu chìm)
        """
        self.my_grid = grid
        self.my_ship_positions = self._find_ship_positions(grid)  # Tìm vị trí tất cả tàu
    
    def _find_ship_positions(self, grid):
        """Tìm vị trí và hướng của tất cả tàu trên lưới
        
        Args:
            grid: Lưới 10x10
        
        Returns:
            Dict {
                'tên_tàu': [
                    {
                        'cells': [(row, col), ...],  # Danh sách ô của tàu
                        'horizontal': True/False     # Tàu ngang hay dọc
                    }
                ]
            }
        
        Thuật toán:
        1. Duyệt qua từng ô trên lưới
        2. Nếu gặp tàu chưa duyệt:
           - Thêm vào danh sách cells
           - Kiểm tra hướng ngang (sang phải)
           - Nếu không ngang thì kiểm tra dọc (xuống dưới)
        3. Đánh dấu ô đã duyệt (visited)
        
        Ví dụ:
        Grid có battleship ngang từ (0,0) đến (0,4):
        → {'battleship': [{'cells': [(0,0), (0,1), (0,2), (0,3), (0,4)], 'horizontal': True}]}
        """
        ships = {}  # Kết quả: {tên_tàu: [{cells: [...], horizontal: True/False}]}
        visited = set()  # Các ô đã duyệt qua
        
        # Duyệt qua từng ô trên lưới
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                # Nếu có tàu và chưa duyệt
                if grid[row][col] and (row, col) not in visited:
                    ship_name = grid[row][col]  # Lấy tên tàu
                    cells = [(row, col)]  # Danh sách ô của tàu
                    visited.add((row, col))
                    
                    # Kiểm tra tàu ngang (horizontal)
                    horizontal = False
                    c = col + 1
                    while c < len(grid[row]) and grid[row][c] == ship_name:
                        cells.append((row, c))
                        visited.add((row, c))
                        horizontal = True
                        c += 1
                    
                    # Kiểm tra tàu dọc (vertical) nếu không phải ngang
                    if not horizontal:
                        r = row + 1
                        while r < len(grid) and grid[r][col] == ship_name:
                            cells.append((r, col))
                            visited.add((r, col))
                            r += 1
                    
                    if ship_name not in ships:
                        ships[ship_name] = []
                    ships[ship_name].append({
                        'cells': cells,
                        'horizontal': horizontal
                    })
        
        return ships
    
    def _check_my_sunk_ships(self):
        """Kiểm tra xem có tàu nào của tôi bị chìm hoàn toàn không
        
        Logic:
        1. Duyệt qua tất cả tàu trong my_ship_positions
        2. Bỏ qua tàu đã đánh dấu chìm (trong my_sunk_ships)
        3. Kiểm tra TẤT CẢ ô của tàu đã bị bắn chưa (my_hits)
        4. Nếu tất cả ô đều bị bắn:
           - Thêm vào my_sunk_ships
           - Tăng ships_sunk
           - Hiển thông báo ship_sunk_message
        
        Được gọi sau mỗi lần đối thủ tấn công
        """
        for ship_name, ship_list in self.my_ship_positions.items():
            if ship_name in self.my_sunk_ships:
                continue  # Tàu đã đánh dấu chìm rồi, bỏ qua
            
            for ship_data in ship_list:
                cells = ship_data['cells']  # Danh sách ô của tàu
                # Kiểm tra TẤT CẢ ô có bị đánh không
                all_hit = all(self.my_hits[r][c] for r, c in cells)
                
                if all_hit:
                    # Tàu chìm hoàn toàn
                    self.my_sunk_ships.add(ship_name)  # Thêm vào danh sách tàu chìm
                    self.ships_sunk += 1  # Cập nhật số tàu bị chìm
                    print(f"[CONTROLLER] My ship sunk locally: {ship_name} ({self.ships_sunk}/5)")
                    self.ship_sunk_message = f"YOUR {ship_name.upper()} SUNK!"  # Hiện thông báo
                    self.ship_sunk_timer = pygame.time.get_ticks()  # Bắt đầu đếm thời gian hiện thông báo
                    break  # Chuyển sang tàu tiếp theo
    
    def update(self):
        """Cập nhật trạng thái game mỗi frame
        
        Công việc:
        1. Xóa thông báo tạm thời (ship_sunk, turn_transition) sau thời gian quy định
        2. Cập nhật timeout_warning (hiển đỏ khi <= 10s)
        3. Đồng hồ đếm ngược:
           - Tính time_remaining = 30 - elapsed
           - Nếu hết giờ (0s) và là lượt tôi:
             * Gửi 'timeout' lên server
             * Tăng my_timeout_count
             * Nếu >= 3 lần → thua game
             * Chuyển lượt đối thủ
        4. Sync với server:
           - CHECK WINNER FIRST (quan trọng nhất)
           - Lấy game_data (turn, timeout_count, enemy_username)
           - Kiểm tra đối thủ disconnect
           - Cập nhật my_turn, reset timer khi chuyển lượt
           - Kiểm tra enemy_attacks → đánh dấu my_hits
           - Cập nhật enemy statistics
           - Kiểm tra tàu của tôi chìm
           - Xử lý ship_sunk notification từ server
        
        Returns:
            True: Game kết thúc (có winner hoặc timeout 3 lần)
            False: Game tiếp tục
        """
        # Xóa thông báo tàu chìm sau 1.5 giây
        if self.ship_sunk_message and self.ship_sunk_timer > 0:
            elapsed = pygame.time.get_ticks() - self.ship_sunk_timer
            if elapsed >= 1500:  # 1.5 giây
                self.ship_sunk_message = None
                self.ship_sunk_timer = 0
        
        # Xóa thông báo chuyển lượt sau khi animation xong
        if self.turn_transition_message and self.turn_transition_timer > 0:
            elapsed = pygame.time.get_ticks() - self.turn_transition_timer
            if elapsed >= self.turn_transition_duration:  # 2 giây
                self.turn_transition_message = None
                self.turn_transition_timer = 0
        
        # Cập nhật cảnh báo timeout (hiện đỏ khi <= 10s)
        self.show_timeout_warning = (self.my_turn and self.time_remaining <= 10)
        
        # Cập nhật đồng hồ đếm ngược (cả 2 người chơi đều đếm)
        if self.turn_start_time > 0:
            elapsed = pygame.time.get_ticks() - self.turn_start_time  # Thời gian đã trôi qua
            self.time_remaining = max(0, 30 - elapsed // 1000)  # Còn lại bao nhiêu giây
            
            # Hết giờ (chỉ xử lý khi là lượt tôi)
            if self.time_remaining == 0 and self.my_turn:
                print("[CONTROLLER] Hết giờ! Kết thúc lượt")
                if self.client:
                    try:
                        self.client.send_data_to_server({'request': 'timeout'})  # Gửi timeout lên server
                    except:
                        pass
                
                # Tăng số lần timeout ngay lập tức
                self.my_timeout_count += 1
                print(f"[CONTROLLER] Số lần timeout: {self.my_timeout_count}/3")
                
                # Kiểm tra timeout lần thứ 3 - thua game
                if self.my_timeout_count >= 3:
                    print("[CONTROLLER] Timeout 3 lần! Bạn thua.")
                    if not self.game_over_message:
                        self.game_over_message = "YOU LOST!"
                        self.game_over_timer = pygame.time.get_ticks()
                        self.game_ended = True  # Đánh dấu đã kết thúc
                    
                    # KHÔNG GỌI ship_sinked() - Server đã xử lý game_over rồi
                    return True  # Game kết thúc
                
                # Chuyển sang lượt đối thủ
                self.my_turn = False
                self.turn_start_time = 0
                # Hiện thông báo chuyển lượt
                self.turn_transition_message = "⏳ OPPONENT'S TURN"
                self.turn_transition_timer = pygame.time.get_ticks()
        
        # Sync with server
        if self.client:
            try:
                # CHECK WINNER FIRST - This is the most important check
                # Must check before anything else to catch opponent quit immediately
                winner = self.client.get_winner()
                if winner:
                    if not self.game_over_message:
                        if winner == self.client.username:
                            self.game_over_message = "YOU WON!"
                            print(f"[CONTROLLER] ========================================")
                            print(f"[CONTROLLER] YOU WON! Winner from server: {winner}")
                            print(f"[CONTROLLER] ========================================")
                        else:
                            self.game_over_message = "YOU LOST!"
                            print(f"[CONTROLLER] ========================================")
                            print(f"[CONTROLLER] YOU LOST! Winner from server: {winner}")
                            print(f"[CONTROLLER] ========================================")
                        self.game_over_timer = pygame.time.get_ticks()
                    return True  # Game finished
                
                game_data = self.client.get_game_data()
                
                # Check opponent disconnect
                if game_data is None or len(game_data) < 2:
                    if not self.game_over_message:
                        self.game_over_message = "YOU WON!"
                        print("[CONTROLLER] Opponent disconnected - You win!")
                    return True  # Game finished
                
                if game_data:
                    username = self.client.username
                    if username in game_data:
                        new_turn = game_data[username]['my_turn']
                        
                        # Update timeout counts
                        self.my_timeout_count = game_data[username].get('timeout_count', 0)
                        
                        # Khởi tạo timer nếu chưa có (lần đầu vào game)
                        if self.turn_start_time == 0:
                            self.turn_start_time = pygame.time.get_ticks()
                            self.time_remaining = 30
                            print("[CONTROLLER] Khởi tạo timer lần đầu")
                        
                        # Update turn
                        if new_turn != self.my_turn:
                            self.my_turn = new_turn
                            # Reset timer khi chuyển lượt
                            self.turn_start_time = pygame.time.get_ticks()
                            self.time_remaining = 30
                            if self.my_turn:
                                # Show turn transition
                                self.turn_transition_message = "➡️ YOUR TURN!"
                                self.turn_transition_timer = pygame.time.get_ticks()
                            else:
                                # Show opponent turn transition
                                self.turn_transition_message = "⏳ OPPONENT'S TURN"
                                self.turn_transition_timer = pygame.time.get_ticks()
                        
                        # Get enemy info
                        for player_name in game_data.keys():
                            if player_name != username:
                                self.enemy_username = player_name
                                self.enemy_timeout_count = game_data[player_name].get('timeout_count', 0)
                                break
                        
                        # Check if anyone has 3 timeouts (game over condition)
                        if self.my_timeout_count >= 3:
                            if not self.game_over_message:
                                print("[CONTROLLER] 3 timeouts! You lose.")
                                self.game_over_message = "YOU LOST!"
                                self.game_over_timer = pygame.time.get_ticks()
                                self.game_ended = True  # Đánh dấu kết thúc
                            
                            # KHÔNG GỌI ship_sinked() - Server đã xử lý game_over rồi
                            return True  # Game finished
                        
                        if self.enemy_timeout_count >= 3:
                            if not self.game_over_message:
                                print("[CONTROLLER] Opponent has 3 timeouts! You win.")
                                self.game_over_message = "YOU WON!"
                                self.game_over_timer = pygame.time.get_ticks()
                                self.game_ended = True  # Đánh dấu kết thúc
                            
                            # KHÔNG GỌI ship_sinked() - Server đã xử lý game_over rồi
                            return True  # Game finished
                        
                        # Check enemy attacks
                        enemy_data = [v for k, v in game_data.items() if k != username]
                        if enemy_data and enemy_data[0]['attacked_tile']['position']:
                            pos = enemy_data[0]['attacked_tile']['position']
                            col, row = pos
                            
                            # Check if this is a new attack (not already marked)
                            if not self.my_hits[row][col]:
                                self.my_hits[row][col] = True
                                
                                # IMPORTANT: Enemy just attacked, reset timer
                                # This happens when it's opponent's turn and they make an attack
                                if not self.my_turn:
                                    self.turn_start_time = pygame.time.get_ticks()
                                    self.time_remaining = 30
                                    print("[CONTROLLER] Enemy attacked - timer reset to 30s")
                                
                                # Track enemy statistics
                                is_hit = self.my_grid[row][col] is not None
                                
                                if is_hit:
                                    self.enemy_hits_count += 1
                                    self.enemy_current_streak += 1
                                    if self.enemy_current_streak > self.enemy_max_streak:
                                        self.enemy_max_streak = self.enemy_current_streak
                                else:
                                    self.enemy_misses_count += 1
                                    self.enemy_current_streak = 0
                                
                                # Check if any of my ships got sunk
                                self._check_my_sunk_ships()
                
                # Check for ship sunk notifications from opponent
                if 'ship_sunk' in game_data.get(username, {}):
                    sunk_ship = game_data[username].get('ship_sunk')
                    print(f"[CONTROLLER] Received ship_sunk notification: {sunk_ship}")
                    print(f"[CONTROLLER] Already sunk: {self.my_sunk_ships}")
                    if sunk_ship and sunk_ship not in self.my_sunk_ships:
                        # Show notification that our ship was sunk
                        self.ship_sunk_message = f"YOUR {sunk_ship.upper()} SUNK!"
                        self.ship_sunk_timer = pygame.time.get_ticks()
                        self.my_sunk_ships.add(sunk_ship)
                        self.ships_sunk += 1  # Cập nhật số tàu bị chìm
                        print(f"[CONTROLLER] My ship sunk: {sunk_ship} ({self.ships_sunk}/5)")
                        
                        # Clear notification on server to prevent re-processing
                        try:
                            self.client.send_data_to_server({'request': 'clear_ship_sunk'})
                            print(f"[CONTROLLER] Sent clear_ship_sunk request")
                        except Exception as e:
                            print(f"[CONTROLLER] Failed to clear ship_sunk: {e}")
                    
            except Exception as e:
                print(f"[CONTROLLER] Error: {e}")
        
        return False  # Game continues
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            # Show Tkinter quit dialog immediately
            return self.show_quit_dialog_tkinter()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on enemy panel (tên đối thủ)
            if self.is_enemy_panel_clicked(event.pos):
                self.show_opponent_info_popup()
            elif self.my_turn:
                return self.handle_attack(event.pos)
        
        if event.type == pygame.MOUSEMOTION:
            # Kiểm tra hover trên enemy panel
            if self.is_enemy_panel_clicked(event.pos):
                self.enemy_panel_hover = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Con trỏ tay
            else:
                self.enemy_panel_hover = False
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Con trỏ bình thường
            
            # Cập nhật hover cell cho attack
            if self.my_turn:
                self.update_hover(event.pos)
            else:
                self.hover_cell = None
        
        return None
    
    def show_quit_dialog_tkinter(self):
        """Hiển thị Tkinter messagebox xác nhận thoát
        
        Returns:
            None: Người dùng chọn No (tiếp tục chơi)
            'quit_confirmed': Người dùng chọn Yes (thoát và thua)
        
        Sử dụng tkinter.messagebox.askyesno() thay vì vẽ Pygame dialog
        - Gọn hơn 50+ dòng code
        - Dialog đẹp hơn, tự động center
        - Không cần xử lý mouse click
        """
        # Create hidden root for messagebox
        root = tk.Tk()
        root.withdraw()
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Quit Game?",
            "You will lose this match!\n\nAre you sure you want to quit?",
            icon='warning'
        )
        
        root.destroy()
        
        if result:  # User clicked Yes
            print("[CONTROLLER] Player quit - saving loss to database")
            if self.client:
                try:
                    # Save game result as loss
                    opponent_username = self.enemy_username or 'Unknown'
                    
                    save_request = {
                        'request': 'save_game_history',
                        'opponent_username': opponent_username,
                        'result': 'lose',
                        'ships_sunk': self.enemy_ships_sunk,
                        'hits': self.total_hits,
                        'misses': self.total_misses,
                        'accuracy': (self.total_hits / (self.total_hits + self.total_misses) * 100) if (self.total_hits + self.total_misses) > 0 else 0,
                        'max_streak': self.max_streak
                    }
                    
                    try:
                        self.client.send_data_to_server(save_request)
                        print(f"[CONTROLLER] ✓ Game history save request sent!")
                    except Exception as e:
                        print(f"[CONTROLLER] Error sending save request: {e}")
                    
                    # Notify server that player quit
                    try:
                        quit_notification = {'request': 'player_quit'}
                        response = self.client.send_data_to_server(quit_notification)
                        if response and response.get('message') == 'quit_acknowledged':
                            print(f"[CONTROLLER] ✓ Server acknowledged quit!")
                    except Exception as e:
                        print(f"[CONTROLLER] Error sending quit notification: {e}")
                    
                    self.client.disconnect()
                    self.client = None
                except Exception as e:
                    print(f"[CONTROLLER] Error during quit: {e}")
            
            # Set game over
            self.game_over_message = "YOU LOST!"
            self.game_over_timer = pygame.time.get_ticks()
            return None
        
        # User clicked No - continue playing
        return None
    
    def is_enemy_panel_clicked(self, mouse_pos):
        """Kiểm tra xem có click vào enemy panel không
        
        Args:
            mouse_pos: (x, y) vị trí chuột
        
        Returns:
            True nếu click vào enemy panel, False nếu không
        
        Enemy panel: Rect(420, 70, 360, 65)
        - Vị trí: x=420-780, y=70-135
        - Hiển thị tên đối thủ và timeout boxes
        """
        enemy_panel_rect = pygame.Rect(420, 70, 360, 65)
        return enemy_panel_rect.collidepoint(mouse_pos)
    
    def show_opponent_info_popup(self):
        """Hiển thị popup thông tin đối thủ
        
        Tạo popup trong thread riêng với protocol đóng cửa sổ
        """
        if not self.client or not self.enemy_username:
            print("[CONTROLLER] Cannot show opponent info: no client or enemy username")
            return
        
        def run_popup():
            try:
                # Lấy thông tin đối thủ từ server
                print(f"[CONTROLLER] Fetching stats for {self.enemy_username}...")
                opponent_stats = self.client.get_opponent_stats(self.enemy_username)
                print(f"[CONTROLLER] Got stats: {opponent_stats}")
                
                # Tạo Tkinter root mới - KHÔNG withdraw để popup hiển thị được
                root = tk.Tk()
                root.attributes('-alpha', 0.0)  # Làm root trong suốt hoàn toàn
                root.geometry('1x1+0+0')  # Root nhỏ nhất có thể
                
                # Tạo popup
                print(f"[CONTROLLER] Creating popup window...")
                popup = show_opponent_info(root, self.enemy_username, opponent_stats)
                
                # Đặt protocol đóng window
                def on_close():
                    print("[CONTROLLER] Closing popup...")
                    popup.destroy()
                    root.quit()
                
                popup.protocol("WM_DELETE_WINDOW", on_close)
                
                print(f"[CONTROLLER] Popup created! Waiting for window...")
                
                # Dùng wait_window thay vì mainloop - đợi popup đóng
                root.wait_window(popup)
                
                print(f"[CONTROLLER] Popup closed, destroying root...")
                root.destroy()
            except Exception as e:
                print(f"[CONTROLLER] Error in popup thread: {e}")
                import traceback
                traceback.print_exc()
        
        # Chạy trong thread daemon=False để giữ popup
        import threading
        popup_thread = threading.Thread(target=run_popup, daemon=False)
        popup_thread.start()
        print("[CONTROLLER] Popup thread started")
    
    def handle_attack(self, mouse_pos):
        """Handle attack on enemy grid"""
        cell = self.get_clicked_cell(mouse_pos, (430, 170))
        
        if cell and not self.enemy_hits[cell[1]][cell[0]]:
            self.attack_cell(cell)
        
        return None
    
    def update_hover(self, mouse_pos):
        """Update hovered cell"""
        cell = self.get_clicked_cell(mouse_pos, (430, 170))
        if cell and not self.enemy_hits[cell[1]][cell[0]]:
            self.hover_cell = cell
        else:
            self.hover_cell = None
    
    def get_clicked_cell(self, mouse_pos, grid_offset):
        """Convert mouse position to grid cell"""
        x, y = mouse_pos
        gx, gy = grid_offset
        
        if x < gx or y < gy:
            return None
        
        col = (x - gx) // 35
        row = (y - gy) // 35
        
        if 0 <= col < 10 and 0 <= row < 10:
            return (col, row)
        
        return None
    
    def attack_cell(self, cell):
        """Tấn công ô địch
        
        Args:
            cell: (col, row) - Tọa độ ô muốn bắn
        
        Luồng:
        1. Gửi request 'attack_tile' + position đến server
        2. Server kiểm tra lưới đối thủ
        3. Nhận response:
           - ship_name khác rỗng → TRÚNG:
             * Lưu tên tàu vào enemy_grid[row][col]
             * Gọi check_ship_sunk() kiểm tra chìm
             * Tăng my_hits_count, my_current_streak
             * Cập nhật my_max_streak
             * Reset timer (tiếp tục lượt)
           - ship_name rỗng → TRƯỢT:
             * Lưu None vào enemy_grid[row][col]
             * Tăng my_misses_count
             * Reset streak = 0
             * Chuyển lượt (server tự động xử lý)
        4. Đánh dấu enemy_hits[row][col] = True
        """
        col, row = cell
        
        if self.client:
            try:
                ship_name = self.client.attack_enemy_tile((col, row))
                
                print(f"[CONTROLLER] Attacked ({col}, {row}) -> '{ship_name}'")
                
                self.enemy_hits[row][col] = True
                
                is_hit = ship_name is not None and ship_name != '' and ship_name.strip() != ''
                
                if is_hit:
                    print(f"[CONTROLLER] HIT! Ship: '{ship_name}'")
                    self.enemy_grid[row][col] = ship_name
                    self.check_ship_sunk(ship_name)
                    
                    # Update hit statistics
                    self.my_hits_count += 1
                    self.my_current_streak += 1
                    if self.my_current_streak > self.my_max_streak:
                        self.my_max_streak = self.my_current_streak
                    
                    # Reset timer for next shot
                    self.turn_start_time = pygame.time.get_ticks()
                    self.time_remaining = 30
                else:
                    print(f"[CONTROLLER] MISS!")
                    self.enemy_grid[row][col] = None
                    
                    # Update miss statistics
                    self.my_misses_count += 1
                    self.my_current_streak = 0
                
            except Exception as e:
                print(f"[CONTROLLER] Attack error: {e}")
    
    def check_ship_sunk(self, ship_name):
        """Kiểm tra tàu địch có chìm hoàn toàn không
        
        Args:
            ship_name: Tên tàu vừa bắn trúng ('battleship', 'cruiser', ...)
        
        Logic:
        1. Lấy kích thước tàu từ ship_sizes dict
        2. Đếm số ô của tàu này đã bị bắn (enemy_hits = True)
        3. Nếu hits >= kích thước tàu:
           - Thêm vào enemy_sunk_ships
           - Tăng enemy_ships_sunk
           - Hiển thông báo ship_sunk_message
           - Gửi 'ship_sunk_notification' lên server
           - Gọi ship_sinked() đến server
        4. Nếu chìm hết 5 tàu → thắng game
        
        Ship sizes:
        - battleship: 5 ô
        - cruiser: 4 ô
        - destroyer1, destroyer2: 3 ô
        - plane: 2 ô
        """
        ship_sizes = {
            'battleship': 5, 
            'cruiser': 4, 
            'destroyer1': 3, 
            'destroyer2': 3, 
            'plane': 2
        }
        
        if ship_name in ship_sizes and ship_name not in self.enemy_sunk_ships:
            hits = 0
            for row in range(10):
                for col in range(10):
                    if self.enemy_grid[row][col] == ship_name and self.enemy_hits[row][col]:
                        hits += 1
            
            print(f"[CONTROLLER] {ship_name}: {hits}/{ship_sizes[ship_name]} hits")
            
            if hits >= ship_sizes[ship_name]:
                print(f"[CONTROLLER] {ship_name} SUNK!")
                self.enemy_sunk_ships.add(ship_name)
                self.enemy_ships_sunk += 1
                
                # Show ship sunk notification
                self.ship_sunk_message = f"{ship_name.upper()} SUNK!"
                self.ship_sunk_timer = pygame.time.get_ticks()
                
                if self.client:
                    # Notify server about ship sunk (will sync to both players)
                    try:
                        self.client.send_data_to_server({
                            'request': 'ship_sunk_notification',
                            'ship_name': ship_name
                        })
                    except:
                        pass
                    self.client.ship_sinked()
                
                if self.enemy_ships_sunk >= self.total_ships:
                    print("[CONTROLLER] ALL ENEMY SHIPS SUNK! YOU WIN!")
    
    def draw(self, window: pygame.display):
        """Draw battle screen using view"""
        state = self.get_state()
        self.view.draw(window, state)
    
    def process_events(self):
        """Handle events and update game logic - main game loop"""
        # Handle events first (before game over check)
        for event in pygame.event.get():
            result = self.handle_event(event)
            
            if result == 'force_quit':
                # Force quit - same as normal quit but without confirmation
                print("[CONTROLLER] Force quit - saving loss and disconnecting")
                if self.client:
                    try:
                        # Save game result as loss
                        opponent_username = self.states.get('enemy_username', 'Unknown')
                        
                        save_request = {
                            'request': 'save_game_history',
                            'opponent_username': opponent_username,
                            'result': 'lose',
                            'ships_sunk': self.states.get('enemy_ships_sunk', 0),
                            'hits': self.total_hits,
                            'misses': self.total_misses,
                            'accuracy': (self.total_hits / (self.total_hits + self.total_misses) * 100) if (self.total_hits + self.total_misses) > 0 else 0,
                            'max_streak': self.max_streak
                        }
                        
                        try:
                            self.client.send_data_to_server(save_request)
                            print(f"[CONTROLLER] ✓ Game history save request sent on force quit!")
                        except Exception as e:
                            print(f"[CONTROLLER] Error sending save request: {e}")
                        
                        # IMPORTANT: Notify server that this player quit (opponent wins)
                        # WAIT for response to ensure server processed it
                        try:
                            quit_notification = {'request': 'player_quit'}
                            response = self.client.send_data_to_server(quit_notification)
                            if response and response.get('message') == 'quit_acknowledged':
                                print(f"[CONTROLLER] ✓ Server acknowledged quit - opponent is now winner!")
                            else:
                                print(f"[CONTROLLER] Server response: {response}")
                        except Exception as e:
                            print(f"[CONTROLLER] Error sending quit notification: {e}")
                        
                        # Disconnect so opponent gets win notification
                        self.client.disconnect()
                        self.client = None  # Clear client reference
                        print(f"[CONTROLLER] Disconnected - opponent should win")
                        
                        # Small delay to ensure disconnect message is sent
                        import time
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"[CONTROLLER] Error during force quit: {e}")
                
                # Exit immediately
                self.states['game_finished'] = True
                self.states['winner_name'] = self.states.get('enemy_username', 'Unknown')
                return self.states
            # Removed 'quit_confirmed' handling - now handled via game_over_message
        
        # Check for game over message (from normal game end)
        if self.game_over_message:
            # Start timer on first detection
            if self.game_over_timer == 0:
                self.game_over_timer = pygame.time.get_ticks()
                print(f"[CONTROLLER] Game over message displayed: {self.game_over_message}")
            
            # Show message for 2 seconds, then transition
            elapsed = pygame.time.get_ticks() - self.game_over_timer
            
            if elapsed >= 2000:
                print("[CONTROLLER] 2 seconds passed - setting game_finished flag")
                self.states['game_finished'] = True
                self.states['winner_name'] = self.client.get_winner() if self.client else None
                return self.states
            
            # Continue showing game over message overlay
            return self.states
        
        # Update game state
        game_finished = self.update()
        
        # Don't immediately transition on game finished - let game_over_message timer handle it
        if game_finished and not self.game_over_message:
            # Only for unexpected endings (like disconnect without message)
            self.states['game_finished'] = True
            self.states['winner_name'] = self.client.get_winner() if self.client else None
            return self.states
        
        return self.states
    
    def get_state(self):
        """Get current state for view"""
        # Calculate turn transition progress (0 to 1)
        turn_transition_progress = 0
        if self.turn_transition_message and self.turn_transition_timer > 0:
            elapsed = pygame.time.get_ticks() - self.turn_transition_timer
            turn_transition_progress = min(elapsed / self.turn_transition_duration, 1.0)
        
        return {
            'my_grid': self.my_grid,
            'enemy_grid': self.enemy_grid,
            'my_hits': self.my_hits,
            'enemy_hits': self.enemy_hits,
            'my_turn': self.my_turn,
            'time_remaining': self.time_remaining,
            'my_timeout_count': self.my_timeout_count,
            'enemy_timeout_count': self.enemy_timeout_count,
            'ships_sunk': self.ships_sunk,
            'enemy_ships_sunk': self.enemy_ships_sunk,
            'total_ships': self.total_ships,
            'my_sunk_ships': self.my_sunk_ships,
            'enemy_sunk_ships': self.enemy_sunk_ships,
            'my_username': self.my_username,
            'enemy_username': self.enemy_username,
            'hover_cell': self.hover_cell,
            'enemy_panel_hover': self.enemy_panel_hover,  # Hover state cho enemy panel
            'game_over_message': self.game_over_message,
            'ship_sunk_message': self.ship_sunk_message,
            'my_ship_positions': self.my_ship_positions,
            'turn_transition_message': self.turn_transition_message,
            'turn_transition_progress': turn_transition_progress,
            'timeout_warning': self.show_timeout_warning
        }
