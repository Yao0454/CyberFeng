#include <webcom.h>

WebCom::WebCom(const char* _serverUrl) {
    serverUrl = _serverUrl;
}

void WebCom::connectWiFi(const char* ssid, const char* password) {
    if (WiFi.status() == WL_CONNECTED) return;

    Serial.printf("Connecting to %s ", ssid);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected!");
}

bool WebCom::isConnected() {
    return (WiFi.status() == WL_CONNECTED);
}

String WebCom::sendGetRequest(const char* endpoint) {
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