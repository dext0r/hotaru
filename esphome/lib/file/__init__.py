import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_FILE, CONF_ID
from esphome.core import HexInt
from esphome.types import ConfigType

CONFIG_SCHEMA = cv.ensure_list(
    {
        cv.Required(CONF_ID): cv.declare_id(cg.uint8),
        cv.Required(CONF_FILE): cv.file_,
    }
)


async def to_code(config: list[ConfigType]) -> None:
    for file_config in config:
        with open(str(file_config[CONF_FILE]), "rb") as f:
            data = f.read()
            rhs = [HexInt(x) for x in data]
            cg.progmem_array(file_config[CONF_ID], rhs)
