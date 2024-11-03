# curl 'wss://banpick-wc.glitch.me/' \
#   -H 'Upgrade: websocket' \
#   -H 'Origin: https://banpick.vercel.app' \
#   -H 'Cache-Control: no-cache' \
#   -H 'Accept-Language: ko-KR,ko;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5' \
#   -H 'Pragma: no-cache' \
#   -H 'Connection: Upgrade' \
#   -H 'Sec-WebSocket-Key: RXIcYIvDPwGTQrB4esU8mg==' \
#   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' \
#   -H 'Sec-WebSocket-Version: 13' \
#   -H 'Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits'


# send {"type":"create"}

# recv {"type":"created","matchId":"3e55a448-9398-4d95-8a8f-a5c3c44d7a8a"}

# connect to the websocket
import json
from websocket import create_connection

class BanPick:
    def __init__(self):
        self.ws = create_connection('wss://banpick-wc.glitch.me/', header = {
            'Origin': 'https://banpick.vercel.app',
            'Accept-Language': 'ko-KR,ko;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5',
            'Sec-WebSocket-Key': 'RXIcYIvDPwGTQrB4esU8mg==',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Sec-WebSocket-Version': '13',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits'
        })
        self.match_id = None
        self.create_match()
        
    def create_match(self):
        self.ws.send('{"type":"create"}')
        response = self.ws.recv()
        response = json.loads(response)
        self.match_id = response['matchId']
        
    def get_ready_link(self, is_red = False):
        if is_red:
            return f"https://banpick.vercel.app/ready/{self.match_id}/red"
        return f"https://banpick.vercel.app/ready/{self.match_id}/blue"