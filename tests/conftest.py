import json

import os
import pytest

test_directory = os.path.dirname(os.path.abspath(__file__))


def _load_json(path):
    with open(path) as infile:
        return json.loads(infile.read())


def auth_info():
    return _load_json(os.path.join(test_directory, "..", "api_keys.txt"))


@pytest.fixture
def riot_auth_info():
    return auth_info()['riot']


@pytest.fixture
def fitbit_auth_info():
    return auth_info()['fitbit']


@pytest.fixture
def timeline_response_match_2721972283():
    return _load_json(
        os.path.join(
            test_directory,
            "riot_responses",
            "2721972283_timeline_response.json"
        )
    )


@pytest.fixture
def bachmann_summoner_response():
    return _load_json(
        os.path.join(
            test_directory,
            "riot_responses",
            "bachmann_summoner_response.json"
        )
    )


@pytest.fixture
def timeline_response_match_2721972283():
    return _load_json(
        os.path.join(
            test_directory,
            "riot_responses",
            "32368871_recent_matches_response.json"
        )
    )
