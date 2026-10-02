# 将合集发布到 GitHub Pages

本仓库维护一个首页和两个演示，无需创建两个 GitHub 仓库。保留的旧部署提示位于项目的 `archive/prior-github-handoff/`，不用于当前部署。

## 上传范围

将本目录的内容放到一个仓库根目录。上传源码、`web/`、`scripts/`、`projects/`、文档、许可与根 `.github/`。不要直接上传交付 ZIP 作为网站，也不要上传 `node_modules`、Python 环境或浏览器缓存。

根 `.gitignore` 排除了可重建的 `site/`、项目 `dist/` 和项目打包入口。它们可以留在本地离线包中，GitHub Actions 会从源码生成。保留项目科学数据、reference 和历史档案。

## 开启 Pages

1. 在目标仓库的 Settings → Pages 中，将 Source 设为 **GitHub Actions**。
2. 使用 `main` 或 `master` 分支；推送后根 `pages.yml` 会构建、检查、运行浏览器 QA，再发布整个合集。
3. Pull request 只验证，不发布。也可以在 Actions 页面手动运行工作流。
4. 发布后检查入口、两个演示和预览图库。所有链接均使用相对路径；本地 QA 覆盖 `/capacitance-demos/` 子路径。

仓库名称可以自行选择；无需改页面中的地址。自定义域名不是本项目的运行依赖。

## 本地复查

```sh
npm run build
npm run check
npm test
npm run preview
```

如需模拟仓库子路径，在运行预览前设置 `PREVIEW_BASE=capacitance-demos`。PowerShell 示例：

```powershell
$env:PREVIEW_BASE = 'capacitance-demos'
npm run preview
```

可选 Python 环境用于浏览器测试，安装步骤见 README。GitHub 工作流会为其安装独立依赖。

官方流程参考：[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。本地成功不代表已在某个账号上发布；线上完成以实际站点为准。
