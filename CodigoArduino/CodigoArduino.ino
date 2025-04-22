void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT); // LED vermelho
  pinMode(12, OUTPUT); // LED verde
}

void loop() {
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');

    if (comando == "ALERTA") {
      digitalWrite(13, HIGH);
      digitalWrite(12, LOW);
    } 
    else if (comando == "POSTURA_ERRADA") {
      digitalWrite(13, HIGH);
      digitalWrite(12, LOW);

    } 
    else if (comando == "TUDO_OK") {
      digitalWrite(13, LOW);
      digitalWrite(12, HIGH);
    }
  }
}
