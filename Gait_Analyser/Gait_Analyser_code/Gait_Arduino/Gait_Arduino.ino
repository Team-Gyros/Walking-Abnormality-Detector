//  The Arduino Environment
//         Sensor Readings will be done by Arduino

#include "HX711.h"

//Share same clock signal
#define SCK 6

//Define dgital pins to read digital data came from ADC
#define D1 3
#define D2 4
#define D3 5
#define D4 7
#define D5 8
#define D6 9
#define D7 10


//Create objects in HX711
HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;
HX711 scale5;
HX711 scale6;
HX711 scale7;


void setup() {
  Serial.begin(9600);
//Begin serial Communication with the objects
  scale1.begin(D1, SCK);
  scale1.set_scale();

  scale2.begin(D2, SCK);
  scale2.set_scale();

  scale3.begin(D3, SCK);
  scale3.set_scale();
  
  scale4.begin(D4, SCK);
  scale4.set_scale();

  scale5.begin(D5, SCK);
  scale5.set_scale();

  scale6.begin(D6, SCK);
  scale6.set_scale();
  
  scale7.begin(D7, SCK);
  scale7.set_scale();
}

void loop() {
  if (scale1.is_ready() && scale2.is_ready() && scale3.is_ready() && scale4.is_ready() && scale5.is_ready() && scale6.is_ready() && scale7.is_ready() ) {
    // Calculate weight and map it in between 0 and 4095
    int weight1 = scale1.get_units()/(-30000);
    int weight2 = scale2.get_units();
    int weight3 = scale3.get_units()/(-30000);
    int weight4 = scale4.get_units();
    int weight5 = scale5.get_units()/(-30000);
    int weight6 = scale6.get_units();
    int weight7 = scale7.get_units();
    
    // output as a List [XX, XX, XX, XX, XX, XX, XX]
    Serial.print("[");
    Serial.print((weight1-71)*82);
    Serial.print(",");
    Serial.print(weight2*0);
    Serial.print(",");
    Serial.print((weight3+119)*82);
    Serial.print(",");
    Serial.print(weight4*0);
    Serial.print(",");
    Serial.print((weight5+66)*82);
    Serial.print(",");
    Serial.print(weight6*0);
    Serial.print(",");
    Serial.print(weight7*0);

    Serial.println("]");

  } else {
    Serial.println("[0,0,0,0,0,0,0]");
  }

  delay(1000);  //Change this according to the FPS in preasure Map
}