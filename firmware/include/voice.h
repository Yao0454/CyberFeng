#ifndef VOICE_H_
#define VOICE_H_

#include <Arduino.h>
#include <driver/i2s.h>
#include <stdint.h>

#define I2S_MIC_PORT I2S_NUM_1
#define I2S_MIC_BCLK 32 // clock_port
#define I2S_MIC_WS 33 // channel_port
#define I2S_MIC_DATA 35 // data_port

class VoiceManager {
public:
    VoiceManager();

    bool init();

    // recording_control
    void startRecording();
    void stopRecording();
    bool isRecording();

    // fetch recorded data
    uint8_t* getAudioBuffer();
    uint32_t getAudioSize();
    void clearBuffer();

private:
    bool _is_recording;
    uint8_t* _audio_buffer;
    uint32_t _audio_size;
    uint32_t _buffer_max_size;

    static void recordTask(void* pvParameters);
};
#endif // VOICE_H_
