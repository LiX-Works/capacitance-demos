# ProxiTouch 第三轮最终精修

**共享中央电极 · 时分复用 · 共享边界阵列**

在完整 R2 源码上做指定范围精修。保留原生 WebGL2 / TypeScript、材质灯光、探索和离线构建系统；仍为封面 + 22 个知识单元（基础 11、设计 8、阵列 3）。S00–S21 标题和正文保持 R2，S22 改为高密度感知皮肤夹鸡蛋的应用概念。

## 打开演示

用支持 WebGL2 的桌面浏览器打开 `dist/ProxiTouch-offline.html`。这个文件包含运行所需的脚本和样式，无需 npm、Node 或外部网络资源。字体使用操作系统字体，未附带字体文件。

推荐演示分辨率：1920×1080 或 2560×1440。本环境的 Chromium 禁止文件和 HTTP 地址导航；交付内容已经实际浏览器渲染，但文件直开和 HTTP 浏览器入口的验证边界请阅读 `QA_REPORT.md`。

## 主要操作

- **→ / Space**：动画播放中先立即完成当前页；再按一次进入下一页。
- **←**：返回上一页的稳定结束状态。**R**：重播当前页。
- **T**：展开 / 折叠原理说明。正文默认显示，可独立滚动。
- **E**：进入或退出探索。**Esc**：返回演示或关闭弹层。
- **G**：目录。**P**：自动演示。**Home / End**：封面 / 结尾。

探索包含器件、电场、微结构、EDL、双通道信号和分层结构六种视图。拖动可旋转，滚轮可缩放，滑块控制共享交互深度。返回时恢复原页面、相机、物理状态和正文滚动位置。

## 编辑与离线构建

已测试构建环境：Node.js 22。在解压后的 `source` 目录执行：

```sh
npm run setup:offline
npm run check
npm test
npm run preview
```

`setup:offline` 从包内 `tools/typescript-5.8.3.tgz` 提取编译器，不访问 npm 仓库。`npm test` 会先构建，再运行模型一致性测试。`preview` 在端口 4173 提供静态服务。也可只执行 `npm run build` 重新输出 `dist/`。

正式文案来自 `revision-spec/01_FINAL_SCENE_PLAN_AND_COPY.md`，由 `scripts/import_revision_copy.py` 导入 `src/scenes/copy.ts`；R3 仅以 `revision-spec/R3_COPY_OVERRIDES.json` 覆盖 S22，重新导入不会丢失结尾修改。场景顺序、时长、关键状态和相机在 `src/scenes/definitions.ts`。基本测试不需要 Python。

## 交付内容

|目录 / 文件|用途|
|---|---|
|`source/src/`|完整可编辑 TypeScript 源码|
|`dist/`|静态站点、ES 模块、单文件离线 HTML|
|`CONTROLS.md`|完整操作说明|
|`PRESENTATION_GUIDE.md`|23 页演示导航与讲解提示|
|`docs/`|读取、迁移、结构、物理边界与来源记录|
|`qa/INDEX.html`|离线截图与测试证据画廊|
|`QA_REPORT.md`|实际测试结果、性能、未验证范围|
|`revision-spec/`|R2 原始 MD、R3 范围记录和 S22 文案覆盖|
|`source/archive/r1/`|不参与新版运行的部分旧版资产|

## R3 循环与截图

S05 / S07 / S10 / S18 使用独立环境动画时钟。循环不会阻塞翻页，离开即停止更新。自动截图可使用 `__PT.captureMode(true)` 与 `__PT.ambientTime(seconds)` 固定状态。详见 `docs/r3/AMBIENT_CAPTURE.md` 和 `docs/CHANGELOG.md`。

## 科学边界

ProxiTouch 是课程级概念设计，未制造、未实测。代表性 Laplace 模型不等于完整三维器件验证；离子动画不是分子动力学；交互深度和 HC / CB 信号不是已标定性能。请将软件测试、截图复查和真实硬件验证分开理解。

夹持动作是预设教学动画；鸡蛋由下方小支座定位，不演示抬升或闭环控制。未验证安全夹持、压力标定或破裂力学。
