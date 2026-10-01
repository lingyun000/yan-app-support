# 砚 · 支持与隐私

macOS 应用“砚”的公开支持网站、隐私政策和真实界面截图。此仓库不包含应用用户数据、凭据或签名材料。

- 网站：https://lingyun000.github.io/yan-app-support/
- 隐私政策：https://lingyun000.github.io/yan-app-support/privacy.html
- 使用支持：https://lingyun000.github.io/yan-app-support/support.html
- 反馈：https://github.com/lingyun000/yan-app-support/issues

通过 GitHub Pages 从 `main` 分支根目录发布。修改隐私政策时更新日期，并同时核对应用内链接、隐私清单和 App Store Connect 声明。

截图使用虚构的演示数据。应用版本与上架状态以 App Store 为准。

## 截图制作

2026-10-01 更新：实际应用深色界面，编辑器采用午夜蓝主题。最终文件为 `assets/editor.jpg`、`tools.jpg`、`base64.jpg`、`http.jpg`，RGB JPEG，2880 × 1800。只使用虚构示例数据；HTTP 为本地演示服务的实际 200 响应。

排版源文件位于 `screenshots/`。原始截图未发布：截取时把控制光标移至顶栏，再通过 HTML/CSS 容器裁掉顶部 110 像素的控制标记区域，其余界面保留真实像素。浏览器完整页面导出为 JPEG。AI 清理曾试用，但会影响小字，未采用生成结果。复现时将原始截图放在 `assets/*-dark-raw.png`（已忽略）。

## Website languages and demo

The overview, support page and complete privacy policy provide English and Chinese. First visits default to English; the language switch remembers the reader's selection locally. No analytics are added.

`assets/yan-demo-web.mp4` is the developer-provided real Mac recording from 2026-10-01 14:05:52, showing launch and typical use. It is published with the developer's authorization. The web MP4 is compressed from 17.8 MB to about 1.7 MB at 1280 px width, with progressive playback. Video data is not loaded until requested. The full-resolution original recording remains on the developer's Mac and in the Apple review attachment. English gallery images are real frames from the developer's English-interface recording. Chinese pages retain the Chinese screenshots.
