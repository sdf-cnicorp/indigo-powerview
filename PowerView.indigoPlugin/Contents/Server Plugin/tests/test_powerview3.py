
import logging
import os
from powerview3 import PowerViewGen3
import requests
import pytest

mock_put_called = False


def mock_put(*args, **kwargs):
    global mock_put_called
    mock_put_called = True
    return MockResponse()


@pytest.fixture(scope='session')
def host():
    host = os.getenv('POWERVIEW3_GATEWAY_IP', default=None)
    if host is None:
        raise AttributeError('Define an Environment Variable: POWERVIEW3_GATEWAY_IP=<host IP or hostname>')
    return host


@pytest.fixture()
def tpv3(monkeypatch):
    monkeypatch.setattr(requests, "put", mock_put)
    tpv3 = PowerViewGen3(TestLogger())
    return tpv3


def test_1_shadeIds(tpv3, host):
    # def scenes(self, hubHostname):
    result = tpv3.shadeIds(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], int)


def test_shade(tpv3, host):
    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(host):
        result = tpv3.shade(host, shadeId)

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)


def test_2_room(tpv3, host):
    # def room(self, hubHostname, roomId):

    room_list = requests.get('http://{}/home/rooms'.format(host))
    rooms = room_list.json()

    for room in rooms:
        result = tpv3.room(host, room['id'])

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))


def test_3_scenes(tpv3, host):
    # def scenes(self, hubHostname):
    result = tpv3.scenes(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_activate_scene(tpv3, host):
    global mock_put_called
    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv3.scenes(host):
        tpv3.activateScene(host, scene['id'])
        assert mock_put_called
        mock_put_called = False


def test_jog_shade(tpv3, host):
    global mock_put_called
    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(host):
        tpv3.jogShade(host, shadeId)
        assert mock_put_called
        mock_put_called = False


def test_set_shade_position(tpv3, host):
    global mock_put_called
    # def setShadePosition(self, hubHostname, shadeId, positions):

    for shadeId in tpv3.shadeIds(host):
        tpv3.setShadePosition(host, shadeId, {'primary':0, 'secondary':0, 'tilt':0, 'velocity':0})
        assert mock_put_called
        mock_put_called = False


# def activateSceneCollection(self, hubHostname, sceneCollectionId):
# def sceneCollections(self, hubHostname):

# custom class to be the mocked return value that
# will override the requests.Response object returned from requests.put
class MockResponse:
    # mock status code is always 200 Success
    status_code = requests.codes.ok

    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"mock_key": "static response json for put() from MockResponse class"}

class TestLogger:

    def error(self, log_msg):
        logging.getLogger().error(log_msg)
