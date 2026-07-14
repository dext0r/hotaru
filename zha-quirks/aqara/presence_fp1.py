# https://github.com/zigpy/zha-device-handlers/pull/2401
import logging
from typing import Any, Final, Union

from zhaquirks.builder import QuirkBuilder
from zhaquirks.xiaomi import CustomCluster, XiaomiCluster
from zigpy import types as t
from zigpy.endpoint import Endpoint
from zigpy.profiles.zha import DeviceType
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.general import Ota
from zigpy.zcl.clusters.measurement import OccupancySensing
from zigpy.zcl.foundation import (
    BaseAttributeDefs,
    BaseCommandDefs,
    CommandSchema,
    DataTypeId,
    GeneralCommand,
    ZCLAttributeDef,
    ZCLCommandDef,
)

MAX_REGIONS = 1

_LOGGER = logging.getLogger(__name__)


class PresenceEvent(t.enum8):
    Enter = 0x00
    Leave = 0x01
    Enter_Left = 0x02
    Leave_Right = 0x03
    Enter_Right = 0x04
    Leave_Left = 0x05
    Approach = 0x06
    Away = 0x07
    Unknown = 0xFF


class RegionEvent(t.enum8):
    Region_Enter = 0x01
    Region_Leave = 0x02
    Region_Occupied = 0x04
    Region_Unoccupied = 0x08


class RegionPresenceEvent(t.Struct):
    region: t.uint8_t
    type: RegionEvent


class RegionDefinitionCommand(CommandSchema):
    class Row(t.bitmap4):
        X1_Left = 0b0001
        X2 = 0b0010
        X3 = 0b0100
        X4_Right = 0b1000

    Y1_Near: None = t.StructField(type=Row, optional=True)
    Y2: None = t.StructField(type=Row, optional=True)
    Y3: None = t.StructField(type=Row, optional=True)
    Y4: None = t.StructField(type=Row, optional=True)
    Y5: None = t.StructField(type=Row, optional=True)
    Y6: None = t.StructField(type=Row, optional=True)
    Y7_Far: None = t.StructField(type=Row, optional=True)


class MonitoringMode(t.enum8):
    Undirected = 0x00
    LeftRight = 0x01


class ApproachDistance(t.enum8):
    Far = 0x00
    Medium = 0x01
    Near = 0x02


class MotionSensitivity(t.enum8):
    Low = 0x01
    Medium = 0x02
    High = 0x03


class LumiManuSpecificCluster(XiaomiCluster):
    cluster_id = 0xFCC0
    ep_attribute = "lumi_cluster"

    class AttributeDefs(BaseAttributeDefs):
        presence: Final = ZCLAttributeDef(
            id=0x142, type=t.uint8_t, manufacturer_code=0x115F
        )
        presence_event: Final = ZCLAttributeDef(
            id=0x143, type=PresenceEvent, access="rp"
        )
        region_config: Final = ZCLAttributeDef(
            id=0x150, type=t.LVBytes, access="w", manufacturer_code=0x115F
        )
        region_presence_event: Final = ZCLAttributeDef(
            id=0x151, type=t.LVBytes, access="rp"
        )
        monitoring_mode: Final = ZCLAttributeDef(
            id=0x0144,
            type=MonitoringMode,
            zcl_type=DataTypeId.uint8,
            manufacturer_code=0x115F,
        )
        approach_distance: Final = ZCLAttributeDef(
            id=0x0146,
            type=ApproachDistance,
            zcl_type=DataTypeId.uint8,
            manufacturer_code=0x115F,
        )
        motion_sensitivity: Final = ZCLAttributeDef(
            id=0x010C,
            type=MotionSensitivity,
            zcl_type=DataTypeId.uint8,
            manufacturer_code=0x115F,
        )

    def _update_attribute(self, attrid: int, value: Any) -> None:
        super()._update_attribute(attrid, value)

        if attrid == self.AttributeDefs.presence.id:
            self.endpoint.occupancy.update_attribute(
                OccupancySensing.AttributeDefs.occupancy.id, value
            )

        if attrid == self.AttributeDefs.presence_event.id:
            # ускорение перехода в occupied при движении у датчика
            if PresenceEvent(value) == PresenceEvent.Enter:
                self.endpoint.occupancy.update_attribute(
                    OccupancySensing.AttributeDefs.occupancy.id,
                    OccupancySensing.Occupancy.Occupied,
                )

        if attrid == self.AttributeDefs.region_presence_event.id:
            event, _ = RegionPresenceEvent.deserialize(value)
            region_endpoint: Endpoint = self.endpoint.device.endpoints[event.region + 1]

            if event.type == RegionEvent.Region_Occupied:
                region_endpoint.occupancy.update_attribute(
                    OccupancySensing.AttributeDefs.occupancy.id,
                    OccupancySensing.Occupancy.Occupied,
                )
            elif event.type == RegionEvent.Region_Unoccupied:
                region_endpoint.occupancy.update_attribute(
                    OccupancySensing.AttributeDefs.occupancy.id,
                    OccupancySensing.Occupancy.Unoccupied,
                )


