#ifndef PI_H
#define PI_H

#include "main.h"

/* Stan jednego koła DC: enkoder, zadanie prędkości i regulator PI. */
typedef struct {
	TIM_HandleTypeDef *timer;	/* timer enkodera (tryb encoder) */
	int32_t pulse_count;		/* impulsy od poprzedniej próbki */
	float actual_speed;		/* prędkość surowa [RPM] */
	int8_t d;			/* znak osi enkodera (+1 / -1), zależny od montażu */
	int16_t max_speed;		/* nasycenie wyjścia PI (PWM) */
	int16_t target_speed;		/* zadana prędkość [RPM] */
	float current_setpoint;		/* rampa: aktualne zadanie dążące do target_speed */
	int32_t error_sum;		/* całka błędu (człon I) */
	int16_t last_output;		/* ostatnie wyjście PI (wypełnienie PWM) */
	float Kp;
	float Ki;
	float filtered_speed;		/* prędkość po filtrze dolnoprzepustowym */
	float alpha;			/* współczynnik filtra: 0 = silne wygładzenie, 1 = bez filtra */
} DC_str;

#define RESOLUTION     168.0f	/* impulsy enkodera na obrót */
#define TIMER_FREQENCY 100.0f	/* częstotliwość próbki TIM13 [Hz] (okres 10 ms) */

void DC_update_speed(DC_str *m);
int16_t PI_Compute(DC_str *m);

#endif
