from zhaquirks import Bus, LocalDataCluster
from zhaquirks.builder import QuirkBuilder
from zhaquirks.const import (
    BatterySize,
)
from zhaquirks.device import CustomZigpyDevice
from zhaquirks.xiaomi import (
    BasicCluster,
    IlluminanceMeasurementCluster,
    OccupancyCluster,
    XiaomiCustomDevice,
    XiaomiMotionManufacturerCluster,
    XiaomiPowerConfiguration,
)
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.general import Ota
from zigpy.zcl.clusters.measurement import OccupancySensing
from zigpy.zcl.clusters.security import IasZone

# без перемычек посылают движение не чаще раз в 60 секунд, даём небольшой запас
DEFAULT_DELAY_S = 75


class AqaraOccupancyCluster(LocalDataCluster, OccupancyCluster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        delay_s: int = {
            "00:15:8d:00:04:60:ba:df": 10,  # Hallway
            "00:15:8d:00:07:92:77:3c": 25,  # Wardrobe
            "00:15:8d:00:03:cb:43:6e": 20,  # Bedroom
        }.get(str(self.endpoint.device.ieee), DEFAULT_DELAY_S)

        self._DEFAULT_VALUES = {
            self.attributes_by_name["pir_o_to_u_delay"].id: delay_s,
        }

        # Сброс "движение обнаружено" при старте HA: иначе после рестарта датчик
        # останется в сработавшем состоянии до следующего реального движения.
        #
        # Прямой _update_attribute в __init__ не срабатывает: zigpy восстанавливает
        # кеш атрибутов из zigbee.db уже ПОСЛЕ создания кластера и затирает наше
        # значение; к тому же сущности ZHA на этот момент ещё не подписаны на
        # attribute_updated. Откладываем сброс, чтобы он лёг поверх восстановленного
        # кеша и дошёл до HA.
        self._loop.call_later(5, self._turn_off)

    @property
    def reset_s(self) -> int:
        return self.endpoint.occupancy.get(
            OccupancySensing.AttributeDefs.pir_o_to_u_delay.id
        )


# RTCGQ01LM/RTCGQ11LM
class AqaraMotionSensor(XiaomiCustomDevice, CustomZigpyDevice):
    def __init__(self, *args, **kwargs):
        self.battery_size = BatterySize.CR2450
        self.motion_bus = Bus()
        super().__init__(*args, **kwargs)


base_quirk = (
    QuirkBuilder(manufacturer="LUMI", model="lumi.sensor_motion")
    .friendly_name(
        model="RTCGQ01LM",
        manufacturer="Aqara",
    )
    .device_class(AqaraMotionSensor)
    .adds(XiaomiMotionManufacturerCluster)
    .replaces(BasicCluster)
    .replaces(AqaraOccupancyCluster)
    .replaces(XiaomiPowerConfiguration)
    .removes(IasZone.cluster_id)
    .removes(IlluminanceMeasurementCluster.cluster_id)
    .removes(Ota.cluster_id, cluster_type=ClusterType.Server)
    .removes(Ota.cluster_id, cluster_type=ClusterType.Client)
)

base_quirk.add_to_registry()

(
    base_quirk.clone()
    .applies_to(manufacturer="LUMI", model="lumi.sensor_motion.aq2")
    .friendly_name(
        model="RTCGQ11LM",
        manufacturer="Aqara",
    )
    .add_to_registry()
)
