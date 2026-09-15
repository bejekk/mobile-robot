#include "PI.h"

void DC_update_speed(DC_str *m)
{
	/* Delta impulsów od ostatniego wywołania (TIM13, 10 ms). */
	m->pulse_count = (int16_t)__HAL_TIM_GET_COUNTER(m->timer);
	__HAL_TIM_SET_COUNTER(m->timer, 0);

	/* RPM = impulsy * 60 * f_próbki / rozdzielczość; d odwraca znak osi. */
	m->actual_speed = (((float)m->pulse_count * TIMER_FREQENCY * 60.0f) / RESOLUTION) * (float)m->d;

	/* Filtr IIR 1. rzędu — ogranicza szum enkodera przed regulatorem. */
	m->filtered_speed = (m->alpha * m->actual_speed) + ((1.0f - m->alpha) * m->filtered_speed);
}

int16_t PI_Compute(DC_str *m)
{
	static float dt = 0.01f;			/* zgodne z okresem TIM13 */
	static float acceleration_step = 10.0f;		/* RPM na próbkę — rampa przyspieszenia */

	/* 1. Rampa: current_setpoint dogania target_speed, żeby nie dawać skoku PWM. */
	if (m->current_setpoint < m->target_speed) {
		m->current_setpoint += acceleration_step;
		if (m->current_setpoint > m->target_speed) {
			m->current_setpoint = m->target_speed;
		}
	} else if (m->current_setpoint > m->target_speed) {
		m->current_setpoint -= acceleration_step;
		if (m->current_setpoint < m->target_speed) {
			m->current_setpoint = m->target_speed;
		}
	}

	/* 2. Błąd względem prędkości przefiltrowanej (nie surowej). */
	float error = (float)m->target_speed - (float)m->filtered_speed;

	/* 3. Człon P */
	float p_term = m->Kp * error;

	/* 4. Człon I (całka * dt) */
	m->error_sum += error;
	float i_term = m->Ki * m->error_sum * dt;

	float total_output = p_term + i_term;

	/*
	 * 5. Saturacja PWM + anti-windup:
	 * gdy wyjście jest na limicie, cofamy ostatni krok całki, żeby error_sum nie „puchł”.
	 */
	if (total_output > m->max_speed) {
		total_output = (float)m->max_speed;
		m->error_sum -= error * dt;
	} else if (total_output < -m->max_speed) {
		total_output = (float)-m->max_speed;
		m->error_sum -= error * dt;
	}

	m->last_output = (int16_t)total_output;
	return m->last_output;
}
