# ProxiTouch / current scene text

Exported from the synchronized, rebuilt scene definitions. Not reworded from memory.

## S00 / ProxiTouch

**接近—触碰—压力连续感知**

从空间场到接触界面





## S01 / 电容：电场中的储能能力

两个导体之间存在电势差时，空间中会建立电场，并在导体表面积累电荷。

\[
C=\frac{Q}{U}
\]

对于理想平行板电容器：

\[
\boxed{C=\frac{\varepsilon A}{d}}
\]

电容的大小由**介质、面积与间距**共同决定。





## S02 / 三个基本变量

由

\[
C=\frac{\varepsilon A}{d}
\]

可以直接得到：

\[
d\downarrow\Rightarrow C\uparrow
\]

\[
A\uparrow\Rightarrow C\uparrow
\]

\[
\varepsilon\uparrow\Rightarrow C\uparrow
\]





## S03 / 从物理量到电容变化

电容传感的基本思想，是把待测物理量转化为：

\[
d,\qquad A,\qquad \varepsilon
\]

的变化，再读取对应的电容响应。

位移、压力、液位、材料变化等，都可以通过这种方式被转换为电信号。





## S04 / 非均匀结构：串联与并联

当不同区域沿**面积方向分区**时，可近似视为并联：

\[
C_{\mathrm{eq}}
\approx
C_1+C_2+\cdots
\]

当不同介质沿**电场方向分层**时，可近似视为串联：

\[
\frac{1}{C_{\mathrm{eq}}}
\approx
\frac{1}{C_1}
+
\frac{1}{C_2}
+\cdots
\]

**横向分区 → 并联**  
**纵向分层 → 串联**





## S05 / 多材料串并联

实际结构中，**面积方向分区**与**电场方向分层**可以同时存在。

\[
\boxed{
C_{\mathrm{eq}}
=
\sum_i
\left(
\sum_j
\frac{d_{ij}}
{\varepsilon_{ij}A_i}
\right)^{-1}
}
\]

**每个面积分区 (i) 内：电场方向分层串联；不同面积分区之间：并联求和。**

> 适用于各区域可近似独立、边缘场影响较弱的情况。





## S06 / 从平行板到共面电极

电极并不一定需要彼此正对。

当一块电极逐渐展开到与另一块电极共面时，原本集中在极板之间的电场会向空间弯曲，形成明显的**边缘电场**。

几何结构改变，但电极之间仍然存在电场耦合。





## S07 / 互电容与边缘场

在一对共面电极中：

**Tx** 周期性改变电势，使边缘电场随时间变化；  
**Rx** 读取由互电容耦合产生的交流响应。

其耦合可用互电容 \(C_m\) 描述：

\[
i_{\mathrm{Rx}}
\approx
C_m\frac{dV_{\mathrm{Tx}}}{dt}
\]

因此，读取互电容响应，就可以观察**空间电场耦合的变化**。





## S08 / 目标接近如何被感知

当人体等目标进入边缘电场区域时，原有电场分布会被重新改变。

由此产生互电容变化：

\[
\Delta C_m=C_m-C_{m0}
\]

可用归一化响应表示：

\[
\boxed{
S_{\mathrm{prox}}
=
\left|
\frac{\Delta C_m}{C_{m0}}
\right|
}
\]





## S09 / 电双层：另一种电容机制

当电子导体与离子凝胶接触并施加电势时，内部可移动离子会在界面重新分布。

电极表面电荷与邻近反离子形成：

\[
\boxed{\text{电双层 EDL}}
\]

此时，主要电容效应集中在极薄的**电极—离子界面**附近。





## S10 / 两个界面：板间距不再主导电容

离子导体夹在上下电极之间时，
电压降主要集中在两个
**电极—离子导体界面的 EDL** 中。

中间的大范围体相近似电中性，
宏观电场被强烈屏蔽。

因此，只要两侧 EDL 不发生明显重叠，
压缩中间体相主要只是改变其厚度，
不会像传统平行板电容那样形成：

\[
C\propto\frac{1}{d}
\]

的响应。

两个界面仍可近似看作串联：

\[
\boxed{
\frac{1}{C}
\approx
\frac{1}{C_{\mathrm{top}}}
+
\frac{1}{C_{\mathrm{bottom}}}
}
\]

因此：

\[
\boxed{
C\not\propto\frac{1}{d}
}
\]

这里真正决定电容的是
**界面状态**，
而不是两块电极之间的宏观距离。





## S11 / 压力改变的是有效接触面积

对于上部 EDL，可近似表示为：

\[
C_{\mathrm{EDL}}
\approx
c_{\mathrm{EDL}}A_{\mathrm{eff}}
\]

初始状态下，
柔性电极只与**微结构**发生局部接触。

压力增大时，
微结构逐渐变形，
有效接触面积随之扩大：

\[
\boxed{
P\uparrow
\Rightarrow
A_{\mathrm{eff}}\uparrow
\Rightarrow
C_{\mathrm{EDL}}\uparrow
}
\]

