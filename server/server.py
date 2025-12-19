"""
Enhanced Game Server with Room Management and Database
Manages multiple game rooms simultaneously
"""
import tkinter as tk
from types import TracebackType
from typing import Optional, Type

from networking.room_server import RoomServer


class GameServerWindow(object):
    """Cửa sổ quản lý server game với giao diện UI
    
    Chức năng:
    - Khởi động/dừng server (Start/Stop buttons)
    - Hiển thị địa chỉ IP và Port của server
    - Theo dõi số phòng đang hoạt động (Active Rooms)
    - Theo dõi số client đang kết nối (Connected Clients)
    - Hiển thị chi tiết từng phòng:
      * Tên phòng, host
      * Số người chơi (x/2)
      * Trạng thái (WAITING/PLAYING/FINISHED)
    - Tự động refresh stats mỗi 1 giây
    
    Sử dụng:
    - Chạy server.py để mở cửa sổ này
    - Click "Start Server" để bắt đầu lắng nghe kết nối
    - Client sẽ kết nối đến localhost:65432
    """

    def __init__(self) -> None:
        """Khởi tạo cửa sổ server
        
        Tạo UI với:
        - Top frame: nút Start/Stop Server
        - Mid frame: hiển thị Address và Port
        - Stats frame: Active Rooms và Connected Clients
        - Rooms frame: danh sách chi tiết các phòng (scrollable)
        - Dev sign frame: chữ ký developer
        
        Polling: Tự động refresh stats mỗi 1000ms (1 giây)
        """
        self.parent = tk.Tk(className='Battleship - Multi-Room Server')
        self.parent.geometry('400x400')
        self.parent.resizable(width=False, height=False)
        self.parent.eval('tk::PlaceWindow . center')

        # Core attributes
        self.server: RoomServer = None
        self.polling_interval = 1000

        # Top frame for start and stop game server
        self.top_frame = tk.Frame(self.parent)
        self.start_btn = tk.Button(
            self.top_frame, text='Start Server', command=lambda: self.start_server())
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(
            self.top_frame, text='Stop Server', command=lambda: self.stop_server(), state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        self.top_frame.pack(side=tk.TOP, pady=(10, 0))

        # Middle frame for showing Server IP address and Port
        self.mid_frame = tk.Frame(self.parent)
        self.lbl_host = tk.Label(self.mid_frame, text='Address: Not Started', font=('Arial', 10))
        self.lbl_host.pack(side=tk.TOP)
        self.lbl_port = tk.Label(self.mid_frame, text='Port: Not Started', font=('Arial', 10))
        self.lbl_port.pack(side=tk.TOP)
        self.mid_frame.pack(side=tk.TOP, pady=(10, 0))

        # Stats frame
        self.stats_frame = tk.Frame(self.parent)
        self.lbl_stats = tk.Label(
            self.stats_frame, text='========== Server Stats ==========', font=('Arial', 10, 'bold'))
        self.lbl_stats.pack()
        
        self.lbl_rooms = tk.Label(self.stats_frame, text='Active Rooms: 0', font=('Arial', 9))
        self.lbl_rooms.pack()
        
        self.lbl_clients = tk.Label(self.stats_frame, text='Connected Clients: 0', font=('Arial', 9))
        self.lbl_clients.pack()
        
        self.stats_frame.pack(side=tk.TOP, pady=(10, 0))

        # Rooms display frame
        self.rooms_frame = tk.Frame(self.parent)
        self.lbl_line = tk.Label(
            self.rooms_frame, text='========== Active Rooms ==========', font=('Arial', 10, 'bold')).pack()
        
        self.text_display = tk.Text(self.rooms_frame, height=12, width=45, font=('Courier', 9))
        self.text_display.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        self.text_display.config(background='#F4F6F7',
                                 highlightbackground='grey', state='disabled')
        
        scrollbar = tk.Scrollbar(self.rooms_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_display.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_display.yview)
        
        self.rooms_frame.pack(side=tk.TOP, pady=(10, 0))

        # Dev sign frame
        self.dev_sign_frame = tk.Frame(self.parent)
        self.lbl_dev_sign = tk.Label(
            self.dev_sign_frame, text='Enhanced by AI Assistant', font=('Arial', 8))
        self.lbl_dev_sign.pack(side=tk.RIGHT)
        self.dev_sign_frame.pack(side=tk.BOTTOM, pady=(10, 10))

        # Define a timer for stats refresh polling
        self.text_display.after(self.polling_interval, self.refresh_server_stats)

    def __enter__(self) -> 'GameServerWindow':
        """Context manager entry - trả về self"""
        return self

    def __exit__(
            self,
            exctype: Optional[Type[BaseException]],
            excinst: Optional[BaseException],
            exctb: Optional[TracebackType]) -> None:
        """Context manager exit - tự động đóng server khi thoát
        
        Được gọi khi:
        - Đóng window
        - Exception xảy ra
        - Exit chương trình
        
        Đảm bảo server luôn được stop properly để giải phóng port
        """
        if self.server:
            self.server.stop_server()
            self.server = None

    def start_server(self) -> None:
        """Khởi động server đa phòng
        
        Luồng:
        1. Disable nút Start, enable nút Stop
        2. Tạo RoomServer instance (localhost:65432)
        3. Gọi server.start_server() để:
           - Tạo socket lắng nghe
           - Bắt đầu accept thread
           - Sẵn sàng nhận kết nối từ client
        4. Update UI hiển thị Address và Port
        
        Lưu ý: Server chạy multi-threaded, mỗi room có thread riêng
        """
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        host_address = 'localhost'
        host_port = 65432

        self.server = RoomServer(host_address, host_port)
        self.server.start_server()

        self.lbl_host['text'] = f'Address: {host_address}'
        self.lbl_port['text'] = f'Port: {host_port}'

    def stop_server(self) -> None:
        """Dừng server hiện tại
        
        Luồng:
        1. Enable nút Start, disable nút Stop
        2. Gọi server.stop_server() để:
           - Đóng tất cả socket client
           - Dừng tất cả thread
           - Giải phóng port
        3. Set server = None
        4. Reset UI về trạng thái "Not Started"
        """
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        if self.server:
            self.server.stop_server()
            self.server = None

        self.lbl_host['text'] = 'Address: Not Started'
        self.lbl_port['text'] = 'Port: Not Started'
        self.lbl_rooms['text'] = 'Active Rooms: 0'
        self.lbl_clients['text'] = 'Connected Clients: 0'

    def refresh_server_stats(self) -> None:
        """Làm mới thống kê server (gọi tự động mỗi 1 giây)
        
        Nếu server đang chạy:
        1. Lấy room_count và client_count từ server
        2. Update labels hiển thị số lượng
        3. Update text_display với danh sách phòng chi tiết:
           - Room ID và tên phòng
           - Host username
           - Số người chơi (x/2)
           - Trạng thái (WAITING/PLAYING/FINISHED)
        4. Schedule lần refresh tiếp theo sau 1000ms
        
        Format hiển thị:
        ```
        Room 1: Player1's Room
          Host: Player1
          Players: 2/2
          Status: PLAYING
        ----------------------------------------
        ```
        """
        if self.server:
            room_count = self.server.get_room_count()
            client_count = self.server.get_client_count()
            
            self.lbl_rooms['text'] = f'Active Rooms: {room_count}'
            self.lbl_clients['text'] = f'Connected Clients: {client_count}'
            
            # Update rooms list
            self.text_display.config(state='normal')
            self.text_display.delete('1.0', tk.END)
            
            if room_count == 0:
                self.text_display.insert(tk.END, 'No active rooms\n')
            else:
                for room_id, room in self.server.rooms.items():
                    player_count = room.get_client_count()
                    status = room.status.name
                    
                    room_info = f'Room {room_id}: {room.room_name}\n'
                    room_info += f'  Host: {room.host_username}\n'
                    room_info += f'  Players: {player_count}/2\n'
                    room_info += f'  Status: {status}\n'
                    room_info += '-' * 40 + '\n'
                    
                    self.text_display.insert(tk.END, room_info)
            
            self.text_display.config(state='disabled')

        # Schedule next refresh
        self.text_display.after(self.polling_interval, self.refresh_server_stats)


def main():
    """Chạy server game
    
    Sử dụng context manager (with statement) để:
    - Tự động cleanup khi đóng window
    - Đảm bảo server luôn được stop properly
    - Giải phóng tài nguyên (socket, thread) an toàn
    
    Chạy Tkinter mainloop để hiển thị UI và xử lý events
    """
    with GameServerWindow() as window:
        window.parent.mainloop()


if __name__ == '__main__':
    main()
