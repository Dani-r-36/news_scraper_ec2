"""test for api"""
from unittest.mock import patch
import pytest
from adding_story_database import adding_stories, adding_tags

@patch("api.conn")
def test_insert_stories(mock_connection):
    """mocks that correct execute is ran"""
    mock_cur = mock_connection.cursor
    mock_cur_execute = mock_cur.return_value.execute
    mock_cur.return_value.fetchall.return_value = []
    response = adding_stories(['title'],['url'])
    print(response)
    mock_cur_execute.assert_called()
    mock_cur_execute.assert_called_with("""INSERT INTO stories(title, url, created_at, updated_at)
            VALUES (%s, %s, %s, %s);""",['title', 'url', '2023-03-16', '2023-03-16'])


def test_stories_return_stories_except():
    """checks successful stories returned"""
    # mock_stories_fail.side_effect = Exception("yikes")
    with pytest.raises(Exception):
        adding_stories()


@patch("adding_story_database.sql_insert_data")
def test_stories_return_stories_except_return(mock_insert_story):
    """checks successful stories returned"""
    mock_insert_story.side_effect = Exception("yikes")
    response=adding_stories(['title'],[])
    assert response['error'] is True
    assert response['Message'] == "Error in inserting data"


@patch("api.conn")
def test_insert_tags(mock_connection):
    """mocks that correct execute is ran"""
    mock_cur = mock_connection.cursor
    mock_cur_execute = mock_cur.return_value.execute
    mock_cur.return_value.fetchall.return_value = []
    response = adding_tags(['tag'])
    mock_cur_execute.assert_called()
    mock_cur_execute.assert_called_with("SELECT tags.id FROM tags WHERE tags.description =%s", ['tag'])


def test_tags_return_tags_except():
    """checks successful stories returned"""
    with pytest.raises(Exception):
        adding_tags()
