
import pytz

KST = pytz.timezone('Asia/Seoul')
from datetime import datetime, timedelta, time

class TIME() :
    
    @classmethod
    def now_time():
        now = datetime.now(KST)
        return now.replace(tzinfo=None)
    
    def now_time_after_m(m : int):
        now = datetime.now(KST)
        after = now + timedelta(minutes=m)
        return after.replace(tzinfo=None)
    
    def get_datetime(istoday, hour, minute):
        today = datetime.now(KST).date()
        
        # 시간과 분으로 datetime 객체 생성
        specified_time = time(hour=hour, minute=minute)
        # 오늘의 날짜와 시간을 합쳐서 datetime 객체 생성
        result_datetime = datetime.combine(today, specified_time)
        
        if "오늘" != istoday:
            result_datetime = result_datetime + timedelta(days=1)
            
        return result_datetime