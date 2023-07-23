
import pytz

KST = pytz.timezone('Asia/Seoul')
from datetime import datetime, timedelta

class TIME() :
    
    @classmethod
    def now_time():
        now = datetime.now(KST)
        return now
    
    def now_time_after_m(m : int):
        now = datetime.now(KST)
        after = now + timedelta(minutes=m)
        return after