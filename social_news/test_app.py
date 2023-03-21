"""test for api"""
import json
from unittest.mock import patch
import pytest

from flask import jsonify
from api import get_list_stories_plus_additional, voting_check
from api import sql_execute, stories, get_tag_stories_execute

def test_index(test_api):
    """tests successful homepage"""
    response = test_api.get("/")
    assert response.status_code == 200

@patch("api.get_list_stories_plus_additional")
def test_stories_return_stories(mock_stories, test_api):
    """checks successful stories returned"""
    mock_stories.return_value = {"stories":[]}
    response = test_api.get("/stories")
    data = response.json
    assert response.status_code == 200
    assert isinstance(data,dict)


@patch("api.get_list_stories_plus_additional")
def test_stories_return_stories_except(mock_stories_fail):
    """checks typeError stories returned"""
    mock_stories_fail.side_effect = TypeError("yikes")
    response = stories()
    assert response['error'] is True
    assert response['Message'] == "Unable to retrieve stories"


def test_voting_id(test_api):
    """check non-valid id"""
    response = test_api.post("/stories/999/votes")
    returned_response = response.json
    print(returned_response)
    print(response)
    assert returned_response['Status_code'] == 400
    assert returned_response['error'] is True


@patch("api.voting_check")
def test_voting_check_up_down(mock_vote, test_api):
    """checks valid posts"""
    mock_vote.return_value = {"direction": "down"}
    response = test_api.post("/stories/1/votes",
    data=json.dumps({"direction": "down"}),content_type='application/json')
    assert response.status_code == 200
    assert isinstance(response.json,dict)
    mock_vote.return_value = {"direction": "up"}
    response = test_api.post("/stories/1/votes",
    data=json.dumps({"direction": "up"}),content_type='application/json')
    assert response.status_code == 200
    assert isinstance(response.json,dict)


def test_voting_post_up():
    """checks invalid posts"""
    data=voting_check({"direction": 1},1)
    assert data['error'] is True


def test_voting_post_up_no_json(test_api):
    """checks post with no json"""
    response = test_api.post("/stories/1/votes",content_type='application/json')
    returned_response = response.json
    assert returned_response['Status_code'] == 400
    assert returned_response['error'] is True


@patch("api.conn")
def test_stories_return_called(mock_connection):
    """mocks that correct execute is ran"""
    mock_cur = mock_connection.cursor
    mock_cur_execute = mock_cur.return_value.execute
    mock_cur.return_value.fetchall.return_value = []
    response = get_list_stories_plus_additional(True)
    print(response)
    mock_cur_execute.assert_called()
    mock_cur_execute.assert_called_with("""SELECT stories.*, SUM
    (CASE direction WHEN 'up' THEN 1 WHEN 'down' THEN -1 ELSE 0 END)
    AS score FROM stories LEFT JOIN votes ON votes.story_id = stories.id 
    GROUP BY stories.id ORDER BY score DESC;""")


@patch("api.conn")
def test_voting_check_return_called_up(mock_connection):
    """mocks update is executed"""
    mock_cur = mock_connection.cursor
    mock_cur_execute = mock_cur.return_value.execute
    mock_cur.return_value.fetchall.return_value = []
    response = voting_check({"direction":"up"},1)
    print(response)
    mock_cur_execute.assert_called()
    mock_cur_execute.assert_called_with("""INSERT INTO votes(direction, story_id, created_at, updated_at) VALUES
        ('up', %s, current_timestamp, current_timestamp);""", [1])


@patch("api.conn")
def test_voting_check_return_called_down(mock_connection):
    """mocks update but for -1"""
    mock_cur = mock_connection.cursor
    mock_cur_execute = mock_cur.return_value.execute
    mock_cur.return_value.fetchall.return_value = []
    response = voting_check({"direction":"down"},1)
    print(response)
    mock_cur_execute.assert_called()
    mock_cur_execute.assert_called_with("""INSERT INTO votes(direction, story_id, created_at, updated_at) VALUES
        ('down', %s, current_timestamp, current_timestamp);""", [1])


@patch("api.get_tag_stories_execute")
def test_tag_stories_return_story_tag(mock_stories, test_api):
    """checks successful stories returned"""
    mock_stories.return_value = [["story"]]
    response = test_api.get("/search?tags=Business")
    data = response.json
    assert response.status_code == 200
    assert isinstance(data,list)


def test_tag_stories_return_story_tag_raised():
    """checks exception raised"""
    with pytest.raises(Exception):
        get_tag_stories_execute()


def test_tag_stories_return_story_tag_invalid(test_api):
    """checks no tags entered"""
    response = test_api.get("/search?tags=")
    data = response.json
    print(response)
    assert data['Status_code'] == 400
    assert data['error'] is True


@patch("api.get_tag_stories_execute")
def test_tag_stories_return_story_tag_type_error(mock_story_tag, test_api):
    """checks raised exception"""
    mock_story_tag.side_effect = TypeError("yikes")
    response = test_api.get("/search?tags=Business")
    data = response.json
    assert data['Status_code'] == 400
    assert data['error'] is True


@patch("api.conn")
def test_sql_execute(mock_connection):
    """mocks that correct execute is ran"""
    mock_cur = mock_connection.cursor
    mock_cur_execute = mock_cur.return_value.execute
    mock_cur.return_value.fetchall.return_value = []
    response = sql_execute("SELECT * FROM %s;",['stories'])
    print(response)
    mock_cur_execute.assert_called()
    mock_cur_execute.assert_called_with("SELECT * FROM %s;",['stories'])
