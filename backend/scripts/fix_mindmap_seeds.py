import re

with open("seed_resource_data.py", "r", encoding="utf-8") as f:
    content = f.read()

# Each replacement is (old_text_fragment_unique_to_this_block, new_markmap_text)
# We use the unique text to find each block

# 1. C语言指针 - identify by unique combination
old1 = '''"mindmap": {
                "root": "C语言指针",'''
new1 = '''"mindmap": "# C语言指针\\n## 基础概念\\n### 什么是指针\\n### 指针的声明与初始化\\n### 取地址运算符 &\\n### 解引用运算符 *\\n## 指针运算\\n### 指针加减\\n### 指针比较\\n### 指针与数组的关系\\n## 指针与函数\\n### 指针作为参数（传址调用）\\n### 指针作为返回值\\n### 函数指针\\n## 多级指针\\n### 二级指针 int **pp\\n### 指针数组 int *arr[]\\n## 常见陷阱\\n### 野指针\\n### 悬挂指针\\n### 内存泄漏\\n### 空指针解引用",'''

idx = content.find(old1)
if idx >= 0:
    # Find the closing "mindmap" block - need to find the matching closing }},
    # which is followed by a line with just 2 spaces and },
    start = idx
    # Find the closing "            }," that ends the resources dict
    search_start = idx + len(old1)
    # Search for the pattern: closing of mindmap dict then closing of resources dict
    end_pattern = "            },\n        },\n    },"
    end_idx = content.find(end_pattern, search_start)
    if end_idx >= 0:
        end_idx += len(end_pattern)
        content = content[:start] + new1 + content[end_idx:]
        print("OK: C语言指针")
    else:
        print("FAIL: C语言指针 - end not found")
else:
    print("FAIL: C语言指针 - start not found")

# 2. C语言函数与递归
old2 = '''"mindmap": {
                "root": "C语言函数与递归",'''
new2 = '''"mindmap": "# C语言函数与递归\\n## 函数基础\\n### 函数声明（原型）\\n### 函数定义\\n### 函数调用\\n### 返回值\\n## 参数传递\\n### 值传递\\n### 指针传递（传址）\\n### 数组传参\\n## 递归\\n### 递归三要素\\n### 阶乘\\n### 斐波那契数列\\n### 汉诺塔\\n## 作用域\\n### 局部变量\\n### 全局变量\\n### static 变量",'''

idx = content.find(old2)
if idx >= 0:
    start = idx
    end_idx = content.find("            },\n        },\n    },", idx + len(old2))
    if end_idx >= 0:
        end_idx += len("            },\n        },\n    },")
        content = content[:start] + new2 + content[end_idx:]
        print("OK: C语言函数与递归")
    else:
        print("FAIL: C语言函数与递归 - end")
else:
    print("FAIL: C语言函数与递归 - start")

# 3. 电路基本定律
old3 = '''"mindmap": {
                "root": "电路基本定律",'''
new3 = '''"mindmap": "# 电路基本定律\\n## 欧姆定律\\n### V = IR\\n### 适用条件：线性电阻\\n### 功率 P = VI\\n## 基尔霍夫定律\\n### KCL（电流定律）\\n#### 节点电流守恒\\n#### I_in = I_out\\n### KVL（电压定律）\\n#### 回路电压守恒\\n#### V_rise = V_drop\\n## 功率\\n### P = VI\\n### P = I\\u00b2R\\n### P = V\\u00b2/R",'''

idx = content.find(old3)
if idx >= 0:
    start = idx
    end_idx = content.find("            },\n        },\n    },", idx + len(old3))
    if end_idx >= 0:
        end_idx += len("            },\n        },\n    },")
        content = content[:start] + new3 + content[end_idx:]
        print("OK: 电路基本定律")
    else:
        print("FAIL: 电路基本定律 - end")
else:
    print("FAIL: 电路基本定律 - start")

# 4. 电路等效变换
old4 = '''"mindmap": {
                "root": "电路等效变换",'''
new4 = '''"mindmap": "# 电路等效变换\\n## 电阻连接\\n### 串联：R_eq = R1 + R2\\n### 并联：1/R_eq = 1/R1 + 1/R2\\n## 星三角变换\\n### \\u0394 \\u2192 Y\\n### Y \\u2192 \\u0394\\n### 对称情况简化\\n## 等效电源\\n### 戴维南定理\\n### 诺顿定理\\n### 两者互换\\n## 叠加定理\\n### 线性电路适用\\n### 分别计算各电源贡献\\n### 代数求和",'''

idx = content.find(old4)
if idx >= 0:
    start = idx
    # Different end pattern because it's before the 练习题 section (different indentation)
    # The structure is: mindmap dict closing -> resources closing -> record closing
    end_idx = content.find("            },\n        },\n    },\n", idx + len(old4))
    # Try without trailing newline
    if end_idx < 0:
        end_idx = content.find("            },\n        },\n    },\n", idx + len(old4))
    if end_idx < 0:
        # Look for the pattern that ends this record before the next comment/record
        rest = content[idx + len(old4):]
        # Find the closing pattern: the mindmap closes, then resources, then record
        # Pattern: "            },\n        },\n    },\n\n"
        search_pattern = "            },\n        },\n    },\n"
        end_idx = content.find(search_pattern, idx + len(old4))
        if end_idx >= 0:
            end_idx += len(search_pattern)
        else:
            end_idx = -1

    if end_idx >= 0:
        content = content[:start] + new4 + content[end_idx:]
        print("OK: 电路等效变换")
    else:
        print("FAIL: 电路等效变换 - end not found")
else:
    print("FAIL: 电路等效变换 - start")

with open("seed_resource_data.py", "w", encoding="utf-8") as f:
    f.write(content)

import ast
try:
    ast.parse(content)
    print("\nPython syntax: OK")
except SyntaxError as e:
    print(f"\nSyntax error: {e}")
