import logging
import requests


API_HOST = 'http://api.open-notify.org/iss-pass.json'

logger = logging.getLogger(__name__)


def get_next_pass(lat, lng):
    params = {'lat': lat, 'lon': lng}
    data = requests.get(API_HOST, params=params).json()
    response = data.get('response')

    return response


# def mock():
#     import datetime, time

#     data = []

#     for i in range(0, 25, 5):
#         dt = datetime.datetime.now() + datetime.timedelta(seconds=5 + i)
#         data.append({
#             'duration': '2',
#             'risetime': time.mktime(dt.timetuple())
#         })

#     return data
