// X range 0-325
// Y range 0-200

#define START_BYTE 55
#define STOP_BYTE 110
#define MSG_MAX_LENGTH 16

#include <AccelStepper.h> // Library created by Mike McCauley at http://www.airspayce.com/mikem/arduino/AccelStepper/

// STEPPER PINS
uint8_t x_step_pin = 2;
uint8_t x_dir_pin = 5;

uint8_t y_step_pin = 3;
uint8_t y_dir_pin = 6;

// MOSFET PINS
uint8_t mosfet_1_pin = 7;
uint8_t mosfet_2_pin = 13;
uint8_t mosfet_3_pin = 12;
uint8_t mosfet_4_pin = 10;
uint8_t mosfet_5_pin = 11;
uint8_t mosfet_6_pin = 9;

// ENDSTOP PINS
uint8_t x_endstop_pin = 52;
uint8_t y_endstop_pin = 53;

// OTHER PINS
uint8_t enable_pin = 8;
uint8_t fan_pin = 4;

// AccelStepper Setup
AccelStepper stepperX(1, x_step_pin, x_dir_pin);   // 1 ... driver is present
AccelStepper stepperY(1, y_step_pin, y_dir_pin);   // 1 ... driver is present

uint8_t x_mode = 32;  //microstepping
uint8_t y_mode = 16;  //microstepping

uint16_t max_vel_X = 150 * x_mode;
uint16_t max_acc_X = 50 * x_mode;
uint16_t max_vel_Y = 50 * y_mode;
uint16_t max_acc_Y = 40 * y_mode;

/* Original
uint16_t x_pos_lim = 320;
uint16_t y_pos_lim = 195;
uint16_t y_center = 104;
*/
// Updated
uint16_t x_pos_lim = 100;
uint16_t y_pos_lim = 195;
uint16_t y_center = 105;

bool homing_x_done = true;
bool homing_y_done = true;
bool homing_done = false;

void setup() {
  // Enable stepper drivers
  pinMode(enable_pin, OUTPUT);
  digitalWrite(enable_pin, LOW);

  // Set fan to cca 30% duty (do not use more than 30 %, fans are 12 V powered by 24 V => duty > 50% = fire)
  pinMode(fan_pin, OUTPUT);
  analogWrite(fan_pin, 70);

  pinMode(x_endstop_pin, INPUT_PULLUP);
  pinMode(y_endstop_pin, INPUT_PULLUP);

  Serial.begin(115200);
  Serial.setTimeout(5);

  //  Set Max Speed and Acceleration
  stepperX.setMaxSpeed(max_vel_X);
  stepperX.setAcceleration(max_acc_X);
  stepperY.setMaxSpeed(max_vel_Y);
  stepperY.setAcceleration(max_acc_Y);
  delay(1); // writes weird error otherwise

  // Homing to endstops
  homing();
}

void loop() {
  uint8_t msg[MSG_MAX_LENGTH];
  uint8_t msg_length = 0;
  bool msg_ok = false;
  uint8_t response[MSG_MAX_LENGTH];

  if (Serial.available()) {
    Serial.readBytes(msg, MSG_MAX_LENGTH);

    // Checko for start byte, stop byte and correct length of message
    if (msg[0] == START_BYTE) {
      msg_length = msg[1];
      if (msg[msg_length - 1] == STOP_BYTE) {
        msg_ok = true;
      }
    }

    if (msg_ok) {
      switch (msg[2]) {
        // Move stepper
        case 1: {
            uint16_t req_pos;
            bool req_ok = false;
            req_pos = (msg[4] << 8) | msg[5];
            if (msg[3] == 1) {
              if (req_pos >= 0 && req_pos <= x_pos_lim) {
                req_ok = true;
                stepperX.moveTo(req_pos * x_mode);
              }
            } else if (msg[3] == 2) {
              if (req_pos >= 0 && req_pos <= y_pos_lim) {
                req_ok = true;
                stepperY.moveTo(req_pos * y_mode);
              }
            }
            // RESPONSE
            response[0] = 55;
            response[1] = 5;
            response[2] = 1;
            response[4] = 110;
            if (req_ok) {
              response[3] = 1;
              Serial.write(response, response[1]);
            } else {
              response[3] = 0;
              Serial.write(response, response[1]);
            }

            break;
          }
        // Read stepper
        case 2: {
            uint16_t cur_pos;
            if (msg[3] == 1) {
              cur_pos = (uint16_t) stepperX.currentPosition() / x_mode;
            } else if (msg[3] == 2) {
              cur_pos = (uint16_t) stepperY.currentPosition() / y_mode;
            }

            // RESPONSE
            response[0] = 55;
            response[1] = 6; // ?????
            response[2] = 2;
            response[3] = cur_pos >> 8;
            response[4] = cur_pos & 0xFF;
            response[5] = 110;

            Serial.write(response, response[1]);

            break;
          }
        // Set MOSFET PWM
        case 3: {
            if (msg[3] == 1) {
              analogWrite(mosfet_1_pin, msg[4]);
            } else if (msg[3] == 2) {
              analogWrite(mosfet_2_pin, msg[4]);
            } else if (msg[3] == 3) {
              analogWrite(mosfet_3_pin, msg[4]);
            } else if (msg[3] == 4) {
              analogWrite(mosfet_4_pin, msg[4]);
            } else if (msg[3] == 5) {
              analogWrite(mosfet_5_pin, msg[4]);
            } else if (msg[3] == 6) {
              analogWrite(mosfet_6_pin, msg[4]);
            }

            // RESPONSE
            response[0] = 55;
            response[1] = 4;
            response[2] = 3;
            response[3] = 110;

            Serial.write(response, response[1]);

            break;
          }
        case 4: {
            // RESPONSE
            response[0] = 55;
            response[1] = 5;
            response[2] = 4;
            response[3] = homing_done;
            response[4] = 110;

            Serial.write(response, response[1]);

            break;
          }

        case 5: {
            homing();

            // RESPONSE
            response[0] = 55;
            response[1] = 5;
            response[2] = 5;
            response[3] = homing_done;
            response[4] = 110;

            Serial.write(response, response[1]);

            break;
          }
      }
    }
  }

  if (homing_done) { // homing_done
    stepperX.run();
    stepperY.run();
  }
}


void homing (void) {
  // Homing to endstops
  unsigned long homing_start_time = millis();
  stepperX.setSpeed(-(int16_t)max_vel_X / 5);
  while (digitalRead(x_endstop_pin)) {
    stepperX.runSpeed();
    if (millis() - homing_start_time > 20000) {
      homing_x_done = false;
      Serial.write(255);
      break;
    }
  }
  stepperX.setCurrentPosition(0);


  homing_start_time = millis();
  stepperY.setSpeed(-(int16_t)max_vel_Y / 5);  //(int16_t)max_vel_Y * 2
  while (digitalRead(y_endstop_pin)) {
    stepperY.runSpeed();
    if (millis() - homing_start_time > 30000) {
      homing_y_done = false;
      Serial.write(254);
      break;
    }
  }
  stepperY.setCurrentPosition(0);


  if (homing_x_done && homing_y_done) {
    homing_done = true;
    // Return to mid point
    stepperX.runToNewPosition(x_pos_lim * x_mode / 2);
    stepperY.runToNewPosition(y_center * y_mode);
  } else {
    homing_done = false;
  }
}
