import logging
from .message import (
    MessageQuery,
    MessageSet,
    MessageNewProtocolSet,
    MessagePower,
    MessageE3Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MiedaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    burning_state = "burning_state"
    zero_cold_water = "zero_cold_water"
    protection = "protection"
    zero_cold_pulse = "zero_cold_pulse"
    smart_volume = "smart_volume"
    current_temperature = "current_temperature"
    target_temperature = "target_temperature"


class MideaE3Device(MiedaDevice):
    def __init__(
            self,
            name: str,
            device_id: int,
            ip_address: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str,
            customize: str
    ):
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=0xE3,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.burning_state: False,
                DeviceAttributes.zero_cold_water: False,
                DeviceAttributes.protection: False,
                DeviceAttributes.zero_cold_pulse: False,
                DeviceAttributes.smart_volume: False,
                DeviceAttributes.current_temperature: None,
                DeviceAttributes.target_temperature: 40,
            })
        self._old_sub_types = [
            32, 33, 34, 35, 36, 37, 40, 43, 48, 49, 80
        ]

    def build_query(self):
        return [MessageQuery(self._device_protocol_version)]

    def process_message(self, msg):
        message = MessageE3Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = self._attributes[status]
        return new_status

    def make_message_set(self):
        message = MessageSet(self._device_protocol_version)
        message.zero_cold_water = self._attributes[DeviceAttributes.zero_cold_water]
        message.protection = self._attributes[DeviceAttributes.protection]
        message.zero_clod_pulse = self._attributes[DeviceAttributes.zero_cold_pulse]
        message.smart_volume = self._attributes[DeviceAttributes.smart_volume]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        return message

    def set_attribute(self, attr, value):
        if attr not in [DeviceAttributes.burning_state,
                        DeviceAttributes.current_temperature,
                        DeviceAttributes.protection]:
            if attr == DeviceAttributes.power:
                message = MessagePower(self._device_protocol_version)
                message.power = value
            elif self.sub_type in self._old_sub_types:
                message = self.make_message_set()
                setattr(message, str(attr), value)
            else:
                message = MessageNewProtocolSet(self._device_protocol_version)
                setattr(message, "key", str(attr))
                setattr(message, "value", value)
            self.build_send(message)


class MideaAppliance(MideaE3Device):
    pass
