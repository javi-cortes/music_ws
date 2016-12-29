# music_ws
Music webservice initial example to implement a song monitoring system. It allows to add channels, performers, songs and plays. And also recover current stored data.

Developed in Python using Flask framework and MongoDB as database.


The web service listens to a port, answers to GET / POST requests and return JSON dictionaries.
(all strings are UTF-8 encoded and all dates are in UTC, in the ISO 8601 format)


### Installation

music_ws uses a number of open source tools to work properly:

* Install [Python 2.7](https://www.python.org/download/releases/2.7/)
* Install [pip] (https://pip.pypa.io/en/stable/installing/)
* Set up the [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) Once in the / of the project, create a virtualenv (tutorial) and run the following command in order to install all the dependencies :
   ```sh
   pip install -r requirements.txt
   ```
* Install [MongoDB Server](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)
* You’re good to go, just run manage.py with runserver option like so (it listens to port 5000 by default):

   ```sh
   manage.py runserver 
   ```
 
### WS Add Data
 
add_channel
```javascript
  POST /add_channel, data={name: 'channel_name'}
```
add_performer
```javascript
  POST /add_performer, data={name: 'performer'}
```  
add_song
```javascript
  POST /add_song, data={title: 'song_name',  performer: 'performer_name'}
```
add_play
```javascript
  POST /add_play, data={title: 'song_name',
                       performer: 'performer_name',
                       start: '2014-10-21T18:41:00',
                       end: '2014-10-21T18:44:00',
                       channel: 'channel_name'}
``` 
### WS Retrieve Data

get_song_plays
```javascript
GET /get_song_plays,
data={title: 'song_name',
    performer: 'performer_name',
    start: '2014-10-21T00:00:00',
    end: '2014-10-28T00:00:00'}
```     
Returns:
```javascript
{result: [{channel: 'channel',
    start: '2014-01-10T01:00:00',
    end: '2014-01-10T01:03:00'],...],
code: 0}
```

get_channel_plays
```javascript
GET /get_channel_plays,
data={start: '2014-10-21T00:00:00',
    end: '2014-10-28T00:00:00',
    channel: 'channel'}
```
Returns:
```javascript
{result: [{performer: 'performer_name',
    title: 'title',
    start: '2014-10-21T00:00:00',
    end: '2014-10-21T00:03:00'},...],
    code: 0}
```

get_top
```javascript
GET /get_top,
data={channels: ['channel_name'],
    start: '2014-10-21T00:00:00',
    limit: 40}
```

Returns:
```javascript
{result: [{performer: 'performer',
    title: 'title',
    plays: plays,
    previous_plays: previous_plays,
    rank: rank,
    previous_rank: previous_rank], ...],
    code: 0}
```
