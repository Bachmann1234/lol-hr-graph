import datetime

from lolhrgraph.fitbit import FitbitClient


def test_get_user_profile(fitbit_auth_info):
    fitbit_client = FitbitClient(fitbit_auth_info)
    profile_data = fitbit_client.get_profile()
    assert profile_data['user']
    assert profile_data['user']['offsetFromUTCMillis']


def test_get_heart_rate_intraday_time_series(fitbit_auth_info):
    fitbit_client = FitbitClient(fitbit_auth_info)
    my_utc_offset = -18000000
    example_lol_game_start_time = 1518991401716 + my_utc_offset
    example_lol_game_num_milliseconds = 1693747
    start_datetime = datetime.datetime.utcfromtimestamp(
        example_lol_game_start_time/1000,
    )
    heart_data = fitbit_client.get_heart_rate_intraday_time_series(
        start_datetime,
        start_datetime,
        start_datetime + datetime.timedelta(milliseconds=example_lol_game_num_milliseconds)
    )
    assert heart_data['activities-heart']
    assert heart_data['activities-heart-intraday']
