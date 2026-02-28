#include "HTTPClient.h"
#include "WString.h"
#include <stddef.h>
#include <stdint.h>
#include <webcom.h>

WebCom::WebCom(String _serverUrl) {
    serverUrl = _serverUrl;
}

void WebCom::connectWiFi(const char* ssid, const char* password) {
    if (WiFi.status() == WL_CONNECTED) return;

    Serial.printf("Connecting to %s \n", ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    Serial.println("WiFi Connection initiated...!");
}

bool WebCom::isConnected() {
    return (WiFi.status() == WL_CONNECTED);
}

String WebCom::sendGetRequest(String endpoint) {
    if (!isConnected()) return "Error: No WiFi!!!!!";

    HTTPClient http;
    String fullUrl = String(serverUrl) + endpoint;

    http.begin(fullUrl);
    int httpCode = http.GET();

    String payload = "{}";
    if (httpCode > 0) {
        payload = http.getString();
    } else {
        Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
    return payload;
}

String WebCom::sendPostRequest(const char* endpoint, String jsonPayload) {
    if (!isConnected()) return "Error: No WiFi";

    HTTPClient http;
    String fullUrl = String(serverUrl) + endpoint;

    http.begin(fullUrl);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(jsonPayload);
    String response = http.getString();
    http.end();

    return response;
}

String WebCom::sendAudioPostRequest(const char* endpoint, uint8_t* audioData, size_t size) {
    if (!isConnected()) return "Error: No WiFi";

    HTTPClient http;
    String fullUrl = String(serverUrl) + endpoint;

    http.begin(fullUrl);
    http.addHeader("Content-Type", "application/octet-stream");

    int httpCode = http.POST(audioData, size);
    String responce = http.getString();
    http.end();

    return responce;
}
