"""Functions for adding stories and its related data"""
from datetime import datetime
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from api import sql_execute, sql_insert_data, conn, error_message


def adding_stories(story_title, url_list):
    """carrys out insert for database"""
    try:
       # curs= conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        current_date = datetime.today().strftime('%Y-%m-%d')
       # curs.execute(" ALTER SEQUENCE stories_id_seq RESTART WITH 1;")
        for index, story in enumerate(story_title):
            story=story.replace("'","''")
            sql_insert_data("""INSERT INTO stories(title, url, created_at, updated_at)
            VALUES (%s, %s, %s, %s);""",[story,url_list[index],current_date,current_date])
            if index == 15:
                break
    except Exception:
        return error_message("Error in inserting data",'')


def adding_tags(story_tag):
    """inserts and gets ids of tags which are being scrapped"""
    print("tags 28")
    try:
        print("before alter tags")
       # curs= conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        tag_id=[]
        print("before execute")
       # curs.execute(" ALTER SEQUENCE tags_id_seq RESTART WITH 1;")
        i = 0
        print("tags before while")
        while i < len(story_tag):
            print("before select")
            data = tags_return_id(story_tag[i])
            print("tag before insert")	
            if len(data) == 0:
                sql_insert_data("INSERT INTO tags (description) VALUES (%s);",[story_tag[i]])
                print("after insert")
                data = tags_return_id(story_tag[i])
            tag_id.append(data[0]['id'])
            i +=1
        return tag_id
    except Exception:
        return error_message("Error in inserting tags",'')


def tags_return_id(description):
    """returns the id of inserted or existing tag"""
    data = sql_execute("SELECT tags.id FROM tags WHERE tags.description =%s",[description])
    return data


def adding_metadata(tags_list):
    """inserting tag_id for each story"""
    curs= conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curs.execute(" ALTER SEQUENCE metadata_id_seq RESTART WITH 1;")
    for index, tag in enumerate(tags_list):
        sql_insert_data("INSERT INTO metadata(story_id, tag_id) VALUES (%s, %s);",[index+1, tag])
    print("worked")
