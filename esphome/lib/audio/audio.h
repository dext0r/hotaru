#include "esphome/core/component.h"

#include "AudioOutputInternalDAC.h"
#include "AudioGeneratorMP3.h"
#include "AudioFileSourcePROGMEM.h"

namespace esphome {
namespace audio {

static const char *TAG = "audio";

class AudioComponent : public Component {
  public:
    void setup() {
      this->out_ = new AudioOutputInternalDAC();
    };

    void loop() {
      if (this->gen_ && this->gen_->isRunning()) {
            if (!this->gen_->loop()) {
                this->stop();
            }
        }
    };

    bool play_mp3_data(const uint8_t *data, size_t size) {
        this->stop();
        if (!this->open_data_(data, size)) {
          return false;
        }

        this->gen_ = new AudioGeneratorMP3();
        ESP_LOGD(TAG, "Playing");
        return this->gen_->begin(this->src_, this->out_);
    }

    void stop() {
      ESP_LOGD(TAG, "Stopped");
      this->stop_();
    }

    bool is_playing() {
        return this->gen_ && this->gen_->isRunning();
    }

  protected:
    AudioFileSource *src_{};
    AudioGenerator *gen_{};
    AudioOutput *out_{};

    bool open_data_(const uint8_t *data, size_t size) {
        this->src_ = new AudioFileSourcePROGMEM(data, size);
        if (!this->src_->isOpen()) {
            ESP_LOGE(TAG, "Read data failed");
            return false;
        }

        return true;
    }

    void stop_() {
        if (this->gen_) {
            this->gen_->stop();
        }
        delete this->gen_;
        this->gen_ = nullptr;
        delete this->src_;
        this->src_ = nullptr;
    }
};

}
}
