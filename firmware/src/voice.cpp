#include "voice.h"
#include "Arduino.h"
#include "HardwareSerial.h"
#include "driver/i2s.h"
#include "freertos/portmacro.h"
#include "freertos/projdefs.h"
#include <cstring>
#include <stddef.h>
#include <stdint.h>

VoiceManager::VoiceManager() {
    _is_recording = false;
    _audio_buffer = nullptr;
    _audio_size = 0;

    // allocate 3 seconds buffer
    _buffer_max_size = 16000 * 2 * 3;

}

bool VoiceManager::init() {
    // allocate heap memory for recordings
    _audio_buffer = (uint8_t*)malloc(_buffer_max_size);
    if (!_audio_buffer) {
        Serial.println("[Voice] Buffer allocation failed!!! Go buy more memory lol");
        return false;
    }

    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 256,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    // config port
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_MIC_BCLK,
        .ws_io_num = I2S_MIC_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_MIC_DATA
    };

    // setup drivers
    esp_err_t err = i2s_driver_install(I2S_MIC_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.println("[Voice] I2S driver install falied!!");
        return false;
    }

    // setup pins
    err = i2s_set_pin(I2S_MIC_PORT, &pin_config);
    if (err != ESP_OK) {
        Serial.println("[Voice] I2S pin setup falied!!");
        return false;
    }

    // create bg recording task
    xTaskCreatePinnedToCore(recordTask, "RecordTask", 4096, this, 3, NULL, 0);

    Serial.println("[Voice] Initialized successfully.");
    return true;
}

void VoiceManager::startRecording() {
    _audio_size = 0;
    _is_recording = true;
    Serial.println("[Voice] Recording started.......");
}

void VoiceManager::stopRecording() {
    _is_recording = false;
    Serial.printf("[Voice] Recording stopped. Audio size: %d bytes\n", _audio_size);
}

bool VoiceManager::isRecording() {
    return _is_recording;
}

uint8_t* VoiceManager::getAudioBuffer() {
    return _audio_buffer;
}

uint32_t VoiceManager::getAudioSize() {
    return _audio_size;
}

void VoiceManager::clearBuffer() {
    _audio_size = 0;
}


void VoiceManager::recordTask(void* pvParameters) {
    VoiceManager* manager = (VoiceManager*)pvParameters;
    size_t bytes_read;
    uint8_t temp_buf[1024];

    while (1) {
        if (manager->_is_recording && manager->_audio_size < manager->_buffer_max_size) {
            // read data from mic
            i2s_read(I2S_MIC_PORT, temp_buf, sizeof(temp_buf), &bytes_read, portMAX_DELAY);

            // cal left space, for inventing memory leak
            uint32_t space_left = manager->_buffer_max_size - manager->_audio_size;
            uint32_t copy_size = (bytes_read > space_left) ? space_left : bytes_read;

            // save into main buffer
            memcpy(manager->_audio_buffer + manager->_audio_size, temp_buf, copy_size);
            manager->_audio_size += copy_size;

            // 3s auto stop
            if (manager->_audio_size >= manager->_buffer_max_size) {
                manager->stopRecording();
            } else {
                vTaskDelay(pdMS_TO_TICKS(20));
            }
        }
    }
}
