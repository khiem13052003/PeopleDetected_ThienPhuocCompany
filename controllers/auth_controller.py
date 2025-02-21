class AuthController:
    def __init__(self):
        # Thông tin đăng nhập cố định
        self.VALID_USERNAME = 'hoatuoitt'
        self.VALID_PASSWORD = 'Thienphuoc2025'

    def login(self, username, password):
        try:
            if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
                return {
                    'success': True,
                    'user': {
                        'username': username,
                        'role': 'admin'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Tên đăng nhập hoặc mật khẩu không đúng'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi đăng nhập: {str(e)}'
            }
