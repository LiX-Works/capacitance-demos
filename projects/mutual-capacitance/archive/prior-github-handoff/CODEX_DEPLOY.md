# 交给 Codex：部署 互电容建模实验室

请将本目录的**内容**放到目标 GitHub 仓库根目录，不要把完整 ZIP 直接当网站上传，也不要将另一份演示的源码混进来。项目代号：`lab`。

## 目标与边界

保留当前文案、动画、数据与样式，仅完成仓库和 Pages 部署。个人信息已移除，不得从旧文件恢复。不重新做物理研究或生成示意曲线替代已有数据。

## 一次性执行步骤

1. 确认 owner/repo、主分支与仓库可见性。如已有仓库，先查看其目录和 Pages 配置，不覆盖无关文件。
2. 在本包根目录运行：

```sh
npm run build:offline
npm run check
npm test
npm run preview
```

3. 只使用生成的 `site/` 作为 Pages 发布产物。包内已有 `.github/workflows/pages.yml`，从主分支构建后运行同步测试，再部署静态文件。
4. 仓库 Settings → Pages → Source 选择 **GitHub Actions**。推送主分支或手动运行 workflow。需要发布权限和站点配置，本包未执行这些账号操作。
5. 确认线上首页、`previews/` 图库和项目子路径下的资源均加载，无个人信息、无外部资源丢失。用实际浏览器检查翻页和循环，不仅以 CI 绿灯作为成功依据。

## 备用方案

不使用自动构建时，可将已构建的 `site/` 内容放到一个专用发布分支的根目录，然后 Pages 选择该分支的 `/ (root)`。不要让 branch deployment 和上面的 Actions 同时争用发布。

## 文件保留与备份

`source/`、数值计算脚本、原始数据、`docs/`、`qa/`和选定预览图均可保留在仓库。`node_modules/` 和 Python 缓存已排除。原始个人命名的上传文件不在包中；仅保留清理后的比较基准。当前交付的当次报告位于 `qa/`，而 `archive/` 的旧测试只是历史备份。

具体 Actions 版本和发布规则参考 `deployment/OFFICIAL_REFERENCES.md`，交付时已核对官方说明，但 workflow 还未在你的账号上执行。
