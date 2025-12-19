import json


# Các hằng số cho game networking
CONN_LIMIT = 2  # Số kết nối tối đa mỗi phòng (2 người chơi)
BUFFER_SIZE = 4096  # Kích thước buffer cho socket communication
SHIPS_NAMES = ['battleship', 'cruiser', 'destroyer1', 'destroyer2', 'plane']  # 5 loại tàu


class Network:
    """Class xử lý logic mạng chung
    
    Chức năng:
    - Tạo datagram với kích thước cố định (padding bằng *)
    - Encode dữ liệu thành JSON bytes
    - Decode bytes thành Python object
    
    Sử dụng: Kế thừa bởi Client và RoomServer
    """

    def create_datagram(self, buffer_size: int, data: object) -> bytes:
        """Tạo datagram với chiều dài cố định
        
        Args:
            buffer_size: Kích thước buffer (4096 bytes)
            data: Python object (Dict, List, str, ...)
        
        Returns:
            bytes với độ dài = buffer_size
        
        Luồng:
        1. Chuyển data thành JSON string
        2. Tính header_size = buffer_size - len(message)
        3. Thêm padding '*' vào đầu
        4. Encode thành UTF-8 bytes
        
        Ví dụ:
        buffer_size=20, data={'a': 1}
        → message = '{"a": 1}' (8 bytes)
        → header_size = 12
        → datagram = '************{"a": 1}'
        """

        message = json.dumps(data)
        header_size = abs(buffer_size - len(message))
        datagram = f'{"":*>{header_size}}' + message

        return bytes(datagram, 'utf-8')

    def decode_data(self, data: bytes) -> object:
        """Giải mã dữ liệu nhận từ server
        
        Args:
            data: bytes nhận từ socket.recv()
        
        Returns:
            Python object (Dict, List, ...)
        
        Luồng:
        1. Decode bytes thành UTF-8 string
        2. Xóa tất cả ký tự padding '*'
        3. Parse JSON string thành Python object
        
        Ví dụ:
        data = b'************{"a": 1}'
        → decoded = '************{"a": 1}'
        → cleaned = '{"a": 1}'
        → return {'a': 1}
        """

        decoded_data = data.decode('utf-8')
        cleaned_data = decoded_data.replace('*', '')

        return json.loads(cleaned_data)
