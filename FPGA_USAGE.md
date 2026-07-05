# Lab 6 机房上板操作说明

## 1. 上板前准备

去机房前，先确认 `lab-6` 目录中已经包含以下内容：

- 仿真参考工程：`source-sc/`
- 板级工程源码：`fpga-src/`
- Vivado 建工程脚本：`build.bat`
- Vivado Tcl 脚本：`scripts/`
- 开发板约束：`constraints/Nexys4DDR_Lab6_CPU.xdc`

本仓库当前已经按学号 `02181044` 配好了上板程序，数码管显示目标为：

```text
原学号：02181044
排序后：00112448
```

## 2. 到机房后先做什么

1. 把整个 `lab-6` 文件夹拷到机房电脑本地磁盘。
2. 打开 PowerShell 或命令提示符。
3. 进入：

```powershell
cd lab-6
```

4. 先确认机房电脑能找到 Vivado。

```powershell
Get-Command vivado
```

如果这条命令没有结果，也可以直接尝试下面的一键命令，脚本会自动检查常见安装路径。

## 3. 一键生成 Vivado 工程

运行：

```powershell
.\build.bat vivado
```

如果成功，会生成工程文件：

```text
lab-6\vivado\lab6_sid_sort_fpga\lab6_sid_sort_fpga.xpr
```

然后双击打开这个 `.xpr` 文件即可。

## 4. 在 Vivado 里生成 bitstream

打开工程后，按以下顺序操作：

1. 确认顶层模块是 `lab6_sid_sort_fpga_top`
2. 点击 `Run Synthesis`
3. 综合完成后点击 `Run Implementation`
4. 实现完成后点击 `Generate Bitstream`

如果你想直接在命令行里尝试生成 bitstream，也可以运行：

```powershell
.\build.bat bitstream
```

成功后会得到：

```text
lab-6\vivado\bitstream_check\lab6_sid_sort_fpga_top.bit
```

## 5. 下载到开发板

1. 用下载线连接 Nexys4 DDR 开发板和机房电脑。
2. 给开发板上电。
3. 在 Vivado 中打开 `Hardware Manager`
4. 点击 `Open Target`
5. 选择 `Auto Connect`
6. 找到器件后点击 `Program Device`
7. 选择生成的 `.bit` 文件
8. 点击 `Program`

下载完成后，程序就会开始运行。

## 6. 上板后如何观察结果

本工程中：

- `sw_i[15]` 用来控制 CPU 时钟快慢
- `sw_i[8]` 用来切换显示原学号还是排序后学号
- `sw_i[5:0]` 用来选择数码管显示通道

建议你按下面方式操作：

### 第一步：先让显示通道回到主结果

把 `SW[5:0]` 全部拨成 `0`。

这样数码管默认显示 CPU 真正写给显示口的数据，而不是调试通道。

### 第二步：先看原学号

把 `SW[8]` 拨成 `0`。

此时数码管应显示：

```text
02181044
```

### 第三步：看排序结果

把 `SW[8]` 拨成 `1`。

此时数码管应显示：

```text
00112448
```

### 第四步：根据需要调整 CPU 运行速度

- `SW[15] = 0`：CPU 跑得较快
- `SW[15] = 1`：CPU 跑得较慢，便于观察

通常建议：

1. 上电后先用较快速度让程序跑完
2. 程序进入死循环显示阶段后，再切换 `SW[8]` 观察原学号和排序结果

## 7. 数码管没有显示对怎么办

优先按下面顺序排查：

1. 确认 `SW[5:0]` 是否全为 `0`
2. 确认是否已经成功下载 `.bit`
3. 确认复位按键/复位电平是否正确
4. 确认约束文件使用的是 `Nexys4DDR_Lab6_CPU.xdc`
5. 确认顶层模块是否是 `lab6_sid_sort_fpga_top`
6. 确认工程中使用的是 `fpga-src/rv32_sid_sort_fpga.mem`

## 8. 如果 Vivado 报错，优先看哪里

### 1. 找不到顶层模块

检查工程顶层是否设成：

```text
lab6_sid_sort_fpga_top
```

### 2. 找不到 `imem`

本工程已经提供了源码版 `fpga-src/imem.v`，不依赖手动建 Block Memory IP。  
如果 Vivado 报错，优先检查这个文件是否被加入工程。

### 3. 找不到内存初始化文件

检查下面这个文件是否被加入工程：

```text
fpga-src/rv32_sid_sort_fpga.mem
```

### 4. 约束报端口不匹配

检查你的顶层端口名是否仍然是：

```text
clk
rstn
sw_i[15:0]
disp_seg_o[7:0]
disp_an_o[7:0]
```

## 9. 验收时建议拍哪些图

建议至少保留这些截图或照片：

1. `.\build.bat vivado` 成功生成工程的截图
2. Vivado 综合成功截图
3. Vivado 生成 bitstream 成功截图
4. `SW[8]=0` 时数码管显示 `02181044` 的照片
5. `SW[8]=1` 时数码管显示 `00112448` 的照片

## 10. 一句话版流程

如果你到机房后只想按最短路径操作，就照这个顺序走：

```powershell
cd lab-6
.\build.bat vivado
```

然后打开：

```text
vivado\lab6_sid_sort_fpga\lab6_sid_sort_fpga.xpr
```

接着在 Vivado 里：

```text
Run Synthesis -> Run Implementation -> Generate Bitstream -> Hardware Manager -> Program Device
```

上板后：

- `SW[5:0] = 0`
- `SW[8] = 0` 看原学号
- `SW[8] = 1` 看排序结果
