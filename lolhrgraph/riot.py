from collections import namedtuple

import requests

RIOT_AUTH_TOKEN_HEADER_NAME = "X-Riot-Token"

LEAGUE_REGION = "na1"

LEAGUE_API_HOST = "https://{}.api.riotgames.com/lol".format(LEAGUE_REGION)


def _make_riot_request(url, auth_key):
    riot_response = requests.get(
        "{}{}".format(LEAGUE_API_HOST, url),
        headers={RIOT_AUTH_TOKEN_HEADER_NAME: auth_key}
    )
    riot_response.raise_for_status()
    return riot_response.json()


def get_summoner(riot_api_key, summoner_name):
    riot_response = _make_riot_request(
        "/summoner/v3/summoners/by-name/{}".format(summoner_name),
        riot_api_key
    )
    return riot_response


def get_recent_matches(riot_api_key, summoner_id):
    return _make_riot_request(
        "/match/v3/matchlists/by-account/{}/recent".format(summoner_id),
        riot_api_key
    )


def get_match_timeline(riot_api_key, match_id):
    return _make_riot_request(
        "/match/v3/timelines/by-match/{}".format(match_id),
        riot_api_key
    )
