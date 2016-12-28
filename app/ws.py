import json
from datetime import timedelta

import dateutil.parser
from flask import Blueprint, request

from app.models.main import Channel, Performer, Song, Play

# Response codes
CODE_KO = 1
CODE_OK = 0

music_ws = Blueprint('music_ws', __name__)


@music_ws.route('/', methods=['GET'])
def index():
    return 'Hello this is dog "/"'


def build_response(result, code, errors=None):
    r = {'result': result, 'code': code}
    if errors:
        r['errors'] = errors
    return json.dumps(r)


# INGESTION


@music_ws.route('/add_channel', methods=['POST'])
def add_channel():
    channel = request.values.get('name', '')
    r = {'result': "", 'code': CODE_KO}

    if channel:
        Channel.objects(name=channel).update_one(upsert=True, name=channel)
        r['result'] = "Channel '%s' added/updated" % channel
        r['code'] = CODE_OK

    if not channel:
        r['errors'] = ['Channel name not provided']

    return build_response(**r)


@music_ws.route('/add_performer', methods=['POST'])
def add_performer():
    performer = request.values.get('name', '')
    r = {'result': "", 'code': CODE_KO}

    if performer:
        Performer.objects(name=performer).update_one(upsert=True, name=performer)
        r['result'] = "Performer '%s' added/updated" % performer
        r['code'] = CODE_OK

    if not performer:
        r['errors'] = ['Performer name not provided']

    return build_response(**r)


@music_ws.route('/add_song', methods=['POST'])
def add_song():
    title = request.values.get('title', '')
    performer = request.values.get('performer', '')
    r = {'result': "", 'code': CODE_KO}

    if title and performer:
        Song.objects(title=title, performer=performer).update_one(upsert=True, title=title, performer=performer)
        r['result'] = "Song '%s' by '%s' added/updated" % (title, performer)
        r['code'] = CODE_OK

    if not (title and performer):
        r['errors'] = ['Title or performer not provided']

    return build_response(**r)


@music_ws.route('/add_play', methods=['POST'])
def add_play():
    title = request.values.get('title', '')
    performer = request.values.get('performer', 'unknown-performer')
    start = request.values.get('start', '')
    end = request.values.get('end', '')
    channel = request.values.get('channel', '')
    r = {'result': "", 'code': CODE_KO, 'errors': []}
    necessary_data = all([title, performer, start, end, channel])

    if necessary_data:
        dates_parsed = _parse_date_helper([start, end])
        if dates_parsed:
            parsed_start, parsed_end = dates_parsed
            play_data = dict(title=title, performer=performer, start=parsed_start, end=parsed_end, channel=channel)
            Play.objects(**play_data).update_one(upsert=True, **play_data)
            r['result'] = "Play '%s' added/updated" % (", ".join(["%s: %s" % (k, v) for k, v in play_data.items()]))
            r['code'] = CODE_OK
        else:
            r['errors'].append("Invalid date format, please provide dates in UTC ISO 8601")

    if not necessary_data:
        r['errors'].append('Title, Performer, Start, End or Channel not provided')

    return build_response(**r)


# REQUEST


@music_ws.route('/get_song_plays', methods=['GET'])
def get_song_plays():
    title = request.values.get('title', '')
    performer = request.values.get('performer', '')
    start = request.values.get('start', '')
    end = request.values.get('end', '')
    r = {'result': [], 'code': CODE_KO, 'errors': []}

    necessary_data = all([title, performer, start, end])
    if necessary_data:
        dates_parsed = _parse_date_helper([start, end])
        if dates_parsed:
            parsed_start, parsed_end = dates_parsed
            plays = Play.objects(start__gte=parsed_start, end__lte=parsed_end, title=title, performer=performer)
            r['result'] = prepare_song_plays(plays)
            r['code'] = CODE_OK
        else:
            r['errors'].append("Invalid date format, please provide dates in UTC ISO 8601")

    if not necessary_data:
        r['errors'].append('Title, Performer, Start or End not provided')

    return build_response(**r)


