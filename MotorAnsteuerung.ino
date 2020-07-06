const int drehendirPin = 12;
const int drehenstepPin = 13;
const int stepsPerRevolution = 200;

const int aufzudirPin = 7;
const int aufzustepPin = 6;

const int button1Pin = 2;
const int button2Pin = 4;

const int faultPin = 8;

#include <AccelStepper.h>

AccelStepper stepper_aufzu(1, aufzustepPin, aufzudirPin);
AccelStepper stepper_drehen(1, drehenstepPin, drehendirPin);

void check_fault(){
  if(digitalRead(faultPin) == LOW){
    Serial.println("Fault Low");
  } else {
    Serial.println("Fault High");
  }
}




void move_auf_zu_motor(){
  Serial.println("move auf zu");
  stepper_aufzu.setSpeed(300);
  stepper_aufzu.runSpeed();
}


void move_drehen_motor(){
  Serial.println("move drehen");
  stepper_drehen.setSpeed(300);
  stepper_drehen.runSpeed();
}



void setup() {
  pinMode(button1Pin, INPUT);
  pinMode(button2Pin, INPUT);
  Serial.begin(112500);
}

void loop() {

  if(digitalRead(button1Pin)==HIGH){
    move_auf_zu_motor();
  }

  if(digitalRead(button2Pin)==HIGH){
    move_drehen_motor();
  }

  delay(1000);
  check_fault();
}
