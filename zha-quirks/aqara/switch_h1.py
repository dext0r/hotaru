from typing import Final

from zhaquirks.builder import QuirkBuilder
from zhaquirks.const import (
    ARGS,
    ATTR_ID,
    BUTTON_1,
    BUTTON_2,
    CLUSTER_ID,
    COMMAND_BUTTON_DOUBLE,
    COMMAND_BUTTON_SINGLE,
    COMMAND_DOUBLE,
    COMMAND_SINGLE,
    ENDPOINT_ID,
    VALUE,
)
from zhaquirks.xiaomi.aqara.opple_remote import CustomCluster
from zhaquirks.xiaomi.aqara.opple_switch import (
    BOTH_BUTTONS,
    PRESS_TYPE,
    MultistateInputCluster,
    OppleOperationMode,
    OppleSwitchCluster,
)
from zigpy import types as t
from zigpy.profiles.zha import DeviceType
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.general import DeviceTemperature, Ota
from zigpy.zcl.foundation import DataTypeId, ZCLAttributeDef


class ModeSwitch(t.enum16):
    Quick = 0x01
    Anti_Flicker = 0x04


class LumiManuSpecificCluster(OppleSwitchCluster):
    class AttributeDefs(OppleSwitchCluster.AttributeDefs):
        mode_switch: Final = ZCLAttributeDef(
            id=0x0004,
            type=ModeSwitch,
            zcl_type=DataTypeId.uint16,
            is_manufacturer_specific=True,
        )

    async def bind(self):
        result = await super(CustomCluster, self).bind()
        # OppleCluster при bind делает запись в 0x0009
        # это вызывает ребут выключателя
        # в итоге ZHA считает, что он полностью не инициализирован и при каждом перезапуске
        # снова пишет в 0x0009 и снова вызвает ребуты, и так по кругу
        return result


(
    QuirkBuilder(manufacturer="LUMI", model="lumi.switch.l2aeu1")
    .friendly_name(
        model="WS-EUK02",
        manufacturer="Aqara",
    )
    .adds_endpoint(41, device_type=DeviceType.ON_OFF_LIGHT_SWITCH)
    .adds_endpoint(42, device_type=DeviceType.ON_OFF_LIGHT_SWITCH)
    .adds_endpoint(51, device_type=DeviceType.ON_OFF_LIGHT_SWITCH)
    .adds(MultistateInputCluster, endpoint_id=41)
    .adds(MultistateInputCluster, endpoint_id=42)
    .adds(MultistateInputCluster, endpoint_id=51)
    .replaces(LumiManuSpecificCluster, endpoint_id=1)
    .replaces(LumiManuSpecificCluster, endpoint_id=2)
    .removes(MultistateInputCluster.cluster_id, endpoint_id=2)
    .removes(Ota.cluster_id, cluster_type=ClusterType.Client)
    .removes(DeviceTemperature.cluster_id)
    .enum(
        LumiManuSpecificCluster.AttributeDefs.mode_switch.name,
        ModeSwitch,
        LumiManuSpecificCluster.cluster_id,
        translation_key="mode_switch",
        fallback_name="Mode switch",
    )
    .enum(
        LumiManuSpecificCluster.AttributeDefs.operation_mode.name,
        OppleOperationMode,
        LumiManuSpecificCluster.cluster_id,
        endpoint_id=1,
        translation_key="operation_mode",
        fallback_name="Operation mode",
    )
    .enum(
        LumiManuSpecificCluster.AttributeDefs.operation_mode.name,
        OppleOperationMode,
        LumiManuSpecificCluster.cluster_id,
        endpoint_id=2,
        translation_key="operation_mode",
        fallback_name="Operation mode",
    )
    .device_automation_triggers(
        {
            (COMMAND_BUTTON_SINGLE, BUTTON_1): {
                ENDPOINT_ID: 41,
                CLUSTER_ID: 18,
                ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_SINGLE, VALUE: 1},
            },
            (COMMAND_BUTTON_DOUBLE, BUTTON_1): {
                ENDPOINT_ID: 41,
                CLUSTER_ID: 18,
                ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_DOUBLE, VALUE: 2},
            },
            (COMMAND_BUTTON_SINGLE, BUTTON_2): {
                ENDPOINT_ID: 42,
                CLUSTER_ID: 18,
                ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_SINGLE, VALUE: 1},
            },
            (COMMAND_BUTTON_DOUBLE, BUTTON_2): {
                ENDPOINT_ID: 42,
                CLUSTER_ID: 18,
                ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_DOUBLE, VALUE: 2},
            },
            (COMMAND_BUTTON_SINGLE, BOTH_BUTTONS): {
                ENDPOINT_ID: 51,
                CLUSTER_ID: 18,
                ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_SINGLE, VALUE: 1},
            },
            (COMMAND_BUTTON_DOUBLE, BOTH_BUTTONS): {
                ENDPOINT_ID: 51,
                CLUSTER_ID: 18,
                ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_DOUBLE, VALUE: 2},
            },
        }
    )
    .add_to_registry()
)