class RegionOccupancySensing(CustomCluster, OccupancySensing):
    class ServerCommandDefs(BaseCommandDefs):
        set_region: Final = ZCLCommandDef(
            id=0x0001, schema=RegionDefinitionCommand, manufacturer_code=0x115F
        )
        clear_region: Final = ZCLCommandDef(
            id=0x0002, schema={}, manufacturer_code=0x115F
        )

    async def command(
        self,
        command_id: Union[GeneralCommand, int, t.uint8_t],
        *args,
        **kwargs,
    ):
        endpoint: Endpoint = self.endpoint.device.endpoints[1]
        region_id = self.endpoint.endpoint_id - 1

        if command_id == self.ServerCommandDefs.set_region.id:
            y1 = kwargs.get("Y1_Near", RegionDefinitionCommand.Row(0))
            y2 = kwargs.get("Y2", RegionDefinitionCommand.Row(0))
            y3 = kwargs.get("Y3", RegionDefinitionCommand.Row(0))
            y4 = kwargs.get("Y4", RegionDefinitionCommand.Row(0))
            y5 = kwargs.get("Y5", RegionDefinitionCommand.Row(0))
            y6 = kwargs.get("Y6", RegionDefinitionCommand.Row(0))
            y7 = kwargs.get("Y7_Far", RegionDefinitionCommand.Row(0))

            payload = [
                command_id,
                region_id,
                y1 + (y2 << 4),
                y3 + (y4 << 4),
                y5 + (y6 << 4),
                int(y7),
                0xFF,
            ]
            await endpoint.lumi_cluster.write_attributes(
                {
                    LumiManuSpecificCluster.AttributeDefs.region_config.id: payload,
                }
            )
        elif command_id == self.ServerCommandDefs.clear_region.id:
            payload = [command_id, region_id, 0, 0, 0, 0, 0]
            await endpoint.lumi_cluster.write_attributes(
                {
                    LumiManuSpecificCluster.AttributeDefs.region_config.id: payload,
                }
            )


quirk = (
    QuirkBuilder(manufacturer="aqara", model="lumi.motion.ac01")
    .friendly_name(
        model="RTCZCGQ11LM",
        manufacturer="Aqara",
    )
    .adds(OccupancySensing)
    .replaces(LumiManuSpecificCluster)
    .removes(Ota.cluster_id, cluster_type=ClusterType.Client)
    .enum(
        LumiManuSpecificCluster.AttributeDefs.monitoring_mode.name,
        MonitoringMode,
        LumiManuSpecificCluster.cluster_id,
        translation_key="monitoring_mode",
        fallback_name="Monitoring mode",
    )
    .enum(
        LumiManuSpecificCluster.AttributeDefs.approach_distance.name,
        ApproachDistance,
        LumiManuSpecificCluster.cluster_id,
        translation_key="approach_distance",
        fallback_name="Approach distance",
    )
    .enum(
        LumiManuSpecificCluster.AttributeDefs.motion_sensitivity.name,
        MotionSensitivity,
        LumiManuSpecificCluster.cluster_id,
        translation_key="motion_sensitivity",
        fallback_name="Motion sensitivity",
    )
)

for region_id in range(1, MAX_REGIONS + 1):
    endpoint_id = region_id + 1
    quirk.adds_endpoint(endpoint_id, device_type=DeviceType.OCCUPANCY_SENSOR)
    quirk.adds(RegionOccupancySensing, endpoint_id=endpoint_id)

quirk.add_to_registry()
