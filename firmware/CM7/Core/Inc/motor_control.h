#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include "main.h"

/* Sterowanie mostkiem H jednego koła DC: znak = kierunek, |velocity| = PWM. */
void fright_motor(int velocity);
void bright_motor(int velocity);
void fleft_motor(int velocity);
void bleft_motor(int velocity);

/*
 * Silnik krokowy A4988:
 * enabled  — SLEEP (1 = aktywny),
 * port/pin — DIR,
 * htim     — timer kroków (przełącza STEP w przerwaniu),
 * sleep_*  — pin SLEEP sterownika.
 */
void stepper_control(uint8_t enabled, GPIO_TypeDef *port, uint16_t pin, uint8_t dir_state,
		     TIM_HandleTypeDef *htim, GPIO_TypeDef *sleep_port, uint16_t sleep_pin);

#endif
