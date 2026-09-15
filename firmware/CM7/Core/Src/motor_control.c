#include "motor_control.h"

extern TIM_HandleTypeDef htim1;	/* PWM wspólny dla czterech mostków H */

/*
 * pin_a / pin_b — para DIR mostka H.
 * velocity == 0  → oba DIR = 0, PWM wyłączony (silnik wolny / hamowanie pasywne).
 * velocity > 0   → jazda „do przodu”, compare = velocity.
 * velocity < 0   → odwrotny DIR, compare = |velocity|.
 */
static void set_hbridge(GPIO_TypeDef *port, uint16_t pin_a, uint16_t pin_b,
			TIM_HandleTypeDef *htim, uint32_t channel, int velocity)
{
	if (velocity == 0) {
		HAL_GPIO_WritePin(port, pin_a, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(port, pin_b, GPIO_PIN_RESET);
		HAL_TIM_PWM_Stop(htim, channel);
		return;
	}

	HAL_TIM_PWM_Start(htim, channel);
	if (velocity > 0) {
		HAL_GPIO_WritePin(port, pin_a, GPIO_PIN_SET);
		HAL_GPIO_WritePin(port, pin_b, GPIO_PIN_RESET);
		__HAL_TIM_SetCompare(htim, channel, velocity);
	} else {
		HAL_GPIO_WritePin(port, pin_a, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(port, pin_b, GPIO_PIN_SET);
		__HAL_TIM_SetCompare(htim, channel, -velocity);
	}
}

void fright_motor(int velocity)
{
	set_hbridge(GPIOG, GPIO_PIN_12, GPIO_PIN_13, &htim1, TIM_CHANNEL_2, velocity);
}

void bright_motor(int velocity)
{
	set_hbridge(GPIOG, GPIO_PIN_10, GPIO_PIN_11, &htim1, TIM_CHANNEL_3, velocity);
}

void fleft_motor(int velocity)
{
	/* Lewa burta ma odwrotną polaryzację mostka względem prawej. */
	set_hbridge(GPIOE, GPIO_PIN_6, GPIO_PIN_5, &htim1, TIM_CHANNEL_4, velocity);
}

void bleft_motor(int velocity)
{
	set_hbridge(GPIOE, GPIO_PIN_4, GPIO_PIN_3, &htim1, TIM_CHANNEL_1, velocity);
}

void stepper_control(uint8_t enabled, GPIO_TypeDef *port, uint16_t pin, uint8_t dir_state,
		     TIM_HandleTypeDef *htim, GPIO_TypeDef *sleep_port, uint16_t sleep_pin)
{
	HAL_GPIO_WritePin(sleep_port, sleep_pin, enabled ? GPIO_PIN_SET : GPIO_PIN_RESET);
	if (enabled) {
		HAL_GPIO_WritePin(port, pin, dir_state ? GPIO_PIN_SET : GPIO_PIN_RESET);
		HAL_TIM_Base_Start_IT(htim);	/* przerwania generują impulsy STEP */
	} else {
		HAL_TIM_Base_Stop_IT(htim);
	}
}
