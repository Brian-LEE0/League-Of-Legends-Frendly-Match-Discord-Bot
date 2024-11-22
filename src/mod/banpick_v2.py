

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

class BanPick:
    def __init__(self, match_name = "lol", red_team_name = "", blue_team_name = ""):
        self.match_name = match_name
        self.red_team_name = red_team_name
        self.blue_team_name = blue_team_name
        self.create_match()
        
    def create_match(self):
        url = "http://prodraft.leagueoflegends.com/draft"
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ko-KR,ko;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': 'io=AccqbVwzMtHWZmcnAACt; AWSALB=/NhFW4XZcwkoQqVNeOHk4XrUO6SkfeTP0eam8FFrQozrd3CVGj4cuZDEmX0uYIk5ppt+9vikvAlvFKaJSKCWtuR18v2V4PRDpw9m5XoqYr9KIZxrMqhPkboAxO6w',
            'Origin': 'http://prodraft.leagueoflegends.com',
            'Referer': 'http://prodraft.leagueoflegends.com/?',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        data = {
            "team1Name": self.red_team_name,
            "team2Name": self.blue_team_name,
            "matchName": self.match_name
        }
        res = requests.post(url, headers=headers, json=data).json()
        self.match_id = res["id"]
        self.blue_auth = res["auth"][0]
        self.red_auth = res["auth"][1]
        
        
    def get_ready_link(self, is_red = False, is_spec=False):
        if is_red:
            return f"http://prodraft.leagueoflegends.com/?draft={self.match_id}&auth={self.red_auth}&locale=en_US"
        elif is_spec:
            return f"http://prodraft.leagueoflegends.com/?draft={self.match_id}&locale=en_US"
        return f"http://prodraft.leagueoflegends.com/?draft={self.match_id}&auth={self.blue_auth}&locale=en_US"