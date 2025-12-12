# 🚢 BATTLESHIP GAME - HƯỚNG DẪN CHI TIẾT

## 📋 MỤC LỤC
1. [Giới thiệu](#giới-thiệu)
2. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
3. [Cài đặt](#cài-đặt)
4. [Cách chơi](#cách-chơi)
5. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
6. [Chi tiết các thành phần](#chi-tiết-các-thành-phần)
7. [Luồng hoạt động](#luồng-hoạt-động)
8. [Cơ chế game](#cơ-chế-game)
9. [Database](#database)
10. [Troubleshooting](#troubleshooting)

---

## 🎮 GIỚI THIỆU

**Battleship Game** là game đánh chìm tàu chiến theo lượt cho 2 người chơi, được xây dựng bằng Python với giao diện đồ họa Pygame và Tkinter.

### Tính năng chính:
- ✅ Chơi online multiplayer qua mạng LAN/Internet
- ✅ Hệ thống đăng ký/đăng nhập tài khoản
- ✅ Tạo và tham gia phòng chơi
- ✅ 5 loại tàu chiến với kích thước khác nhau
- ✅ Đếm giờ mỗi lượt (30 giây)
- ✅ Hệ thống timeout (3 lần timeout = thua)
- ✅ Hiệu ứng nổ và lửa khi trúng đích
- ✅ Thống kê chi tiết sau mỗi trận
- ✅ Lưu lịch sử 20 trận gần nhất
- ✅ Biểu đồ phân tích hiệu suất
- ✅ **Xem thông tin đối thủ trong trận đấu** (Click vào tên đối thủ)
- ✅ **Hiệu ứng hover trên enemy panel** (Thay đổi con trỏ chuột, nền sáng lên)
- ✅ **8 chỉ số thống kê tổng quan**: Accuracy, Win Streak, Current Streak, Ships Sunk
- ✅ **Biểu đồ Win/Loss Timeline** thay thế Accuracy Trend
- ✅ **Quit dialog sử dụng Tkinter** (Thay thế Pygame custom dialog)
- ✅ **Ship Image Auto-Rotation**: Tự động xoay ảnh tàu 90° khi nằm ngang

---

## 💻 YÊU CẦU HỆ THỐNG

### Phần cứng tối thiểu:
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Màn hình: 1024x768 trở lên
- Kết nối mạng: LAN hoặc Internet

### Phần mềm:
- **Python**: 3.8 trở lên
- **MySQL**: 8.0 trở lên (để lưu dữ liệu người dùng)
- **Hệ điều hành**: Windows 10/11, Linux, MacOS

---

## ⚙️ CÀI ĐẶT

### Bước 1: Cài đặt Python
```bash
# Tải Python từ: https://www.python.org/downloads/
# Đảm bảo chọn "Add Python to PATH" khi cài đặt
```

### Bước 2: Cài đặt MySQL
```bash
# Tải MySQL từ: https://dev.mysql.com/downloads/mysql/
# Cài đặt với password mặc định hoặc tùy chỉnh
```

### Bước 3: Cài đặt thư viện Python
```bash
# Di chuyển vào thư mục dự án
cd battleship-go-master

# Cài đặt tất cả thư viện cần thiết
pip install -r requirements.txt
```

**Danh sách thư viện chính:**
- `pygame`: Giao diện game
- `mysql-connector-python`: Kết nối database
- `pillow`: Xử lý hình ảnh
- `matplotlib`: Vẽ biểu đồ thống kê

### Bước 4: Thiết lập Database
```bash
# 1. Mở MySQL Command Line hoặc MySQL Workbench
# 2. Tạo database
CREATE DATABASE battleship;
```

### Bước 5: Cấu hình Database
Mở file `config/db_config.py` và chỉnh sửa:
```python
DB_CONFIG = {
    'host': 'localhost',      # Địa chỉ MySQL server
    'user': 'root',           # Username MySQL
    'password': 'your_password',  # Password MySQL của bạn
    'database': 'battleship'  # Tên database
}
```

---

## 🎯 CÁCH CHƠI

### 1. Khởi động Server
```bash
# Mở terminal/cmd tại thư mục dự án
python server.py

# Server sẽ chạy tại: localhost:5555
# Log: "Server started on localhost:5555"
```

### 2. Khởi động Client (Người chơi 1)
```bash
# Mở terminal mới
python main-client.py
```

### 3. Khởi động Client (Người chơi 2)
```bash
# Mở terminal thứ 3 (trên cùng máy hoặc máy khác)
python main-client.py
```

### 4. Đăng ký/Đăng nhập
- Nếu lần đầu: Click **"Register"** → Nhập username + password
- Nếu đã có tài khoản: Nhập username + password → **"Login"**

### 5. Tạo hoặc tham gia phòng
- **Tạo phòng**: Click "Create Room" → Nhập Room ID → Đợi đối thủ
- **Tham gia phòng**: Nhập Room ID của phòng đã tạo → "Join Room"

### 6. Bố trí tàu
- Chọn tàu từ danh sách bên trái
- Click vào lưới để đặt tàu (ngang hoặc dọc)
- Nhấn **R** để xoay tàu
- Nhấn **"Lock Ships"** khi hoàn tất

### 7. Chiến đấu
- **Lượt của bạn**: Click vào ô trên lưới bên phải (đối thủ)
- **Trúng**: Ô màu đỏ + hiệu ứng nổ
- **Trượt**: Ô màu xám + dấu X
- **Thời gian**: 30 giây/lượt
- **Timeout 3 lần**: Tự động thua

### 8. Kết thúc game
- Đánh chìm hết 5 tàu đối thủ = Thắng
- Bị đánh chìm hết 5 tàu = Thua
- Timeout 3 lần = Thua
- Đối thủ quit = Thắng

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Tổng quan
```
┌─────────────────────────────────────────────────────────────┐
│                    BATTLESHIP GAME SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   CLIENT 1   │◄───────►│    SERVER    │                  │
│  │  (Player 1)  │         │  (Room Mgr)  │                  │
│  └──────────────┘         └──────┬───────┘                  │
│         ▲                         │                          │
│         │                         ▼                          │
│         │                  ┌─────────────┐                  │
│         │                  │   DATABASE  │                  │
│         │                  │    MySQL    │                  │
│         │                  └─────────────┘                  │
│         │                         ▲                          │
│         │                         │                          │
│         ▼                         │                          │
│  ┌──────────────┐                │                          │
│  │   CLIENT 2   │────────────────┘                          │
│  │  (Player 2)  │                                            │
│  └──────────────┘                                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Mô hình Client-Server
- **Server**: Quản lý phòng, đồng bộ trạng thái game, xử lý logic
- **Client**: Hiển thị giao diện, nhận input người chơi, gửi request
- **Database**: Lưu tài khoản, lịch sử trận đấu, thống kê

---

## 📁 CHI TIẾT CÁC THÀNH PHẦN

### 1. Entry Point (Điểm khởi đầu)

#### `main_tk_modern.py` (1459 dòng)
**Chức năng**: File chính khởi động client game
**Luồng hoạt động**:
```python
1. Khởi tạo Pygame window (800x600)
2. Kết nối đến lobby server
3. Hiển thị màn hình login/register
4. Sau khi login → Room list
5. Tham gia room → Ship placement
6. Bắt đầu battle → Battle screen
7. Kết thúc → Battle stats screen
8. Quay về room list hoặc thoát
```

**Code chính**:
```python
class BattleshipApp:
    def __init__(self):
        self.lobby_client = LobbyClient()  # Kết nối lobby
        self.controller = None
        
    def run(self):
        # Login/Register flow
        # Room management flow  
        # Battle flow
        # Stats flow
```

#### `game_server_new.py` (605 dòng)
**Chức năng**: Server quản lý tất cả các phòng và người chơi
**Luồng hoạt động**:
```python
1. Lắng nghe kết nối tại localhost:5555
2. Mỗi client kết nối → Tạo thread riêng
3. Xử lý requests: login, create_room, join_room, attack, etc.
4. Đồng bộ game state giữa 2 players trong room
5. Xác định thắng/thua, lưu database
```

**Các loại request**:
- `login`: Xác thực người dùng
- `register`: Tạo tài khoản mới
- `create_room`: Tạo phòng mới
- `join_room`: Tham gia phòng
- `ship_locked`: Xác nhận đã đặt tàu
- `attack_tile`: Tấn công ô
- `player_quit`: Người chơi thoát
- `save_game_history`: Lưu kết quả trận

---

### 2. Controllers (Bộ điều khiển)

#### `controllers/main_controller.py`
**Chức năng**: Quản lý luồng chuyển đổi giữa các màn hình
```python
- Khởi tạo lobby client
- Quản lý room client  
- Chuyển đổi giữa: Login → Room List → Battle → Stats
```

#### `controllers/auth_controller.py`
**Chức năng**: Xử lý đăng nhập/đăng ký
```python
def handle_login(username, password):
    # Gửi request đến server
    # Nhận response với user_id
    # Lưu session
    
def handle_register(username, password):
    # Validate input
    # Tạo tài khoản mới trong DB
    # Auto login
```

#### `controllers/battle_controller.py` (940+ dòng)
**Chức năng**: Logic chính của game battle
**Xử lý**:
```python
1. Đồng bộ game state từ server
2. Quản lý timer (30s/lượt)
3. Xử lý attack: hit/miss
4. Kiểm tra tàu chìm
5. Phát hiện timeout (3 lần = thua)
6. Kiểm tra win/lose conditions
7. Tính toán statistics (accuracy, streak)
8. Xử lý enemy panel hover effect (NEW)
9. Hiển thị opponent info popup (NEW)
```

**Các thuộc tính quan trọng**:
```python
self.my_turn: bool              # Lượt của mình
self.time_remaining: int        # Thời gian còn lại
self.my_timeout_count: int      # Số lần timeout
self.ships_sunk: int            # Số tàu mình bị chìm
self.enemy_ships_sunk: int      # Số tàu đối thủ bị chìm
self.total_hits: int            # Tổng số phát trúng
self.total_misses: int          # Tổng số phát trượt
self.max_streak: int            # Chuỗi trúng dài nhất
self.enemy_panel_hover: bool    # Enemy panel đang hover (NEW)
self.enemy_username: str        # Tên đối thủ để xem stats (NEW)
```

**Tính năng mới**:
```python
def show_opponent_info_popup():
    # Tạo thread riêng để không block Pygame
    # Fetch stats từ server qua client.get_opponent_stats()
    # Hiển thị OpponentInfoView popup
    # Sử dụng wait_window() để giữ popup mở
    
def is_enemy_panel_clicked(mouse_pos):
    # Kiểm tra click vào enemy panel rect (420, 70, 360, 65)
    # Return True nếu click vào tên đối thủ
    
def show_quit_dialog_tkinter():
    # Sử dụng tkinter.messagebox.askyesno()
    # Thay thế Pygame custom dialog (đã xóa ~100 dòng code)
```

**Flow update() mỗi frame**:
```
1. Check winner (ưu tiên cao nhất)
2. Check opponent disconnect
3. Sync game_data từ server
4. Update turn & timer
5. Check timeout (3 lần = game over)
6. Process enemy attacks
7. Check ship sunk notifications
8. Return game state
```

#### `controllers/room_controller.py`
**Chức năng**: Quản lý danh sách phòng
```python
- Lấy danh sách rooms từ server
- Tạo room mới
- Join room
- Refresh room list
```

---

### 3. Views (Giao diện)

#### `views/login_view.py`
**Giao diện**: Màn hình đăng nhập
```
┌─────────────────────────────┐
│      🚢 BATTLESHIP 🚢       │
│                              │
│  Username: [________]        │
│  Password: [________]        │
│                              │
│  [  LOGIN  ] [ REGISTER ]    │
└─────────────────────────────┘
```

#### `views/room_list_view.py`
**Giao diện**: Danh sách phòng
```
┌─────────────────────────────────────┐
│       AVAILABLE ROOMS               │
│                                     │
│  Room ID    Players   Status        │
│  ────────────────────────────       │
│  room1      1/2       Waiting...    │
│  room2      2/2       Playing       │
│                                     │
│  [Create Room]  [Join]  [Refresh]   │
└─────────────────────────────────────┘
```

#### `views/battle_view.py` (900+ dòng)
**Giao diện**: Màn hình chiến đấu chính (Pygame)
```
┌────────────────────────────────────────────────────────────────┐
│                    ⚓ BATTLESHIP BATTLE                         │
├────────────────────────────────────────────────────────────────┤
│  👤 player1        ⬜⬜⬜     🎯 player2        ⬜⬜⬜         │
│  ⚓ Ships: 5/5                ⚓ Ships: 5/5                      │
│                               📊 Click to view stats (hover)   │
├────────────────────────────────────────────────────────────────┤
│   A B C D E F G H I J          A B C D E F G H I J            │
│ 1 [MY GRID - LEFT]          1  [ENEMY GRID - RIGHT]           │
│ 2 🚢 🚢 🚢                  2  💥 ❌ ❌                       │
│ 3 🚢 🚢                     3  ❌ 💥 ❌                       │
│ ...                          ...                               │
│                                                                │
│            🎯 YOUR TURN - Click enemy grid!                    │
│                        ⏱ 25s                                  │
└────────────────────────────────────────────────────────────────┘
```

**Tính năng mới**:
- **Enemy Panel Hover Effect**: Khi di chuột qua tên đối thủ:
  - Nền chuyển sang màu hồng nhạt (#fff0f0)
  - Border dày hơn (4px thay vì 3px)
  - Con trỏ chuột đổi thành hình bàn tay (HAND cursor)
  - Hiện hint "📊 Click to view stats"
  
- **Click Enemy Name**: Click vào tên đối thủ để xem popup thông tin
  - Popup hiển thị 8 chỉ số thống kê
  - Không block game (dùng thread riêng)
  - Toplevel window có thể đóng bất kỳ lúc nào

- **Ship Image Rotation**: Xoay ảnh tàu khi nằm ngang
  - Tàu nằm dọc: Giữ nguyên ảnh gốc
  - Tàu nằm ngang: Tự động xoay -90° để giữ nguyên tỷ lệ
  - Áp dụng cho cả tàu nổi và tàu chìm
  - Không bị kéo dãn/bẹp ảnh

**Các hàm vẽ chính**:
```python
draw_grids()           # Vẽ 2 lưới 10x10
draw_ships()           # Vẽ tàu + hiệu ứng
draw_attacks()         # Vẽ hit/miss markers
draw_player_panels()   # Vẽ thông tin người chơi + hover effect
draw_timer()           # Vẽ đồng hồ đếm ngược
draw_turn_indicator()  # Hiển thị lượt
draw_coordinates()     # Vẽ A-J, 1-10
```

#### `views/battle_stats_view.py`
**Giao diện**: Thống kê sau trận (Pygame)
```
┌──────────────────────────────────────────────────┐
│           BATTLE STATISTICS                      │
├──────────────────────────────────────────────────┤
│  player1          vs          player2            │
│                                                  │
│    Ships Sunk      2    -    5                  │
│    Total Hits      12   -    28                 │
│    Total Misses    18   -    10                 │
│    Accuracy        40%  -    73.7%              │
│    Max Streak      3    -    7                  │
│                                                  │
│              ✗ DEFEAT                            │
│                                                  │
│  [Bar Chart Comparison]                          │
│                                                  │
│              [   NEXT   ]                        │
└──────────────────────────────────────────────────┘
```

#### `views/statistics_view_tk.py` (500+ dòng)
**Giao diện**: Tổng quan thống kê tài khoản (Tkinter + Matplotlib)
```
┌─────────────────────────────────────────────────────────────────┐
│          ⚓ PLAYER STATISTICS - username                         │
├─────────────────────────────────────────────────────────────────┤
│  🎮 Total: 50  🏆 Wins: 35  ✗ Losses: 15  🎯 Accuracy: 67.5%  │
│  🔥 Best Streak: 12  ⚓ Ships Sunk: 180  📊 Current: 3         │
├─────────────────────────────────────────────────────────────────┤
│  [Pie Chart: Win/Loss]  [Radar Chart: Performance]             │
├─────────────────────────────────────────────────────────────────┤
│  📈 Win/Loss Timeline (Last 20 Games)                           │
│     ● Win  ○ Loss                                               │
├─────────────────────────────────────────────────────────────────┤
│  [Hits vs Misses]      [Avg Ships/Hits per Game]               │
├─────────────────────────────────────────────────────────────────┤
│  🎯 Recent Battles (Last 20 games) - Double Click to view info │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Date     Opponent Result Ships Acc Streak                │  │
│  │ 12/10/24 player2  WIN    5    75%   8                    │  │
│  │ 12/10/24 player3  LOSS   2    45%   3                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│              [  ← BACK TO HOME  ]                               │
└─────────────────────────────────────────────────────────────────┘
```

**Tính năng mới**:
- **8 Summary Cards** (2 rows x 4 cols):
  1. Total Games (Tổng số trận)
  2. Wins (Thắng)
  3. Losses (Thua)
  4. **Accuracy** (Độ chính xác %) - **MỚI**
  5. **Best Win Streak** (Chuỗi thắng dài nhất) - **MỚI**
  6. Ships Sunk (Tàu đã đánh chìm)
  7. Win Rate (Tỷ lệ thắng %)
  8. **Current Streak** (Chuỗi hiện tại) - **MỚI**

- **Win/Loss Timeline Chart**: Thay thế Accuracy Trend
  - Hiển thị 20 trận gần nhất theo thứ tự thời gian
  - Điểm xanh (●) = Win, Điểm đỏ (○) = Loss
  - Dễ nhìn hơn, thấy ngay xu hướng thắng/thua

- **Double-click on Recent Battles**: Click vào tên đối thủ trong bảng
  - Hiện popup thông tin đối thủ (OpponentInfoView)
  - Hiển thị 8 chỉ số thống kê của đối thủ

**Các biểu đồ**:
1. **Win/Loss Pie Chart**: Tỷ lệ thắng/thua
2. **Performance Radar**: 3 metrics (Accuracy, Win Rate, Efficiency)
3. **Win/Loss Timeline**: 20 trận gần nhất (thay Accuracy Trend)
4. **Hits vs Misses**: So sánh số phát trúng/trượt
5. **Performance Breakdown**: Trung bình tàu và hits mỗi ván

#### `views/opponent_info_view.py` (230+ dòng) - **MỚI**
**Giao diện**: Popup thông tin đối thủ (Tkinter Toplevel)
```
┌────────────────────────────────────────────────────┐
│    📊 Thông Tin Đối Thủ: player2                   │
├────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ 🎮 Total │  │ 🏆 Wins  │  │ ✗ Losses │         │
│  │    50    │  │    35    │  │    15    │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ 🎯 Acc%  │  │ 🔥 Best  │  │ ⚓ Ships  │         │
│  │  67.5%   │  │    12    │  │   180    │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                    │
│  ┌──────────┐  ┌──────────┐                       │
│  │ 📈 Win%  │  │ 📊 Now   │                       │
│  │   70%    │  │    +3    │                       │
│  └──────────┘  └──────────┘                       │
│                                                    │
│                [ ✕ Close ]                         │
└────────────────────────────────────────────────────┘
```

**Tính năng**:
- **Popup kích thước**: 480x580 pixels
- **Dark theme**: Background #0f172a (Navy blue đậm)
- **8 thẻ thống kê** (2x4 layout):
  1. Total Games (Tổng số trận)
  2. Wins (Thắng)
  3. Losses (Thua)
  4. Accuracy (Độ chính xác %)
  5. Best Streak (Chuỗi thắng dài nhất)
  6. Ships Sunk (Tàu đã đánh chìm)
  7. Win Rate (Tỷ lệ thắng %)
  8. Current Streak (Chuỗi hiện tại)

**Cách mở popup**:
1. Trong **Battle Screen**: Click vào tên đối thủ (enemy panel)
2. Trong **Statistics View**: Double-click vào tên trong bảng Recent Battles

**Đặc điểm kỹ thuật**:
- Sử dụng `threading.Thread` để không block Pygame loop
- `Toplevel` window với `transient(parent)` để luôn ở trên
- Không dùng `grab_set()` để tránh modal blocking
- `wait_window()` để giữ popup mở cho đến khi user đóng
- Tự động center vào giữa màn hình

---

### 4. Models (Mô hình dữ liệu)

#### `models/user_model.py`
**Chức năng**: Quản lý dữ liệu người dùng
```python
class UserModel:
    @staticmethod
    def authenticate(username, password):
        # Kiểm tra username/password trong DB
        # Return user_id nếu đúng
        
    @staticmethod
    def create_user(username, password):
        # Hash password
        # Insert vào bảng users
        # Return user_id
        
    @staticmethod
    def get_user_by_id(user_id):
        # Lấy thông tin user
        # Return dict: {id, username, created_at}
```

#### `models/room_model.py`
**Chức năng**: Quản lý dữ liệu phòng
```python
class RoomModel:
    @staticmethod
    def get_all_rooms():
        # Lấy danh sách rooms đang active
        # Return list of rooms
        
    @staticmethod
    def create_room(room_id, creator_id):
        # Tạo room mới trong DB
        
    @staticmethod
    def add_player_to_room(room_id, user_id):
        # Thêm player vào room
```

#### `models/game_history_model.py`
**Chức năng**: Lưu và truy vấn lịch sử trận đấu
```python
class GameHistoryModel:
    @staticmethod
    def save_game(user_id, opponent_id, result, 
                  ships_sunk, hits, misses, accuracy, max_streak):
        # Insert vào bảng game_history
        # played_at = NOW()
        
    @staticmethod
    def get_user_stats(user_id):
        # Tính tổng: games, wins, losses, accuracy, etc.
        # Return dict with aggregated stats
        
    @staticmethod
    def get_recent_games(user_id, limit=20):
        # Lấy 20 trận gần nhất
        # JOIN với users để lấy opponent_username
        # ORDER BY played_at DESC
```

---

### 5. Networking (Mạng)

#### `networking/room_server.py` (640+ dòng)
**Chức năng**: Server chính xử lý tất cả logic multiplayer

**Class GameRoom**:
```python
class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.status = GameStatus.waiting  # waiting/ship_lock/battle/finished
        self.lock = threading.Lock()      # Thread-safe
        self.game_data = {
            'winner': None,
            'game_grid': {},
            'clients': {},
            'sockets': {}
        }
    
    def add_client(username, socket, user_id):
        # Thêm player vào room
        # Nếu đủ 2 người → chuyển sang ship_lock
        
    def remove_client(username):
        # Xóa player
        # Nếu đang battle → set winner cho người còn lại
        
    def attack_enemy_tile(attacker, row, col):
        # Xử lý tấn công
        # Kiểm tra hit/miss
        # Kiểm tra tàu chìm
        # Chuyển lượt hoặc giữ lượt (nếu hit)
        
    def game_over(loser_username):
        # Set winner
        # Chuyển status = finished
```

**Process Request**:
```python
def process_request(request_data, username, room):
    request_type = request_data.get('request')
    
    if request_type == 'ship_locked':
        # Lưu grid của player
        # Check nếu cả 2 đã lock → start battle
        
    elif request_type == 'attack_tile':
        # Gọi room.attack_enemy_tile()
        # Return kết quả: hit/miss
        
    elif request_type == 'player_quit':
        # Set winner = opponent
        # Return quit_acknowledged
        
    elif request_type == 'game_data':
        # Return game state của cả 2 players
        
    elif request_type == 'winner':
        # Return winner username
        
    elif request_type == 'timeout':
        # Tăng timeout_count
        # Nếu >= 3 → game_over()
        # Chuyển lượt
```

**Thread Safety**:
```python
# Mọi thao tác với game_data đều dùng lock
with room.lock:
    room.game_data['winner'] = winner
    # Đảm bảo không có race condition
```

**Socket Timeout**:
```python
client_socket.settimeout(1.0)
# Timeout 1s để detect disconnect nhanh
# Tránh block vô hạn khi client ngắt kết nối
```

#### `networking/room_client.py`
**Chức năng**: Client kết nối với room server
```python
class RoomClient:
    def connect_to_server(username, room_id, user_id):
        # Tạo socket kết nối tới localhost:5555
        # Gửi connection_data: {username, room_id, user_id}
        
    def send_data_to_server(data):
        # Gửi request dạng JSON
        # Nhận response
        # Return decoded response
        
    def get_game_data():
        # Request 'game_data'
        # Return clients dict
        
    def get_winner():
        # Request 'winner'
        # Return winner username hoặc None
        
    def attack_tile(row, col):
        # Gửi attack request
        # Return hit/miss/game_over
        
    def ship_sinked():
        # Thông báo tàu bị chìm
        
    def disconnect():
        # Gửi disconnect request
        # Shutdown socket
        # Close connection
```

#### `networking/client.py`
**Chức năng**: Client kết nối lobby server
```python
class LobbyClient:
    def connect():
        # Kết nối tới lobby server
        
    def login(username, password):
        # Gửi login request
        # Return user data
        
    def register(username, password):
        # Gửi register request
        # Return success/fail
        
    def get_rooms():
        # Lấy danh sách rooms
        
    def create_room(room_id):
        # Tạo room mới
```

---

### 6. Sprites (Game Objects)

#### `sprites/ship.py`
**Base class cho tất cả các tàu**
```python
class Ship(pygame.sprite.Sprite):
    def __init__(self, name, length, image_path):
        self.name = name          # "battleship", "cruiser", etc.
        self.length = length      # 2-5 ô
        self.cells = []           # Danh sách (row, col)
        self.horizontal = True    # Hướng ngang/dọc
        self.image = load_image() # Hình ảnh tàu
        
    def rotate():
        # Xoay tàu 90 độ
        
    def is_valid_position(grid, row, col):
        # Kiểm tra có đặt được tại vị trí này không
        # Check: trong lưới, không trùng tàu khác, không sát nhau
```

#### Các loại tàu:
```python
Battleship (5 ô)    sprites/battleship.py
Cruiser (4 ô)       sprites/cruiser.py
Destroyer (3 ô)     sprites/destroyer.py
Submarine (3 ô)     sprites/submarine.py
Rescue Ship (2 ô)   sprites/rescue_ship.py
```

#### `sprites/animations/explosion.py`
**Hiệu ứng nổ khi trúng đích**
```python
class Explosion:
    def __init__(x, y):
        self.frames = load_explosion_sprites()  # 8 frames
        self.current_frame = 0
        
    def update():
        # Chuyển frame tiếp theo
        # Khi hết frames → remove
```

#### `sprites/animations/fire.py`
**Hiệu ứng lửa cháy trên tàu chìm**
```python
class Fire:
    def __init__(x, y):
        self.frames = load_fire_sprites()  # 4 frames loop
        
    def update():
        # Lặp vô hạn các frames
```

---

## 🔄 LUỒNG HOẠT ĐỘNG

### 1. Khởi động và Đăng nhập
```
User khởi động main_tk_modern.py
    ↓
Kết nối đến Lobby Server (localhost:5555)
    ↓
Hiển thị Login Screen
    ↓
User nhập username + password
    ↓
Click "Login" → Gửi request
    ↓
Server kiểm tra DB:
    - Đúng → Return user_id
    - Sai → Return error
    ↓
Client lưu user session → Chuyển sang Room List
```

### 2. Tạo/Tham gia Phòng
```
User tại Room List Screen
    ↓
Option 1: Create Room
    - Nhập Room ID
    - Gửi create_room request
    - Server tạo GameRoom object
    - Client đợi player 2
    ↓
Option 2: Join Room
    - Nhập Room ID
    - Gửi join_room request
    - Server add client vào room
    - Nếu đủ 2 người → Chuyển sang Ship Placement
```

### 3. Bố trí Tàu
```
Ship Placement Screen (Auto hoặc Manual)
    ↓
User đặt 5 tàu trên lưới 10x10
    ↓
Click "Lock Ships"
    ↓
Gửi ship_locked request + grid data
    ↓
Server lưu grid của player
    ↓
Kiểm tra: Cả 2 players đã lock?
    - Nếu chưa → Đợi
    - Nếu rồi → Start Battle
    ↓
Server chuyển room.status = battle
Server random người đi trước (my_turn = True)
```

### 4. Chiến Đấu (Battle Loop)
```
┌─────────────────────────────────────────────┐
│         BATTLE GAME LOOP (30 FPS)           │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 1. Check Winner (Ưu tiên cao nhất)          │
│    - Gửi get_winner() request               │
│    - Nếu có winner → Game Over              │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 2. Check Opponent Disconnect                │
│    - game_data < 2 players?                 │
│    - → You Win!                             │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 3. Sync Game Data                           │
│    - Gửi get_game_data() request            │
│    - Nhận: turn, timeout_count, attacks     │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 4. Update Timer                             │
│    - Mỗi giây: time_remaining -= 1          │
│    - Nếu <= 10s: Hiệu ứng cảnh báo đỏ       │
│    - Nếu <= 0: Gửi timeout request          │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 5. Kiểm tra Timeout                         │
│    - my_timeout_count >= 3? → You Lose      │
│    - enemy_timeout_count >= 3? → You Win    │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 6. Process Turn                             │
│    ┌─────────────────────────────────────┐  │
│    │ If MY TURN:                         │  │
│    │   - Chờ user click ô địch           │  │
│    │   - Gửi attack_tile request         │  │
│    │   - Server xử lý:                   │  │
│    │     * Check hit/miss                │  │
│    │     * Check tàu chìm                │  │
│    │     * Hit → Giữ lượt                │  │
│    │     * Miss → Đổi lượt               │  │
│    │   - Client nhận response            │  │
│    │   - Hiển thị kết quả (💥/❌)        │  │
│    │   - Reset timer                     │  │
│    └─────────────────────────────────────┘  │
│    ┌─────────────────────────────────────┐  │
│    │ If OPPONENT'S TURN:                 │  │
│    │   - Hiển thị "Waiting..."           │  │
│    │   - Check enemy attacks             │  │
│    │   - Hiển thị hits trên my grid      │  │
│    │   - Check my ships sunk             │  │
│    │   - Update timer khi enemy attack   │  │
│    └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 7. Render Screen                            │
│    - Draw grids (my + enemy)                │
│    - Draw ships với transparency            │
│    - Draw hits/misses                       │
│    - Draw explosions/fire                   │
│    - Draw player info                       │
│    - Draw timer                             │
│    - Draw turn indicator                    │
│    - pygame.display.update()                │
└─────────────────────────────────────────────┘
    │
    └──────► Loop lại từ bước 1
```

### 5. Kết thúc và Thống kê
```
Game Over (5 tàu chìm hoặc timeout 3 lần)
    ↓
Hiển thị "YOU WON!" hoặc "YOU LOST!" (2 giây)
    ↓
Disconnect khỏi room
    ↓
Tính toán statistics:
    - Ships sunk, hits, misses, accuracy
    - Max streak, win/lose
    ↓
Gửi save_game_history request
    ↓
Server lưu vào database
    ↓
Hiển thị Battle Stats Screen:
    - So sánh 2 players
    - Bar chart
    - Victory/Defeat banner
    ↓
Click "Next" → Quay về Room List
```

---

## ⚙️ CƠ CHẾ GAME

### 1. Timer System (Hệ thống đếm giờ)

**Cách hoạt động**:
```python
# Mỗi lượt có 30 giây
TURN_TIME = 30

# Khi bắt đầu lượt:
turn_start_time = pygame.time.get_ticks()  # Lưu timestamp
time_remaining = 30

# Mỗi frame:
elapsed = (pygame.time.get_ticks() - turn_start_time) / 1000  # Giây
time_remaining = max(0, TURN_TIME - elapsed)

# Cảnh báo:
if time_remaining <= 10:
    # Hiển thị timer màu đỏ nhấp nháy
    
# Timeout:
if time_remaining <= 0:
    send_timeout_request()
    timeout_count += 1
    switch_turn()
```

**Reset timer khi**:
1. Chuyển lượt
2. Player attack (hit hoặc miss)
3. Khởi tạo game lần đầu

### 2. Attack Mechanism (Cơ chế tấn công)

**Flow khi user click ô địch**:
```
1. User click vào ô (row, col) trên enemy grid
    ↓
2. Client validation:
    - Có phải lượt mình? (my_turn == True)
    - Ô này đã attack chưa? (enemy_hits[row][col])
    ↓
3. Gửi attack_tile request: {row, col}
    ↓
4. Server nhận request:
    - Lấy grid của đối thủ
    - Check ô này: có tàu không?
    ↓
5. Hit (có tàu):
    - Mark hit
    - Check tàu chìm:
        * Đếm số ô hit của tàu này
        * Nếu = chiều dài → Tàu chìm
        * Notify cả 2 players
    - Giữ lượt cho attacker (my_turn = True)
    - Return: {result: 'hit', ship_name: '...'}
    ↓
6. Miss (không có tàu):
    - Mark miss
    - Đổi lượt (switch turn)
    - Return: {result: 'miss'}
    ↓
7. Client nhận response:
    - Update enemy_grid
    - Hiển thị hiệu ứng:
        * Hit → Explosion animation (8 frames)
        * Miss → Gray marker + X
    - Update statistics
    - Reset timer
    ↓
8. Check win condition:
    - enemy_ships_sunk == 5? → You Win!
```

**Server side logic**:
```python
def attack_enemy_tile(attacker, row, col):
    with room.lock:  # Thread-safe
        # Get defender's grid
        defender = [p for p in clients if p != attacker][0]
        defender_grid = game_grid[defender]
        
        # Check hit/miss
        ship_name = defender_grid[row][col]
        
        if ship_name:  # HIT
            # Mark hit
            attacked_tile[attacker] = {
                'position': (col, row),
                'ship_name': ship_name
            }
            
            # Check ship sunk
            if is_ship_fully_hit(ship_name):
                # Notify both players
                game_data[defender]['ship_sunk'] = ship_name
                
                # Check all ships sunk (win condition)
                if count_ships_sunk(defender) >= 5:
                    game_data['winner'] = attacker
            
            # Keep turn
            clients[attacker]['my_turn'] = True
            
            return {'result': 'hit', 'ship_name': ship_name}
            
        else:  # MISS
            attacked_tile[attacker] = {
                'position': (col, row),
                'ship_name': None
            }
            
            # Switch turn
            clients[attacker]['my_turn'] = False
            clients[defender]['my_turn'] = True
            
            return {'result': 'miss'}
```

### 3. Timeout System (Hệ thống timeout)

**Flow timeout**:
```
Timer <= 0
    ↓
Client gửi timeout request
    ↓
Server:
    - timeout_count += 1
    - Log: "Player timeout #{count}"
    - Switch turn
    ↓
Check timeout_count >= 3:
    - Yes → game_over(username)
    - No → Tiếp tục game
    ↓
Return: {timeout_count, turn_switched}
    ↓
Client nhận:
    - Update my_timeout_count
    - Hiển thị timeout boxes (⬜→🔴)
    - Reset timer
```

**Hiển thị timeout**:
```
Player info panel:
┌─────────────────────────┐
│ 👤 player1   ⬜⬜⬜    │  ← 0 timeout
│ 👤 player2   🔴🔴⬜    │  ← 2 timeouts
└─────────────────────────┘
```

### 4. Ship Sinking Detection (Phát hiện tàu chìm)

**Client side (kiểm tra tàu mình)**:
```python
def _check_my_sunk_ships():
    for ship in my_ships:
        if ship.name in my_sunk_ships:
            continue  # Đã chìm rồi
            
        # Check tất cả cells của tàu
        all_hit = True
        for (row, col) in ship.cells:
            if not my_hits[row][col]:
                all_hit = False
                break
        
        if all_hit:
            # Tàu mới chìm!
            my_sunk_ships.add(ship.name)
            ships_sunk += 1
            print(f"My {ship.name} sunk! ({ships_sunk}/5)")
```

**Server side (kiểm tra tàu địch)**:
```python
def is_ship_fully_hit(ship_name, defender_grid, attacks):
    # Tìm tất cả ô của tàu này
    ship_cells = []
    for row in range(10):
        for col in range(10):
            if defender_grid[row][col] == ship_name:
                ship_cells.append((row, col))
    
    # Check tất cả ô đã bị attack chưa
    for (row, col) in ship_cells:
        if (col, row) not in attacks:
            return False  # Còn ô chưa bị hit
    
    return True  # Tàu chìm hoàn toàn
```

**Notification flow**:
```
Server phát hiện tàu chìm
    ↓
Set game_data[defender]['ship_sunk'] = ship_name
    ↓
Client (defender) nhận notification:
    - Hiển thị: "YOUR BATTLESHIP SUNK!" (2 giây)
    - Add vào my_sunk_ships set
    - ships_sunk += 1
    ↓
Client gửi clear_ship_sunk request
    ↓
Server clear notification (tránh hiện lại)
```

### 5. Win/Lose Conditions (Điều kiện thắng/thua)

**Các cách thắng**:
1. **Đánh chìm 5 tàu địch**: `enemy_ships_sunk >= 5`
2. **Đối thủ timeout 3 lần**: `enemy_timeout_count >= 3`
3. **Đối thủ quit**: Nhận `player_quit` request
4. **Đối thủ disconnect**: `game_data` chỉ còn 1 người

**Kiểm tra mỗi frame**:
```python
# Ưu tiên 1: Check winner từ server
winner = client.get_winner()
if winner:
    if winner == my_username:
        game_over_message = "YOU WON!"
    else:
        game_over_message = "YOU LOST!"
    return True  # Game finished

# Ưu tiên 2: Check disconnect
if len(game_data) < 2:
    game_over_message = "YOU WON!"  # Opponent left
    return True

# Ưu tiên 3: Check timeout
if my_timeout_count >= 3:
    game_over_message = "YOU LOST!"
    return True
    
if enemy_timeout_count >= 3:
    game_over_message = "YOU WON!"
    return True

# Ưu tiên 4: Check ships sunk
if enemy_ships_sunk >= 5:
    game_over_message = "YOU WON!"
    return True
    
if ships_sunk >= 5:
    game_over_message = "YOU LOST!"
    return True
```

### 6. Quit Handling (Xử lý thoát game)

**Flow khi người chơi quit**:
```
User bấm X (pygame.QUIT)
    ↓
Hiển thị quit confirmation dialog:
    "Quit Game?"
    "You will lose this match!"
    [Yes]  [No]
    ↓
Click Yes:
    ↓
1. Lưu kết quả thua:
    - save_game_history(result='lose', ...)
    ↓
2. Gửi player_quit request:
    - Server nhận
    - Set winner = opponent
    - Return quit_acknowledged
    ↓
3. Client nhận response:
    - Biết server đã set winner
    ↓
4. Disconnect:
    - Gửi disconnect request
    - Close socket
    - client = None
    ↓
5. Hiển thị "YOU LOST!" (2 giây)
    ↓
6. Chuyển sang Stats Screen
    ↓
---ĐỒNG THỜI---
    ↓
Opponent client:
    - Check winner mỗi frame
    - Nhận winner = opponent_username
    - Hiển thị "YOU WON!" ngay lập tức
    - KHÔNG cần đợi người quit bấm Next!
```

**Key point**: 
- `player_quit` request đảm bảo server set winner TRƯỚC KHI người quit disconnect
- Opponent check winner ở đầu game loop nên nhận ngay

---

## 💾 DATABASE

### Cấu trúc Database

#### Table: `users`
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_online TINYINT DEFAULT 0      -- 1 = online, 0 = offline
);
```

**Ví dụ dữ liệu**:
```
| id | username | password (hashed)      | created_at          | is_online |
|----|----------|------------------------|---------------------|-----------|
| 1  | player1  | $2b$12$xyz...         | 2024-12-10 10:00:00 | 1         |
| 2  | player2  | $2b$12$abc...         | 2024-12-10 10:05:00 | 0         |
```

#### Table: `game_history`
```sql
CREATE TABLE game_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    opponent_id INT NOT NULL,
    result ENUM('win', 'lose') NOT NULL,
    ships_sunk INT DEFAULT 0,         -- Số tàu mình đánh chìm
    hits INT DEFAULT 0,                -- Số phát trúng
    misses INT DEFAULT 0,              -- Số phát trượt
    accuracy DECIMAL(5,2) DEFAULT 0,   -- Độ chính xác (%)
    max_streak INT DEFAULT 0,          -- Chuỗi trúng dài nhất
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (opponent_id) REFERENCES users(id)
);
```

**Ví dụ dữ liệu**:
```
| id | user_id | opponent_id | result | ships_sunk | hits | misses | accuracy | max_streak | played_at           |
|----|---------|-------------|--------|------------|------|--------|----------|------------|---------------------|
| 1  | 1       | 2           | win    | 5          | 28   | 10     | 73.68    | 7          | 2024-12-10 14:30:00 |
| 2  | 2       | 1           | lose   | 2          | 12   | 18     | 40.00    | 3          | 2024-12-10 14:30:00 |
| 3  | 1       | 2           | lose   | 3          | 15   | 20     | 42.86    | 4          | 2024-12-10 15:00:00 |
```

### Queries Quan Trọng

#### 1. Get User Statistics
```sql
SELECT 
    COUNT(*) as total_games,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as total_wins,
    SUM(CASE WHEN result = 'lose' THEN 1 ELSE 0 END) as total_losses,
    ROUND(SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_rate,
    SUM(ships_sunk) as total_ships_sunk,
    SUM(hits) as total_hits,
    SUM(misses) as total_misses,
    ROUND(AVG(accuracy), 2) as avg_accuracy,
    MAX(max_streak) as best_streak
FROM game_history
WHERE user_id = ?
```

**Kết quả**:
```json
{
    "total_games": 50,
    "total_wins": 35,
    "total_losses": 15,
    "win_rate": 70.0,
    "total_ships_sunk": 180,
    "total_hits": 850,
    "total_misses": 450,
    "avg_accuracy": 65.38,
    "best_streak": 12
}
```

#### 2. Get Recent Games
```sql
SELECT 
    u.username as opponent_username,
    gh.result,
    gh.ships_sunk,
    gh.hits,
    gh.misses,
    gh.accuracy,
    gh.max_streak,
    gh.played_at
FROM game_history gh
JOIN users u ON gh.opponent_id = u.id
WHERE gh.user_id = ?
ORDER BY gh.played_at DESC
LIMIT 20
```

#### 3. Save Game History
```sql
INSERT INTO game_history 
(user_id, opponent_id, result, ships_sunk, hits, misses, accuracy, max_streak)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
```

**Note**: Mỗi trận đấu tạo 2 records (1 cho mỗi người)

---

## 🐛 TROUBLESHOOTING

### 1. Không kết nối được Server

**Triệu chứng**: 
- Client báo "Connection failed"
- Server không log gì

**Nguyên nhân**:
- Server chưa chạy
- Firewall chặn port 5555
- Sai địa chỉ IP

**Giải pháp**:
```bash
# 1. Kiểm tra server đang chạy
# Mở terminal server, phải thấy:
# "Server started on localhost:5555"

# 2. Kiểm tra port
netstat -an | findstr 5555
# Phải thấy: TCP    0.0.0.0:5555    LISTENING

# 3. Tắt firewall tạm thời (Windows)
# Control Panel → Firewall → Turn off

# 4. Nếu chơi qua mạng khác máy:
# Sửa file main_tk_modern.py
self.lobby_client.connect('192.168.1.100', 5555)  # IP của máy server
```

### 2. Database Connection Error

**Triệu chứng**:
```
Error: Access denied for user 'root'@'localhost'
```

**Giải pháp**:
```python
# Kiểm tra file config/db_config.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_ACTUAL_PASSWORD',  # ← Sửa đây!
    'database': 'battleship'
}

# Test kết nối
python -c "from config.db_config import get_db_connection; get_db_connection()"
```

### 3. Game bị lag/giật

**Nguyên nhân**:
- FPS thấp
- Network lag
- CPU/RAM cao

**Giải pháp**:
```python
# 1. Tăng FPS (main_tk_modern.py)
FPS = 60  # Thay vì 30

# 2. Giảm hiệu ứng
# Tắt explosion/fire animations nếu cần

# 3. Kiểm tra network
ping localhost  # Phải < 1ms nếu cùng máy
```

### 4. Timer không đồng bộ

**Triệu chứng**:
- Timer 2 người khác nhau
- Timeout không đúng

**Giải pháp**:
- Timer được tính ở client dựa trên `turn_start_time`
- Khi attack hoặc switch turn → reset timer
- Đảm bảo cả 2 client đều reset khi có sự kiện

### 5. Ships không hiển thị

**Nguyên nhân**:
- Thiếu file ảnh trong `assets/ships/`
- Đường dẫn sai

**Giải pháp**:
```bash
# Kiểm tra cấu trúc thư mục
assets/ships/
    battleship/
        battleship_h.png
        battleship_v.png
    cruiser/
        ...
```

### 6. Lỗi "Room full"

**Nguyên nhân**:
- Room đã có 2 người
- Server cache room cũ

**Giải pháp**:
```python
# Restart server
# Hoặc tạo room với ID mới
```

### 7. Game không kết thúc khi quit

**Triệu chứng**:
- Người quit mà opponent không thấy win
- Phải chờ timeout

**Giải pháp**:
- Đảm bảo code đã update (có `player_quit` request)
- Check log xem có nhận `quit_acknowledged` không
- Restart cả server và client

---

## 📊 PERFORMANCE TIPS

### Tối ưu hóa Client
```python
# 1. Giảm polling frequency
# Thay vì check game_data mỗi frame, check mỗi 0.1s

# 2. Cache images
# Load tất cả sprites 1 lần ở đầu

# 3. Optimize rendering
# Chỉ redraw phần thay đổi thay vì toàn bộ màn hình
```

### Tối ưu hóa Server
```python
# 1. Dùng connection pooling cho DB
# Thay vì tạo connection mỗi query

# 2. Thread pooling
# Giới hạn số threads đồng thời

# 3. Timeout socket
# Detect disconnect nhanh hơn
client_socket.settimeout(1.0)
```

---

## 🎓 HƯỚNG DẪN MỞ RỘNG

### Thêm loại tàu mới
```python
# 1. Tạo file sprites/carrier.py
class Carrier(Ship):
    def __init__(self):
        super().__init__('carrier', 6, 'assets/ships/carrier/')

# 2. Thêm vào ship list
SHIPS = [
    Battleship(), Cruiser(), Destroyer(),
    Submarine(), RescueShip(), Carrier()  # ← Mới
]
```

### Thêm power-ups
```python
# Ví dụ: Radar - reveal 1 ô random của địch

# 1. Thêm UI button
# 2. Gửi request 'use_powerup'
# 3. Server process và return revealed cell
# 4. Client hiển thị
```

### Thêm game modes
```python
# Mode: Time Attack (giới hạn tổng thời gian)
# Mode: Sudden Death (1 hit = 1 ship down)
# Mode: Team Battle (2v2)
```

---

## 📝 CREDITS

**Developers**: [Your Team Name]
**Version**: 2.0
**Last Updated**: December 2024

**Technologies Used**:
- Python 3.11
- Pygame 2.5.2
- MySQL 8.0
- Matplotlib 3.8.0

**Assets**:
- Ship sprites: Custom designed
- Sound effects: [Source]
- Background music: [Source]

---

## 📞 SUPPORT

Nếu gặp vấn đề:
1. Check [Troubleshooting](#troubleshooting)
2. Xem log trong console
3. Restart server và client
4. Contact: your.email@example.com

---

**Chúc bạn chơi game vui vẻ! 🚢💥🎯**
