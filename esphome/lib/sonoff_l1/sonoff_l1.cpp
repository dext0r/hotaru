#include "esphome/core/log.h"
#include "sonoff_l1.h"

namespace esphome {
namespace sonoff_l1 {

static const char *const TAG = "sonoff_l1";

void SonoffL1::setup() {
  ESP_LOGCONFIG(TAG, "Setting up Sonoff L1...");
  delay(900);  // Nuvoton MCU startup time
  this->initialized_ = true;
}

void SonoffL1::setup_state(light::LightState *state) {
  this->state_ = state;
}

light::LightTraits SonoffL1::get_traits() {
  auto traits = light::LightTraits();
  traits.set_supported_color_modes({light::ColorMode::RGB});
  return traits;
}

void SonoffL1::dump_config() {
  ESP_LOGCONFIG(TAG, "Sonoff L1:");
  this->check_uart_settings(19200);
}

void SonoffL1::set_mode(uint8_t mode) {
  if (mode < 1 || mode > 12) return;
  this->mode_ = mode;
  this->send_command_();
}

void SonoffL1::write_state(light::LightState *state) {
  if (!this->initialized_) return;
  this->send_command_();
}

void SonoffL1::send_command_() {
  if (!this->initialized_ || this->state_ == nullptr) return;

  float red, green, blue;
  this->state_->current_values_as_rgb(&red, &green, &blue);

  bool power;
  this->state_->current_values_as_binary(&power);

  float bri;
  this->state_->current_values_as_brightness(&bri);

  char buf[200];
  int len = snprintf(buf, sizeof(buf),
      "AT+UPDATE=\"sequence\":\"%d%03d\",\"switch\":\"%s\",\"light_type\":1",
      millis(), millis() % 1000, power ? "on" : "off");

  if (this->mode_ <= 7) {
    len += snprintf(buf + len, sizeof(buf) - len,
        ",\"colorR\":%d,\"colorG\":%d,\"colorB\":%d,\"bright\":%d",
        (int)(red * 255), (int)(green * 255), (int)(blue * 255),
        (int)(bri * 100));
  } else if (this->mode_ <= 11) {
    len += snprintf(buf + len, sizeof(buf) - len,
        ",\"bright\":%d", (int)(bri * 100));
  }

  len += snprintf(buf + len, sizeof(buf) - len, ",\"mode\":%d", this->mode_);

  if (this->mode_ >= 4 && this->mode_ <= 7) {
    len += snprintf(buf + len, sizeof(buf) - len,
        ",\"speed\":%d", this->speed_);
  }

  if (this->mode_ == 12) {
    len += snprintf(buf + len, sizeof(buf) - len,
        ",\"sensitive\":%d,\"speed\":%d", this->sensitivity_, this->speed_);
  }

  ESP_LOGV(TAG, "TX: %s", buf);
  this->send_raw_(buf);
}

void SonoffL1::send_raw_(const char *payload) {
  this->write_str(payload);
  this->write_byte(0x1B);
  this->flush();
}

SonoffL1Effect::SonoffL1Effect(const char *name, uint8_t mode)
    : LightEffect(name), mode_(mode) {}

void SonoffL1Effect::start() {
  auto *out = static_cast<SonoffL1 *>(this->state_->get_output());
  out->set_mode(this->mode_);
}

void SonoffL1Effect::apply() {}

void SonoffL1Effect::stop() {
  auto *out = static_cast<SonoffL1 *>(this->state_->get_output());
  out->set_mode(SONOFF_L1_MODE_COLORFUL);
}

}  // namespace sonoff_l1
}  // namespace esphome
