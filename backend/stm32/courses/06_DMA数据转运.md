# 第六章：DMA数据转运

## 学习目标

完成本章后，你将能够：
- 理解 DMA 工作原理
- 配置 DMA 进行内存到内存传输
- 使用 DMA 配合 ADC 实现高效采集

---

## 6.1 DMA基础 - 内存到内存

### 实验目的
掌握 DMA 基本配置，实现内存数据拷贝。

### 知识点：DMA原理

#### DMA参数
```
传输方向: 内存→内存 / 外设→内存 / 内存→外设
传输宽度: 字节(8位) / 半字(16位) / 字(32位)
传输数量: 0~65535
```

### 完整代码
```c
#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"

#define BUFFER_SIZE 10

uint16_t srcBuffer[BUFFER_SIZE] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
uint16_t dstBuffer[BUFFER_SIZE];

void DMA_Init(void)
{
    // 1. 开启DMA时钟
    RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
    
    // 2. 配置DMA通道
    DMA_InitTypeDef DMA_InitStructure;
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)srcBuffer;      // 源地址
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)dstBuffer;          // 目标地址
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;                   // 外设为源
    DMA_InitStructure.DMA_BufferSize = BUFFER_SIZE;                      // 传输数量
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Enable;      // 源地址自增
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;              // 目标地址自增
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord;  // 16位
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;                        // 正常模式
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
    DMA_InitStructure.DMA_M2M = DMA_M2M_Enable;                         // 内存到内存
    DMA_Init(DMA1_Channel1, &DMA_InitStructure);
}

int main(void)
{
    OLED_Init();
    DMA_Init();
    
    char buffer[20];
    
    // 显示源数据
    OLED_ShowString(0, 0, "Source:");
    for (int i = 0; i < BUFFER_SIZE; i++)
    {
        sprintf(buffer, "%d ", srcBuffer[i]);
        OLED_ShowString(48 + i * 18, 0, buffer);
    }
    
    // 启动DMA传输
    DMA_Cmd(DMA1_Channel1, ENABLE);
    while (DMA_GetFlagStatus(DMA1_IT_TC1) == RESET);  // 等待传输完成
    DMA_ClearFlag(DMA1_IT_TC1);
    
    // 显示目标数据
    OLED_ShowString(0, 2, "Dest:");
    for (int i = 0; i < BUFFER_SIZE; i++)
    {
        sprintf(buffer, "%d ", dstBuffer[i]);
        OLED_ShowString(48 + i * 18, 2, buffer);
    }
    
    while (1)
    {
        
    }
}
```

### 实验现象
DMA 将源缓冲区数据复制到目标缓冲区。

---

## 6.2 DMA+ADC多通道

### 实验目的
使用 DMA 自动传输 ADC 采集数据。

### 完整代码
```c
#include "stm32f10x.h"
#include "Delay.h"

#define ADC_CH_NUM  2

uint16_t adcBuffer[ADC_CH_NUM];

void ADC_DMA_Init(void)
{
    // ADC初始化（同步骤）
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_ADCCLKConfig(RCC_PCLK2_Div6);
    
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AIN;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    ADC_InitTypeDef ADC_InitStructure;
    ADC_InitStructure.ADC_Mode = ADC_Mode_Independent;
    ADC_InitStructure.ADC_ScanConvMode = ENABLE;
    ADC_InitStructure.ADC_ContinuousConvMode = ENABLE;      // 连续转换
    ADC_InitStructure.ADC_ExternalTrigConv = ADC_ExternalTrigConv_None;
    ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
    ADC_InitStructure.ADC_NbrOfChannel = ADC_CH_NUM;
    ADC_Init(ADC1, &ADC_InitStructure);
    
    ADC_RegularChannelConfig(ADC1, ADC_Channel_0, 1, ADC_SampleTime_239Cycles5);
    ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 2, ADC_SampleTime_239Cycles5);
    
    // DMA初始化
    RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
    
    DMA_InitTypeDef DMA_InitStructure;
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&ADC1->DR;  // ADC数据寄存器
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)adcBuffer;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;
    DMA_InitStructure.DMA_BufferSize = ADC_CH_NUM;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;  // 外设地址不增
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;                    // 循环模式
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
    DMA_InitStructure.DMA_M2M = DMA_M2M_Disable;
    DMA_Init(DMA1_Channel1, &DMA_InitStructure);
    
    // 使能DMA
    DMA_Cmd(DMA1_Channel1, ENABLE);
    ADC_DMACmd(ADC1, ENABLE);
    
    // ADC校准
    ADC_ResetCalibration(ADC1);
    while (ADC_GetResetCalibrationStatus(ADC1));
    ADC_StartCalibration(ADC1);
    while (ADC_GetCalibrationStatus(ADC1));
    
    // 启动ADC
    ADC_Cmd(ADC1, ENABLE);
    ADC_SoftwareStartConvCmd(ADC1, ENABLE);
}

int main(void)
{
    ADC_DMA_Init();
    
    while (1)
    {
        // adcBuffer[0]和adcBuffer[1]会自动更新
        float v0 = (float)adcBuffer[0] / 4095 * 3.3;
        float v1 = (float)adcBuffer[1] / 4095 * 3.3;
        
        // 显示或处理数据...
    }
}
```

---

## 本章小结

| 技能 | 掌握程度 |
|------|----------|
| DMA基础配置 | ☐ 独立完成 |
| 内存到内存传输 | ☐ 独立完成 |
| DMA+ADC | ☐ 独立完成 |
| 循环模式 | ☐ 独立完成 |

---

*下一章：[串口通信](07_串口通信.md)*
