# 计算机设计实践 lab-6：RISC-V CPU

武汉大学国家网络安全学院 - 计算机设计实践课程实验。

基于 RISC-V RV32I 指令集，使用 Verilog HDL 设计并实现：

- **单周期 CPU**（`source-sc/`）— 支持30+条指令的RV32I子集
- **五级流水线 CPU**（`source-pl/`）— 完整实现数据冒险转发、load-use阻塞与跳转冲刷

并在Nexys 4 DDR开发板上完成学号排序的硬件演示。

## 目录结构

| 路径 | 内容 |
|---|---|
| `source-sc/` | 单周期CPU源代码 + testbench |
| `source-pl/` | 流水线CPU源代码 + testbench |
| `fpga-src/` | FPGA上板顶层模块（时钟分频、数码管显示等） |
| `testcode/` | 测试程序（.asm汇编 + .dat机器码） |
| `constraints/` | Nexys4 DDR引脚约束文件 |
| `diff-report/` | 代码diff报告 |
| `tools/` | 辅助脚本（diff报告生成） |

## 实验环境

- **硬件描述语言**：Verilog HDL
- **仿真工具**：iverilog + vvp
- **汇编工具**：RARS (rars1_6.jar)
- **综合工具**：Vivado 2017.4
- **开发板**：Nexys 4 DDR (XC7A100TCSG324-1)

## 实验结果

- 单周期 + 流水线CPU均通过 `Test_30_Instr.dat` 综合指令测试
- 单周期 + 流水线CPU均通过 `riscv_sidascsorting_sim.dat` 学号排序仿真，自动检查输出 `[PASS]`
- 流水线 CPU 通过 fwd / jmpflush / jmpfwd0 / jmpfwd1 四组冒险分步测试
- FPGA 上板：拨码开关 sw_i[0]=1 时显示原始学号 02181164，sw_i[0]=0 时显示排序结果 01112468

## 实验报告

见 [穆宣言-2024302181164.docx](./docs/穆宣言-2024302181164.docx)

## 快速运行

### 单周期CPU仿真

```powershell
cd source-sc
.\build.bat
```

成功时输出：

```text
[RESULT] original_sid=02181164
[RESULT] sorted_sid=01112468
[PASS] lab-6 sid sorting simulation passed.
```
