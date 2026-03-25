#pragma once

#include "esphome/core/component.h"
#include "esphome/components/light/light_output.h"
#include "esphome/components/light/light_effect.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace sonoff_l1 {

static const uint8_t SONOFF_L1_MODE_COLORFUL          =  1;
static const uint8_t SONOFF_L1_MODE_COLORFUL_GRADIENT =  2;
static const uint8_t SONOFF_L1_MODE_COLORFUL_BREATH   =  3;
static const uint8_t SONOFF_L1_MODE_DIY_GRADIENT      =  4;
static const uint8_t SONOFF_L1_MODE_DIY_PULSE         =  5;
static const uint8_t SONOFF_L1_MODE_DIY_BREATH        =  6;
static const uint8_t SONOFF_L1_MODE_DIY_STROBE        =  7;
static const uint8_t SONOFF_L1_MODE_RGB_GRADIENT      =  8;
static const uint8_t SONOFF_L1_MODE_RGB_PULSE         =  9;
static const uint8_t SONOFF_L1_MODE_RGB_BREATH        = 10;
static const uint8_t SONOFF_L1_MODE_RGB_STROBE        = 11;
static const uint8_t SONOFF_L1_MODE_SYNC_TO_MUSIC     = 12;

class SonoffL1 : public light::LightOutput,
                 public uart::UARTDevice,
                 public Component {
 public:
  void setup() override;
  void dump_config() override;
  void setup_state(light::LightState *state) override;
  void write_state(light::LightState *state) override;
  light::LightTraits get_traits() override;

  void set_mode(uint8_t mode);
  void set_speed(uint8_t speed) { this->speed_ = speed; }
  void set_sensitivity(uint8_t sensitivity) { this->sensitivity_ = sensitivity; }

  uint8_t get_mode() const { return this->mode_; }
  uint8_t get_speed() const { return this->speed_; }
  uint8_t get_sensitivity() const { return this->sensitivity_; }

 protected:
  void send_command_();
  void send_raw_(const char *payload);

  light::LightState *state_{nullptr};
  bool initialized_{false};
  uint8_t mode_{SONOFF_L1_MODE_COLORFUL};
  uint8_t speed_{50};
  uint8_t sensitivity_{5};
};

class SonoffL1Effect : public light::LightEffect {
 public:
  SonoffL1Effect(const char *name, uint8_t mode);
  void apply() override;
  void start() override;
  void stop() override;

 protected:
  uint8_t mode_;
};

}  // namespace sonoff_l1
}  // namespace esphome
