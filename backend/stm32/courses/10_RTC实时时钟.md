# 第十章：RTC实时时钟

## 学习目标

完成本章后，你将能够：
- 理解 RTC 工作原理
- 配置实时时钟
- 使用备份寄存器

---

## 10.1 读写备份寄存器

### 实验目的
掌握 BKP 备份寄存器使用。

### 知识点
```
BKP容量: 10个16位寄存器
特点: 掉电保持（需VBAT供电）
用途: 存储重要数据、RTC校准
```

### 完整代码
```c
#include "stm32f10x.h"

void BKP_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_BKP, ENABLE);
    
    PWR_BackupAccessCmd(ENABLE);  // 允许访问备份域
}

void BKP_Write(uint16_t data)
{
    BKP_WriteBackupRegister(BKP_DR1, data);
}

uint16_t BKP_Read(void)
{
    return BKP_ReadBackupRegister(BKP_DR1);
}

int main(void)
{
    BKP_Init();
    
    uint16_t savedValue = BKP_Read();
    
    if (savedValue != 0xA5A5)  // 首次运行
    {
        BKP_Write(0xA5A5);
        // 初始化操作...
    }
    
    while (1)
    {
        
    }
}
```

---

## 10.2 实时时钟

### 实验目的
配置 RTC，实现日历功能。

### 完整代码
```c
#include "stm32f10x.h"

void RTC_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR | RCC_APB1Periph_BKP, ENABLE);
    PWR_BackupAccessCmd(ENABLE);
    
    if (BKP_ReadBackupRegister(BKP_DR1) != 0xA5A5)
    {
        BKP_DeInit();
        RCC_LSEConfig(RCC_LSE_ON);
        while (RCC_GetFlagStatus(RCC_FLAG_LSERDY) == RESET);
        
        RCC_RTCCLKConfig(RCC_RTCCLKSource_LSE);
        RCC_RTCCLKCmd(ENABLE);
        RTC_WaitForSynchro();
        RTC_WaitForLastTask();
        RTC_SetPrescaler(32767);
        RTC_WaitForLastTask();
        RTC_SetCounter(0);
        RTC_WaitForLastTask();
        
        BKP_WriteBackupRegister(BKP_DR1, 0xA5A5);
    }
    else
    {
        RCC_RTCCLKConfig(RCC_RTCCLKSource_LSE);
        RCC_RTCCLKCmd(ENABLE);
        RTC_WaitForSynchro();
        RTC_WaitForLastTask();
    }
}

uint32_t RTC_GetSeconds(void)
{
    return RTC_GetCounter();
}

int main(void)
{
    RTC_Init();
    
    while (1)
    {
        uint32_t seconds = RTC_GetSeconds();
        // 显示时间...
    }
}
```

---

*下一章：[低功耗模式](11_低功耗模式.md)*
