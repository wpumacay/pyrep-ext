import numpy as np

from pyrep_ext.const import ObjectType
from pyrep_ext.objects.object import Object


class VisionSensor(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolution = self._sim_api.getVisionSensorRes(self._handle)

    def _get_requested_type(self) -> ObjectType:
        return ObjectType.VISION_SENSOR

    def handle_explicitly(self) -> None:
        pass

    def capture_rgb(self) -> np.ndarray:
        enc_image, resolution = self._sim_api.getVisionSensorImg(self._handle)
        if isinstance(enc_image, str):
            enc_image = enc_image.encode()
        image = np.frombuffer(enc_image, dtype=np.uint8).reshape(
            resolution[1], resolution[0], 3
        )
        image = np.flip(image, 0).copy()
        return image
