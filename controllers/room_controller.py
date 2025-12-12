"""
Room Controller
Handles room creation and management logic - IN MEMORY (No Database)
Rooms are managed by the server in memory
"""
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.INFO)


class RoomController:
    """Controller quản lý phòng chơi - đơn giản hóa cho in-memory
    
    Chức năng:
    - Validate tên phòng trước khi tạo
    - Kiểm tra độ dài, ký tự hợp lệ
    
    Lưu ý: Phòng được quản lý bởi server trong RAM, không lưu database
    """

    @staticmethod
    def validate_room_name(room_name):
        """Validate tên phòng
        
        Args:
            room_name: Tên phòng cần kiểm tra
        
        Returns:
            Dict:
            - success=True: Hợp lệ
            - success=False + message: Không hợp lệ và lý do
        
        Validate:
        - Không được để trống
        - Từ 3 đến 100 ký tự
        """
        if not room_name:
            return {
                'success': False,
                'message': 'Room name is required'
            }
        
        if len(room_name) < 3 or len(room_name) > 100:
            return {
                'success': False,
                'message': 'Room name must be between 3 and 100 characters'
            }
        
        return {'success': True}
