# 互电容建模实验室

从平行板到共面电极的定量电容演示，共12个场景。保留真实尺寸参数、解析近似、BEM 数据、独立 FVM 核查与有限宽度检查点。

**本仓库的源码已按本次最终 HTML 同步，不是旧源码加一个新 HTML。** 首页的汇报人、导师、号码等个人信息已从页面、源码与打包文件中移除。

![实际浏览器渲染预览](previews/overview.png)

[查看预览图库](previews/index.html) · [本次 QA](QA_REPORT.md) · [源码同步说明](docs/SOURCE_SYNC.md) · [给 Codex 的部署任务](CODEX_DEPLOY.md)

## 直接打开

双击根目录的 `index.html`，或 `dist/Capacitance-Lab-offline.html`。它们由同一次构建生成，不需要运行 Python、Node 或外部 CDN。浏览器需要支持 WebGL2。

普通电极页保持“场线 → 电势 → 场强”循环；04 理想扇区与 09 介质边缘场页保留专用行为。按钮保留深蓝底，选中的场显示模式使用浅蓝底。

## 离线构建（在本仓库根目录）

```sh
npm run build:offline
npm run check
npm test
npm run preview
```

已附本地 TypeScript 5.8.3 包，`build:offline` 自动安装到 `source/node_modules/`。也可在有网环境中运行 `npm --prefix source ci`。本次实测的 Node 版本为 22.16.0。

`npm run build` 从 `source/src/`、`source/public/` 与 `source/index.html` 生成 `dist/`、根目录 `index.html` 和部署用 `site/`。**不要只改生成的 HTML 而不更新源码。**

## 交给 Codex

先读 `AGENTS.md` 和 `CODEX_DEPLOY.md`。建议使用包内 `.github/workflows/pages.yml`：从源码构建，仅将 `site/` 部署到 GitHub Pages。完整源码、数据和历史报告仍留在仓库中作备份，无需把这些全部发布为网页资源。

## 目录

| 目录 | 用途 |
|---|---|
| `source/src/` | 同步后的可编辑 TypeScript 源码 |
| `source/public/` | 样式、本地公式库 |
| `dist/` | 构建后模块、source map、单文件 HTML |
| `site/` | 仅部署需要的 HTML 与预览图库 |
| `previews/` | 本次重新渲染的代表性图片与清单 |
| `reference/final-upload.html` | 已去除个人信息的用户最终版基准，用于比较，不是编辑入口 |
| `qa/` | 本次源码同步、渲染、构建与隐私检查 |
| `docs/` | 场景清单、模型说明、复现说明 |
| `archive/` / `source/legacy-tests/` | 原工程的历史备份，不是当前生成流程 |
| `physics/` / `data/` / `parameters.json` | 原数值求解、数据与统一真实参数 |
| `requirements-reproduce.txt` | 可选数值重算依赖 |
| `tools/` / `licenses/` | 离线编译器与第三方许可 |

## 验证边界

本次是依照上传 HTML 的同步与部署准备，没有重新设计物理模型或重算数据。历史数值报告保留其原有边界，不冒充本次实验验证。

浏览器检查在 Chromium / SwiftShader 中运行。此环境的 URL 导航受管理策略限制，所以使用 Playwright 加载完整离线 HTML 内容，没有修改策略。实体 GPU 性能与线上 Pages 地址尚未验证。此包没有替你创建仓库或执行线上发布。
