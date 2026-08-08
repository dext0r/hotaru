from typing import Any, Final

from zhaquirks import Bus
from zhaquirks.builder import QuirkBuilder, UnitOfTime
from zhaquirks.const import (
    BatterySize,
)
from zhaquirks.device import CustomZigpyDevice
from zhaquirks.xiaomi import (
    BasicCluster,
    IlluminanceMeasurementCluster,
    LocalOccupancyCluster,
    XiaomiCluster,
    XiaomiCustomDevice,
    XiaomiMotionManufacturerCluster,
    XiaomiPowerConfiguration,
)
from zigpy import types as t
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.general import Ota
from zigpy.zcl.clusters.measurement import IlluminanceMeasurement, OccupancySensing
from zigpy.zcl.clusters.security import IasZone
from zigpy.zcl.foundation import ZCLAttributeDef

DEFAULT_DETECTION_INTERVAL_S = 60


class AqaraOccupancyCluster(LocalOccupancyCluster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Сброс "движение обнаружено" при старте HA: иначе после рестарта датчик
        # останется в сработавшем состоянии до следующего реального движения.
        #
        # Прямой _update_attribute в __init__ не срабатывает: zigpy восстанавливает
        # кеш атрибутов из zigbee.db уже ПОСЛЕ создания кластера и затирает наше
        # значение; к тому же сущности ZHA на этот момент ещё не подписаны на
        # attribute_updated. Откладываем сброс, чтобы он лёг поверх восстановленного
        # кеша и дошёл до HA.
        self._loop.call_later(5, self._turn_off)

    def is_attribute_unsupported(self, attr):
        """Отключает создание entity для атрибутов pir_*_delay."""
        return True

    @property
    def reset_s(self) -> int:
        interval = self.endpoint.lumi_cluster.get(
            LumiManuSpecificCluster.AttributeDefs.detection_interval.id,
            DEFAULT_DETECTION_INTERVAL_S,
        )
        return interval + 3


class LumiManuSpecificCluster(XiaomiCluster):
    cluster_id = 0xFCC0
    ep_attribute = "lumi_cluster"

    class AttributeDefs(XiaomiMotionManufacturerCluster.AttributeDefs):
        detection_interval: Final = ZCLAttributeDef(
            id=0x102, type=t.uint8_t, manufacturer_code=0x115F
        )

    async def bind(self):
        result = await super().bind()
        await self.read_attributes([self.AttributeDefs.detection_interval.id])
        return result

    def _update_attribute(
        self, attrid: int | t.uint16_t | ZCLAttributeDef, value: Any
    ) -> None:
        super()._update_attribute(attrid, value)
        if attrid == 274:
            value = value - 65536
            self.endpoint.illuminance.update_attribute(
                IlluminanceMeasurement.AttributeDefs.measured_value.id, value
            )
            self.endpoint.occupancy.update_attribute(
                OccupancySensing.AttributeDefs.occupancy.id,
                OccupancySensing.Occupancy.Occupied,
            )


class AqaraMotionSensor(XiaomiCustomDevice, CustomZigpyDevice):
    def __init__(self, *args, **kwargs):
        self.battery_size = BatterySize.CR2450
        self.motion_bus = Bus()
        super().__init__(*args, **kwargs)


(
    QuirkBuilder(manufacturer="LUMI", model="lumi.motion.agl02")
    .friendly_name(
        model="RTCGQ12LM",
        manufacturer="Aqara",
    )
    .device_class(AqaraMotionSensor)
    .adds(LumiManuSpecificCluster)
    .adds(IlluminanceMeasurementCluster)
    .replaces(BasicCluster)
    .replaces(AqaraOccupancyCluster)
    .replaces(XiaomiPowerConfiguration)
    .removes(IasZone.cluster_id)
    .removes(Ota.cluster_id, cluster_type=ClusterType.Client)
    .number(
        LumiManuSpecificCluster.AttributeDefs.detection_interval.name,
        LumiManuSpecificCluster.cluster_id,
        min_value=2,
        max_value=65535,
        step=1,
        unit=UnitOfTime.SECONDS,
        translation_key="detection_interval",
        fallback_name="Detection interval",
    )
    .add_to_registry()
)
