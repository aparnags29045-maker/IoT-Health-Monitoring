smart_patirnt_ monitoring _system 
#define BLYNK_PRINT Serial

#define BLYNK_TEMPLATE_ID "TMPL3hHougpcA"
#define BLYNK_TEMPLATE_NAME "Patient Health System"
#define BLYNK_AUTH_TOKEN "ImMyVMK8YtSMCKrssS5cMwNAvH3Qg9Pf"

#include <Wire.h>
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include "MAX30100_PulseOximeter.h"

// -------- WiFi & Blynk --------
char auth[] = BLYNK_AUTH_TOKEN;
char ssid[] = "WiFi Username";
char pass[] = "WiFi Password";

// -------- LCD --------
LiquidCrystal_I2C lcd(0x27, 16, 2); // ✅ Correct I2C address

// -------- DHT --------
#define DHTPIN D4 // GPIO2
#define DHTTYPE DHT11DHT dht(DHTPIN, DHTTYPE);

// -------- Pulse Oximeter --------
PulseOximeter pox;

// -------- Variables --------
int BPM = 0;
int SpO2 = 0;
float temperature = 0;
float humidity = 0;

#define REPORTING_PERIOD_MS 1000
uint32_t tsLastReport = 0;

// -------- Beat callback --------
void onBeatDetected() {
Serial.println("Beat Detected!");
}

// -------- SETUP --------
void setup() {
Serial.begin(115200);
delay(100);

// LCD init
lcd.init();
lcd.backlight();

lcd.setCursor(0, 0);
lcd.print("Patient Health");
lcd.setCursor(0, 1);
lcd.print("Monitoring");
delay(2000);
lcd.clear();

// DHT init
dht.begin();

// Blynk
Blynk.begin(auth, ssid, pass);

// Pulse Oximeter init
Serial.print("Initializing MAX30100...");
if (!pox.begin()) {
 Serial.println("FAILED");
 lcd.print("MAX30100 FAIL");
 while (1);
} 
Serial.println("SUCCESS");

pox.setOnBeatDetectedCallback(onBeatDetected);
pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
} 

// -------- LOOP --------
void loop() {
Blynk.run();
pox.update();

// Read sensors
BPM = pox.getHeartRate();
SpO2 = pox.getSpO2();
temperature = dht.readTemperature();
humidity = dht.readHumidity();

// Safety check
if (isnan(temperature) || isnan(humidity)) {
Serial.println("DHT read failed");
return;
}

if (millis() - tsLastReport > REPORTING_PERIOD_MS) {

// LCD Display
lcd.setCursor(0, 0);
lcd.print("B:");
lcd.print(BPM);
lcd.print(" S:");
lcd.print(SpO2);
lcd.print("% ");

lcd.setCursor(0, 1);
lcd.print("T:");
lcd.print(temperature);
lcd.print((char)223);
lcd.print("C ");

lcd.print("H:");
lcd.print(humidity);
lcd.print("% ");

// Serial Monitor
Serial.print("BPM: ");
Serial.print(BPM);
Serial.print(" | SpO2: ");
Serial.print(SpO2);
Serial.print("% | Temp: ");
Serial.print(temperature);
Serial.print("C | Humidity: ");
Serial.println(humidity);

// Blynk virtual pins
Blynk.virtualWrite(V1, BPM);
Blynk.virtualWrite(V2, SpO2);
Blynk.virtualWrite(V3, temperature);
Blynk.virtualWrite(V4, humidity);

tsLastReport = millis();
}
}
