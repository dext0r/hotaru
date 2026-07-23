from typing import Final, Union

import zigpy.types as t
from zhaquirks import CustomCluster
from zhaquirks.builder import QuirkBuilder
from zigpy.zcl import foundation
from zigpy.zcl.foundation import (
    BaseCommandDefs,
    ZCLCommandDef,
)


# https://github.com/Koenkk/zigbee2mqtt/files/13756188/MAN003.DanalockV3.Zigbee.Product.Manual.-.20211209.pdf
class DanalockManufacturerCluster(CustomCluster):
    cluster_id: Final[t.uint16_t] = 0x115C
    ep_attribute = "danalock"

    class ServerCommandDefs(BaseCommandDefs):
        start_auto_calibration: Final = ZCLCommandDef(id=0x00, schema={})

    async def command(
        self,
        command_id: Union[foundation.GeneralCommand, int, t.uint8_t],
        *args,
        **kwargs,
    ):
        if command_id == self.ServerCommandDefs.start_auto_calibration.id:
            return await self.endpoint.door_lock.command(
                0x0, manufacturer=0x115C, expect_reply=True
            )

        return foundation.GENERAL_COMMANDS[
            foundation.GeneralCommand.Default_Response
        ].schema(command_id=command_id, status=foundation.Status.UNSUP_CLUSTER_COMMAND)


(
    QuirkBuilder(manufacturer="Danalock", model="V3-BTZBE")
    .adds(DanalockManufacturerCluster)
    .command_button(
        DanalockManufacturerCluster.ServerCommandDefs.start_auto_calibration.name,
        DanalockManufacturerCluster.cluster_id,
        translation_key="auto_calibration",
        fallback_name="Auto calibration",
    )
    .add_to_registry()
)
