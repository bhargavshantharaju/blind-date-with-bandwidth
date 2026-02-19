import pytest
from unittest.mock import Mock, patch
from mqtt_handler import MQTTHandler

def test_mqtt_handler_init():
    config = {'mqtt': {'broker': 'localhost', 'port': 1883}}
    handler = MQTTHandler(config, lambda t, p: None)
    assert handler.config == config

@patch('paho.mqtt.client.Client.connect')
@patch('paho.mqtt.client.Client.loop_start')
def test_mqtt_connect(mock_loop, mock_connect):
    config = {'mqtt': {'broker': 'localhost', 'port': 1883}}
    handler = MQTTHandler(config, lambda t, p: None)
    handler.connect()
    mock_connect.assert_called_with('localhost', 1883, 60)

def test_mqtt_publish():
    config = {'mqtt': {'broker': 'localhost', 'port': 1883}}
    handler = MQTTHandler(config, lambda t, p: None)
    handler.connected = True
    with patch.object(handler.client, 'publish') as mock_publish:
        handler.publish('test/topic', {'key': 'value'})
        mock_publish.assert_called_with('test/topic', '{"key": "value"}')