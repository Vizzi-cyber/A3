# 第九章：SPI通信

## 学习目标

完成本章后，你将能够：
- 掌握 SPI 协议时序
- 读写 W25Q64 Flash 存储器

---

## 9.1 软件SPI读写W25Q64

### 实验目的
软件模拟 SPI 时序，读写 W25Q64。

### 硬件连接
```
STM32          W25Q64模块
PA5(SCK) ────── CLK
PA7(MOSI) ───── DI
PA6(MISO) ───── DO
PA4 ─────────── CS
3.3V ────────── VCC
GND ────────── GND
```

**接线图参考**: `1-1 接线图/11-1 软件SPI读写W25Q64.jpg`

### 知识点：W25Q64

#### W25Q64参数
```
容量: 8MB (64Mbit)
扇区: 4KB
页: 256字节
```

#### W25Q64指令
```
0x9F: 读取制造商ID
0x03: 读数据
0x06: 写使能
0x02: 页编程
0x20: 扇区擦除
```

### 完整代码
```c
#include "stm32f10x.h"
#include "Delay.h"

#define W25Q64_CS_LOW()   GPIO_ResetBits(GPIOA, GPIO_Pin_4)
#define W25Q64_CS_HIGH()  GPIO_SetBits(GPIOA, GPIO_Pin_4)

void SPI_Init(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_4 | GPIO_Pin_5 | GPIO_Pin_7;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    GPIO_SetBits(GPIOA, GPIO_Pin_4);  // CS高
}

uint8_t SPI_TransferByte(uint8_t data)
{
    uint8_t recv = 0;
    for (int i = 0; i < 8; i++)
    {
        if (data & 0x80)
            GPIO_SetBits(GPIOA, GPIO_Pin_7);
        else
            GPIO_ResetBits(GPIOA, GPIO_Pin_7);
        
        data <<= 1;
        GPIO_SetBits(GPIOA, GPIO_Pin_5);   // SCK高
        recv <<= 1;
        if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_6))
            recv |= 0x01;
        GPIO_ResetBits(GPIOA, GPIO_Pin_5); // SCK低
    }
    return recv;
}

uint16_t W25Q64_ReadID(void)
{
    W25Q64_CS_LOW();
    SPI_TransferByte(0x9F);
    uint8_t manufacturer = SPI_TransferByte(0xFF);
    uint8_t device = SPI_TransferByte(0xFF);
    W25Q64_CS_HIGH();
    return (manufacturer << 8) | device;
}

void W25Q64_ReadData(uint32_t addr, uint8_t *buf, uint32_t len)
{
    W25Q64_CS_LOW();
    SPI_TransferByte(0x03);
    SPI_TransferByte(addr >> 16);
    SPI_TransferByte(addr >> 8);
    SPI_TransferByte(addr);
    for (uint32_t i = 0; i < len; i++)
    {
        buf[i] = SPI_TransferByte(0xFF);
    }
    W25Q64_CS_HIGH();
}

void W25Q64_WritePage(uint32_t addr, uint8_t *buf, uint32_t len)
{
    W25Q64_CS_LOW();
    SPI_TransferByte(0x06);  // 写使能
    W25Q64_CS_HIGH();
    
    W25Q64_CS_LOW();
    SPI_TransferByte(0x02);
    SPI_TransferByte(addr >> 16);
    SPI_TransferByte(addr >> 8);
    SPI_TransferByte(addr);
    for (uint32_t i = 0; i < len; i++)
    {
        SPI_TransferByte(buf[i]);
    }
    W25Q64_CS_HIGH();
}

int main(void)
{
    SPI_Init();
    
    uint16_t id = W25Q64_ReadID();
    // 显示ID...
    
    while (1)
    {
        
    }
}
```

---

*下一章：[RTC实时时钟](10_RTC实时时钟.md)*