因此，可以将：

**机械压力**

转化为：

**界面电容变化**。

> 黄色区域表示有效接触面积 \(A_{\mathrm{eff}}\)。





## S12 / 能否连续感知“接近—触碰—压力”？

接近感知主要读取**空间边缘场**的变化；  
压力感知则更适合读取接触后的**界面变化**。

而真实的人机交互本身就是连续的：

\[
\text{Approach}\rightarrow\text{Touch}\rightarrow\text{Pressure}
\]

**能否让同一个传感像素连续完成这三阶段感知？**





## S13 / 关键思路：共享中央电极

如果只是把两种传感器嵌套在一起，它们仍然只是两个独立器件。

因此，我们让中央柔性电极 \(E_C\) 同时参与两种测量：

\[
\boxed{
E_H\leftrightarrow E_C
\quad\longrightarrow\quad
E_C\leftrightarrow E_B
}
\]

接近时，它参与空间互电容；

接触后，它成为离子界面的上电极。

**同一个物理电极，连接两种感知机制。**





## S14 / ProxiTouch：单像素结构

单个像素主要由三类电极组成：

**外围边框 \(E_H\)**  
负责建立空间边缘场。

**中央柔性共享电极 \(E_C\)**  
连接接近感知与压力感知。

**底电极 \(E_B\)**  
与 \(E_C\) 构成离子界面压力通道。

中央区域布置可变形的**离子凝胶微穹顶**，并保留微小空气隙。





## S15 / Approach：读取空间边缘场

目标尚未接触时，主要测量：

\[
\boxed{E_H\leftrightarrow E_C}
\]

外围边框与中央电极之间形成向空间延伸的边缘场。

目标靠近后，电场重新分布：

\[
\Delta C_{HC}
=
C_{HC}-C_{HC,0}
\]

因此，在接触发生之前，传感器已经能够感知目标靠近。





## S16 / Touch：从空间场进入界面

目标继续下降并产生轻触后，柔性 \(E_C\) 开始向下形变。

当它首次接触离子凝胶微穹顶时：

\[
A_{\mathrm{eff}}>0
\]

上部离子界面开始建立。

此时空间场响应仍然存在，而界面响应开始出现。

**Touch 是两种感知机制交叠的过渡阶段。**





## S17 / Pressure：读取接触界面

继续施压后，主要测量：

\[
\boxed{E_C\leftrightarrow E_B}
\]

离子凝胶微穹顶逐渐变形，真实接触区域扩大：

\[
P\uparrow
\Rightarrow
A_{\mathrm{eff}}\uparrow
\Rightarrow
C_{\mathrm{EDL}}\uparrow
\]

压力因此被转化为界面电容变化。





## S18 / 共享电极如何分时工作？

三个电极同时存在，会产生不同耦合通道。

因此，ProxiTouch 采用**时分复用**。

接近窗口：

\[
E_H\leftrightarrow E_C
\]

压力窗口：

\[
E_C\leftrightarrow E_B
\]

两个测量快速交替：

\[
HC\rightarrow CB\rightarrow HC\rightarrow CB\rightarrow\cdots
\]

电子切换远快于人的动作，因此宏观上仍表现为连续感知。





## S19 / 一次完整的连续交互

目标从远处靠近：

\[
\Delta C_{HC}
\]

首先产生响应。

轻触后：

\[
A_{\mathrm{eff}}>0
\]

界面通道开始建立。

继续施压：

\[
P\uparrow
\Rightarrow
A_{\mathrm{eff}}\uparrow
\Rightarrow
C_{\mathrm{EDL}}\uparrow
\]

于是同一个像素完成：

\[
\boxed{
\text{Approach}
\rightarrow
\text{Touch}
\rightarrow
\text{Pressure}
}
\]

以及：

\[
\boxed{
\text{空间场}
\rightarrow
\text{接触界面}
}
\]





## S20 / 从单像素到共享边框阵列

方形结构可以自然铺展为二维阵列。

如果每个像素都保留一整圈独立外围电极，会产生大量重复结构。

因此，相邻像素可以进一步**共享边界电极**：

\[
\boxed{
\text{单像素}
\rightarrow
\text{共享边界}
\rightarrow
\text{二维阵列}
}
\]

中央 \(E_C\) 保持为局部感知节点，外围边界由相邻像素共同利用。

阵列可以通过扫描方式实现局部寻址。





## S21 / 从一个像素到一片感知表面

阵列化后，不同像素可以提供空间分布信息。

接近阶段：

\[
\text{读取空间场分布}
\]

接触以后：

\[
\text{读取局部压力分布}
\]

因此，同一块感知表面有可能连续获得：

\[
\boxed{
\text{接近位置}
\rightarrow
\text{接触位置}
\rightarrow
\text{压力分布}
}
\]





## S22 / ProxiTouch

接近时提前感知目标，
接触后识别首次接触，
继续施压时读取局部压力。

Approach → Touch → Pressure

**从空间，到接触，再到压力。**

> 应用概念演示；未经实验验证。





