# define ledR 13
# define ledG 12

void setup() {
  Serial.begin(9600);

  pinMode(ledR, OUTPUT); 
  pinMode(ledG, OUTPUT); 
}

void loop() {
  if (Serial.available()>0) {
    char comando = Serial.read();

    if (comando == 'S') {
      digitalWrite(ledR, LOW);
      digitalWrite(ledG, HIGH);
    } 
    else if (comando == 'N') {
      digitalWrite(ledR, HIGH);
      digitalWrite(ledG, LOW);

    } 
  }
}
