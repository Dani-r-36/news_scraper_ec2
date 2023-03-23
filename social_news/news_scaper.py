"""program to scrap bbc news articles"""

from urllib.request import urlopen
import validators
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from bs4 import BeautifulSoup
from rich.console import Console
from adding_story_database import adding_stories, adding_metadata, adding_tags

console = Console()

BBC = "http://bbc.co.uk"

def get_html(url):
    """opens bbc website for extraction"""
    with urlopen(url) as page:
        html_bytes = page.read()
        html = html_bytes.decode("utf_8")
    return html


def parse_stories_bs():
    """makes soup from html info"""
    html = get_html(BBC)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def story_link(soup):
    """extracts the stories titles and url"""
    story_title=[]
    url_list=[]
    stories = soup.select("a.e1f5wbog1")
    for story in stories:
        url_extension = story.get('href')
        url_list.append(url_extension)
        span_tag = story.find('span', {'role': 'text'})
        if span_tag:
            text = span_tag.text.strip()
            story_title.append(text)
    return story_title, url_list


def metadata_link(soup):
    """extracts tags and returns in list"""
    metadata_tags=[]
    metadata_collect = soup.select("a.ecn1o5v2")
    for metadata in metadata_collect:
        story_tags = metadata.text
        metadata_tags.append(story_tags)
    return metadata_tags


def get_stories():
    """brain function to call others"""
    soup = parse_stories_bs()
    titles, url = story_link(soup)
    tag=metadata_link(soup)
    return titles, url, tag


def valid_url(url_list):
    """makes sure url works"""
    for index, url in enumerate(url_list):
        if validators.url(f'{BBC}{url}'):
            url_list[index]=f'{BBC}{url}'
        else:
            url_list[index]=f'{url}'
    return url_list


if __name__ == "__main__":
    print("news 75")
    story_name, story_url, story_tag =get_stories()
    print("after get stories")
    urls=valid_url(story_url)
    print("before adding tags")
    tags=adding_tags(story_tag)
    print("before sotries")
    adding_stories(story_name, urls)
    print("before metadata")
    adding_metadata(tags)
    
