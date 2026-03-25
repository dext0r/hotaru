import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

audio_ns = cg.esphome_ns.namespace("audio")
AudioComponent = audio_ns.class_("AudioComponent", cg.Component)

CONFIG_SCHEMA = cv.COMPONENT_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(AudioComponent),
    }
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