@music_ws.route('/get_channel_plays', methods=['GET'])
def get_channel_plays():
    channel = request.values.get('channel', '')
    start = request.values.get('start', '')
    end = request.values.get('end', '')
    r = {'result': [], 'code': CODE_KO, 'errors': []}

    necessary_data = all([channel, start, end])
    if necessary_data:
        dates_parsed = _parse_date_helper([start, end])
        if dates_parsed:
            parsed_start, parsed_end = dates_parsed
            plays = Play.objects(start__gte=parsed_start, end__lte=parsed_end, channel=channel)
            r['result'] = prepare_channel_plays(plays)
            r['code'] = CODE_OK
        else:
            r['errors'].append("Invalid date format, please provide dates in UTC ISO 8601")

    if not necessary_data:
        r['errors'].append('Title, Performer, Start or End not provided')

    return build_response(**r)


@music_ws.route('/get_top', methods=['GET'])
def get_top():
    channels = json.loads(request.values.get('channels', '{}'))
    start = request.values.get('start', '')
    r = {'result': [], 'code': CODE_KO, 'errors': []}
    try:
        limit = int(request.values.get('limit', 0))
    except:
        r['errors'].append("Invalid limit, provide a valid integer")
        return build_response(**r)

    start_parsed = _parse_date_helper(start)
    if not start_parsed:
        r['errors'].append("Invalid date format, please provide dates in UTC ISO 8601")
        return build_response(**r)

    # from a given date substract its position in the week, so we get start and end of the week of the provided date.
    start_week = start_parsed[0] - timedelta(days=start_parsed[0].weekday())
    end_week = start_week + timedelta(days=6)

    # calculate current week
    top_plays = get_top_aggregate(channels, start_week, end_week, limit)

    # calculate past week
    # TODO : this query should be cached or pre-calculated in another structure.
    lastweek_start = start_week - timedelta(days=7)
    lastweek_end = lastweek_start + timedelta(days=6)
    top_plays_lastweek = get_top_aggregate(channels, lastweek_start, lastweek_end, limit)

    r['result'] = prepare_top_plays(top_plays, top_plays_lastweek)
    r['code'] = CODE_OK

    return build_response(**r)


# Helpers

def _parse_date_helper(dates):
    """
        Date helper to parse dates in UTC ISO 8601 format.
        Accepts single date or list.
    """
    dates = [dates] if type(dates) is not list else dates
    try:
        return map(lambda d: dateutil.parser.parse(d), dates)
    except Exception:
        return []


# TODO : prepare_song_plays and prepare_channel_plays could be more generic.
def prepare_song_plays(plays):
    _plays = []
    for plays in plays:
        _plays.append({
            'channel': plays.channel,
            'start': plays.start.isoformat(),
            'end': plays.end.isoformat()
        })
    return _plays


def prepare_channel_plays(plays):
    _plays = []
    for plays in plays:
        _plays.append({
            'performer': plays.performer,
            'title': plays.title,
            'start': plays.start.isoformat(),
            'end': plays.end.isoformat()
        })
    return _plays


def prepare_top_plays(plays, lastweek_plays):
    """
        Join current plays with last week.
        TODO : This is a temporary process, all top plays should be summarized and stored in the DB.
    """
    for rank, p in enumerate(plays):
        p['previous_plays'] = 0  # default value
        p['previous_rank'] = None  # default value
        p['rank'] = rank
        for rank_lastweek, lp in enumerate(lastweek_plays):
            if p['title'] == lp['title'] and p['performer'] == lp['performer']:
                # that guy was in the last week, push up his data to plays list.
                p['previous_plays'] = lp['plays']
                p['previous_rank'] = rank_lastweek
    return plays


def get_top_aggregate(channels, start_week, end_week, limit):

    plays = Play._get_collection().aggregate([
        {
            "$match": {
                "channel": {"$in": channels},
                "start": {"$gte": start_week},
                "end": {"$lte": end_week}
            }
        },
        {
            "$group": {
                "_id": {
                    "performer": "$performer",
                    "title": "$title"
                },
                "plays": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "performer": "$_id.performer",
                "title": "$_id.title",
                "plays": 1
            }
        },
        {"$sort": {"plays": -1}},
        {"$limit": limit}
    ])

    return list(plays)