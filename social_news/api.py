"""api program to retrieve story and post them"""
import psycopg2
import psycopg2.extras 
import sys
from flask import Flask, current_app, request
from dotenv import dotenv_values
app = Flask(__name__)

if sys.argv[1] == 'production':
  config = dotenv_values('.env.production')
  app.run(host='0.0.0.0', port=5000)
else:
  config = dotenv_values('.env.development')
  app.run(host='0.0.0.0', port=5000)
print(config)


def get_db_connection():
    """establishes connection to database"""
    try:
        connection = psycopg2.connect( user = config["DATABASE_USERNAME"], password = config["DATABASE_PASSWORD"], host = config["DATABASE_IP"], port = config["DATABASE_PORT"], database = config["DATABASE_NAME"]) 
        return connection
    except:
        print("Error connecting to database.")

conn = get_db_connection()

@app.route("/", methods=["GET"])
def index():
    """returns static html"""
    return current_app.send_static_file("index.html")


@app.route("/stories", methods=["GET"])
def stories():
    """handling of get request"""
    try:
        data = {}
        success = "false"
        if conn:
            success = 'true'
        else:
            return error_message("Error connecting to server", 500)
        data= get_list_stories_plus_additional(success)
        return data
    except TypeError:
        return error_message("Unable to retrieve stories",500)


def get_list_stories_plus_additional(success: str):
    """collects story and puts in dict"""
    data = {}
    news_list=[]
    unique_curs = get_stories_sql()
    for row in unique_curs:
        news_list.append(row)
    if len(news_list) == 0:
        return error_message("oops no stories",404)
    data['stories'] = news_list
    data['success'] = success
    data['total_stories'] = len(news_list)
    return data


def get_stories_sql():
    """sql command to sort vote to number"""
    unique_curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    unique_curs.execute("""SELECT stories.*, SUM
    (CASE direction WHEN 'up' THEN 1 WHEN 'down' THEN -1 ELSE 0 END)
    AS score FROM stories LEFT JOIN votes ON votes.story_id = stories.id 
    GROUP BY stories.id ORDER BY score DESC;""")
    return unique_curs


@app.route("/stories/<int:story_id>/votes", methods=["POST"])
def voting_id(story_id):
    """handles intial post got vote"""
    try:
        if request.method == 'POST':
            data = sql_execute("SELECT * FROM stories WHERE id = %s", (story_id,))#test here for id
            if len(data) == 0:
                raise Exception 
            return_data = voting_check(request.json,story_id)
            return return_data
    except Exception:
        return error_message("Invalid query",400)

def voting_check(data, story_id):
    """handles the json data for vote"""
    if data['direction'] == 'up':
        sql_insert_data("""INSERT INTO votes(direction, story_id, created_at, updated_at) VALUES
        ('up', %s, current_timestamp, current_timestamp);""", [story_id])
        return data
    if data['direction'] == 'down':
        sql_insert_data("""INSERT INTO votes(direction, story_id, created_at, updated_at) VALUES
        ('down', %s, current_timestamp, current_timestamp);""", [story_id])
        return data
    return error_message("Invalid POST", 400)


@app.route("/search", methods=["GET"])
def tag_stories():
    """return stories from tags"""
    output =[]
    try:
        tag_description = request.args.get('tags').split(",")
        if tag_description[0] == "":
            raise TypeError
        for tag in tag_description:
            output=get_tag_stories_execute(tag,output)
        return output
    except TypeError:
        return error_message("No tags searched",400)


def get_tag_stories_execute(tag,output):
    """handles query for story details from tag"""
    query = """select stories.title, stories.url, tags.description from stories
    join metadata on metadata.story_id = stories.id
    join tags on tags.id=metadata.tag_id where tags.description = %s;"""
    data = sql_execute(query,[tag])
    if len(data) == 0:
        return error_message("oops no stories",404)
    for row in data:
        each_story =[]
        each_story.append(row['title'])
        print(row['title'])
        each_story.append(row['url'])
        each_story.append(row['description'])
        output.append(each_story)
    return output


def error_message(message,num):
    """handles all error messages"""
    return {"error": True, "Message": message, "Status_code":num}


def sql_execute(sql,params):
    """handles most sql executes"""
    curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curs.execute(sql, params)
    data =curs.fetchall()
    curs.close()
    return data


def sql_insert_data(sql,params):
    """handles most sql inserts"""
    curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curs.execute(sql, params)
    conn.commit()
    curs.close()
