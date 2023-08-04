#include "SHT85.h"
#include "DFRobot_OxygenSensor.h"
#include <LiquidCrystal.h>

#define SHT85_ADDRESS         0x44
#define Oxygen_IICAddress ADDRESS_3
#define COLLECT_NUMBER  10

DFRobot_OxygenSensor oxygen;
int incomingByte;
int Contrast = 75;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

SHT85 sht;

void setup()
{
  Serial.begin(9600);
  Wire.begin();
  sht.begin(SHT85_ADDRESS);
  delay(1000);
  oxygen.begin(Oxygen_IICAddress);
  Wire.setClock(100000);
  sht.read();
  delay(1000);

  analogWrite(6, Contrast);
  lcd.begin(16, 2);

}

void loop()
{
  sht.read();
  float oxygenData = oxygen.getOxygenData(COLLECT_NUMBER);

  lcd.setCursor(0, 0);
  lcd.print("RH:");
  lcd.print(sht.getHumidity(), 1);

  lcd.setCursor(8, 0);
  lcd.print("O2:");
  lcd.print(oxygenData);

  lcd.setCursor(3, 1);
  lcd.print("Temp:");
  lcd.print(sht.getTemperature(), 1);
  lcd.print("C");
  //Serial.println(oxygenData);

  if (Serial.available() > 0)
  {
    incomingByte = Serial.read();
    if (incomingByte == 'H') {
      Serial.println(sht.getHumidity(), 1);
    }
    if (incomingByte == 'T') {
      Serial.println(sht.getTemperature(), 1);
    }
    if (incomingByte == 'O') {
      Serial.println(oxygenData);
    }
  }
}