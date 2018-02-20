import datetime

from lolhrgraph.riot import get_summoner, get_recent_matches, get_match_timeline

BACHMANN_SUMMONER_ID = 32368871


def test_get_summoner(riot_auth_info):
    assert get_summoner(riot_auth_info, 'Bachmann')['id'] == BACHMANN_SUMMONER_ID


def test_get_recent_matches(riot_auth_info):
    recent_matches = get_recent_matches(riot_auth_info, BACHMANN_SUMMONER_ID)
    # Since this makes a live api call and can return different data I am
    # just gonna assert some basic type info.
    assert len(recent_matches)


def test_get_match_details(riot_auth_info):
    # Just assert the request works. Actual logic is gonna be tested wAith a unit
    match_timeline = get_match_timeline(riot_auth_info, 2715330195)
    assert len(match_timeline)
