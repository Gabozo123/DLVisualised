from flask import Flask, render_template
import requests
import sqlite3
from urllib.parse import urlparse, parse_qs


def main():

    conn = sqlite3.connect('leveldata.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS leveldata")


    createTable = """
    CREATE TABLE IF NOT EXISTS leveldata(
    Placement INTERGER NOT NULL,
    Name TEXT NOT NULL,
    Length INTERGER NOT NULL,
    Date TEXT NOT NULL,
    Victors INTERGER NOT NULL,
    Records INTERGER NOT NULL,
    Objects INTERGER NOT NULL,
    Views INTERGER NOT NULL,
    Likes INTERGER NOT NULL,
    Comments INTERGER NOT NULL
    )
    """
    cursor.execute(createTable)


    ytKey = '[insert key here]'

    params = {"limit": 75}
    responseDL = requests.get('https://api.demonlist.org/level/classic/list', params=params)
    if responseDL.status_code != 200:
        print(f"responseDL Error: {responseDL.status_code}")
        return 1

    levelsDetail = responseDL.json()['data']['levels']

    for level in levelsDetail:
        placement = level['placement']
        name = level['name']
        length = level['length']
        DLdate = level['date_created'][:9]

        
        level_id = level['id']
        responseVictors = requests.get('https://api.demonlist.org/level/classic/record/list', params={'level_id': level_id})
        if responseVictors.status_code != 200:
            print(f"responseVictors Error: {responseVictors.status_code}")
        
        victors = responseVictors.json()['data']['completed_count']
        records = responseVictors.json()['data']['total_count']


        responseObjects = requests.get('https://api.demonlist.org/level/classic/get', params={'id': level_id})
        if responseObjects.status_code != 200:
            print(f"responseObjects Error: {responseObjects.status_code}")
        
        objects = responseObjects.json()['data']['objects']

        # Default Values (Youtube data)
        YTdate = DLdate
        YTviews = 0
        YTlikes = 0
        YTcomments = 0
        
        # YOUTUBE API CALL
        video = level['verification_url']
        vidID = get_vidID(video)

        YTdata = True
        responseYT = requests.get(f'https://www.googleapis.com/youtube/v3/videos?id={vidID}&key={ytKey}&part=snippet,statistics')
        if responseYT.status_code != 200:
            print(f"responseYT. Error: {responseYT.status_code}")
            continue

        #print(responseYT.json())

    
        if responseYT.json()['items']:
            videoDetails = responseYT.json()['items'][0]
            YTdate = videoDetails['snippet']['publishedAt']
            YTviews = videoDetails['statistics']['viewCount']
            YTlikes = videoDetails['statistics']['likeCount']
            YTcomments = videoDetails['statistics']['commentCount']

        else:
            print(f'{placement} {name}: GET request valid but video details failed to find')
        

        print(f'Date: {YTdate}, Views: {YTviews}, Likes: {YTlikes}, Comments: {YTcomments}')

        print(f'Placement: {placement}, Level: {name}, Length: {length}, Date: {YTdate}, Victors: {victors}, Records: {records}, Objects: {objects}')

        cursor.execute("INSERT INTO leveldata VALUES (?,?,?,?,?,?,?,?,?,?)", 
                       (placement, name, length, YTdate, victors, records, objects, YTviews, YTlikes, YTcomments))
        
    conn.commit()
    conn.close()

        

def get_vidID(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname == 'www.youtube.com':
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            return query['v'][0]
        elif query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        elif query.path[:3] == '/v/':
            return query.path.split('/')[2]
        

if __name__ == '__main__':
    main()