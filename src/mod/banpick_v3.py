

# curl 'http://prodraft.leagueoflegends.com/draft' \
#   -H 'Accept: */*' \
#   -H 'Accept-Language: ko-KR,ko;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5' \
#   -H 'Connection: keep-alive' \
#   -H 'Content-Type: application/json' \
#   -H 'Cookie: io=AccqbVwzMtHWZmcnAACt; AWSALB=/NhFW4XZcwkoQqVNeOHk4XrUO6SkfeTP0eam8FFrQozrd3CVGj4cuZDEmX0uYIk5ppt+9vikvAlvFKaJSKCWtuR18v2V4PRDpw9m5XoqYr9KIZxrMqhPkboAxO6w' \
#   -H 'Origin: http://prodraft.leagueoflegends.com' \
#   -H 'Referer: http://prodraft.leagueoflegends.com/?' \
#   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' \
#   --data-raw '{"team1Name":"ㅎㅇ","team2Name":"ㅂㅇ","matchName":"ㅁㅊ"}' \
#   --insecure
import requests
import urllib.parse

class BanPick:
    def __init__(self, match_name = "lol", red_team_name = "", blue_team_name = ""):
        self.match_name = match_name
        self.red_team_name = red_team_name
        self.blue_team_name = blue_team_name
        self.room_name = urllib.parse.quote(f"{self.match_name} 1경기")
        
    def get_ready_link(self, is_red = False, is_spec=False):
        ban = urllib.parse.quote("나나이슬")
        if is_red:
            return f"https://nolchamps-draft.burumarket.shop/rooms/{self.room_name}?team=red&ban={ban}"
        elif is_spec:
            return f"https://nolchamps-draft.burumarket.shop/rooms/{self.room_name}?team=spec&ban={ban}"
        return f"https://nolchamps-draft.burumarket.shop/rooms/{self.room_name}?team=blue&ban={ban}"