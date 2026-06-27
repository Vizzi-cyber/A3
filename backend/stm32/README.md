# STM32 课程资源库

## 目录结构

```
stm32/
├── README.md                          # 本文件
├── knowledge_tree.json                # 知识点树形结构（含实验）
├── resources_full.json                # 完整资源清单（43个资源）
├── frontend_mapping.json              # 前端显示映射关系
├── database_seed.json                 # 数据库导入数据（旧版）
├── import_to_database.py              # 数据库导入脚本
│
├── courses/                           # 课程文档
│   ├── README.md                      # 课程总览
│   ├── INDEX.md                       # 课程索引
│   ├── 01_基础入门.md
│   ├── 02_显示模块.md
│   ├── 03_输入设备.md
│   ├── 04_定时器.md
│   ├── 05_ADC模数转换.md
│   ├── 06_DMA数据转运.md
│   ├── 07_串口通信.md
│   ├── 08_I2C通信.md
│   ├── 09_SPI通信.md
│   ├── 10_RTC实时时钟.md
│   ├── 11_低功耗模式.md
│   ├── 12_看门狗.md
│   └── 13_Flash操作.md
│
└── STM32Project-有注释版/             # Keil工程源码
    ├── 1-1 接线图/                    # 39张接线图（JPG）
    ├── 1-2 keilkill批处理/
    ├── 1-3 Delay函数模块/
    ├── 1-4 OLED驱动函数模块/
    ├── 2-1 STM32工程模板/
    ├── 3-1 LED闪烁/
    ├── 3-2 LED流水灯/
    ├── ... (共37个实验工程)
    └── 15-2 读取芯片ID/
```

## 数据文件说明

### 1. knowledge_tree.json
**用途**: 知识点树形结构，包含课程、知识点、实验的完整定义

**数据结构**:
- `courses`: 课程信息（1个课程）
- `knowledge_points`: 知识点（14个，分2层）
- `experiments`: 实验（7个完整实验）

**字段说明**:
```json
{
  "id": 1,
  "name": "STM32基础入门",
  "parent_id": null,           // 父节点ID
  "level": 1,                  // 层级
  "difficulty": "简单",
  "resource_ids": [1, 40, 43], // 关联的资源ID
  "experiment_ids": []          // 关联的实验ID
}
```

### 2. resources_full.json
**用途**: 完整资源清单，包含所有代码工程和接线图

**数据统计**:
- 代码工程: 43个
- 接线图: 39张
- 总计: 43条资源记录

**字段说明**:
```json
{
  "id": 1,
  "title": "STM32工程模板",
  "type": "code",                    // code/image/document
  "knowledge_id": 1,                 // 关联知识点
  "file_path": "STM32Project-有注释版/2-1 STM32工程模板/",
  "image_path": "STM32Project-有注释版/1-1 接线图/2-1 工程模板.jpg"
}
```

### 3. frontend_mapping.json
**用途**: 前端显示映射关系，包含图标、颜色、树形结构

**数据结构**:
```json
{
  "icon_mapping": {
    "chip": "💻",
    "output": "🔌",
    ...
  },
  "knowledge_tree": {
    "1": {
      "name": "STM32基础入门",
      "icon": "chip",
      "resources": [...],
      "experiments": [...]
    },
    ...
  }
}
```

## 导入数据库

### 方法1: 使用Python脚本

```bash
cd backend
python ../stm32/import_to_database.py
```

### 方法2: 手动导入

参考 `knowledge_tree.json` 和 `resources_full.json` 的数据结构，手动插入数据库。

## 前端使用

### 知识树显示

使用 `frontend_mapping.json` 中的 `knowledge_tree` 字段：

```javascript
import mapping from '@/assets/stm32/frontend_mapping.json';

// 获取根节点
const rootNode = mapping.knowledge_tree['1'];

// 获取子节点
const children = rootNode.children.map(id => mapping.knowledge_tree[id]);

// 显示资源列表
children.forEach(node => {
  node.resources.forEach(resource => {
    console.log(resource.title, resource.image);
  });
});
```

### 图标和颜色

```javascript
// 获取图标
const icon = mapping.icon_mapping[node.icon]; // 💻

// 获取难度颜色
const color = mapping.difficulty_labels[resource.difficulty].color; // #4CAF50
```

## 资源路径

所有资源路径相对于 `stm32/` 目录：

| 类型 | 路径格式 |
|------|----------|
| 代码工程 | `STM32Project-有注释版/{序号}-{名称}/` |
| 接线图 | `STM32Project-有注释版/1-1 接线图/{序号}-{名称}.jpg` |
| 课程文档 | `courses/{章节}.md` |

## 数据统计

| 类型 | 数量 |
|------|------|
| 课程 | 1 |
| 知识点（一级） | 1 |
| 知识点（二级） | 13 |
| 资源 | 43 |
| 实验 | 7 |
| 接线图 | 39 |
| 代码工程 | 37 |

## 注意事项

1. 所有文件路径都是相对于 `stm32/` 目录
2. 图片文件需要复制到前端项目的 `public/` 目录才能在浏览器中显示
3. 导入数据库前确保后端已创建好数据表
4. `resource_ids` 和 `experiment_ids` 是外键关联，需要先导入主表再导入关联表
