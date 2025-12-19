"""
Main Entry Point - Beautiful Tkinter UI Version (MVC Architecture)
Modern design with dark theme and better UX
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time
import pygame
import subprocess
import sys

from controllers.main_controller import MainController
from views.login_view import LoginView
from views.register_view import RegisterView
from views.home_view import HomeView
from views.room_list_view import RoomListView
from views.room_lobby_view import RoomLobbyView
from views.statistics_view import StatisticsViewTk

# Import Pygame game stages
from stages.auto_ship_location import AutoShipLocation
from controllers.battle_controller import BattleController
from views.battle_stats_view import BattleStatsView


class BattleshipApp:
    """Ứng dụng chính - Kiến trúc MVC
    
    Chức năng:
    - Quản lý tất cả các view (Login, Register, Home, Room List, Room Lobby)
    - Kết nối Controller với View
    - Xử lý chuyển đổi giữa Tkinter UI và Pygame battle
    - Quản lý luồng game: đăng nhập → tạo/vào phòng → chiến đấu → thống kê
    - Polling room status để phát hiện khi trận đấu bắt đầu
    - Lưu lịch sử trận đấu vào database
    
    Thuộc tính:
    - root: Tkinter window chính
    - controller: MainController (MVC)
    - current_view: View hiện tại đang hiển thị
    - lobby_poll_thread: Thread polling trạng thái phòng chờ
    - lobby_poll_active: Flag điều khiển polling
    """
    
    def __init__(self):
        """Khởi tạo ứng dụng
        
        - Tạo Tkinter window 900x650 với dark theme
        - Khởi tạo MainController (MVC)
        - Hiển thị màn hình login đầu tiên
        - Đăng ký handler cho sự kiện đóng window
        """
        self.root = tk.Tk()
        self.root.title("⚓ Battleship Game")
        self.root.geometry("900x650")
        self.root.minsize(900, 650)  # Minimum size
        self.root.resizable(True, True)  # Allow resizing
        self.root.configure(bg='#0f172a')
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # MVC Controller
        self.controller = MainController()
        
        # Current view
        self.current_view = None
        
        # Room lobby polling
        self.lobby_poll_thread = None
        self.lobby_poll_active = False
        
        # Show login
        self.show_login()
    
    def show_login(self):
        """Hiển thị màn hình đăng nhập
        
        - Hủy view hiện tại
        - Tạo LoginView mới
        - Gán callback: on_login → _handle_login, on_register → show_register
        """
        self._destroy_current_view()
        
        view = LoginView(self.root)
        view.on_login = self._handle_login
        view.on_register = self.show_register
        
        self.current_view = view
    
    def show_register(self):
        """Hiển thị màn hình đăng ký
        
        - Hủy view hiện tại
        - Tạo RegisterView mới
        - Gán callback: on_register → _handle_register, on_back_to_login → show_login
        """
        self._destroy_current_view()
        
        view = RegisterView(self.root)
        view.on_register = self._handle_register
        view.on_back_to_login = self.show_login
        
        self.current_view = view
    
    def _handle_login(self, username, password):
        """Xử lý đăng nhập qua controller
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
        
        Luồng:
        1. Validate không để trống
        2. Gọi controller.login()
        3. Nếu thành công → hiển thị home sau 500ms
        4. Nếu thất bại → hiển thị lỗi, xóa password
        """
        if not username or not password:
            self.current_view.show_message("Username and password required", is_error=True)
            return
        
        
        # Call controller
        result = self.controller.login(username, password)
        
        if result['success']:
            self.current_view.show_message(f"Welcome back, {username}!", is_error=False)
            self.root.after(500, self.show_home)
        else:
            self.current_view.show_message(result['message'], is_error=True)
            self.current_view.clear_password()
    
    def _handle_register(self, username, password):
        """Xử lý đăng ký tài khoản qua controller
        
        Args:
            username: Tên đăng nhập mới
            password: Mật khẩu mới
        
        Validate:
        - Không để trống username/password
        - Password ít nhất 4 ký tự
        
        Luồng:
        1. Validate đầu vào
        2. Gọi controller.register()
        3. Nếu thành công → hiển thị thông báo, chuyển về login sau 1.5s
        4. Nếu thất bại → hiển thị lỗi
        """
        if not username or not password:
            self.current_view.show_message("Username and password required", is_error=True)
            return
        
        if len(password) < 4:
            self.current_view.show_message("Password must be at least 4 characters", is_error=True)
            return
        
        # Call controller
        result = self.controller.register(username, password)
        
        if result['success']:
            self.current_view.show_message("✓ Account created successfully!", is_error=False)
            # Show login view after 1.5 seconds
            self.root.after(1500, self.show_login)
        else:
            self.current_view.show_message(result['message'], is_error=True)
            self.current_view.clear_password()
    
    def show_home(self):
        """Hiển thị màn hình chính sau khi đăng nhập
        
        - Lấy thông tin user và online status từ controller
        - Tạo HomeView với 4 nút: Create Room, Browse Rooms, Statistics, Logout
        - Gán callback cho từng nút
        """
        self._destroy_current_view()
        
        user = self.controller.get_user()
        is_online = self.controller.is_connected_to_lobby()
        
        view = HomeView(self.root, user['username'], is_online)
        view.on_create_room = self._handle_create_room
        view.on_browse_rooms = self.show_room_list
        view.on_statistics = self._handle_statistics
        view.on_logout = self._handle_logout
        
        self.current_view = view
    
    def _handle_create_room(self):
        """Xử lý tạo phòng chơi mới
        
        Luồng:
        1. Tạo tên phòng theo format: "<username>'s Room"
        2. Gọi controller.create_room()
        3. Nếu thành công → chuyển đến room lobby
        4. Nếu thất bại → hiển thị lỗi
        """
        print("[APP] Create room button clicked")
        user = self.controller.get_user()
        room_name = f"{user['username']}'s Room"
        
        print(f"[APP] Calling controller.create_room with name: {room_name}")
        result = self.controller.create_room(room_name)
        print(f"[APP] Create room result: {result}")
        
        if result['success']:
            self.show_room_lobby(result['room'])
        else:
            messagebox.showerror("Error", result['message'])
    
    def show_room_list(self):
        """Hiển thị danh sách phòng chơi có sẵn
        
        - Tạo RoomListView
        - Gán callback: refresh → _refresh_rooms, join → _handle_join_room, back → show_home
        - Tự động refresh danh sách phòng lần đầu
        """
        self._destroy_current_view()
        
        view = RoomListView(self.root)
        view.on_refresh = lambda: self._refresh_rooms(view)
        view.on_join = self._handle_join_room
        view.on_back = self.show_home
        
        self.current_view = view
        self._refresh_rooms(view)
    
    def _refresh_rooms(self, view):
        """Làm mới danh sách phòng chơi
        
        Args:
            view: RoomListView instance để update
        
        - Gọi controller.get_rooms() để lấy danh sách từ server
        - Update view với danh sách mới
        - Hiển thị lỗi nếu thất bại
        """
        result = self.controller.get_rooms()
        
        if result['success']:
            view.update_rooms(result['rooms'])
        else:
            messagebox.showerror("Error", result['message'])
    
    def _handle_join_room(self, room_data):
        """Xử lý tham gia phòng chơi
        
        Args:
            room_data: Dict chứa thông tin phòng (room_id, room_name, host_username)
        
        Luồng:
        1. Gọi controller.join_room()
        2. Nếu thành công → chuyển đến room lobby
        3. Nếu thất bại (phòng đầy/không tồn tại) → hiển thị lỗi
        """
        result = self.controller.join_room(room_data)
        
        if result['success']:
            self.show_room_lobby(result['room'])
        else:
            messagebox.showerror("Error", result['message'])
    
    def show_room_lobby(self, room):
        """Hiển thị phòng chờ (đợi đủ 2 người chơi)
        
        Args:
            room: Dict chứa room_name
        
        - Tạo RoomLobbyView
        - Gán callback: on_leave → _handle_leave_room
        - Bắt đầu polling để kiểm tra số người và trạng thái game
        """
        self._destroy_current_view()
        
        view = RoomLobbyView(self.root, room['room_name'])
        view.on_leave = self._handle_leave_room
        
        self.current_view = view
        self._start_lobby_polling(view)
    
    def _start_lobby_polling(self, view):
        """Bắt đầu polling trạng thái phòng chờ
        
        Args:
            view: RoomLobbyView instance để update
        
        Luồng:
        1. Tạo thread polling chạy mỗi 1 giây
        2. Gọi controller.get_room_status()
        3. Update số người chơi lên view
        4. Nếu game_started=True → gọi _start_battle()
        5. Nếu room closed → quay về home
        
        Lưu ý: Dùng self.root.after(0, ...) để update UI từ thread an toàn
        """
        self.lobby_poll_active = True
        
        def poll():
            while self.lobby_poll_active:
                result = self.controller.get_room_status()
                
                if result['success']:
                    status = result['status']
                    self.root.after(0, lambda: view.update_player_count(status['player_count']))
                    
                    if status.get('game_started'):
                        self.root.after(0, self._start_battle)
                        break
                else:
                    self.root.after(0, lambda: messagebox.showinfo("Info", "Room closed"))
                    self.root.after(0, self.show_home)
                    break
                
                time.sleep(1)
        
        self.lobby_poll_thread = threading.Thread(target=poll, daemon=True)
        self.lobby_poll_thread.start()
    
    def _handle_leave_room(self):
        """Xử lý rời khỏi phòng chờ
        
        Luồng:
        1. Dừng polling thread (lobby_poll_active = False)
        2. Gọi controller.leave_room() để ngắt kết nối
        3. Quay về màn hình home
        """
        self.lobby_poll_active = False
        
        result = self.controller.leave_room()
        
        if result['success']:
            self.show_home()
        else:
            messagebox.showerror("Error", result['message'])
    
    def _start_battle(self):
        """Bắt đầu trận chiến (chuyển sang Pygame)
        
        Luồng hoàn chỉnh:
        1. Ẩn Tkinter window
        2. Khởi tạo Pygame window 800x600
        3. GIAI ĐOẠN 1 - Đặt tàu (AutoShipLocation):
           - Người chơi sắp xếp 6 loại tàu trên lưới 10x10
           - Tàu có thể xoay, di chuyển, random
           - Nhấn "Lock Ships" để xác nhận
        4. GIAI ĐOẠN 2 - Chiến đấu (BattleController):
           - Hiển thị 2 lưới: lưới tàu của mình + lưới tấn công địch
           - Lượt chơi luân phiên, click vào ô để tấn công
           - Socket gửi/nhận kết quả tấn công realtime
           - Hiển thị hit/miss, tàu bị chìm, streak
        5. GIAI ĐOẠN 3 - Kết thúc:
           - Khi 1 người mất hết tàu → hiển thị winner
           - Lưu lịch sử trận đấu vào database ngay lập tức
           - Hiển thị BattleStatsView với biểu đồ thống kê
        6. Dọn dẹp:
           - Đóng Pygame
           - Ngắt kết nối room
           - Hiện lại Tkinter window và quay về home
        
        Exception handling:
        - Try-catch toàn bộ để không crash app
        - Finally luôn disconnect và quay về home
        """
        self.lobby_poll_active = False
        
        print("[APP] Starting Pygame battle...")
        
        # Hide Tkinter window
        self.root.withdraw()
        
        try:
            # Initialize Pygame if not already done
            if not pygame.get_init():
                pygame.init()
            
            # Create Pygame window
            WIDTH, HEIGHT = 800, 600
            WIN = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption('Battleship - Battle')
            
            # Start ship location stage
            ship_location_stage = AutoShipLocation()
            ship_location_stage.load_client(self.controller.room_client)
            
            # Run ship location stage
            clock = pygame.time.Clock()
            FPS = 30
            running = True
            ship_locked = False
            
            while running:
                clock.tick(FPS)
                states = ship_location_stage.process_events()
                ship_location_stage.draw(WIN)
                pygame.display.update()
                
                if states['ship_locked']:
                    ship_locked = True
                    my_grid = ship_location_stage.get_grid()
                    break
            
            if ship_locked:
                # Start battle stage
                battle_stage = BattleController()
                battle_stage.load_client(self.controller.room_client)
                battle_stage.load_my_grid(my_grid)
                
                game_finished = False
                battle_stats_data = None
                
                print("[APP] Starting battle loop...")
                
                winner_name = None
                while running and not game_finished:
                    clock.tick(FPS)
                    states = battle_stage.process_events()
                    battle_stage.draw(WIN)
                    pygame.display.update()
                    
                    # Controller shows game over message for 2 seconds, then sets game_finished
                    if states.get('game_finished'):
                        game_finished = True
                        winner_name = states.get('winner_name')
                        
                        print(f"[APP] ========================================")
                        print(f"[APP] Game finished! Winner: {winner_name}")
                        print(f"[APP] game_finished={game_finished}, running={running}")
                        print(f"[APP] Loop will exit next iteration")
                        print(f"[APP] ========================================")
                
                print(f"[APP] After battle loop: game_finished={game_finished}, running={running}")
                
                battle_stats_data = None
                
                print(f"[APP] Checking conditions: game_finished={game_finished}, running={running}")
                
                # After battle loop - prepare battle stats and save immediately
                if game_finished:
                    print("[APP] *** GAME FINISHED ***")
                    print(f"[APP] Winner is: {winner_name}")
                    
                    # Store battle stats
                    battle_stats_data = {
                        'winner_name': winner_name,
                        'my_user_id': battle_stage.my_user_id,
                        'my_username': battle_stage.my_username,
                        'enemy_user_id': battle_stage.enemy_user_id,
                        'enemy_username': battle_stage.enemy_username,
                        'my_ships_sunk': battle_stage.enemy_ships_sunk,
                        'enemy_ships_sunk': battle_stage.ships_sunk,
                        'my_hits': battle_stage.my_hits_count,
                        'my_misses': battle_stage.my_misses_count,
                        'enemy_hits': battle_stage.enemy_hits_count,
                        'enemy_misses': battle_stage.enemy_misses_count,
                        'my_max_streak': battle_stage.my_max_streak,
                        'enemy_max_streak': battle_stage.enemy_max_streak
                    }
                    
                    # Save game history IMMEDIATELY
                    print("[APP] Saving game history immediately...")
                    self._save_game_history(battle_stats_data)
                    
                    # Then show battle stats view if user didn't quit
                    if running:
                        try:
                            print("[APP] Creating BattleStatsView...")
                            battle_stats_view = BattleStatsView()
                            print("[APP] BattleStatsView created successfully")
                            waiting_for_next = True
                            
                            print("[APP] Entering battle stats loop...")
                            while running and waiting_for_next:
                                clock.tick(FPS)
                                
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        print("[APP] QUIT event received in battle stats")
                                        running = False
                                        waiting_for_next = False
                                    elif event.type == pygame.MOUSEBUTTONDOWN:
                                        if event.button == 1:
                                            print(f"[APP] Mouse clicked at {event.pos}")
                                            result = battle_stats_view.handle_click(event.pos)
                                            print(f"[APP] Click result: {result}")
                                            if result == 'next':
                                                print("[APP] Next button clicked!")
                                                waiting_for_next = False
                                
                                battle_stats_view.draw(WIN, battle_stats_data)
                                pygame.display.update()
                            
                            print("[APP] Battle stats view finished")
                        except Exception as e:
                            print(f"[APP] ERROR in battle stats view: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("[APP] User quit during game over, stats already saved")
                else:
                    print(f"[APP] Game did not finish normally: game_finished={game_finished}")
                
                print(f"[APP] Out of battle loop. game_finished={game_finished}, running={running}")
            
            # Clean up Pygame
            print("[APP] Cleaning up Pygame...")
            pygame.quit()
            
        except Exception as e:
            print(f"[APP] Error in battle: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Disconnect from room
            if self.controller.room_client:
                try:
                    print("[APP] Disconnecting from room...")
                    self.controller.room_client.disconnect()
                except Exception as e:
                    print(f"[APP] Error disconnecting: {e}")
                    pass
            self.controller.room_client = None
            self.controller.room = None
            
            # Show Tkinter window again
            print("[APP] Returning to home screen...")
            self.root.deiconify()
            self.show_home()
    
    def _save_game_history(self, battle_stats_data):
        """Lưu lịch sử trận đấu vào database qua server
        
        Args:
            battle_stats_data: Dict chứa:
                - winner_name: Tên người thắng
                - my_username, enemy_username: Tên 2 người chơi
                - my_ships_sunk, enemy_ships_sunk: Số tàu bị chìm
                - my_hits, my_misses: Số phát trúng/trượt
                - my_max_streak, enemy_max_streak: Streak dài nhất
        
        Luồng:
        1. Kiểm tra user đã đăng nhập
        2. Reconnect lobby client nếu bị disconnect
        3. Tính toán:
           - result: 'win'/'lose' dựa vào winner_name
           - accuracy: (hits / total_shots) * 100
        4. Gửi request 'save_game_history' đến lobby server
        5. Server lưu vào bảng game_history
        
        Lưu ý: 
        - Mỗi trận lưu 2 records (1 cho mỗi người chơi)
        - Được gọi NGAY SAU khi game kết thúc
        """
        user = self.controller.get_user()
        
        if not user:
            print("[APP] Cannot save game history - no user")
            return
        
        # Reconnect to lobby if needed
        if not self.controller.lobby_client:
            print("[APP] Lobby client disconnected, reconnecting...")
            self.controller._connect_to_lobby()
        
        if not self.controller.lobby_client:
            print("[APP] Cannot save game history - failed to connect to lobby")
            return
        
        print(f"[APP] Saving game history for user {user.get('username')}")
        print(f"[APP] Battle stats data: {battle_stats_data}")
        
        try:
            # Determine result for current player
            winner_name = battle_stats_data.get('winner_name')
            my_username = battle_stats_data.get('my_username')
            result = 'win' if winner_name == my_username else 'lose'
            
            print(f"[APP] Winner: {winner_name}, My username: {my_username}, Result: {result}")
            
            # Calculate accuracy
            my_total_shots = battle_stats_data['my_hits'] + battle_stats_data['my_misses']
            accuracy = (battle_stats_data['my_hits'] / my_total_shots * 100) if my_total_shots > 0 else 0
            
            # Calculate enemy accuracy
            enemy_total_shots = battle_stats_data['enemy_hits'] + battle_stats_data['enemy_misses']
            enemy_accuracy = (battle_stats_data['enemy_hits'] / enemy_total_shots * 100) if enemy_total_shots > 0 else 0
            
            game_data = {
                'user_id': user['id'],
                'username': my_username,
                'opponent_username': battle_stats_data.get('enemy_username'),
                'result': result,
                'ships_sunk': battle_stats_data['enemy_ships_sunk'],  # Enemy ships I sunk
                'enemy_ships_sunk': battle_stats_data['my_ships_sunk'],  # My ships enemy sunk
                'hits': battle_stats_data['my_hits'],
                'misses': battle_stats_data['my_misses'],
                'accuracy': round(accuracy, 2),
                'max_streak': battle_stats_data['my_max_streak'],
                'enemy_hits': battle_stats_data['enemy_hits'],
                'enemy_misses': battle_stats_data['enemy_misses'],
                'enemy_accuracy': round(enemy_accuracy, 2),
                'enemy_max_streak': battle_stats_data['enemy_max_streak']
            }
            
            print(f"[APP] Sending game data to server: {game_data}")
            
            # Send save request to server
            response = self.controller.lobby_client.send_data_to_server({
                'request': 'save_game_history',
                'game_data': game_data
            })
            
            print(f"[APP] Server response: {response}")
            
            if response and response.get('success'):
                print(f"[APP] ✓ Game history saved successfully for user {my_username}")
            else:
                error = response.get('error') if response else 'No response'
                print(f"[APP] ✗ Failed to save game history: {error}")
        except Exception as e:
            print(f"[APP] ✗ Error saving game history: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_statistics(self):
        """Hiển thị thống kê trận đấu của người chơi
        
        - Tạo Toplevel window mới 1000x700
        - Hiển thị StatisticsViewTk với:
          * Tổng số trận, thắng/thua, win rate
          * Biểu đồ pie chart tỷ lệ thắng/thua
          * Biểu đồ bar chart độ chính xác
          * Danh sách 10 trận gần nhất
        - Lấy dữ liệu từ lobby_client qua API
        """
        print("[APP] Statistics button clicked")
        user = self.controller.get_user()
        print(f"[APP] User: {user}")
        print(f"[APP] Lobby client: {self.controller.lobby_client}")
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Battle Statistics")
        stats_window.geometry("1000x700")
        stats_window.configure(bg='#0f172a')
        
        stats_view = StatisticsViewTk(
            stats_window,
            user,
            self.controller.lobby_client,
            lambda: stats_window.destroy()
        )
    
    def _handle_logout(self):
        """Xử lý đăng xuất
        
        - Gọi controller.logout() để:
          * Set user offline trong database
          * Ngắt kết nối lobby/room client
          * Xóa session
        - Quay về màn hình login
        """
        self.controller.logout()
        self.show_login()
    
    def _destroy_current_view(self):
        """Hủy view hiện tại trước khi chuyển sang view mới
        
        - Dừng lobby polling nếu đang chạy
        - Gọi destroy() trên view hiện tại
        - Set current_view = None
        """
        if self.current_view:
            self.lobby_poll_active = False
            if hasattr(self.current_view, 'destroy'):
                self.current_view.destroy()
            self.current_view = None
    
    def _on_closing(self):
        """Xử lý khi đóng window (click X)
        
        Cleanup:
        - Gửi logout request tới server (server set offline)
        - Logout và ngắt tất cả kết nối
        - Destroy Tkinter window
        
        Đảm bảo user không còn hiển thị online khi đóng app
        """
        # Controller.logout() sẽ tự gửi logout request tới server
        self.controller.logout()
        self.root.destroy()
    
    def run(self):
        """Chạy ứng dụng (bắt đầu Tkinter event loop)"""
        self.root.mainloop()


def main():
    """Điểm khởi đầu chương trình client
    
    Tạo và chạy BattleshipApp:
    - Hiển thị màn hình login
    - Cho phép người chơi đăng ký/đăng nhập
    - Tạo hoặc tham gia phòng chơi
    - Chiến đấu với người chơi khác qua mạng
    - Xem thống kê lịch sử trận đấu
    """
    app = BattleshipApp()
    app.run()


if __name__ == "__main__":
    main()
