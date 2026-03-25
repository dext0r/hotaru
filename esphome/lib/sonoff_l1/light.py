import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import light, uart
from esphome.components.light.effects import register_rgb_effect
from esphome.const import CONF_NAME, CONF_OUTPUT_ID, CONF_SPEED

CODEOWNERS = ["@codebullfrog"]
DEPENDENCIES = ["uart"]

sonoff_l1_ns = cg.esphome_ns.namespace("sonoff_l1")
SonoffL1 = sonoff_l1_ns.class_(
    "SonoffL1", light.LightOutput, uart.UARTDevice, cg.Component
)

light_ns = cg.esphome_ns.namespace("light")
LightEffect = light_ns.class_("LightEffect")
SonoffL1Effect = sonoff_l1_ns.class_("SonoffL1Effect", LightEffect)

CONF_MODE = "mode"
CONF_SENSITIVITY = "sensitivity"

SONOFF_L1_MODES = {
    "Colorful": 1,
    "Colorful Gradient": 2,
    "Colorful Breath": 3,
    "DIY Gradient": 4,
    "DIY Pulse": 5,
    "DIY Breath": 6,
    "DIY Strobe": 7,
    "RGB Gradient": 8,
    "RGB Pulse": 9,
    "RGB Breath": 10,
    "RGB Strobe": 11,
    "Sync to Music": 12,
}


@register_rgb_effect(
    "sonoff_l1_mode",
    SonoffL1Effect,
    "Sonoff L1 Mode",
    {
        cv.Required(CONF_MODE): cv.one_of(*SONOFF_L1_MODES, upper=False),
    },
)
async def sonoff_l1_effect_to_code(config, effect_id):
    mode_num = SONOFF_L1_MODES[config[CONF_MODE]]
    var = cg.new_Pvariable(effect_id, config[CONF_NAME], mode_num)
    return var


CONFIG_SCHEMA = cv.All(
    light.RGB_LIGHT_SCHEMA.extend(
        {
            cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(SonoffL1),
            cv.Optional(CONF_SPEED, default=50): cv.int_range(min=1, max=100),
            cv.Optional(CONF_SENSITIVITY, default=5): cv.int_range(min=1, max=10),
        }
    )
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    await cg.register_component(var, config)
    await light.register_light(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_speed(config[CONF_SPEED]))
    cg.add(var.set_sensitivity(config[CONF_SENSITIVITY]))
