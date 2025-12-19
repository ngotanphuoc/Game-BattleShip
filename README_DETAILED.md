# 🚢 BATTLESHIP GAME - HƯỚNG DẪN CHI TIẾT

## 📋 MỤC LỤC
1. [Tổng quan](#tổng-quan)
2. [Kiến trúc Client-Server](#kiến-trúc-client-server)
3. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
4. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
5. [Hướng dẫn cài đặt](#hướng-dẫn-cài-đặt)
6. [Hướng dẫn chạy game](#hướng-dẫn-chạy-game)
7. [Cách chơi](#cách-chơi)
8. [Luồng hoạt động](#luồng-hoạt-động)
9. [Troubleshooting](#troubleshooting)
10. [Tính năng](#tính-năng)

---

## 🎯 TỔNG QUAN

**Battleship Game** là game đánh tàu chiến multiplayer được xây dựng theo mô hình **Client-Server**:
- **Server**: Quản lý phòng chơi, xử lý logic game, lưu trữ dữ liệu trong MySQL
- **Client**: Giao diện người chơi, hiển thị game qua Tkinter + Pygame

**Công nghệ sử dụng:**
- **Python 3.11+**: Ngôn ngữ lập trình chính
- **MySQL 8.0+**: Lưu trữ tài khoản, lịch sử trận đấu
- **Socket TCP**: Giao tiếp Client-Server real-time
- **Tkinter**: Giao diện menu, đăng nhập, phòng chờ
- **Pygame**: Giao diện trận đấu, hiệu ứng

---

## 🏗️ KIẾN TRÚC CLIENT-SERVER

### Tại sao tách Client và Server?

**Trước đây**: Tất cả code trong 1 project → Khó maintain, deploy và scale

**Bây giờ**: Tách thành 2 project riêng biệt:

```
┌─────────────────┐         Socket TCP          ┌─────────────────┐
│                 │    (localhost:65432)         │                 │
│     CLIENT      │◄────────────────────────────►│     SERVER      │
│                 │                              │                 │
│  - Giao diện    │   • Auth requests            │  - Logic game   │
│  - Input/Output │   • Room management          │  - Database     │
│  - Pygame       │   • Game data                │  - MySQL        │
└─────────────────┘                              └─────────────────┘
```

**Lợi ích:**
- ✅ **Client** không cần MySQL, chỉ cần pygame + matplotlib
- ✅ **Server** có thể chạy trên máy khác (VPS, cloud)
- ✅ Nhiều client kết nối cùng 1 server
- ✅ Bảo mật: Database credentials chỉ ở server
- ✅ Dễ maintain: Sửa server không ảnh hưởng client

---

## 📁 CẤU TRÚC THỰ MỤC

### 🖥️ SERVER (Máy chủ game)

```
server/
│
├── server.py                 # ⭐ File chính - Chạy server
├── requirements.txt          # Dependencies cho server
│
├── config/                   # Cấu hình
│   ├── __init__.py
│   ├── db_config.py         # Kết nối MySQL
│   ├── battleship.sql       # Database schema
│   ├── migration_*.sql      # SQL migrations (nếu có)
│   └── run_migration.py     # Script chạy migration
│
├── models/                   # Database Models (ORM)
│   ├── __init__.py
│   ├── base_model.py        # Base class, query executor
│   ├── user_model.py        # ⭐ User: login, register, stats
│   ├── room_model.py        # Room management
│   └── game_history_model.py # Lịch sử trận đấu
│
└── networking/               # Socket networking
    ├── network.py           # Base Network class (encode/decode)
    ├── constants.py         # BUFFER_SIZE, SHIPS_NAMES
    ├── server.py            # Old server (legacy)
    └── room_server.py       # ⭐ Multi-room server handler
```

**File quan trọng:**
- **`server.py`**: UI quản lý server (Tkinter), start/stop server
- **`user_model.py`**: Xử lý authentication, tính stats từ `game_history`
- **`room_server.py`**: Xử lý:
  - Auth requests (`auth:login`, `auth:register`, `auth:logout`)
  - Room management (create, join, list rooms)
  - Game logic (attack, ship placement, win/lose)

---

### 🎮 CLIENT (Máy người chơi)

```
client/
│
├── main-client.py            # ⭐ File chính - Chạy game
├── requirements.txt          # Dependencies cho client (pygame, matplotlib)
│
├── assets/                   # Tài nguyên game
│   ├── background/          # Hình nền
│   ├── crosshair/           # Con trỏ ngắm
│   ├── fire/                # Hiệu ứng nổ
│   ├── fonts/               # Font chữ
│   └── ships/               # Hình các loại tàu
│
├── data/                     # Client-side data structures
│   ├── __init__.py
│   └── user_session.py      # ⭐ Lưu thông tin user local (không có DB)
│
├── controllers/              # MVC Controllers
│   ├── __init__.py
│   ├── auth_controller.py   # ⭐ Xử lý login/register qua networking
│   ├── main_controller.py   # ⭐ Controller chính
│   ├── battle_controller.py # Logic trận đấu
│   └── room_controller.py   # Quản lý phòng
│
├── views/                    # Giao diện Tkinter
│   ├── __init__.py
│   ├── login_view.py        # Màn hình đăng nhập
│   ├── register_view.py     # Màn hình đăng ký
│   ├── home_view.py         # Màn hình chính
│   ├── room_list_view.py    # Danh sách phòng
│   ├── room_lobby_view.py   # Phòng chờ
│   ├── battle_view.py       # Màn hình chiến đấu (Pygame)
│   ├── battle_stats_view.py # Thống kê sau trận
│   └── statistics_view.py   # Tổng quan thống kê
│
├── stages/                   # Game stages (Pygame)
│   └── auto_ship_location.py # Đặt tàu tự động
│
└── networking/               # Client-side networking
    ├── network.py           # Base Network class (giống server)
    ├── constants.py         # Constants (giống server)
    ├── auth_client.py       # ⭐ Gửi auth requests (login/register)
    ├── client.py            # Old client (legacy)
    └── room_client.py       # ⭐ Kết nối lobby + room
```

**File quan trọng:**
- **`main-client.py`**: Entry point, khởi tạo Tkinter app
- **`auth_controller.py`**: Gửi auth requests qua `AuthClient` (không truy cập DB)
- **`main_controller.py`**: Xử lý tất cả logic: login, room, stats (qua networking)
- **`user_session.py`**: Class đơn giản lưu user info local (kế thừa dict)
- **`auth_client.py`**: Socket client riêng cho authentication
- **`room_client.py`**: Socket client cho lobby và room

---

## 💻 YÊU CẦU HỆ THỐNG

### Server cần:
- **Python 3.11+**
- **MySQL 8.0+** (hoặc MariaDB)
- **RAM**: 512MB+
- **OS**: Windows, Linux, macOS

### Client cần:
- **Python 3.11+**
- **RAM**: 256MB+
- **OS**: Windows (khuyến nghị), Linux, macOS
- **Màn hình**: 900x650 trở lên

---

## 📦 HƯỚNG DẪN CÀI ĐẶT

### Bước 1: Cài đặt Python
Tải Python 3.11+ từ: https://www.python.org/downloads/

### Bước 2: Cài đặt MySQL
Tải MySQL từ: https://dev.mysql.com/downloads/installer/

**Lưu ý:** Nhớ username, password khi cài đặt MySQL!

### Bước 3: Tạo Database

**Cách 1: Dùng MySQL Command Line**
```bash
mysql -u root -p
```
```sql
CREATE DATABASE battleship;
USE battleship;
SOURCE d:/Python/Game BattleShip/server/config/battleship.sql;
EXIT;
```

**Cách 2: Dùng phpMyAdmin hoặc MySQL Workbench**
1. Tạo database mới tên `battleship`
2. Import file `server/config/battleship.sql`

### Bước 4: Cấu hình Database

Sửa file `server/config/db_config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # ← Sửa username của bạn
    'password': 'your_password',  # ← Sửa password của bạn
    'database': 'battleship',
    'port': 3306,
}
```

### Bước 5: Cài đặt Dependencies

**Server:**
```bash
cd server
pip install -r requirements.txt
```

Dependencies: `mysql-connector-python`

**Client:**
```bash
cd client
pip install -r requirements.txt
```

Dependencies: `pygame`, `matplotlib`

---

## 🚀 HƯỚNG DẪN CHẠY GAME

### Bước 1: Chạy Server

```bash
cd server
python server.py
```

Cửa sổ server sẽ mở ra:
1. Click **"Start Server"**
2. Thấy status: "Room Server started on localhost:65432"
3. **ĐỂ CỬA SỔ NÀY MỞ** (không được tắt!)

### Bước 2: Chạy Client (Player 1)

**Mở terminal mới:**
```bash
cd client
python main-client.py
```

### Bước 3: Chạy Client (Player 2)

**Mở terminal thứ 3:**
```bash
cd client
python main-client.py
```

**Lưu ý quan trọng:**
- ✅ Server phải chạy TRƯỚC khi chạy client
- ✅ Để server running cả lúc chơi
- ✅ Chạy ít nhất 2 client để chơi multiplayer

---

## 🎮 CÁCH CHƠI

### 1. Đăng ký/Đăng nhập

**Đăng ký tài khoản mới:**
- Click "Register"
- Nhập username (3-50 ký tự)
- Nhập password (tối thiểu 6 ký tự)
- Click "Register"

**Đăng nhập:**
- Nhập username
- Nhập password
- Click "Login"

**Test accounts có sẵn:**
- `player1` / `123`
- `player2` / `123`

### 2. Tạo hoặc Vào Phòng

**Tạo phòng mới:**
- Click "Create Room"
- Nhập tên phòng (tùy chọn)
- Đợi người chơi thứ 2 join

**Vào phòng có sẵn:**
- Xem danh sách phòng
- Click "Join" phòng muốn vào
- Đợi host sẵn sàng

### 3. Đặt Tàu

**5 loại tàu:**
1. Battleship (Tàu chiến) - 5 ô
2. Cruiser (Tuần dương) - 4 ô
3. Destroyer 1 (Khu trục) - 3 ô
4. Destroyer 2 (Khu trục) - 3 ô
5. Plane (Máy bay) - 2 ô

**Cách đặt:**
- Kéo thả tàu lên lưới 10x10
- Xoay tàu: Nhấn phím **R**
- Đặt tự động: Click "Auto Place"
- Xong thì click "Lock Ships"

### 4. Chiến Đấu

**Luật chơi:**
- 2 người chơi luân phiên bắn
- Click vào ô trên lưới đối thủ để bắn
- 🔴 Đỏ = Trúng tàu (Hit)
- ⚪ Trắng = Trượt (Miss)
- Đánh chìm hết tàu của đối thủ = Thắng!

**Hiển thị:**
- **Lưới bên trái**: Tàu của bạn
- **Lưới bên phải**: Bắn vào đối thủ
- **Timer**: Thời gian còn lại của lượt
- **Stats**: Số tàu còn lại, hits/misses

### 5. Kết Thúc Trận

**Sau khi thắng/thua:**
- Xem thống kê chi tiết
- Accuracy (độ chính xác)
- Số tàu đánh chìm
- Longest streak (chuỗi trúng dài nhất)

**Stats được lưu vào database!**

### 6. Xem Thống Kê

**Trong Home:**
- Click "View Statistics"
- Xem tổng số trận, tỷ lệ thắng
- Xem lịch sử trận đấu gần đây
- Biểu đồ thống kê

---

## 🔄 LUỒNG HOẠT ĐỘNG CHI TIẾT

### 📡 CƠ CHẾ TRUYỀN DỮ LIỆU (Network Protocol)

#### **1. Datagram Format - Giao thức tự định nghĩa**

Game sử dụng **TCP Socket** với **datagram format** cố định:

```python
# Hằng số quan trọng
BUFFER_SIZE = 4096  # Mỗi message đúng 4096 bytes
PADDING_CHAR = '*'  # Ký tự padding

# Cấu trúc Datagram:
[PADDING (****...)][JSON DATA]
←─── BUFFER_SIZE (4096 bytes) ───→

# Ví dụ:
"**************************{'request': 'attack_tile', 'position': (5, 7)}"
│                          │
│← Padding (26 chars)      │← JSON data (70 chars)
│                          │
└────────── Total: 4096 bytes ──────────┘
```

**Tại sao dùng Datagram Format?**
- ✅ **Kích thước cố định**: Dễ đọc/ghi qua socket
- ✅ **Tránh粘包 (packet sticking)**: Biết rõ ranh giới message
- ✅ **Thread-safe**: Mỗi send/recv là 1 đơn vị hoàn chỉnh
- ✅ **Đơn giản**: Không cần header phức tạp như HTTP

#### **2. Encoding/Decoding Process**

**ENCODING (Client → Server):**
```python
# Bước 1: Chuẩn bị data
data = {
    'request': 'attack_tile',
    'position': (5, 7)
}

# Bước 2: Chuyển thành JSON string
json_str = json.dumps(data)  # → '{"request": "attack_tile", "position": [5, 7]}'

# Bước 3: Tính padding
padding_size = BUFFER_SIZE - len(json_str)  # → 4096 - 54 = 4042

# Bước 4: Thêm padding
datagram = ('*' * padding_size) + json_str  # → '****...****{"request":...}'

# Bước 5: Encode UTF-8
bytes_data = datagram.encode('utf-8')  # → b'****...****{"request":...}'

# Bước 6: Gửi qua socket
socket.sendall(bytes_data)
```

**DECODING (Server → Client):**
```python
# Bước 1: Nhận data từ socket
bytes_data = socket.recv(BUFFER_SIZE)  # → b'****...****{"request":...}'

# Bước 2: Decode UTF-8
datagram = bytes_data.decode('utf-8')  # → '****...****{"request":...}'

# Bước 3: Xóa padding
json_str = datagram.replace('*', '')  # → '{"request": "attack_tile", ...}'

# Bước 4: Parse JSON
data = json.loads(json_str)  # → {'request': 'attack_tile', 'position': [5, 7]}

# Bước 5: Xử lý request
response = process_request(data)
```

#### **3. Request/Response Pattern**

**Synchronous Request-Response** (Đồng bộ):
```
CLIENT                                SERVER
  │                                     │
  │ 1. Tạo request dict                 │
  │ 2. Encode → datagram                │
  │ 3. socket.sendall()                 │
  ├────────────────────────────────────►│ 4. socket.recv()
  │                                     │ 5. Decode → dict
  │                                     │ 6. Xử lý logic
  │                                     │ 7. Tạo response
  │                                     │ 8. Encode → datagram
  │ 11. socket.recv()                   │ 9. socket.sendall()
  │◄────────────────────────────────────┤
  │ 12. Decode → dict                   │
  │ 13. Sử dụng response                │
  ▼                                     ▼
```

**Ví dụ cụ thể - Attack Tile:**
```python
# === CLIENT SIDE ===
# Gửi request
request = {
    'request': 'attack_tile',
    'position': (5, 7)
}
datagram = create_datagram(BUFFER_SIZE, request)
socket.sendall(datagram)

# Chờ response
response_data = socket.recv(BUFFER_SIZE)
response = decode_data(response_data)
# response = {'attacked': 'battleship'} hoặc {'attacked': None}

# === SERVER SIDE ===
# Nhận request
request_data = socket.recv(BUFFER_SIZE)
request = decode_data(request_data)

# Xử lý
position = request['position']  # (5, 7)
enemy_grid = get_enemy_grid()
ship_name = enemy_grid[position[0]][position[1]]  # 'battleship' hoặc None

# Gửi response
response = {'attacked': ship_name}
datagram = create_datagram(BUFFER_SIZE, response)
socket.sendall(datagram)
```

---

### 🔐 LUỒNG AUTHENTICATION (Đăng nhập/Đăng ký)

#### **Bước 1: Client gửi Auth Request**

```
[CLIENT - AuthClient.py]
     │
     │ 1. User nhập username + password
     │    → Tkinter LoginView
     │
     │ 2. Click "Login" button
     │    → auth_controller.login()
     │
     │ 3. Tạo AuthClient()
     │    → Kế thừa Network class
     │
     │ 4. Tạo request dict
     ├─── request = {
     │        'action': 'auth:login',
     │        'username': 'player1',
     │        'password': '123'
     │    }
     │
     │ 5. Encode → Datagram
     │    → create_datagram(4096, request)
     │
     │ 6. Tạo socket TẠM THỜI
     │    → socket.socket(AF_INET, SOCK_STREAM)
     │    → socket.connect(('localhost', 65432))
     │
     │ 7. Gửi datagram
     │    → socket.sendall(datagram)
     │
     │ 8. Chờ response (BLOCKING)
     │    → response = socket.recv(4096)
     │
     │ 9. Đóng socket ngay
     │    → socket.close()
     │
     ▼
```

#### **Bước 2: Server xử lý Authentication**

```
[SERVER - RoomServer.py]
     │
     │ 1. Accept connection
     │    → client_socket, addr = server_socket.accept()
     │
     │ 2. Tạo thread xử lý
     │    → Thread(target=handle_client)
     │
     │ 3. Nhận data đầu tiên
     │    → data = client_socket.recv(4096)
     │
     │ 4. Decode request
     │    → request = decode_data(data)
     │
     │ 5. Kiểm tra action
     │    → action = request.get('action')
     │    → if action.startswith('auth:'):
     │
     │ 6. Gọi handle_auth_request()
     │    ├─── action = 'auth:login'
     │    ├─── username = 'player1'
     │    └─── password = '123'
     │
     │ 7. Query database
     │    [user_model.py]
     │    │
     │    ├─ SQL Query:
     │    │  SELECT id, username, is_online
     │    │  FROM users
     │    │  WHERE username = ? AND password = ?
     │    │
     │    ├─ Kiểm tra kết quả:
     │    │  • Nếu NULL → Sai username/password
     │    │  • Nếu is_online = 1 → Đã đăng nhập
     │    │  • Nếu OK → Tiếp tục
     │    │
     │    ├─ Tính stats từ game_history:
     │    │  SELECT 
     │    │    COUNT(*) as total_games,
     │    │    SUM(result='win') as wins,
     │    │    SUM(result='loss') as losses
     │    │  FROM game_history
     │    │  WHERE player_id = ?
     │    │
     │    └─ Set is_online = 1:
     │       UPDATE users SET is_online = 1 WHERE id = ?
     │
     │ 8. Tạo response
     │    response = {
     │        'success': True,
     │        'message': 'Login successful',
     │        'user': {
     │            'id': 1,
     │            'username': 'player1',
     │            'total_games': 10,
     │            'total_wins': 7,
     │            'total_losses': 3,
     │            'win_rate': 70.0,
     │            'avg_accuracy': 65.5
     │        }
     │    }
     │
     │ 9. Encode → Datagram
     │    → datagram = create_datagram(4096, response)
     │
     │ 10. Gửi response
     │    → client_socket.sendall(datagram)
     │
     │ 11. Đóng connection auth
     │    → client_socket.close()
     │
     ▼
```

#### **Bước 3: Client xử lý Response**

```
[CLIENT]
     │
     │ 1. Nhận response từ AuthClient
     │    → response = auth_client.send_auth_request()
     │
     │ 2. Kiểm tra success
     │    → if response['success']:
     │
     │ 3. Lưu UserSession (local, không DB)
     │    [user_session.py]
     │    │
     │    └─ user = UserSession({
     │           'id': 1,
     │           'username': 'player1',
     │           'total_games': 10,
     │           ...
     │       })
     │
     │ 4. Kết nối tới Lobby
     │    [room_client.py]
     │    │
     │    ├─ socket = socket.socket(AF_INET, SOCK_STREAM)
     │    ├─ socket.connect(('localhost', 65432))
     │    │
     │    ├─ Gửi lobby connection:
     │    │  {
     │    │    'username': 'player1',
     │    │    'room_id': None  ← Lobby mode
     │    │  }
     │    │
     │    └─ GIỮ socket này MỞ để nhận updates
     │
     │ 5. Chuyển màn hình
     │    → show_home_view()
     │    → Hiển thị "Welcome, player1!"
     │
     ▼
```

**Đặc điểm Authentication:**
- ✅ **Stateless**: Mỗi request tạo socket mới
- ✅ **Fast**: Không giữ connection lâu
- ✅ **Secure**: Password kiểm tra server-side
- ⚠️ **TODO**: Hash passwords (hiện tại plain text)

---

### 🏠 LUỒNG ROOM MANAGEMENT (Quản lý phòng)

#### **Kết nối Lobby (Persistent Connection)**

```
[CLIENT]                                [SERVER]
     │                                      │
     │ 1. Tạo RoomClient(username, None)    │
     │    room_id = None → Lobby mode       │
     │                                      │
     │ 2. connect_to_server()               │
     │    socket.connect(localhost:65432)   │
     ├─────────────────────────────────────►│ 3. Accept connection
     │                                      │    Thread(handle_client)
     │                                      │
     │ 4. Gửi connection_data               │
     ├─ {                                   │
     │    'username': 'player1',            │
     │    'room_id': None  ← LOBBY          │
     │  }                                   │
     ├─────────────────────────────────────►│ 5. Nhận connection_data
     │                                      │    room_id = None
     │                                      │    → in_lobby = True
     │                                      │
     │                                      │ 6. Add vào lobby_clients:
     │                                      │    lobby_clients['player1'] = socket
     │                                      │
     │ 7. Nhận ACK                          │ 8. Gửi ACK
     │◄─────────────────────────────────────┤─ {'status': 'connected'}
     │                                      │
     │ 9. Vào lobby_listener loop           │ 10. Vào lobby_listener()
     │    GIỮ socket MỞ để:                 │     Lắng nghe requests:
     │    • List rooms                      │     • get_rooms
     │    • Create room                     │     • create_room
     │    • Get stats                       │     • get_user_stats
     │                                      │     • auth:logout
     │                                      │
     └──────────────────────────────────────┴──────────────────────
                   ↓
         Connection vẫn MỞ suốt trong Lobby
```

#### **Tạo Phòng (Create Room)**

```
[CLIENT]                                [SERVER]
     │                                      │
     │ 1. User click "Create Room"          │
     │    → room_controller.create_room()   │
     │                                      │
     │ 2. Gửi request qua lobby socket      │
     ├─ {                                   │
     │    'request': 'create_room',         │
     │    'room_name': "Player1's Room"     │
     │  }                                   │
     ├─────────────────────────────────────►│ 3. Nhận request
     │                                      │    trong lobby_listener()
     │                                      │
     │                                      │ 4. Tạo GameRoom object:
     │                                      │    room = GameRoom(
     │                                      │        room_id = next_room_id,
     │                                      │        room_name = "...",
     │                                      │        host = 'player1',
     │                                      │        status = waiting
     │                                      │    )
     │                                      │
     │                                      │ 5. Add vào rooms dict:
     │                                      │    rooms[room_id] = room
     │                                      │
     │ 6. Nhận response                     │ 7. Gửi response
     │◄─────────────────────────────────────┤─ {
     │    'success': True,                  │      'room_id': 1,
     │    'room_id': 1                      │      'room_name': "..."
     │                                      │    }
     │ 8. Disconnect lobby socket           │
     │    lobby_client.disconnect()         │ 9. Remove from lobby_clients
     │                                      │    lobby_clients.pop('player1')
     │                                      │
     │ 10. Tạo RoomClient mới               │
     │     room_client = RoomClient(        │
     │         username='player1',          │
     │         room_id=1  ← Room mode       │
     │     )                                │
     │                                      │
     │ 11. Connect to room                  │
     ├─────────────────────────────────────►│ 12. Accept new connection
     │    {'username': 'player1',           │     Thread(handle_client)
     │     'room_id': 1}                    │
     │                                      │ 13. room.add_client()
     │                                      │     • Thêm vào game_data
     │                                      │     • is_first_player = True
     │                                      │     • my_turn = True
     │                                      │
     │ 14. Vào room_lobby_view              │
     │     Hiển thị: "Waiting for opponent" │
     │                                      │
     └──────────────────────────────────────┘
```

#### **Tham gia Phòng (Join Room)**

```
[CLIENT 2]                              [SERVER]
     │                                      │
     │ 1. List rooms qua lobby              │
     ├─ {'request': 'get_rooms'}            │
     ├─────────────────────────────────────►│ 2. Query rooms dict
     │                                      │    return [{
     │◄─────────────────────────────────────┤      'room_id': 1,
     │    {'rooms': [...]}                  │      'room_name': "...",
     │                                      │      'players': 1/2
     │                                      │    }]
     │ 2. User click "Join Room 1"          │
     │                                      │
     │ 3. Disconnect lobby                  │
     │    Connect to room với room_id=1     │
     ├─────────────────────────────────────►│ 4. Accept connection
     │    {'username': 'player2',           │    Thread(handle_client)
     │     'room_id': 1}                    │
     │                                      │ 5. room.add_client()
     │                                      │    • Thêm player2
     │                                      │    • is_first_player = False
     │                                      │    • my_turn = False
     │                                      │    • players count = 2
     │                                      │
     │                                      │ 6. Update room status:
     │                                      │    status = ship_lock
     │                                      │
     │ 7. Cả 2 clients nhận update          │ 8. Broadcast to all:
     │◄─────────────────────────────────────┤    "Room full - Start!"
     │                                      │
     │ 9. Chuyển sang Ship Placement        │
     │                                      │
     └──────────────────────────────────────┘
```

---

### ⚔️ LUỒNG BATTLE (Chiến đấu chi tiết)

#### **Giai đoạn 1: Ship Placement**

```
[PLAYER 1]                              [SERVER]                              [PLAYER 2]
     │                                      │                                      │
     │ 1. Đặt 5 tàu lên grid 10x10          │                                      │ 1. Đặt tàu
     │    • Kéo thả hoặc Auto Place         │                                      │
     │    • Xoay tàu bằng phím R            │                                      │
     │                                      │                                      │
     │ 2. Click "Lock Ships"                │                                      │ 2. Click "Lock Ships"
     │                                      │                                      │
     │ 3. Gửi ship_locked request           │                                      │ 3. Gửi request
     ├─ {                                   │                                      │
     │    'request': 'ship_locked',         │                                      │
     │    'grid': [                         │                                      │
     │      ['', '', 'battleship', ...],    │                                      │
     │      ['cruiser', '', '', ...],       │                                      │
     │      ...                             │                                      │
     │    ]                                 │                                      │
     │  }                                   │                                      │
     ├─────────────────────────────────────►│ 4. Lưu grid của P1                   │
     │                                      │    game_data['game_grid']['player1']  │
     │                                      │    clients['player1']['ship_locked'] = True
     │                                      │                                      │
     │                                      │◄─────────────────────────────────────┤ 5. Lưu grid của P2
     │                                      │    game_data['game_grid']['player2']  │
     │                                      │    clients['player2']['ship_locked'] = True
     │                                      │                                      │
     │                                      │ 6. Check: Cả 2 đã lock?              │
     │                                      │    → YES!                            │
     │                                      │                                      │
     │                                      │ 7. Update room status:               │
     │                                      │    status = GameStatus.battle        │
     │                                      │                                      │
     │                                      │ 8. Random người đi trước:            │
     │                                      │    clients['player1']['my_turn'] = True
     │                                      │    clients['player2']['my_turn'] = False
     │                                      │                                      │
     │ 9. Nhận game_data, thấy status=battle│                                      │ 9. Nhận update
     │    → Chuyển sang BattleView          │                                      │    → Chuyển BattleView
     │    → Timer bắt đầu: 30s              │                                      │    → Hiển thị "Waiting"
     │                                      │                                      │
     └──────────────────────────────────────┴──────────────────────────────────────┘
```

#### **Giai đoạn 2: Battle Loop (Game Play)**

```
GAME LOOP (30 FPS) - Chạy trên cả 2 clients

┌──────────────────────────────────────────────────────────────────┐
│                      FRAME 1-900 (30 giây)                       │
└──────────────────────────────────────────────────────────────────┘

[PLAYER 1 - MY TURN]                   [SERVER]                   [PLAYER 2 - WAITING]
     │                                      │                            │
     │ 1. Mỗi frame (1/30s):                │                            │ 1. Mỗi frame:
     │    • Render grids                    │                            │    • Render grids
     │    • Update timer: 30→29→28...       │                            │    • Hiển thị "Enemy's turn"
     │    • Chờ user click                  │                            │    • Poll game_data
     │                                      │                            │
     │ 2. User click ô (5, 7)               │                            │
     │    Validation:                       │                            │
     │    • my_turn == True? ✓              │                            │
     │    • Ô chưa bắn? ✓                   │                            │
     │                                      │                            │
     │ 3. Gửi attack request                │                            │
     ├─ {                                   │                            │
     │    'request': 'attack_tile',         │                            │
     │    'position': (5, 7)                │                            │
     │  }                                   │                            │
     ├─────────────────────────────────────►│ 4. Nhận attack              │
     │                                      │    • Lấy grid của player2   │
     │                                      │    • Check grid[5][7]       │
     │                                      │    • ship = 'battleship'    │
     │                                      │                            │
     │                                      │ 5. Xử lý hit:              │
     │                                      │    • Đánh dấu ô đã bị bắn  │
     │                                      │    • Check tàu chìm:       │
     │                                      │      count hits on 'battleship'
     │                                      │      if hits == 5:         │
     │                                      │        ship_sunk = True    │
     │                                      │                            │
     │                                      │ 6. Quyết định turn:        │
     │                                      │    • HIT → Giữ lượt P1     │
     │                                      │    • MISS → Chuyển cho P2  │
     │                                      │                            │
     │ 7. Nhận response                     │ 8. Gửi response            │
     │◄─────────────────────────────────────┤─ {                         │
     │    {                                 │      'attacked': 'battleship',
     │      'attacked': 'battleship',       │      'ship_sunk': True,    │
     │      'ship_sunk': True               │      'keep_turn': True     │
     │    }                                 │    }                       │
     │                                      │                            │
     │ 9. Hiển thị kết quả:                 │                            │ 10. Poll thấy attack:
     │    • Mark ô (5,7) đỏ = HIT           │                            │     • Update my_grid
     │    • Hiệu ứng nổ 💥                  │                            │     • Ô (5,7) bị hit
     │    • "Battleship sunk!"              │                            │     • Hiệu ứng lửa 🔥
     │    • Sound effect                    │                            │     • Thông báo sunk
     │    • Reset timer = 30s               │                            │
     │    • Giữ lượt (my_turn = True)       │                            │
     │                                      │                            │
     │ 11. Tiếp tục click ô khác...         │                            │ 12. Vẫn đợi...
     │                                      │                            │
     └──────────────────────────────────────┴────────────────────────────┘

── CẢ 2 PLAYERS SYNC LIÊN TỤC QUA game_data ──

Mỗi frame, cả 2 đều gửi: {'request': 'game_data'}
Response chứa:
{
    'player1': {
        'my_turn': True/False,
        'timeout_count': 0,
        'sinked_ships': 2,
        'attacked_tile': {'position': (5,7), 'ship_name': 'battleship'}
    },
    'player2': {...}
}
```

#### **Giai đoạn 3: Win Condition**

```
[PLAYER 1]                              [SERVER]                              [PLAYER 2]
     │                                      │                                      │
     │ Đã chìm 5 tàu của địch               │                                      │
     │                                      │                                      │
     │ Gửi ship_sinked (lần thứ 5)         │                                      │
     ├─────────────────────────────────────►│ Check:                               │
     │                                      │ sinked_ships == 5?                   │
     │                                      │ → YES!                               │
     │                                      │                                      │
     │                                      │ Gọi room.game_over('player2')        │
     │                                      │ • winner = 'player1'                 │
     │                                      │ • status = finished                  │
     │                                      │                                      │
     │                                      │ Lưu vào database:                    │
     │                                      │ INSERT INTO game_history             │
     │                                      │ • player1: result='win'              │
     │                                      │ • player2: result='loss'             │
     │                                      │ • stats: hits, misses, ships_sunk    │
     │                                      │                                      │
     │ Poll thấy winner                     │                                      │ Poll thấy winner
     │◄─────────────────────────────────────┼─────────────────────────────────────►│
     │   {'winner': 'player1'}              │                                      │ {'winner': 'player1'}
     │                                      │                                      │
     │ Hiển thị: "🏆 YOU WON!"              │                                      │ Hiển thị: "💀 YOU LOST"
     │ • Fireworks effect                   │                                      │ • Fade to gray
     │ • Victory sound                      │                                      │ • Sad sound
     │ • Show stats                         │                                      │ • Show stats
     │                                      │                                      │
     │ Disconnect                           │                                      │ Disconnect
     │ → Back to Home                       │                                      │ → Back to Home
     │                                      │                                      │
     └──────────────────────────────────────┴──────────────────────────────────────┘
```

---

### ⏰ CƠ CHẾ TIMEOUT CHI TIẾT

```
┌────────────────────────────────────────────────────────────┐
│            TIMEOUT MECHANISM (30 giây/lượt)                │
└────────────────────────────────────────────────────────────┘

[CLIENT]                                   [SERVER]
    │                                          │
    │ 1. Bắt đầu lượt                          │
    │    turn_start = pygame.time.get_ticks()  │
    │    TURN_TIME = 30                        │
    │                                          │
    │ 2. Mỗi frame (1/30s):                    │
    │    elapsed = (now - turn_start) / 1000   │
    │    time_remaining = 30 - elapsed         │
    │                                          │
    │    if time_remaining <= 10:              │
    │      # Cảnh báo: Timer đỏ nhấp nháy      │
    │                                          │
    │    if time_remaining <= 0:               │
    │      # HẾT GIỜ!                          │
    │                                          │
    │ 3. Gửi timeout request                   │
    ├─ {'request': 'timeout'}                  │
    ├───────────────────────────────────────────►│ 4. Xử lý timeout:
    │                                          │    • timeout_count += 1
    │                                          │    • Switch turn
    │                                          │    • Reset timer
    │                                          │
    │                                          │ 5. Check: timeout_count >= 3?
    │                                          │    → Thua game! (quá nhiều timeout)
    │                                          │    → winner = đối thủ
    │                                          │
    │ 6. Nhận response                         │
    │◄──────────────────────────────────────────┤ {'timeout_count': 1}
    │                                          │
    │ 7. Hiển thị:                             │
    │    "⏰ Time's up! Turn switched"         │
    │    "Timeouts: 1/3"                       │
    │                                          │
    └──────────────────────────────────────────┘

**Timeout Rules:**
• Mỗi lượt có 30 giây
• Timeout 3 lần → Thua game
• Timeout reset về 0 khi thắng game
• Timer reset khi: attack, switch turn, game start
```

---

### 💾 DATABASE INTERACTION (Tương tác cơ sở dữ liệu)

#### **Schema - Cấu trúc bảng**

```sql
-- Bảng users: Lưu tài khoản
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- ⚠️ Plain text (TODO: hash)
    is_online TINYINT DEFAULT 0,      -- 0=offline, 1=online
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng game_history: Lưu lịch sử trận đấu
CREATE TABLE game_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,           -- FK → users.id
    opponent_id INT NOT NULL,         -- FK → users.id
    result ENUM('win', 'loss'),       -- Kết quả
    ships_sunk INT DEFAULT 0,         -- Số tàu đánh chìm
    hits INT DEFAULT 0,               -- Số phát trúng
    misses INT DEFAULT 0,             -- Số phát trượt
    accuracy DECIMAL(5,2),            -- Độ chính xác (%)
    max_streak INT DEFAULT 0,         -- Chuỗi trúng dài nhất
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES users(id),
    FOREIGN KEY (opponent_id) REFERENCES users(id)
);
```

#### **Query Flow - Login**

```
[CLIENT]                     [SERVER]                      [DATABASE]
    │                            │                              │
    │ Login request              │                              │
    ├───────────────────────────►│ 1. UserModel.authenticate()  │
    │   username='player1'       │                              │
    │   password='123'           │ 2. Query users table         │
    │                            ├─────────────────────────────►│
    │                            │   SELECT id, username        │
    │                            │   FROM users                 │
    │                            │   WHERE username='player1'   │
    │                            │   AND password='123'         │
    │                            │                              │
    │                            │◄─────────────────────────────┤
    │                            │   Result: {id:1, ...}        │
    │                            │                              │
    │                            │ 3. Calculate stats           │
    │                            ├─────────────────────────────►│
    │                            │   SELECT                     │
    │                            │     COUNT(*) as total_games, │
    │                            │     SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) as wins,
    │                            │     SUM(CASE WHEN result='loss' THEN 1 ELSE 0 END) as losses,
    │                            │     SUM(ships_sunk) as total_ships,
    │                            │     SUM(hits) as total_hits  │
    │                            │   FROM game_history          │
    │                            │   WHERE player_id = 1        │
    │                            │                              │
    │                            │◄─────────────────────────────┤
    │                            │   Stats data                 │
    │                            │                              │
    │                            │ 4. Set online                │
    │                            ├─────────────────────────────►│
    │                            │   UPDATE users               │
    │                            │   SET is_online = 1          │
    │                            │   WHERE id = 1               │
    │                            │                              │
    │◄───────────────────────────┤ 5. Response                  │
    │   {success: True,          │                              │
    │    user: {...stats...}}    │                              │
    │                            │                              │
    └────────────────────────────┴──────────────────────────────┘
```

#### **Query Flow - Save Game Result**

```
[SERVER]                                              [DATABASE]
    │                                                     │
    │ Game finished: player1 won vs player2              │
    │                                                     │
    │ 1. Collect stats from game_data:                   │
    │    • Player1: ships=5, hits=35, misses=20          │
    │    • Player2: ships=3, hits=28, misses=25          │
    │                                                     │
    │ 2. Calculate accuracy:                             │
    │    accuracy = hits / (hits + misses) * 100         │
    │    P1: 35/(35+20) = 63.6%                          │
    │    P2: 28/(28+25) = 52.8%                          │
    │                                                     │
    │ 3. Insert winner record                            │
    ├────────────────────────────────────────────────────►│
    │   INSERT INTO game_history                         │
    │   (player_id, opponent_id, result,                 │
    │    ships_sunk, hits, misses, accuracy, max_streak) │
    │   VALUES                                            │
    │   (1, 2, 'win', 5, 35, 20, 63.6, 8)                │
    │                                                     │
    │ 4. Insert loser record                             │
    ├────────────────────────────────────────────────────►│
    │   INSERT INTO game_history                         │
    │   (player_id, opponent_id, result,                 │
    │    ships_sunk, hits, misses, accuracy, max_streak) │
    │   VALUES                                            │
    │   (2, 1, 'loss', 3, 28, 25, 52.8, 5)               │
    │                                                     │
    │◄────────────────────────────────────────────────────┤
    │   Success                                           │
    │                                                     │
    │ 5. Set both players offline                        │
    ├────────────────────────────────────────────────────►│
    │   UPDATE users SET is_online = 0                   │
    │   WHERE id IN (1, 2)                               │
    │                                                     │
    └─────────────────────────────────────────────────────┘
```

---

### 🔒 NGUYÊN TẮC BẢO MẬT VÀ THREAD-SAFETY

#### **1. Thread-Safety với Lock**

```python
# Server sử dụng threading.Lock() để tránh race condition

class GameRoom:
    def __init__(self):
        self.lock = Lock()  # ← Khóa thread
        self.game_data = {}
    
    def add_client(self, username):
        with self.lock:  # ← Acquire lock tự động
            # Code trong này là thread-safe
            self.game_data['clients'][username] = {...}
            # Khi thoát block, lock tự động release
    
    def attack_enemy_tile(self, username, position):
        with self.lock:
            # Chỉ 1 thread được thực thi tại 1 thời điểm
            enemy_grid = self.get_enemy_grid(username)
            ship_name = enemy_grid[position[0]][position[1]]
            return ship_name
```

**Tại sao cần Lock?**
- ✅ **Multi-threaded server**: Mỗi client = 1 thread riêng
- ✅ **Shared data**: `game_data` được truy cập bởi nhiều threads
- ✅ **Tránh corruption**: Không cho 2 threads sửa cùng data cùng lúc
- ✅ **Atomic operations**: Đảm bảo operation hoàn thành trước khi thread khác vào

#### **2. Validation Rules**

```python
# CLIENT-SIDE Validation (UX)
def on_enemy_grid_click(row, col):
    # 1. Kiểm tra có phải lượt mình?
    if not my_turn:
        show_message("Wait for your turn!")
        return
    
    # 2. Ô này đã bắn chưa?
    if enemy_hits[row][col] or enemy_misses[row][col]:
        show_message("Already attacked!")
        return
    
    # 3. OK → Gửi request
    attack_tile(row, col)

# SERVER-SIDE Validation (Security)
def process_attack(username, position):
    with self.lock:
        # 1. Kiểm tra có phải lượt người này?
        if not game_data['clients'][username]['my_turn']:
            return {'error': 'Not your turn'}
        
        # 2. Kiểm tra position hợp lệ?
        row, col = position
        if not (0 <= row < 10 and 0 <= col < 10):
            return {'error': 'Invalid position'}
        
        # 3. Xử lý attack
        enemy_grid = get_enemy_grid(username)
        ship_name = enemy_grid[row][col]
        
        # 4. Update state
        if ship_name:
            # Hit - giữ lượt
            pass
        else:
            # Miss - đổi lượt
            switch_turn(username)
        
        return {'attacked': ship_name}
```

#### **3. Error Handling**

```python
# Graceful disconnect handling
def client_listener(socket, username, room):
    socket.settimeout(1.0)  # 1s timeout
    
    try:
        while True:
            try:
                data = socket.recv(BUFFER_SIZE)
                if not data:
                    # Client đóng connection
                    logging.info(f'{username} disconnected')
                    break
                
                # Xử lý request...
                
            except socket.timeout:
                # Timeout bình thường, tiếp tục loop
                continue
                
    except socket.error as e:
        logging.error(f'{username} error: {e}')
    
    finally:
        # Cleanup: Luôn được thực thi
        room.remove_client(username)
        if room.is_empty():
            delete_room(room.room_id)
```

**Error Recovery:**
- ✅ **Client disconnect**: Đối thủ tự động thắng
- ✅ **Server crash**: Client hiển thị "Connection lost"
- ✅ **Database error**: Trả về error message, không crash
- ✅ **Invalid data**: Validation trước khi xử lý

---

### 📊 PERFORMANCE CONSIDERATIONS

#### **Network Optimization**

```
Tần suất gửi request:

1. BATTLE LOOP: 30 FPS (mỗi frame)
   └─ get_game_data(): Sync state
      • 30 requests/giây × 2 players = 60 req/s
      • Payload: ~500 bytes
      • Bandwidth: ~30 KB/s (rất nhẹ)

2. ON-DEMAND: Khi có event
   └─ attack_tile(): Khi user click
   └─ ship_locked(): 1 lần setup
   └─ timeout(): Mỗi 30s nếu AFK

→ Tổng: ~60-100 requests/giây cho 1 phòng
→ Với 10 phòng: ~1000 req/s (server handle được)
```

#### **Database Optimization**

```sql
-- Index để tăng tốc queries
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_player_id ON game_history(player_id);
CREATE INDEX idx_played_at ON game_history(played_at DESC);

-- Query với LIMIT để tránh load quá nhiều
SELECT * FROM game_history 
WHERE player_id = ? 
ORDER BY played_at DESC 
LIMIT 20;  -- Chỉ lấy 20 trận gần nhất

-- Aggregate stats 1 lần thay vì nhiều queries
SELECT 
    COUNT(*) as total_games,
    SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) as wins,
    AVG(accuracy) as avg_accuracy
FROM game_history 
WHERE player_id = ?;
```

---

## 🎯 TÓM TẮT CÁC ĐIỂM QUAN TRỌNG

### Datagram Protocol
- ✅ Cố định 4096 bytes mỗi message
- ✅ Padding bằng `*` để đủ kích thước
- ✅ JSON format cho dễ debug và extend

### Authentication
- ✅ Stateless: Mỗi auth request = 1 socket mới
- ✅ Password plain text (TODO: hash)
- ✅ Stats tính real-time từ game_history

### Room Management
- ✅ Lobby connection: Persistent socket
- ✅ Room connection: Mỗi phòng = 1 socket riêng
- ✅ Thread-safe với Lock()

### Battle Mechanics
- ✅ 30 FPS game loop
- ✅ Sync state qua get_game_data()
- ✅ Hit = giữ lượt, Miss = đổi lượt
- ✅ 30s/lượt, timeout 3 lần = thua

### Database
- ✅ MySQL với 2 bảng: users, game_history
- ✅ Stats tính từ game_history (không có cột wins/losses trong users)
- ✅ Index cho performance

### Error Handling
- ✅ Graceful disconnect
- ✅ Validation client & server
- ✅ Timeout mechanism
- ✅ Thread-safe operations

---

## 🛠️ TROUBLESHOOTING

### Lỗi thường gặp

#### 1. Server không start được

**Lỗi:** `Error creating connection pool`

**Nguyên nhân:** Không kết nối được MySQL

**Giải pháp:**
```bash
# Kiểm tra MySQL đang chạy
# Windows:
services.msc → Tìm MySQL → Start

# Linux:
sudo systemctl start mysql

# Kiểm tra config
server/config/db_config.py
# Sửa username, password cho đúng
```

#### 2. Client lỗi "Connection refused"

**Nguyên nhân:** Server chưa chạy hoặc sai port

**Giải pháp:**
1. Đảm bảo server đang running
2. Kiểm tra port trong `networking/constants.py`
3. Kiểm tra firewall không block port 65432

#### 3. Đăng nhập không được

**Lỗi:** `Invalid username or password`

**Nguyên nhân:** Password trong DB là plain text

**Giải pháp:**
- Dùng accounts test: `player1` / `123`
- Hoặc đăng ký tài khoản mới

#### 4. Client lỗi "No module named 'pygame'"

**Giải pháp:**
```bash
cd client
pip install pygame matplotlib
```

#### 5. Lỗi JSON serialization

**Lỗi:** `Object of type datetime/Decimal is not JSON serializable`

**Nguyên nhân:** Server trả về datetime hoặc Decimal

**Giải pháp:** 
- Code đã xử lý trong `user_model.py`
- Nếu vẫn lỗi, restart server

#### 6. Không tìm thấy assets

**Lỗi:** `No such file or directory: 'assets/...'`

**Nguyên nhân:** Chạy client từ sai thư mục

**Giải pháp:**
```bash
# Phải chạy từ thư mục client
cd client
python main-client.py

# KHÔNG phải
cd D:\Python\Game BattleShip
python client\main-client.py  # ← SAI!
```

---

## ✨ TÍNH NĂNG

### Đã hoàn thành ✅

- [x] Kiến trúc Client-Server riêng biệt
- [x] Authentication (Login/Register)
- [x] Multi-room support (nhiều phòng cùng lúc)
- [x] Room management (create, join, leave)
- [x] Ship placement (drag & drop, auto-place)
- [x] Turn-based combat system
- [x] Real-time game state sync
- [x] Hit/Miss detection with animation
- [x] Game history tracking
- [x] User statistics (wins, losses, accuracy)
- [x] Recent games history
- [x] Win streak tracking
- [x] Opponent stats display
- [x] Online/Offline status
- [x] Auto-disconnect handling

### Có thể cải tiến 🔮

- [ ] Hash passwords (hiện tại plain text)
- [ ] Chat trong phòng
- [ ] Spectator mode (xem người khác chơi)
- [ ] Matchmaking tự động
- [ ] Replay system
- [ ] Leaderboard (bảng xếp hạng)
- [ ] Achievements (thành tựu)
- [ ] Sound effects đầy đủ
- [ ] Deploy server lên cloud (AWS, Azure)
- [ ] Web-based client (HTML5 Canvas)

---

## 📞 HỖ TRỢ

**Nếu gặp vấn đề:**

1. **Check logs:**
   - Server: Xem terminal đang chạy server
   - Client: Xem terminal đang chạy client

2. **Restart:**
   - Đóng tất cả client
   - Stop server → Start server
   - Chạy lại client

3. **Reset database:**
   ```sql
   UPDATE users SET is_online = 0;
   ```

4. **Clear Python cache:**
   ```bash
   # Windows
   del /s /q __pycache__
   del /s /q *.pyc
   
   # Linux/macOS
   find . -type d -name __pycache__ -exec rm -r {} +
   ```

---

## 🎓 KẾT LUẬN

Bạn đã có trong tay một game Battleship multiplayer hoàn chỉnh với kiến trúc Client-Server chuẩn mực!

**Điểm mạnh của kiến trúc này:**
- ✅ Tách biệt rõ ràng giữa frontend (Client) và backend (Server)
- ✅ Client không cần quan tâm database, chỉ lo giao diện
- ✅ Server xử lý tất cả logic và lưu trữ
- ✅ Dễ dàng mở rộng: thêm tính năng, nhiều room, nhiều client
- ✅ Bảo mật: credentials chỉ ở server

**Chúc bạn chơi game vui vẻ!** 🎮🚢

---

*Tài liệu được cập nhật: December 19, 2025*

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
