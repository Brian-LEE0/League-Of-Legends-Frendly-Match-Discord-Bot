import psycopg2
import os
from mod.util.logger import logger

def create_table():
    # PostgreSQL에 연결
    try:
        connection = psycopg2.connect(
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PW'],
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
        )
        
        cursor = connection.cursor()

    
        create_table_query = []
        
        # 'discord_users' 테이블 생성 SQL 문
        create_table_query.append('''
        CREATE TABLE discord_users (
            user_mention_id CHAR(22) PRIMARY KEY,
            league_id CHAR() FORIEGN KEY,
        );
        ''')
        
        # 'league_users' 테이블 생성 SQL 문
        create_table_query.append('''
        CREATE TABLE league_users (
            user_mention_id CHAR(22) PRIMARY KEY,
            league_id CHAR() FORIEGN KEY,
        );
        ''')
        
        # 'match_log' 테이블 생성 SQL 문
        create_table_query.append('''
        CREATE TABLE match_log (
            user_mention_id CHAR(22) PRIMARY KEY,
            league_id CHAR() FORIEGN KEY,
        );
        ''')
        
        # SQL 문 실행
        [cursor.execute(i) for i in create_table_query]
        connection.commit()
        logger.info("테이블이 성공적으로 생성되었습니다.")
        # logging all tables name
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        

    except (Exception, psycopg2.Error) as error:
        logger.info("오류 발생:", error)

    finally:
        # 연결과 커서 닫기
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL 연결이 닫혔습니다.")