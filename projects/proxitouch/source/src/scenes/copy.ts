// Approved R2 copy with the explicit R3 S22 override.
export const COPY:Record<string,{title:string;body:string;source:string;page:number}>={
    "S01": {
        "title": "电容：电场中的储能能力",
        "body": "两个导体之间存在电势差时，空间中会建立电场，并在导体表面积累电荷。\n\n\\[\nC=\\frac{Q}{U}\n\\]\n\n对于理想平行板电容器：\n\n\\[\n\\boxed{C=\\frac{\\varepsilon A}{d}}\n\\]\n\n电容的大小由**介质、面积与间距**共同决定。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 1
    },
    "S02": {
        "title": "三个基本变量",
        "body": "由\n\n\\[\nC=\\frac{\\varepsilon A}{d}\n\\]\n\n可以直接得到：\n\n\\[\nd\\downarrow\\Rightarrow C\\uparrow\n\\]\n\n\\[\nA\\uparrow\\Rightarrow C\\uparrow\n\\]\n\n\\[\n\\varepsilon\\uparrow\\Rightarrow C\\uparrow\n\\]",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 2
    },
    "S03": {
        "title": "从物理量到电容变化",
        "body": "电容传感的基本思想，是把待测物理量转化为：\n\n\\[\nd,\\qquad A,\\qquad \\varepsilon\n\\]\n\n的变化，再读取对应的电容响应。\n\n位移、压力、液位、材料变化等，都可以通过这种方式被转换为电信号。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 3
    },
    "S04": {
        "title": "非均匀结构：串联与并联",
        "body": "当不同区域沿**面积方向分区**时，可近似视为并联：\n\n\\[\nC_{\\mathrm{eq}}\n\\approx\nC_1+C_2+\\cdots\n\\]\n\n当不同介质沿**电场方向分层**时，可近似视为串联：\n\n\\[\n\\frac{1}{C_{\\mathrm{eq}}}\n\\approx\n\\frac{1}{C_1}\n+\n\\frac{1}{C_2}\n+\\cdots\n\\]\n\n**横向分区 → 并联**  \n**纵向分层 → 串联**",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 4
    },
    "S05": {
        "title": "多材料串并联",
        "body": "实际结构中，**面积方向分区**与**电场方向分层**可以同时存在。\n\n\\[\n\\boxed{\nC_{\\mathrm{eq}}\n=\n\\sum_i\n\\left(\n\\sum_j\n\\frac{d_{ij}}\n{\\varepsilon_{ij}A_i}\n\\right)^{-1}\n}\n\\]\n\n**每个面积分区 \(i\) 内：电场方向分层串联；不同面积分区之间：并联求和。**\n\n> 适用于各区域可近似独立、边缘场影响较弱的情况。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 5
    },
    "S06": {
        "title": "从平行板到共面电极",
        "body": "电极并不一定需要彼此正对。\n\n当一块电极逐渐展开到与另一块电极共面时，原本集中在极板之间的电场会向空间弯曲，形成明显的**边缘电场**。\n\n几何结构改变，但电极之间仍然存在电场耦合。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 6
    },
    "S07": {
        "title": "互电容与边缘场",
        "body": "在一对共面电极中：\n\n**Tx** 周期性改变电势，使边缘电场随时间变化；  \n**Rx** 读取由互电容耦合产生的交流响应。\n\n其耦合可用互电容 \\(C_m\\) 描述：\n\n\\[\ni_{\\mathrm{Rx}}\n\\approx\nC_m\\frac{dV_{\\mathrm{Tx}}}{dt}\n\\]\n\n因此，读取互电容响应，就可以观察**空间电场耦合的变化**。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 7
    },
    "S08": {
        "title": "目标接近如何被感知",
        "body": "当人体等目标进入边缘电场区域时，原有电场分布会被重新改变。\n\n由此产生互电容变化：\n\n\\[\n\\Delta C_m=C_m-C_{m0}\n\\]\n\n可用归一化响应表示：\n\n\\[\n\\boxed{\nS_{\\mathrm{prox}}\n=\n\\left|\n\\frac{\\Delta C_m}{C_{m0}}\n\\right|\n}\n\\]",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 8
    },
    "S09": {
        "title": "电双层：另一种电容机制",
        "body": "当电子导体与离子凝胶接触并施加电势时，内部可移动离子会在界面重新分布。\n\n电极表面电荷与邻近反离子形成：\n\n\\[\n\\boxed{\\text{电双层 EDL}}\n\\]\n\n此时，主要电容效应集中在极薄的**电极—离子界面**附近。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 9
    },
    "S10": {
        "title": "两个界面：板间距不再主导电容",
        "body": "离子导体夹在上下电极之间时，\n电压降主要集中在两个\n**电极—离子导体界面的 EDL** 中。\n\n中间的大范围体相近似电中性，\n宏观电场被强烈屏蔽。\n\n因此，只要两侧 EDL 不发生明显重叠，\n压缩中间体相主要只是改变其厚度，\n不会像传统平行板电容那样形成：\n\n\\[\nC\\propto\\frac{1}{d}\n\\]\n\n的响应。\n\n两个界面仍可近似看作串联：\n\n\\[\n\\boxed{\n\\frac{1}{C}\n\\approx\n\\frac{1}{C_{\\mathrm{top}}}\n+\n\\frac{1}{C_{\\mathrm{bottom}}}\n}\n\\]\n\n因此：\n\n\\[\n\\boxed{\nC\\not\\propto\\frac{1}{d}\n}\n\\]\n\n这里真正决定电容的是\n**界面状态**，\n而不是两块电极之间的宏观距离。",
        "source": "FINAL_PATCH user instruction",
        "page": 10
    },
    "S11": {
        "title": "压力改变的是有效接触面积",
        "body": "对于上部 EDL，可近似表示为：\n\n\\[\nC_{\\mathrm{EDL}}\n\\approx\nc_{\\mathrm{EDL}}A_{\\mathrm{eff}}\n\\]\n\n初始状态下，\n柔性电极只与**微结构**发生局部接触。\n\n压力增大时，\n微结构逐渐变形，\n有效接触面积随之扩大：\n\n\\[\n\\boxed{\nP\\uparrow\n\\Rightarrow\nA_{\\mathrm{eff}}\\uparrow\n\\Rightarrow\nC_{\\mathrm{EDL}}\\uparrow\n}\n\\]\n\n因此，可以将：\n\n**机械压力**\n\n转化为：\n\n**界面电容变化**。\n\n> 黄色区域表示有效接触面积 \\(A_{\\mathrm{eff}}\\)。",
        "source": "FINAL_PATCH user instruction",
        "page": 11
    },
    "S12": {
        "title": "能否连续感知“接近—触碰—压力”？",
        "body": "接近感知主要读取**空间边缘场**的变化；  \n压力感知则更适合读取接触后的**界面变化**。\n\n而真实的人机交互本身就是连续的：\n\n\\[\n\\text{Approach}\\rightarrow\\text{Touch}\\rightarrow\\text{Pressure}\n\\]\n\n**能否让同一个传感像素连续完成这三阶段感知？**",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 12
    },
    "S13": {
        "title": "关键思路：共享中央电极",
        "body": "如果只是把两种传感器嵌套在一起，它们仍然只是两个独立器件。\n\n因此，我们让中央柔性电极 \\(E_C\\) 同时参与两种测量：\n\n\\[\n\\boxed{\nE_H\\leftrightarrow E_C\n\\quad\\longrightarrow\\quad\nE_C\\leftrightarrow E_B\n}\n\\]\n\n接近时，它参与空间互电容；\n\n接触后，它成为离子界面的上电极。\n\n**同一个物理电极，连接两种感知机制。**",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 13
    },
    "S14": {
        "title": "ProxiTouch：单像素结构",
        "body": "单个像素主要由三类电极组成：\n\n**外围边框 \\(E_H\\)**  \n负责建立空间边缘场。\n\n**中央柔性共享电极 \\(E_C\\)**  \n连接接近感知与压力感知。\n\n**底电极 \\(E_B\\)**  \n与 \\(E_C\\) 构成离子界面压力通道。\n\n中央区域布置可变形的**离子凝胶微穹顶**，并保留微小空气隙。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 14
    },
    "S15": {
        "title": "Approach：读取空间边缘场",
        "body": "目标尚未接触时，主要测量：\n\n\\[\n\\boxed{E_H\\leftrightarrow E_C}\n\\]\n\n外围边框与中央电极之间形成向空间延伸的边缘场。\n\n目标靠近后，电场重新分布：\n\n\\[\n\\Delta C_{HC}\n=\nC_{HC}-C_{HC,0}\n\\]\n\n因此，在接触发生之前，传感器已经能够感知目标靠近。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 15
    },
    "S16": {
        "title": "Touch：从空间场进入界面",
        "body": "目标继续下降并产生轻触后，柔性 \\(E_C\\) 开始向下形变。\n\n当它首次接触离子凝胶微穹顶时：\n\n\\[\nA_{\\mathrm{eff}}>0\n\\]\n\n上部离子界面开始建立。\n\n此时空间场响应仍然存在，而界面响应开始出现。\n\n**Touch 是两种感知机制交叠的过渡阶段。**",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 16
    },
    "S17": {
        "title": "Pressure：读取接触界面",
        "body": "继续施压后，主要测量：\n\n\\[\n\\boxed{E_C\\leftrightarrow E_B}\n\\]\n\n离子凝胶微穹顶逐渐变形，真实接触区域扩大：\n\n\\[\nP\\uparrow\n\\Rightarrow\nA_{\\mathrm{eff}}\\uparrow\n\\Rightarrow\nC_{\\mathrm{EDL}}\\uparrow\n\\]\n\n压力因此被转化为界面电容变化。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 17
    },
    "S18": {
        "title": "共享电极如何分时工作？",
        "body": "三个电极同时存在，会产生不同耦合通道。\n\n因此，ProxiTouch 采用**时分复用**。\n\n接近窗口：\n\n\\[\nE_H\\leftrightarrow E_C\n\\]\n\n压力窗口：\n\n\\[\nE_C\\leftrightarrow E_B\n\\]\n\n两个测量快速交替：\n\n\\[\nHC\\rightarrow CB\\rightarrow HC\\rightarrow CB\\rightarrow\\cdots\n\\]\n\n电子切换远快于人的动作，因此宏观上仍表现为连续感知。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 18
    },
    "S19": {
        "title": "一次完整的连续交互",
        "body": "目标从远处靠近：\n\n\\[\n\\Delta C_{HC}\n\\]\n\n首先产生响应。\n\n轻触后：\n\n\\[\nA_{\\mathrm{eff}}>0\n\\]\n\n界面通道开始建立。\n\n继续施压：\n\n\\[\nP\\uparrow\n\\Rightarrow\nA_{\\mathrm{eff}}\\uparrow\n\\Rightarrow\nC_{\\mathrm{EDL}}\\uparrow\n\\]\n\n于是同一个像素完成：\n\n\\[\n\\boxed{\n\\text{Approach}\n\\rightarrow\n\\text{Touch}\n\\rightarrow\n\\text{Pressure}\n}\n\\]\n\n以及：\n\n\\[\n\\boxed{\n\\text{空间场}\n\\rightarrow\n\\text{接触界面}\n}\n\\]",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 19
    },
    "S20": {
        "title": "从单像素到共享边框阵列",
        "body": "方形结构可以自然铺展为二维阵列。\n\n如果每个像素都保留一整圈独立外围电极，会产生大量重复结构。\n\n因此，相邻像素可以进一步**共享边界电极**：\n\n\\[\n\\boxed{\n\\text{单像素}\n\\rightarrow\n\\text{共享边界}\n\\rightarrow\n\\text{二维阵列}\n}\n\\]\n\n中央 \\(E_C\\) 保持为局部感知节点，外围边界由相邻像素共同利用。\n\n阵列可以通过扫描方式实现局部寻址。",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 20
    },
    "S21": {
        "title": "从一个像素到一片感知表面",
        "body": "阵列化后，不同像素可以提供空间分布信息。\n\n接近阶段：\n\n\\[\n\\text{读取空间场分布}\n\\]\n\n接触以后：\n\n\\[\n\\text{读取局部压力分布}\n\\]\n\n因此，同一块感知表面有可能连续获得：\n\n\\[\n\\boxed{\n\\text{接近位置}\n\\rightarrow\n\\text{接触位置}\n\\rightarrow\n\\text{压力分布}\n}\n\\]",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 21
    },
    "S22": {
        "title": "ProxiTouch",
        "body": "接近时提前感知目标，\n接触后识别首次接触，\n继续施压时读取局部压力。\n\nApproach → Touch → Pressure\n\n**从空间，到接触，再到压力。**\n\n> 应用概念演示；未经实验验证。",
        "source": "R3_SCOPED_REQUEST.md",
        "page": 22
    },
    "S00": {
        "title": "ProxiTouch",
        "body": "**接近—触碰—压力连续感知**\n\n从空间场到接触界面",
        "source": "01_FINAL_SCENE_PLAN_AND_COPY.md",
        "page": 0
    }
};
