import type { CircuitTemplate } from "./types";

export const circuitTemplates: CircuitTemplate[] = [
  {
    id: "stm32-led-blink",
    name: "LED 闪烁 (STM32)",
    description:
      "STM32 GPIO 输出控制 LED，使用标准库 GPIO_SetBits/ResetBits 实现闪烁",
    difficulty: "beginner",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 200,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "led1",
        type: "led",
        x: 440,
        y: 100,
        rotation: 0,
        props: { color: "#ff3333", forwardVoltage: 2.0, maxCurrent: 20 },
        label: "LED",
      },
      {
        id: "r1",
        type: "resistor",
        x: 440,
        y: 200,
        rotation: 0,
        props: { resistance: 220, unit: "Ω" },
        label: "220Ω",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA0" },
        to: { componentId: "led1", pinId: "anode" },
        waypoints: [
          { x: 350, y: 106 },
          { x: 390, y: 80 },
          { x: 430, y: 90 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "led1", pinId: "cathode" },
        to: { componentId: "r1", pinId: "pin1" },
        waypoints: [
          { x: 450, y: 160 },
          { x: 430, y: 190 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "r1", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 510, y: 220 },
          { x: 470, y: 250 },
          { x: 340, y: 230 },
          { x: 320, y: 160 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include "Delay.h"

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    while (1)
    {
        GPIO_ResetBits(GPIOA, GPIO_Pin_0);  // LED 亮（低电平驱动）
        Delay_ms(500);
        GPIO_SetBits(GPIOA, GPIO_Pin_0);    // LED 灭
        Delay_ms(500);
    }
}`,
  },
  {
    id: "stm32-button-led",
    name: "按键控制 LED (STM32)",
    description: "GPIO 输入检测按键，上拉输入模式，按下时切换 LED 状态",
    difficulty: "beginner",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 180,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "btn1",
        type: "button",
        x: 420,
        y: 80,
        rotation: 0,
        props: { momentary: true, pressed: false },
        label: "按键",
      },
      {
        id: "led1",
        type: "led",
        x: 420,
        y: 220,
        rotation: 0,
        props: { color: "#33cc33" },
        label: "LED",
      },
      {
        id: "r1",
        type: "resistor",
        x: 500,
        y: 220,
        rotation: 0,
        props: { resistance: 220 },
        label: "220Ω",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA1" },
        to: { componentId: "btn1", pinId: "pin1" },
        waypoints: [
          { x: 330, y: 119 },
          { x: 380, y: 95 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "btn1", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 470, y: 105 },
          { x: 480, y: 145 },
          { x: 340, y: 155 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "mcu1", pinId: "PA0" },
        to: { componentId: "led1", pinId: "anode" },
        waypoints: [
          { x: 340, y: 136 },
          { x: 400, y: 200 },
          { x: 430, y: 215 },
        ],
      },
      {
        id: "w4",
        from: { componentId: "led1", pinId: "cathode" },
        to: { componentId: "r1", pinId: "pin1" },
        waypoints: [
          { x: 445, y: 280 },
          { x: 490, y: 240 },
        ],
      },
      {
        id: "w5",
        from: { componentId: "r1", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 565, y: 235 },
          { x: 580, y: 260 },
          { x: 350, y: 250 },
          { x: 325, y: 165 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include "Delay.h"

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;

    // PA0: 推挽输出 (LED)
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    // PA1: 上拉输入 (按键)
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    while (1)
    {
        if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)
        {
            Delay_ms(20);  // 消抖
            if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)
            {
                GPIO_WriteBit(GPIOA, GPIO_Pin_0,
                    (BitAction)(1 - GPIO_ReadOutputDataBit(GPIOA, GPIO_Pin_0)));
                while (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0);
            }
        }
    }
}`,
  },
  {
    id: "stm32-pwm-breathing",
    name: "PWM 呼吸灯 (STM32)",
    description: "使用 TIM2 CH1 输出 PWM，控制 LED 亮度渐变实现呼吸灯效果",
    difficulty: "intermediate",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 180,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "led1",
        type: "led",
        x: 420,
        y: 100,
        rotation: 0,
        props: { color: "#ff3333" },
        label: "LED",
      },
      {
        id: "r1",
        type: "resistor",
        x: 420,
        y: 200,
        rotation: 0,
        props: { resistance: 220 },
        label: "220Ω",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA0" },
        to: { componentId: "led1", pinId: "anode" },
        waypoints: [
          { x: 330, y: 106 },
          { x: 380, y: 80 },
          { x: 410, y: 90 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "led1", pinId: "cathode" },
        to: { componentId: "r1", pinId: "pin1" },
        waypoints: [
          { x: 430, y: 160 },
          { x: 415, y: 190 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "r1", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 490, y: 215 },
          { x: 460, y: 245 },
          { x: 340, y: 230 },
          { x: 320, y: 160 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include "Delay.h"

void PWM_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
    TIM_TimeBaseStructure.TIM_Period = 100 - 1;
    TIM_TimeBaseStructure.TIM_Prescaler = 0;
    TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);

    TIM_OCInitTypeDef TIM_OCInitStructure;
    TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
    TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OCInitStructure.TIM_Pulse = 0;
    TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;
    TIM_OC1Init(TIM2, &TIM_OCInitStructure);

    TIM_Cmd(TIM2, ENABLE);
}

int main(void)
{
    PWM_Init();
    uint8_t i;
    while (1)
    {
        for (i = 0; i <= 100; i++)
        {
            TIM_SetCompare1(TIM2, i);
            Delay_ms(10);
        }
        for (i = 0; i <= 100; i++)
        {
            TIM_SetCompare1(TIM2, 100 - i);
            Delay_ms(10);
        }
    }
}`,
  },
  {
    id: "stm32-servo",
    name: "舵机控制 (STM32)",
    description: "使用 TIM2 产生 50Hz PWM 信号控制 SG90 舵机角度",
    difficulty: "intermediate",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 180,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "servo1",
        type: "servo",
        x: 420,
        y: 100,
        rotation: 0,
        props: { angle: 90, minAngle: 0, maxAngle: 180 },
        label: "SG90 舵机",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA0" },
        to: { componentId: "servo1", pinId: "signal" },
        waypoints: [
          { x: 340, y: 115 },
          { x: 400, y: 95 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "mcu1", pinId: "5V" },
        to: { componentId: "servo1", pinId: "vcc" },
        waypoints: [
          { x: 280, y: 55 },
          { x: 350, y: 50 },
          { x: 420, y: 70 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "servo1", pinId: "gnd" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 445, y: 160 },
          { x: 400, y: 190 },
          { x: 280, y: 180 },
          { x: 250, y: 100 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include "Delay.h"

void Servo_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
    TIM_TimeBaseStructure.TIM_Period = 20000 - 1;  // 20ms 周期
    TIM_TimeBaseStructure.TIM_Prescaler = 72 - 1;   // 1MHz 计数频率
    TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);

    TIM_OCInitTypeDef TIM_OCInitStructure;
    TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
    TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OCInitStructure.TIM_Pulse = 1500;  // 90° 初始位置
    TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;
    TIM_OC1Init(TIM2, &TIM_OCInitStructure);

    TIM_Cmd(TIM2, ENABLE);
}

void Servo_SetAngle(uint16_t angle)
{
    uint16_t pulse = 500 + angle * 2000 / 180;
    TIM_SetCompare1(TIM2, pulse);
}

int main(void)
{
    Servo_Init();
    while (1)
    {
        Servo_SetAngle(0);
        Delay_ms(1000);
        Servo_SetAngle(90);
        Delay_ms(1000);
        Servo_SetAngle(180);
        Delay_ms(1000);
    }
}`,
  },
  {
    id: "stm32-uart",
    name: "串口通信 (STM32)",
    description: "配置 USART1 实现串口发送，通过 printf 重定向输出调试信息",
    difficulty: "intermediate",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 180,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "usb1",
        type: "usb_ttl",
        x: 420,
        y: 100,
        rotation: 0,
        props: {},
        label: "USB-TTL",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA9" },
        to: { componentId: "usb1", pinId: "RXD" },
        waypoints: [
          { x: 340, y: 168 },
          { x: 400, y: 130 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "mcu1", pinId: "PA10" },
        to: { componentId: "usb1", pinId: "TXD" },
        waypoints: [
          { x: 345, y: 179 },
          { x: 400, y: 155 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "mcu1", pinId: "GND1" },
        to: { componentId: "usb1", pinId: "GND" },
        waypoints: [
          { x: 310, y: 90 },
          { x: 380, y: 80 },
          { x: 430, y: 130 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include <stdio.h>

void USART1_Init(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    // PA9: TX - 复用推挽输出
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    // PA10: RX - 浮空输入
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    USART_InitTypeDef USART_InitStructure;
    USART_InitStructure.USART_BaudRate = 115200;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
    USART_Init(USART1, &USART_InitStructure);

    USART_Cmd(USART1, ENABLE);
}

// printf 重定向
int fputc(int ch, FILE *f)
{
    USART_SendData(USART1, (uint8_t)ch);
    while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
    return ch;
}

int main(void)
{
    USART1_Init();
    printf("Hello STM32!\\r\\n");
    printf("USART1 OK at 115200bps\\r\\n");
    while (1)
    {
        printf("TICK\\r\\n");
        // Delay_ms(1000);
    }
}`,
  },
  {
    id: "stm32-mpu6050",
    name: "MPU6050 传感器 (STM32)",
    description: "通过 I2C 读取 MPU6050 六轴传感器数据，OLED 显示加速度",
    difficulty: "advanced",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 160,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "mpu1",
        type: "mpu6050",
        x: 400,
        y: 80,
        rotation: 0,
        props: { address: "0x68", ax: 0, ay: 0, az: 0 },
        label: "MPU6050",
      },
      {
        id: "oled1",
        type: "oled_ssd1306",
        x: 400,
        y: 220,
        rotation: 0,
        props: { address: "0x3C", width: 128, height: 64 },
        label: "OLED 显示屏",
      },
    ],
    wires: [
      // I2C bus (shared)
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PB10" },
        to: { componentId: "mpu1", pinId: "SCL" },
        waypoints: [
          { x: 310, y: 135 },
          { x: 370, y: 110 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "mcu1", pinId: "PB11" },
        to: { componentId: "mpu1", pinId: "SDA" },
        waypoints: [
          { x: 315, y: 147 },
          { x: 370, y: 120 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "mcu1", pinId: "PB10" },
        to: { componentId: "oled1", pinId: "SCL" },
        waypoints: [
          { x: 305, y: 140 },
          { x: 340, y: 200 },
          { x: 380, y: 245 },
        ],
      },
      {
        id: "w4",
        from: { componentId: "mcu1", pinId: "PB11" },
        to: { componentId: "oled1", pinId: "SDA" },
        waypoints: [
          { x: 310, y: 152 },
          { x: 345, y: 210 },
          { x: 385, y: 255 },
        ],
      },
      // Power
      {
        id: "w5",
        from: { componentId: "mcu1", pinId: "3V3" },
        to: { componentId: "mpu1", pinId: "VCC" },
        waypoints: [
          { x: 215, y: 55 },
          { x: 350, y: 50 },
          { x: 395, y: 80 },
        ],
      },
      {
        id: "w6",
        from: { componentId: "mcu1", pinId: "GND1" },
        to: { componentId: "mpu1", pinId: "GND" },
        waypoints: [
          { x: 235, y: 55 },
          { x: 360, y: 60 },
          { x: 395, y: 90 },
        ],
      },
      {
        id: "w7",
        from: { componentId: "mcu1", pinId: "3V3" },
        to: { componentId: "oled1", pinId: "VCC" },
        waypoints: [
          { x: 210, y: 65 },
          { x: 200, y: 200 },
          { x: 380, y: 230 },
        ],
      },
      {
        id: "w8",
        from: { componentId: "mcu1", pinId: "GND1" },
        to: { componentId: "oled1", pinId: "GND" },
        waypoints: [
          { x: 230, y: 65 },
          { x: 210, y: 210 },
          { x: 380, y: 240 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"
// MPU6050 I2C 驱动（软件 I2C）

#define MPU6050_ADDR  0xD0

void MPU6050_WriteReg(uint8_t reg, uint8_t data)
{
    // I2C 起始 -> 设备地址 -> 寄存器地址 -> 数据 -> 停止
    // （简化示例，实际需实现完整的 I2C 时序）
}

uint8_t MPU6050_ReadReg(uint8_t reg)
{
    // I2C 读取单个寄存器
    return 0;
}

void MPU6050_Init(void)
{
    MPU6050_WriteReg(0x6B, 0x80);  // 复位
    Delay_ms(100);
    MPU6050_WriteReg(0x6B, 0x00);  // 唤醒
    MPU6050_WriteReg(0x1B, 0x00);  // 陀螺仪 ±250°/s
    MPU6050_WriteReg(0x1C, 0x00);  // 加速度计 ±2g
}

void MPU6050_ReadAccel(int16_t *ax, int16_t *ay, int16_t *az)
{
    *ax = (MPU6050_ReadReg(0x3B) << 8) | MPU6050_ReadReg(0x3C);
    *ay = (MPU6050_ReadReg(0x3D) << 8) | MPU6050_ReadReg(0x3E);
    *az = (MPU6050_ReadReg(0x3F) << 8) | MPU6050_ReadReg(0x40);
}

int main(void)
{
    OLED_Init();
    MPU6050_Init();

    OLED_ShowString(1, 1, "MPU6050 Ready");

    int16_t ax, ay, az;
    while (1)
    {
        MPU6050_ReadAccel(&ax, &ay, &az);
        OLED_ShowSignedNum(2, 1, ax, 5);
        OLED_ShowSignedNum(3, 1, ay, 5);
        OLED_ShowSignedNum(4, 1, az, 5);
        Delay_ms(100);
    }
}`,
  },
  {
    id: "stm32-light-buzzer",
    name: "光敏传感器控蜂鸣器 (STM32)",
    description: "光敏传感器检测光照，光照不足时蜂鸣器报警",
    difficulty: "beginner",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 180,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "ir1",
        type: "ir_sensor",
        x: 420,
        y: 80,
        rotation: 0,
        props: { detected: false },
        label: "光敏传感器",
      },
      {
        id: "buzzer1",
        type: "buzzer",
        x: 420,
        y: 220,
        rotation: 0,
        props: { frequency: 2000, active: false },
        label: "蜂鸣器",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA1" },
        to: { componentId: "ir1", pinId: "OUT" },
        waypoints: [
          { x: 330, y: 119 },
          { x: 390, y: 115 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "mcu1", pinId: "3V3" },
        to: { componentId: "ir1", pinId: "VCC" },
        waypoints: [
          { x: 270, y: 55 },
          { x: 360, y: 50 },
          { x: 415, y: 80 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "mcu1", pinId: "GND1" },
        to: { componentId: "ir1", pinId: "GND" },
        waypoints: [
          { x: 285, y: 55 },
          { x: 370, y: 60 },
          { x: 420, y: 95 },
        ],
      },
      {
        id: "w4",
        from: { componentId: "mcu1", pinId: "PA2" },
        to: { componentId: "buzzer1", pinId: "positive" },
        waypoints: [
          { x: 335, y: 136 },
          { x: 390, y: 210 },
          { x: 430, y: 218 },
        ],
      },
      {
        id: "w5",
        from: { componentId: "buzzer1", pinId: "negative" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 440, y: 270 },
          { x: 400, y: 290 },
          { x: 300, y: 250 },
          { x: 290, y: 150 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;

    // PA1: 上拉输入（传感器）
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    // PA2: 推挽输出（蜂鸣器）
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    while (1)
    {
        if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)
            GPIO_SetBits(GPIOA, GPIO_Pin_2);    // 光照不足，蜂鸣器响
        else
            GPIO_ResetBits(GPIOA, GPIO_Pin_2);  // 光照充足，蜂鸣器停
    }
}`,
  },
  {
    id: "stm32-traffic-light",
    name: "交通灯控制器 (STM32)",
    description: "红黄绿三色 LED 模拟交通灯，PA0/PA1/PA2 分别控制，定时切换",
    difficulty: "beginner",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 160,
        y: 80,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "led_r",
        type: "led",
        x: 400,
        y: 80,
        rotation: 0,
        props: { color: "#ff0000", forwardVoltage: 2.0, maxCurrent: 20 },
        label: "红灯",
      },
      {
        id: "led_y",
        type: "led",
        x: 400,
        y: 180,
        rotation: 0,
        props: { color: "#ffaa00", forwardVoltage: 2.0, maxCurrent: 20 },
        label: "黄灯",
      },
      {
        id: "led_g",
        type: "led",
        x: 400,
        y: 280,
        rotation: 0,
        props: { color: "#00cc00", forwardVoltage: 2.0, maxCurrent: 20 },
        label: "绿灯",
      },
      {
        id: "r1",
        type: "resistor",
        x: 500,
        y: 80,
        rotation: 0,
        props: { resistance: 220, unit: "Ω" },
        label: "220Ω",
      },
      {
        id: "r2",
        type: "resistor",
        x: 500,
        y: 180,
        rotation: 0,
        props: { resistance: 220, unit: "Ω" },
        label: "220Ω",
      },
      {
        id: "r3",
        type: "resistor",
        x: 500,
        y: 280,
        rotation: 0,
        props: { resistance: 220, unit: "Ω" },
        label: "220Ω",
      },
    ],
    wires: [
      // PA0 → 红灯 (水平直线)
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA0" },
        to: { componentId: "led_r", pinId: "anode" },
        waypoints: [],
      },
      // 红灯 → R1 (短水平)
      {
        id: "w2",
        from: { componentId: "led_r", pinId: "cathode" },
        to: { componentId: "r1", pinId: "pin1" },
        waypoints: [],
      },
      // R1 → GND (向左回连)
      {
        id: "w3",
        from: { componentId: "r1", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 560, y: 92 },
          { x: 580, y: 120 },
          { x: 300, y: 120 },
        ],
      },
      // PA1 → 黄灯 (水平直线)
      {
        id: "w4",
        from: { componentId: "mcu1", pinId: "PA1" },
        to: { componentId: "led_y", pinId: "anode" },
        waypoints: [],
      },
      // 黄灯 → R2 (短水平)
      {
        id: "w5",
        from: { componentId: "led_y", pinId: "cathode" },
        to: { componentId: "r2", pinId: "pin1" },
        waypoints: [],
      },
      // R2 → GND (向左回连)
      {
        id: "w6",
        from: { componentId: "r2", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 560, y: 192 },
          { x: 575, y: 150 },
          { x: 300, y: 130 },
        ],
      },
      // PA2 → 绿灯 (水平直线)
      {
        id: "w7",
        from: { componentId: "mcu1", pinId: "PA2" },
        to: { componentId: "led_g", pinId: "anode" },
        waypoints: [],
      },
      // 绿灯 → R3 (短水平)
      {
        id: "w8",
        from: { componentId: "led_g", pinId: "cathode" },
        to: { componentId: "r3", pinId: "pin1" },
        waypoints: [],
      },
      // R3 → GND (向左回连)
      {
        id: "w9",
        from: { componentId: "r3", pinId: "pin2" },
        to: { componentId: "mcu1", pinId: "GND1" },
        waypoints: [
          { x: 560, y: 292 },
          { x: 570, y: 180 },
          { x: 300, y: 140 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"
#include "Delay.h"

// 交通灯控制器
// PA0 = 红灯, PA1 = 黄灯, PA2 = 绿灯

void LED_Init(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
}

void All_LED_Off(void)
{
    GPIO_SetBits(GPIOA, GPIO_Pin_0);  // 红灯灭（低电平驱动）
    GPIO_SetBits(GPIOA, GPIO_Pin_1);  // 黄灯灭
    GPIO_SetBits(GPIOA, GPIO_Pin_2);  // 绿灯灭
}

int main(void)
{
    LED_Init();
    All_LED_Off();

    while (1)
    {
        // 绿灯亮 5 秒
        All_LED_Off();
        GPIO_ResetBits(GPIOA, GPIO_Pin_2);  // 绿灯亮
        Delay_ms(5000);

        // 黄灯闪烁 3 次
        for (int i = 0; i < 3; i++)
        {
            All_LED_Off();
            GPIO_ResetBits(GPIOA, GPIO_Pin_1);  // 黄灯亮
            Delay_ms(500);
            GPIO_SetBits(GPIOA, GPIO_Pin_1);    // 黄灯灭
            Delay_ms(500);
        }

        // 红灯亮 5 秒
        All_LED_Off();
        GPIO_ResetBits(GPIOA, GPIO_Pin_0);  // 红灯亮
        Delay_ms(5000);

        // 黄灯闪烁 3 次
        for (int i = 0; i < 3; i++)
        {
            All_LED_Off();
            GPIO_ResetBits(GPIOA, GPIO_Pin_1);  // 黄灯亮
            Delay_ms(500);
            GPIO_SetBits(GPIOA, GPIO_Pin_1);    // 黄灯灭
            Delay_ms(500);
        }
    }
}`,
  },
  {
    id: "stm32-encoder",
    name: "旋转编码器计次 (STM32)",
    description: "使用外部中断读取旋转编码器的正反转和计数",
    difficulty: "advanced",
    components: [
      {
        id: "mcu1",
        type: "stm32_bluepill",
        x: 180,
        y: 60,
        rotation: 0,
        props: { board: "stm32f103c8t6", clock: 72 },
        label: "STM32F103C8T6",
      },
      {
        id: "enc1",
        type: "rotary_encoder",
        x: 420,
        y: 100,
        rotation: 0,
        props: { position: 0, direction: "clockwise" },
        label: "旋转编码器",
      },
    ],
    wires: [
      {
        id: "w1",
        from: { componentId: "mcu1", pinId: "PA0" },
        to: { componentId: "enc1", pinId: "CLK" },
        waypoints: [
          { x: 340, y: 110 },
          { x: 400, y: 105 },
        ],
      },
      {
        id: "w2",
        from: { componentId: "mcu1", pinId: "PA1" },
        to: { componentId: "enc1", pinId: "DT" },
        waypoints: [
          { x: 345, y: 119 },
          { x: 400, y: 120 },
        ],
      },
      {
        id: "w3",
        from: { componentId: "mcu1", pinId: "PA2" },
        to: { componentId: "enc1", pinId: "SW" },
        waypoints: [
          { x: 350, y: 128 },
          { x: 400, y: 135 },
        ],
      },
      {
        id: "w4",
        from: { componentId: "mcu1", pinId: "3V3" },
        to: { componentId: "enc1", pinId: "VCC" },
        waypoints: [
          { x: 270, y: 55 },
          { x: 360, y: 50 },
          { x: 455, y: 95 },
        ],
      },
      {
        id: "w5",
        from: { componentId: "mcu1", pinId: "GND1" },
        to: { componentId: "enc1", pinId: "GND" },
        waypoints: [
          { x: 280, y: 55 },
          { x: 370, y: 55 },
          { x: 455, y: 115 },
        ],
      },
    ],
    code: `#include "stm32f10x.h"

int16_t encoder_count = 0;

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;

    // PA0: 上拉输入 (CLK)
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    // 配置 EXTI0 中断（CLK 下降沿触发）
    GPIO_EXTILineConfig(GPIO_PortSourceGPIOA, GPIO_PinSource0);
    EXTI_InitTypeDef EXTI_InitStructure;
    EXTI_InitStructure.EXTI_Line = EXTI_Line0;
    EXTI_InitStructure.EXTI_Mode = EXTI_Mode_Interrupt;
    EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Falling;
    EXTI_InitStructure.EXTI_LineCmd = ENABLE;
    EXTI_Init(&EXTI_InitStructure);

    NVIC_SetPriority(EXTI0_IRQn, 2);
    NVIC_EnableIRQ(EXTI0_IRQn);

    while (1)
    {
        // 主循环可处理其他任务
    }
}

void EXTI0_IRQHandler(void)
{
    if (EXTI_GetITStatus(EXTI_Line0) != RESET)
    {
        if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)
            encoder_count++;   // 顺时针
        else
            encoder_count--;   // 逆时针
        EXTI_ClearITPendingBit(EXTI_Line0);
    }
}`,
  },
];
