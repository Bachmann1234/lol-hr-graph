import json
import os
from pprint import pprint

import datetime

from lolhrgraph import riot
from lolhrgraph.fitbit import FitbitClient


def read_auth_info():
    with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "api_keys.txt"
            )
    ) as auth:
        return json.loads(auth.read())


def get_heart_rate_during_match(fitbit_auth_info, match, match_timeline):
    fitbit_client = FitbitClient(fitbit_auth_info)
    utc_offset = fitbit_client.get_profile()['user']['offsetFromUTCMillis']
    game_start_mili = match["timestamp"] + utc_offset
    game_length_mili = match_timeline["frames"][-1]["timestamp"] - match_timeline["frames"][0]["timestamp"]
    start_datetime = datetime.datetime.utcfromtimestamp(
        game_start_mili / 1000,
    )
    return fitbit_client.get_heart_rate_intraday_time_series(
        start_datetime,
        start_datetime,
        start_datetime + datetime.timedelta(milliseconds=game_length_mili)
    )


def add_hr_to_frames(hr_data, match_timeline):
    hr_intraday = hr_data["activities-heart-intraday"]["dataset"]
    assert len(hr_intraday) == len(match_timeline["frames"])
    for index, frame in enumerate(match_timeline["frames"]):
        frame["heartrate"] = hr_intraday[index]


def simplify_to_key_events(match_timeline):
    results = []
    for frame in match_timeline["frames"]:
        hr = frame["heartrate"]["value"]
        timestamp = frame["timestamp"]
        events = [e for e in frame["events"] if e["type"] in {"BUILDING_KILL", "ELITE_MONSTER_KILL", "CHAMPION_KILL"}]
        results.append({
            "hr": hr,
            "timestamp": timestamp,
            "events": events
        })
    return results


def main():
    auth_info = read_auth_info()
    summoner_name = input("What is your summoner name?\n")
    summoner_profile = riot.get_summoner(auth_info['riot'], summoner_name)
    recent_matches = riot.get_recent_matches(auth_info['riot'], summoner_profile['accountId'])['matches']
    print("Here are your recent matches")
    pprint(
        ["index {} role {} timestamp {}".format(
            index,
            match['role'],
            match['timestamp']
        ) for index, match in enumerate(recent_matches)]
    )
    match_index = int(input("Enter the index of the match you want a graph for\n"))
    match_timeline = riot.get_match_timeline(
        auth_info['riot'],
        recent_matches[match_index]["gameId"]
    )
    heart_data = get_heart_rate_during_match(
        auth_info['fitbit'],
        recent_matches[match_index],
        match_timeline
    )
    add_hr_to_frames(heart_data, match_timeline)
    final_timeline = simplify_to_key_events(match_timeline)
    print(json.dumps(final_timeline, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
