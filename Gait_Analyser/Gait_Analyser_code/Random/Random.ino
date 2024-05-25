void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0)); // Seed the random number generator with an analog input
}

void loop() {
  int randomNumber;
  Serial.print("[");
  for (int i = 0; i < 7; ++i) {
    randomNumber = random(4096); // Generate a random number between 0 and 4095
    Serial.print(randomNumber);
    if (i < 6) {
      Serial.print(",");
    }
  }
  Serial.println("]");
  delay(30); // Optional delay to control the output rate
}
