#include "voice.h"

VoiceManager::VoiceManager() {
    _is_recording = false;
    _audio_buffer = nullptr;
    _audio_size = 0;
    _record_task_handle = NULL;

    // 减小到 2 秒缓存 (16000 * 2字节 * 2秒 = 64000 字节)，保证内存绝对安全
    _buffer_max_size = 16000 * 2 * 2;
}

bool VoiceManager::init() {
    _audio_buffer = (uint8_t*)malloc(_buffer_max_size);
    if (!_audio_buffer) {
        Serial.println("[Voice] Buffer allocation failed! Out of memory.");
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

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_MIC_BCLK,
        .ws_io_num = I2S_MIC_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_MIC_DATA
    };

    if (i2s_driver_install(I2S_MIC_PORT, &i2s_config, 0, NULL) != ESP_OK) return false;
    if (i2s_set_pin(I2S_MIC_PORT, &pin_config) != ESP_OK) return false;

    // 创建任务，并保存句柄到 _record_task_handle
    xTaskCreatePinnedToCore(recordTask, "RecordTask", 8192, this, 2, &_record_task_handle, 0);

    Serial.println("[Voice] Initialized successfully.");
    return true;
}

void VoiceManager::startRecording() {
    _audio_size = 0;
    _is_recording = true;
    Serial.println("[Voice] Recording started...");

    // 唤醒后台录音任务
    if (_record_task_handle != NULL) {
        xTaskNotifyGive(_record_task_handle);
    }
}

void VoiceManager::stopRecording() {
    _is_recording = false;
    Serial.printf("[Voice] Recording stopped. Total size: %d bytes\n", _audio_size);
}

bool VoiceManager::isRecording() { return _is_recording; }
uint8_t* VoiceManager::getAudioBuffer() { return _audio_buffer; }
uint32_t VoiceManager::getAudioSize() { return _audio_size; }
void VoiceManager::clearBuffer() { _audio_size = 0; }

// 彻底重写的后台任务
void VoiceManager::recordTask(void* pvParameters) {
    VoiceManager* manager = (VoiceManager*)pvParameters;
    size_t bytes_read;
    uint8_t temp_buf[1024];

    while (1) {
        // 1. 死等唤醒信号（不录音时，任务在这里彻底挂起，0 CPU 占用）
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        // 2. 被唤醒后，开始循环录音
        while (manager->_is_recording && manager->_audio_size < manager->_buffer_max_size) {
            esp_err_t err = i2s_read(I2S_MIC_PORT, temp_buf, sizeof(temp_buf), &bytes_read, portMAX_DELAY);

            if (err == ESP_OK && bytes_read > 0) {
                uint32_t space_left = manager->_buffer_max_size - manager->_audio_size;
                uint32_t copy_size = (bytes_read > space_left) ? space_left : bytes_read;

                memcpy(manager->_audio_buffer + manager->_audio_size, temp_buf, copy_size);
                manager->_audio_size += copy_size;

                if (manager->_audio_size >= manager->_buffer_max_size) {
                    manager->stopRecording();
                }
            } else {
                vTaskDelay(pdMS_TO_TICKS(10));
            }
        }
        // 录音结束，跳出内层循环，回到外层继续死等下一次唤醒
    }
}
