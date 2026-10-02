# ProxiTouch R3 FINAL PATCH — 修改记录

本补丁严格限定在 S05、S10、S11；未修改章节结构、EH/EC/EB 架构、阵列、夹鸡蛋 Ending、Explore、导航体系或总体视觉风格。

## S05｜多材料串并联
- 介质几何由 3×2 六块改为四个主要 volume：左整块、中间上层、中间下层、右整块。
- 原公式保持不变。
- ambient loop 改为：默认 → 横向区域 i → 纵向层 j → 不同材料状态 → 默认。
- 材料阶段中间上层为暖金、中间下层为青蓝；左右整块分别为浅绿与浅粉。
- 左右材料加入固定 seed 的低对比内部颗粒分布，capture mode 下确定性复现。

## S10｜两个界面：板间距不再主导电容
- 正式正文完全替换为 FINAL PATCH 指定版本，并保留“两侧 EDL 不发生明显重叠”的适用前提。
- 删除 C_bottom >> C_top、C ≈ C_top、面积稳定/可变上界面等旧叙事。
- 主动画改为：基础 → 体相屏蔽 → 板间距压缩。
- 上下 EDL 在屏蔽阶段同时强调；bulk 离子与体相降权。
- 压缩阶段上电极下降约 35%，上部 EDL 随动、下部 EDL 保持、bulk 压缩，局部 EDL 厚度不缩放。
- 增加“体相近似电中性 / 宏观电场被屏蔽 · E ≈ 0”与“d₂ < d₁ / ΔC ≈ 0”视觉辅助。
- S10 已从 ambient scene 列表移除；删除旧 breathing loop。

## S11｜压力改变的是有效接触面积
- 正文替换为 FINAL PATCH 指定版本。
- PART I 页面不再出现“离子凝胶微穹顶”，模型标签改为“微结构”。
- 删除重复的“而不是简单 d↓”解释。
- 原有轻触 → 微结构变形 → A_eff 扩大的 geometry 与动画保持不变。

## 构建与 QA
- TypeScript `npm run check`：通过。
- `npm test`：40/40 软件/模型/时序一致性检查通过。
- 实际 Chromium/WebGL2：1920×1080 与 2560×1440 均完成 S05/S10/S11 关键状态截图。
- S05 固定 ambient time 的重复截图字节一致。
- S05 ambient 不阻塞 ArrowRight。
- S10 第一次 ArrowRight 完成主动画，第二次进入 S11；S10 不再有 ambient loop。
