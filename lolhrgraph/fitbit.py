import base64
import json
import socketserver
import webbrowser
from http.server import BaseHTTPRequestHandler

import os
import requests

socketserver.TCPServer.allow_reuse_address = True

_AUTH_CACHE = "auth_cache.txt"


class FitbitClient(object):
    _API_HOST = "https://api.fitbit.com/1"

    class _ConsentRequestHandler(BaseHTTPRequestHandler):
        # My inner justin is screaming right now
        fitbit_client = None

        """
        I dont like what im doing here. Im trying to have
        minimum user interaction... there must be a better way ::slams desk::
        
        But basically. I want to smooth the user experience. When requesting consent a browser
        will open once they log in and hit ok it will redirect hitting this server that is up for
        one request. This handler slurps up the credentials an stores them off.
        
        Its all pretty slick but it is a bit ugly code wise. But im hiding all this ugliness in the client
        """

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            FitbitClient._ConsentRequestHandler.fitbit_client._request_access_token(self.requestline[11:-9])
            self.wfile.write(b"ok")

    def __init__(self, auth_dict):
        self.access_token = None
        self.refresh_token = None
        self.client_id = auth_dict['client_id']
        self.client_secret = auth_dict['client_secret']
        self.callback_url = auth_dict['callback_url']
        self.auth_uri = auth_dict['auth_uri']
        self.refresh_uri = auth_dict['refresh_uri']
        self._refresh_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(
                base64.b64encode(
                    "{}:{}".format(
                        self.client_id,
                        self.client_secret
                    ).encode('utf-8')
                ).decode('utf-8')
            ),
        }

    def _set_access_token(self, response_json):
        self.access_token = response_json['access_token']
        self.refresh_token = response_json['refresh_token']

    def _request_access_token(self, code):
        fitbit_response = requests.post(
            "{}?code={}&client_id={}&grant_type=authorization_code".format(
                self.refresh_uri,
                code,
                self.client_id
            ),
            headers=self._refresh_headers
        )
        fitbit_response.raise_for_status()
        with open(_AUTH_CACHE, 'w') as outfile:
            outfile.write(fitbit_response.text)

        self._auth()

    def _refresh(self):
        fitbit_response = requests.post(
            "{}?grant_type=refresh_token&refresh_token={}".format(
                self.refresh_uri,
                self.refresh_token
            ),
            headers=self._refresh_headers
        )
        with open(_AUTH_CACHE, 'w') as outfile:
            outfile.write(fitbit_response.text)
            response_json = fitbit_response.json()
            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']

    def _auth(self):
        if os.path.isfile(_AUTH_CACHE):
            with open(_AUTH_CACHE) as infile:
                auth_info = json.loads(infile.read())
                self.access_token = auth_info['access_token']
                self.refresh_token = auth_info['refresh_token']
            self._refresh()  # this is a bit wasteful because even on the first call I refresh. But um. Whatever
        else:
            FitbitClient._ConsentRequestHandler.fitbit_client = self
            with socketserver.TCPServer(("localhost", 5000), FitbitClient._ConsentRequestHandler) as httpd:
                consent_url = "{}?response_type=code&client_id={}&scope=heartrate%20profile".format(
                    self.auth_uri,
                    self.client_id
                )
                print("Opening a browser to {}. If one does not open copy and paste the url".format(consent_url))
                webbrowser.open(consent_url)
                httpd.allow_reuse_address = True
                httpd.handle_request()
                httpd.server_close()

    def _make_fitbit_request(self, url):
        if not self.access_token:
            self._auth()
        fitbit_response = requests.get(
            "{}{}".format(self._API_HOST, url),
            headers={
                'Authorization': 'Bearer {}'.format(self.access_token),
                'Accept-Language': 'en_US'
            }
        )
        fitbit_response.raise_for_status()
        return fitbit_response.json()

    def get_heart_rate_intraday_time_series(self, date, start_time, end_time):
        return self._make_fitbit_request(
            "/user/-/activities/heart/date/{:%Y-%m-%d}/1d/1min/time/{:%H:%M}/{:%H:%M}.json".format(
                date,
                start_time,
                end_time
            )
        )

    def get_profile(self):
        return self._make_fitbit_request(
            "/user/-/profile.json",
        )
