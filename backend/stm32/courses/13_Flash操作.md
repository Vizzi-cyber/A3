# 第十三章：Flash操作

## 学习目标

完成本章后，你将能够：
- 读写内部 Flash
- 读取芯片唯一ID

---

## 13.1 读写内部Flash

### 知识点
```
STM32F103C8T6 Flash: 64KB
页大小: 1KB
写入: 半字(16位)编程
擦除: 页擦除
```

### 代码
```c
#include "stm32f10x.h"

#define FLASH_SAVE_ADDR  0x0800FC00  // 最后一页

void Flash_Write(uint32_t addr, uint16_t *data, uint16_t len)
{
    FLASH_Unlock();
    
    FLASH_ErasePage(FLASH_SAVE_ADDR);
    
    for (uint16_t i = 0; i < len; i++)
    {
        FLASH_ProgramHalfWord(addr + i * 2, data[i]);
    }
    
    FLASH_Lock();
}

void Flash_Read(uint32_t addr, uint16_t *data, uint16_t len)
{
    for (uint16_t i = 0; i < len; i++)
    {
        data[i] = *(volatile uint16_t *)(addr + i * 2);
    }
}

int main(void)
{
    uint16_t writeData[3] = {0x1234, 0x5678, 0xABCD};
    uint16_t readData[3];
    
    Flash_Write(FLASH_SAVE_ADDR, writeData, 3);
    Flash_Read(FLASH_SAVE_ADDR, readData, 3);
    
    while (1)
    {
        
    }
}
```

---

## 13.2 读取芯片ID

### 代码
```c
#include "stm32f10x.h"

uint32_t Get_ChipID(void)
{
    return *(volatile uint32_t *)(0x1FFFF7E8);  // 唯一ID低32位
}

int main(void)
{
    uint32_t chipID = Get_ChipID();
    // 显示ID...
    
    while (1)
    {
        
    }
}
```

---

*课程结束！返回[课程目录](INDEX.md)*
