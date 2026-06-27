# 第五章：ADC模数转换

## 学习目标

完成本章后，你将能够：
- 配置 ADC 进行模拟量采集
- 理解 ADC 转换原理
- 实现多通道采集

---

## 5.1 ADC单通道采集

### 实验目的
掌握 ADC 单通道配置，采集电位器电压。

### 硬件连接
```
STM32          电位器
PA0(ADC_IN0) ──── 中间引脚
3.3V ──────────── 一端
GND ───────────── 另一端
```

**接线图参考**: `1-1 接线图/7-1 AD单通道.jpg`

### 知识点：ADC原理

#### ADC参数
```
分辨率: 12位 (0~4095)
采样时间: 1.5 ~ 239.5 个周期
转换时间 = 采样时间 + 12.5 个周期

例：采样时间1.5周期，ADC时钟14MHz
转换时间 = 1.5 + 12.5 = 14个周期 = 1us
```

#### 电压计算
```
电压 = (ADC值 / 4095) * 3.3V
```

### 完整代码
```c
#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"

void ADC_Init(void)
{
    // 1. 开启时钟
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_ADCCLKConfig(RCC_PCLK2_Div6);  // ADC时钟 = 72MHz/6 = 12MHz
    
    // 2. 配置PA0为模拟输入
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AIN;     // 模拟输入
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // 3. ADC校准
    ADC_ResetCalibration(ADC1);
    while (ADC_GetResetCalibrationStatus(ADC1));
    ADC_StartCalibration(ADC1);
    while (ADC_GetCalibrationStatus(ADC1));
}

// 读取ADC值
uint16_t ADC_Read(void)
{
    ADC_SoftwareStartConvCmd(ADC1, ENABLE);            // 启动转换
    while (!ADC_GetFlagStatus(ADC1, ADC_FLAG_EOC));    // 等待转换完成
    return ADC_GetConversionValue(ADC1);               // 返回结果
}

int main(void)
{
    OLED_Init();
    ADC_Init();
    
    char buffer[20];
    
    while (1)
    {
        uint16_t adcValue = ADC_Read();
        float voltage = (float)adcValue / 4095 * 3.3;
        
        sprintf(buffer, "ADC: %d", adcValue);
        OLED_ShowString(0, 0, buffer);
        
        sprintf(buffer, "Voltage: %.2fV", voltage);
        OLED_ShowString(0, 2, buffer);
        
        Delay_ms(500);
    }
}
```

### 实验现象
OLED 显示 ADC 采集值和对应的电压值。

---

## 5.2 ADC多通道采集

### 实验目的
掌握 ADC 扫描模式，实现多通道采集。

### 硬件连接
```
STM32          传感器
PA0(ADC_IN0) ──── 光敏电阻模块AO
PA1(ADC_IN1) ──── 电位器中间引脚
```

**接线图参考**: `1-1 接线图/7-2 AD多通道.jpg`

### 完整代码
```c
#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"

#define ADC_CH_NUM  2

uint16_t adcBuffer[ADC_CH_NUM];  // ADC数据缓冲区

void ADC_Multi_Init(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_ADCCLKConfig(RCC_PCLK2_Div6);
    
    // 配置PA0, PA1为模拟输入
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AIN;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // ADC规则通道配置
    ADC_InitTypeDef ADC_InitStructure;
    ADC_InitStructure.ADC_Mode = ADC_Mode_Independent;
    ADC_InitStructure.ADC_ScanConvMode = ENABLE;        // 扫描模式
    ADC_InitStructure.ADC_ContinuousConvMode = DISABLE; // 单次转换
    ADC_InitStructure.ADC_ExternalTrigConv = ADC_ExternalTrigConv_None;
    ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
    ADC_InitStructure.ADC_NbrOfChannel = ADC_CH_NUM;
    ADC_Init(ADC1, &ADC_InitStructure);
    
    // 配置转换顺序
    ADC_RegularChannelConfig(ADC1, ADC_Channel_0, 1, ADC_SampleTime_239Cycles5);
    ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 2, ADC_SampleTime_239Cycles5);
    
    // 校准
    ADC_ResetCalibration(ADC1);
    while (ADC_GetResetCalibrationStatus(ADC1));
    ADC_StartCalibration(ADC1);
    while (ADC_GetCalibrationStatus(ADC1));
}

// 读取多通道ADC
void ADC_ReadMulti(void)
{
    for (int i = 0; i < ADC_CH_NUM; i++)
    {
        ADC_SoftwareStartConvCmd(ADC1, ENABLE);
        while (!ADC_GetFlagStatus(ADC1, ADC_FLAG_EOC));
        adcBuffer[i] = ADC_GetConversionValue(ADC1);
    }
}

int main(void)
{
    OLED_Init();
    ADC_Multi_Init();
    
    char buffer[20];
    
    while (1)
    {
        ADC_ReadMulti();
        
        float v0 = (float)adcBuffer[0] / 4095 * 3.3;
        float v1 = (float)adcBuffer[1] / 4095 * 3.3;
        
        sprintf(buffer, "CH0: %d (%.2fV)", adcBuffer[0], v0);
        OLED_ShowString(0, 0, buffer);
        
        sprintf(buffer, "CH1: %d (%.2fV)", adcBuffer[1], v1);
        OLED_ShowString(0, 2, buffer);
        
        Delay_ms(500);
    }
}
```

---

## 本章小结

| 技能 | 掌握程度 |
|------|----------|
| ADC初始化 | ☐ 独立完成 |
| 单通道采集 | ☐ 独立完成 |
| 多通道采集 | ☐ 独立完成 |
| 电压计算 | ☐ 独立完成 |

---

*下一章：[DMA数据转运](06_DMA数据转运.md)*
