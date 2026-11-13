# 砚 插件开发手册

> 砚 1.0.4 及后续版本支持插件。

> 本手册说明如何为“砚”开发插件，覆盖全部能力：**命令**、**文本动作**、**预览器**、**工具面板**、**编辑器与交互 API**、**插件设置**、**事件**、**校验器**、**格式化器**、**编辑器增强**（状态栏、装饰、悬停、补全、检查器分区）、**界面集成**（菜单、工作区工具、粘贴识别、设置页、自定义编辑器）、**插件中心页面**、**插件存储**，以及需要权限的**网络**、**剪贴板**、**文档**与**应用命令**。
>
> 能力不绑定在某种“插件类型”上：一个插件可以同时提供命令、文本动作、预览器、面板，命令里可以读写编辑器、询问用户、读取设置。
> 语言、语法高亮、主题、快捷键、文本工具分类等**声明式贡献**（不需要写代码）见 [扩展开发手册](extension-guide.md)。

---

[先看插件效果和可扩展的界面区域](plugin-examples.md)

## 目录

1. [插件能做什么](#1-插件能做什么)
2. [五分钟上手](#2-五分钟上手)
3. [插件包结构](#3-插件包结构)
4. [plugin.json 完整参考](#4-pluginjson-完整参考)
5. [JavaScript API 参考](#5-javascript-api-参考)
6. [文本动作详解](#6-文本动作详解)
7. [预览器详解](#7-预览器详解)
8. [工具面板详解](#8-工具面板详解)
9. [通用命令](#9-通用命令)
10. [编辑器与交互 API](#10-编辑器与交互-api)
11. [插件设置](#11-插件设置)
12. [事件](#12-事件)
13. [校验器](#13-校验器)
14. [格式化器](#14-格式化器)
15. [格式化、预览与校验的选择](#15-格式化预览与校验的选择)
16. [扩展名关联语言](#16-扩展名关联语言)
17. [编辑器增强：状态栏、装饰、悬停、补全、检查器分区](#17-编辑器增强状态栏装饰悬停补全检查器分区)
18. [界面集成：菜单、工作区工具、粘贴识别、设置页、自定义编辑器](#18-界面集成菜单工作区工具粘贴识别设置页自定义编辑器)
19. [插件中心：详情页与自定义页面](#19-插件中心详情页与自定义页面)
20. [插件存储与秘密](#20-插件存储与秘密)
21. [权限：网络、剪贴板、文档与命令](#21-权限网络剪贴板文档与命令)
22. [运行环境与限制](#22-运行环境与限制)
23. [调试](#23-调试)
24. [打包、分发与更新](#24-打包分发与更新)
25. [常见错误对照表](#25-常见错误对照表)
26. [完整示例](#26-完整示例)
27. [常见问题](#27-常见问题)

---

## 1. 插件能做什么

| 能力 | 你写什么 | 用户在哪里用 |
|---|---|---|
| **文本动作** | 一个函数：收到选区或全文，返回新文本 | 编辑器右键 → 插件、菜单栏 工具 → 插件、命令面板（⌘K）、处理步骤 |
| **预览器** | 一个函数：收到全文，返回一段 HTML | 打开匹配的文件时，标签顶部出现 预览 / 源码 / 分屏 |
| **工具面板** | 一个 HTML 页面 + `main.js` 中的处理函数 | 菜单栏 工具 → 插件、命令面板、插件中心，在独立窗口打开 |
| **通用命令** | 一个函数：可以读写编辑器、询问用户、读取设置 | 编辑器右键、工具菜单、命令面板（位置和显示条件由你声明） |
| **插件设置** | 在清单中声明设置项 | 插件中心 → 你的插件 → 设置 标签，自动生成表单 |
| **事件** | 订阅打开、保存、切换文档 | 自动触发 |
| **校验器** | 一个函数：返回问题列表（行、列、说明、严重程度、快速修复） | 编辑器标出问题位置，F8 / ⇧F8 跳转，检查器中一键修复 |
| **格式化器** | 一个函数：返回格式化后的文本 | “按当前语言格式化”（⇧⌘F） |
| **扩展名关联语言** | 在清单中声明，例如 `.jsonc` → JSON | 打开文件时自动选择语言 |
| **编辑器增强** | 状态栏项、文本装饰、行号栏图标、悬停提示、补全、检查器分区 | 编辑器内 |
| **语言功能** | 转到定义、符号、引用、语义高亮、重命名、参数提示、内联提示、折叠、**内联补全**（灰色幽灵文本，可接 AI）、**代码透镜**（行上方可点击的文字） | 编辑器内、前往与工具菜单 |
| **界面集成** | 菜单项（含标签右键菜单、按条件启用）、工作区工具、粘贴识别、设置页、自定义编辑器 | 应用菜单、工具栏、标签右键、工作区、粘贴时、设置窗口、文档标签 |
| **插件中心页面** | 图标、说明文档、更新记录、自定义页面 | 插件中心 → 你的插件 |
| **插件存储与秘密** | 调用 `toolbox.storage`、`toolbox.secrets` | 记住历史记录、缓存；在钥匙串中保存令牌 |
| **网络**（需权限） | `fetch` / `toolbox.net.request`、WebSocket、SSE、原始 TCP（`toolbox.net.tcp`） | 访问你在清单里声明的主机（可限定端口、网段）；流式接收、二进制、上传文件、Cookie、代理；也可申请访问所有网站，需用户明确同意 |
| **剪贴板**（需权限） | 调用 `toolbox.clipboard` | 读写文本、HTML、RTF、图片和文件 |
| **所有文档**（需权限） | 声明 `documents: "all"` | 事件收到文档内容、列出全部标签、后台入口联网 |
| **应用命令**（需权限） | 调用 `toolbox.executeCommand` | 执行应用的保存、格式化等命令 |

插件**不能**做的事（这是有意的安全边界）：读写用户没有交给它的磁盘文件（可以用自己的私有文件夹 `files.dataFolder()`，以及用户选择或拖入的文件和文件夹）、访问未声明的主机、在未获授权时读取其他标签页、加载原生代码、启动其他程序。声明 `background` 权限后可以常驻运行，保持连接和定时任务。插件的预览页面和面板页面本身**不能联网**，联网经由 `main.js`，且仅限声明过的主机（声明 `"*"` 并经用户同意后不限主机）。用户可以随时关闭任意插件的网络访问。

---

## 2. 五分钟上手

**第 1 步**：新建一个文件夹，例如 `reverse-lines/`，放入两个文件。

`plugin.json`：

```json
{
  "id": "com.yourname.reverse-lines",
  "name": "行倒序",
  "version": "1.0.0",
  "main": "main.js",
  "contributes": {
    "textActions": [
      { "id": "reverse", "title": "倒序排列行" }
    ]
  }
}
```

`main.js`：

```js
toolbox.registerTextAction("reverse", (input) => {
  return input.text.split("\n").reverse().join("\n");
});
```

请将示例中的 `com.yourname.reverse-lines` 换成你自己的反向域名标识，发布后保持该标识不变。

**第 2 步**：打开 砚 → 设置 → 插件（或按 ⇧⌘X 打开插件中心窗口），点列表上方的 **＋ → 导入插件…**，选择 `reverse-lines` 文件夹，确认安装。

**第 3 步**：在编辑器里选中几行，右键 → 插件 → 倒序排列行。

**修改后**：再次“导入插件…”选择同一个文件夹即可覆盖更新（同一个 `id` 视为同一个插件）。开发期间更方便的做法是 **＋ → 链接开发文件夹…**：直接从源文件夹载入，保存文件后自动重新载入（见第 23 节）。

---

## 3. 插件包结构

```
my-plugin/
├── plugin.json        必需：清单
├── main.js            入口脚本（文件名由 plugin.json 的 main 决定）；只有声明式贡献时可以没有
├── style.css          可选：预览页面引用的资源
└── panel/             可选：工具面板的页面、脚本、样式、图片
    ├── index.html
    └── panel.js
```

- 分发时把文件夹**内容**压缩成 zip，并把扩展名改为 `.toolboxplugin`（见第 24 节）。zip 内可以是文件直接位于根目录，也可以是只有一个顶层文件夹。
- 插件包上限 **256 MiB**、最多 **10000 个文件**（足够放 `node_modules`、WebAssembly 和数据文件）；不能包含符号链接。
- 通过“导入插件…”安装后，插件被复制到应用的数据目录中，与原文件夹不再关联；通过“链接开发文件夹…”载入的插件始终读取源文件夹。

---

## 4. plugin.json 完整参考

```json
{
  "id": "com.example.github-repo",
  "name": "GitHub 仓库信息",
  "version": "1.0.0",
  "description": "查询 GitHub 公开仓库的信息。",
  "author": "Example",
  "homepage": "https://example.com/plugins/github",
  "minAppVersion": "1.0.0",
  "main": "main.js",
  "permissions": {
    "network": ["api.github.com"],
    "clipboard": true
  },
  "contributes": {
    "textActions": [ ... ],
    "previewers": [ ... ],
    "panels": [ ... ]
  }
}
```

### 顶层字段

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | ✅ | 全局唯一标识，建议使用自己域名的反向形式，如 `com.yourname.my-plugin`。`com.yan.*` 保留给“砚”官方插件，请不要使用。只能用字母、数字、`.`、`-`，2–128 个字符，以字母或数字开头。**发布后不要更改**：更新、存储数据都按 id 关联。 |
| `name` | ✅ | 显示名称。 |
| `version` | ✅ | 1–4 段数字，如 `1.0.0`。 |
| `main` | 视情况 | 入口脚本相对路径，必须位于插件包内，须为 UTF-8 编码。提供命令、文本动作、预览器、事件、校验器、格式化器、悬停或补全时必需；只提供声明式内容（主题、语言、语法、快捷键等）时省略，插件不会启动进程。 |
| `contributes` | ✅ | 插件提供的功能：`commands`（第 9 节）、`textActions`、`previewers`、`panels`、`configuration`（第 11 节）、`events`（第 12 节）、`validators`（第 13 节）、`formatters`（第 14 节）、`languageAssociations`（第 16 节）、`statusItems`、`hoverProviders`、`completionProviders`、`inspectorSections`（第 17 节）、`languageFeatures`（第 17 节）、`menus`、`workspaceTools`、`pasteDetectors`、`settingsPages`、`customEditors`（第 18 节）、`pages`（第 19 节），以及声明式的 `languages`、`languageGroups`、`grammars`、`themes`、`keybindings`、`textTools`、`toolCategories`（见[扩展开发手册](extension-guide.md)）。除 `configuration` 外至少提供一种。 |
| `description` | | 一句话说明，显示在安装确认框和设置页。 |
| `author` | | 作者。 |
| `homepage` | | 主页，必须是 http(s) 地址；设置页显示“主页”链接。 |
| `minAppVersion` | | 需要的最低应用版本；应用版本更低时拒绝导入并提示。 |
| `permissions` | | 见下表与[第 21 节](#21-权限网络剪贴板文档与命令)。不需要时不要填写。 |
| `limits` | | 需要超过缺省值的资源上限，见下方[资源上限](#资源上限)。 |
| `apiVersion` | | 编写插件时使用的 API 版本，即 `toolbox.version` 的值（当前为 1）。可省略；高于应用支持的版本时拒绝导入。 |
| `icon`、`readme`、`changelog`、`repository`、`license`、`categories` | | 插件中心详情页显示的信息，见 第 19 节。 |
| `extensionDependencies`、`activationEvents` | | 依赖的其他扩展、唤醒时机，见下方[依赖与唤醒](#依赖与唤醒)。只有缺了就无法工作的插件才需要列在这里。 |
| `exports` | | 其他插件可以调用的函数名，由 `toolbox.extensions.export(name, fn)` 实现。列在这里就是公开的：任何插件都可以用 `toolbox.extensions.call` 调用，`context.caller` 是调用方；可选依赖先用 `toolbox.extensions.info(id)` 判断是否存在。只提供导出函数、没有其他功能的“库插件”也可以安装。 |
| `singleProcess` | | `true` 时插件的所有代码共用一个进程（共享全局变量）；见[第 22 节](#22-运行环境与限制)。联网插件需要同时声明 `"documents": "all"`。 |

### `permissions`

| 键 | 取值 | 作用 |
|---|---|---|
| `network` | 主机数组，最多 100 个：精确域名或 IP（`api.github.com`、`localhost`、`192.168.1.10`、`::1`）；通配域名 `*.example.com`（包括 `example.com` 本身和所有子域）；加端口只允许该端口（`localhost:8080`、`[::1]:3000`，不加端口为任意端口）；网段 `192.168.0.0/16`、`10.0.0.0/8`、`fd00::/8`。不要写 `http://` 或路径。需要访问所有网站时只写 `["*"]`（不能和其他主机混写）。 | 允许 `fetch`、`toolbox.net` 访问这些主机（http/https/ws/wss）；面板与预览页面也可以显示这些主机上的图片和音视频 |
| `clipboard` | `true` / `"write"` / `false` | `true`：读写剪贴板；`"write"`：只写入（如“复制为 curl”），安装时不显示“读取剪贴板” |
| `documents` | `"active"`（缺省）/ `"all"` | 读取所有打开的文档，并允许在后台入口联网，见[第 21 节](#21-权限网络剪贴板文档与命令) |
| `background` | `true` / `false` | 插件进程常驻：保持 WebSocket 等长连接和定时任务，不因空闲结束；用户可在插件中心停止 |
| `commands` | 命令 id 数组，可用通配，如 `["file.save", "tools.*"]` | 允许执行应用命令，见[第 21 节](#21-权限网络剪贴板文档与命令) |

出现其他键时导入失败。安装确认框会逐项列出申请的权限，用户同意后才安装；更新时如果新增了权限，确认框会单独指出。

### `contributes.textActions[]`

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | ✅ | 插件内唯一，`[A-Za-z0-9_.-]`，最长 64。需与 `registerTextAction` 的第一个参数一致。 |
| `title` | ✅ | 菜单中显示的名称。 |
| `description` | | 菜单提示、命令面板副标题。 |
| `icon` | | SF Symbols 名称（如 `arrow.up.arrow.down`），缺省为拼图图标。可在 Apple 的“SF Symbols”应用中查找。 |
| `languages` | | 只在这些语言的文档中出现；省略或空数组表示所有语言。取值见[语言名称](#语言名称)。 |
| `resultTarget` | | 结果去向：`replace`（替换选区/全文）、`newTab`（新标签）、`preview`（右侧分屏预览，可再选择替换或新建）。省略时使用用户在检查器中选的“结果去向”。 |
| `resultLanguage` | | 结果在新标签打开时使用的语言，如 `markdown`。 |
| `keywords` | | 命令面板搜索用的额外关键词（空格分隔）。 |

### `contributes.previewers[]`

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | ✅ | 插件内唯一，规则同上。需与 `registerPreviewer` 的第一个参数一致。 |
| `title` | ✅ | 预览器名称。 |
| `description` | | 说明。 |
| `fileExtensions` | 二选一 | 匹配的文件扩展名，**不带点**，不区分大小写，如 `["csv", "tsv"]`。 |
| `languages` | 二选一 | 匹配的编辑器语言，取值见[语言名称](#语言名称)。 |

### `contributes.panels[]`

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | ✅ | 插件内唯一，规则同上。 |
| `title` | ✅ | 窗口标题、菜单名称。 |
| `entry` | ✅ | 面板页面在包内的相对路径，必须是 `.html`/`.htm` 文件，须为 UTF-8 编码。 |
| `description` | | 命令面板副标题。 |
| `icon` | | SF Symbols 名称，缺省为窗口图标。 |
| `width` / `height` | | 初始窗口大小（点），默认 560 × 440，范围 320–1600 × 240–1200。用户调整过的大小与位置会被记住。 |
| `multiple` | | `true` 时可以同时打开多个窗口：`toolbox.panels.open(id, { newWindow: true, args })`。 |

### 语言名称

`languages` 中的值不区分大小写，可以写显示名或内部名，例如：

| 写法 | 语言 |
|---|---|
| `json` / `JSON` | JSON |
| `xml`、`yaml`、`toml`、`ini`、`sql`、`graphql` | 对应格式 |
| `markdown`、`html`、`css`、`scss`、`less` | 对应格式 |
| `javascript`、`typescript`、`jsx`、`tsx`、`vue`、`svelte` | 前端 |
| `swift`、`kotlin`、`java`、`go`、`rust`、`python`、`ruby`、`php`、`c`、`cpp`（或 `C++`）、`csharp`（或 `C#`）、`shell`… | 编程语言 |
| `plainText`（或 `纯文本`） | 纯文本（包括 .csv、.log 等没有专门语言的文件） |

写了无法识别的名称时导入会失败并指出是哪一个。

### 资源上限

**等待没有时间上限**：网络请求、对话框、定时器、长连接都可以等任意久，等待期间不占 CPU，也不阻塞同一插件的其他调用。下面的上限只约束内存中一次持有的大小，以及自动运行的代码连续计算的时间。需要更多时，在清单中用 `limits` 申请：

```json
"limits": { "storageBytes": 268435456, "responseBytes": 268435456, "memoryBytes": 4294967296 }
```

| 键 | 作用 | 缺省 | 最多 |
|---|---|---|---|
| `storageBytes` | `toolbox.storage` 的总大小 | 16 MiB | 1 GiB |
| `fileReadBytes` | 一次**整体**读取的文件（`pickFile`、`files.readText`）。`files.readBase64` 分段读取不受限 | 64 MiB | 1 GiB |
| `responseBytes` | 同一插件保存在宿主内存中的响应正文总量。流式响应使用背压，下载文件使用磁盘预算 | 64 MiB | 1 GiB |
| `privateDiskBytes` | 私有文件目录和临时下载合计 | 4 GiB | 64 GiB |
| `networkConnections` | 同时进行的 HTTP 请求、WebSocket、SSE 和 TCP 连接合计 | 64 | 512 |
| `transferBytes` | 插件与应用之间一次传递的数据：返回值、写入编辑器或文件的文本、面板消息、存储的单个值 | 64 MiB | 512 MiB |
| `documentBytes` | 整篇交给校验器、事件、悬停、补全、语言功能的文档；更大的文档，悬停等功能拿到光标附近的片段（`textOffset` 标明起点） | 8 MiB | 128 MiB |
| `memoryBytes` | 插件进程的内存；超过时进程被结束 | 2 GiB | 16 GiB |
| `busySeconds` | **自动运行**的代码（校验器、预览器、事件、内联提示、折叠）连续计算多少秒后被停止。用户触发的代码从不被自动停止，见[第 22 节](#22-运行环境与限制) | 120 | 3600 |

- 更大的数据不必放进内存：文件用令牌分段读写（第 10 节），响应用 `stream` 或 `file` 接收（第 21 节）。
- 申请高于缺省值时，安装确认框会列出“使用更多资源”；更新时提高了上限，也会标为新增。
- 超过最大值或写了其他键时，导入失败。只申请真正需要的大小。

### 依赖与唤醒

| 字段 | 取值 | 作用 |
|---|---|---|
| `extensionDependencies` | 扩展 id 数组，可写 `id@版本范围`，如 `com.example.base@^2.1` | 依赖缺失、未启用或版本不符时，本插件不生效并显示原因。 |
| `activationEvents` | `onStartup`、`onLanguage:<语言 id>`、`onCommand:<命令 id>`、`onWorkspaceTool:<工具 id>` | 在指定时机提前启动插件进程。 |

### 清单本地化

`plugin.json` 的展示字段可以写成 `"%key%"`。应用从插件包的 `nls.json` 取值，并优先使用当前语言文件中的同名键。可翻译字段包括插件名称、描述、贡献项的标题和说明、设置选项的标签。请直接填写插件 ID、入口路径、依赖、权限及设置默认值。

```json
{ "name": "%plugin.name%" }
```

```json
{ "plugin.name": "行倒序" }
```

---

## 5. JavaScript API 参考

插件代码运行在两个地方，能用的 API 不同：

| 环境 | 是什么 | 能用 |
|---|---|---|
| **main.js** | 插件自己的 JavaScript 环境（JavaScriptCore），没有 DOM | 下面的 `toolbox`（同步 API），以及[常用的 Web 标准全局对象](#mainjs-中的-web-标准全局对象) |
| **面板页面** | WebKit 页面（工具面板的 HTML） | 第 8 节的 `window.toolbox`（全部返回 Promise） |
| **预览页面** | WebKit 页面（预览器返回的 HTML） | 没有 `toolbox`，只是一个展示页面 |

### main.js 中的 `toolbox`

快速的本地读写（`storage`、`settings`、`secrets`、纯文本剪贴板）是同步的；凡是可能等待的调用（网络、编辑器、对话框、文件、其他插件）都返回 **Promise**。同一个插件可以同时进行多个调用，等待期间不占用插件，也不计入任何时限。

```ts
toolbox.version: number; toolbox.has(name: string): boolean
toolbox.env: { appName, appVersion, apiVersion, language, platform, arch, osVersion, pluginID, pluginVersion, callbackURI(path?), onOpenURI(fn) }
toolbox.lane: 'interactive' | 'background'                         // 当前进程，见第 22 节“进程与并发”

// 入口：每个函数的第二个参数（命令为第一个）是 context
type EntryContext = { signal: AbortSignal, progress(fraction: number | null, message?: string): void,
                      language?, fileName?, hasSelection?, tab?, panel?, instance?, caller? }   // caller：导出函数的调用方插件
                                                                    // tab：命令所针对的文档；从标签右键菜单、代码透镜、行号栏图标运行时是那个标签
toolbox.commands.register(id, (context, ...args) => any)          // 第 9 节；返回值交给 executeCommand 的调用方
toolbox.registerTextAction(id, (input, context) => string | { text, message? })
toolbox.registerPreviewer(id, (input, context) => string | { html })
toolbox.registerPanelHandler(name, (payload, context) => any)      // 第 8 节
toolbox.registerValidator / registerFormatter / registerHoverProvider / registerCompletionProvider   // 第 13、14、17 节
toolbox.languages.register(kind, id, fn)                           // 定义、符号、引用、语义高亮、代码操作、重命名、内联补全、代码透镜…，第 17 节
toolbox.languages.setDiagnostics(key, problems, { tab? }) / clearDiagnostics(key, { tab? })   // 随时推送问题，第 13 节
toolbox.events.on(name, (doc, context) => void | Promise)          // 第 12 节；返回取消订阅的函数
toolbox.lifecycle.onDeactivate(() => void | Promise)               // 进程即将结束（空闲、更新、停用），最多 2 秒
// 以上 register 都返回取消注册的函数。

// 网络（需要 permissions.network），第 21 节
fetch(input, init?): Promise<Response>                             // 标准 fetch：Request、Response、ReadableStream 正文
toolbox.net.request(options): Promise<NetResponse>                 // 暴露全部能力的底层接口
new WebSocket(url, protocols?) / new EventSource(url)              // 与浏览器相同
toolbox.net.socket(url, { protocols?, headers?, cookies?, proxy?, tls?, timeout? }): Connection
toolbox.net.eventSource(url, { method?, body?, headers?, cookies?, proxy?, tls? }): Connection   // 可用 POST
toolbox.net.tcp(host, port, { tls?, timeout? }): Connection        // 原始 TCP（Redis、SMTP、数据库协议）；tls 为 true 或选项对象
toolbox.net.clearCookies(): Promise<void>

// 编辑器（Promise），第 10 节
toolbox.editor.getText({ start?, length?, tab? }) / replace(text) / replaceRange(start, length, text, { tab? })
toolbox.editor.applyEdits([{ start, length, text }], { tab?, expectedRevision? })   // 多处修改，一次撤销
toolbox.editor.insert(text) / getSelection() / setSelection(start, length?, { ranges? })
toolbox.editor.openTab(text, { language?, title?, fileName? }): Promise<tabID> / closeTab(tab)
toolbox.editor.openFile(fileToken): Promise<tabID>                 // 把用户给的文件作为真正的文档打开
toolbox.editor.setLanguage(language, { tab? })
toolbox.editor.reveal(offset, { tab? }) / positionAt(offset) / offsetAt(line, column) / listTabs()
toolbox.editor.setDecorations(key, decorations, { tab? }) / clearDecorations(key, { tab? })   // 背景、下划线、行尾文字、行号栏图标（gutter），第 17 节

// 交互（Promise），第 10 节
toolbox.ui.showMessage(text, kind?, { buttons? }) / showInput(options) / showPick(items, { multiple?, … }) / confirm(text, options)
toolbox.ui.openExternal(url) / notify(title, { body? })            // 默认浏览器打开链接；系统通知
toolbox.statusBar.set(id, { text, tooltip?, command?, args?, symbol?, color?, menu? }) / clear(id)
toolbox.executeCommand(id, ...args): Promise<any>
toolbox.context.set(key, value)                                    // 供 when.context 使用，第 9 节
toolbox.panels.open(id, { args?, newWindow? }) / post(target, message) / onMessage(fn) / close(target) / list()
toolbox.previews.refresh()                                         // 让本插件的预览重新渲染

// 文件：用户选择的文件以令牌表示，第 10 节
toolbox.workspace.pickFile(options) / pickFiles(options) / pickFolder({ remember? }) / saveFile(content, { name?, types? })
toolbox.files.stat / list / readText / readBase64 / readBytes / writeText / writeBytes / watch(token, fn)
toolbox.files.dataFolder() / remove / mkdir / move / copy / release   // 插件私有文件夹与文件管理

// 数据（同步）
toolbox.storage.get(key, fallback?) / set(key, value) / remove(key) / keys(prefix?) / getMany(keys) / setMany(values) / usage()
toolbox.settings.get(key) / getAll() / set(key, value?)
toolbox.secrets.get(key) / set(key, value) / delete(key)
toolbox.clipboard.readText() / writeText(text)                     // 同步
toolbox.clipboard.read({ types? }) / write(items)                  // Promise：HTML、RTF、图片、文件

// 其他插件
toolbox.extensions.export(name, fn); toolbox.extensions.call(pluginID, name, ...args): Promise<any>; toolbox.extensions.info(pluginID)

toolbox.log(...values); console.log / info / debug / warn / error / assert
```

`input` 的字段：

```ts
type Input = {
  text: string           // 文本动作：有选区时为选区，否则为全文；预览器：全文
  hasSelection: boolean
  language: string       // 编辑器语言显示名，如 "JSON"、"Markdown"、"纯文本"
  fileName: string       // 文件名（未保存的新文档为空字符串）
  tab?: string           // 标签页 id
}
```

- `input` 是只读对象，修改它不会生效。
- 同一个 id 重复注册时，以后注册的为准。
- 命令、文本动作、预览器、面板、语言功能的 id 必须在 `plugin.json` 中声明，菜单里才会出现；声明了但没有注册时，运行时会报“插件没有注册 …”。面板处理函数的名称不需要声明。
- **取消**：调用方不再等待时（用户点“停止”、面板关闭、悬停已过时、有更新的请求），`context.signal` 会触发。把它传给 `fetch`/`toolbox.net.request` 的 `signal`，请求会真正中断。

### main.js 中的 Web 标准全局对象

JavaScriptCore 本身只有 ECMAScript。运行时补上了下面这些常用的 Web 标准对象，行为与浏览器一致，为浏览器写的库（以及很多为 Node 写的库）可以直接使用。除网络外都是纯计算，不需要权限，也可以在后台入口中使用。

| 全局对象 | 说明 |
|---|---|
| `TextEncoder`、`TextDecoder` | UTF-8 编码与解码。`TextDecoder` 还支持 `utf-16le`、`utf-16be`，以及 `fatal`、`ignoreBOM`、`{ stream: true }` |
| `atob`、`btoa` | Base64，与浏览器相同：处理的是每个字符 0–255 的“二进制字符串”。编码 UTF-8 文本请先用 `TextEncoder`（见下例） |
| `URL`、`URLSearchParams` | 按 WHATWG 标准解析和拼接地址：相对地址、`..`、默认端口、IPv4/IPv6、中文域名（转为 `xn--`）、百分号编码；`searchParams` 与 `url.search` 双向同步 |
| `crypto.getRandomValues`、`crypto.randomUUID` | 系统安全随机数；`getRandomValues` 一次最多 65536 字节 |
| `crypto.subtle`、`CryptoKey` | 标准 Web Crypto，所有方法（`digest`、`generateKey`、`importKey`、`exportKey`、`sign`、`verify`、`encrypt`、`decrypt`、`deriveBits`、`deriveKey`、`wrapKey`、`unwrapKey`）。算法见下表；运算在应用中用 CryptoKit 和系统安全框架完成 |
| `AbortController`、`AbortSignal` | 包括 `AbortSignal.abort()`、`timeout()`、`any()`、`throwIfAborted()`；传给 `fetch`/`toolbox.net.request` 的 `signal` 可以中断进行中的请求 |
| `fetch`、`Headers`、`Request`、`Response` | 标准 fetch：响应正文是字节流（`response.body` 是 `ReadableStream`），`arrayBuffer()`、`blob()`、`text()`、`json()` 都按标准工作，二进制不会损坏，大响应也不必整个放进内存。见第 21 节；需要 `permissions.network` |
| `WebSocket`、`EventSource` | 与浏览器相同；`EventSource` 断开后自动重连（遵守 `retry`，带 `Last-Event-ID`）。需要 `permissions.network` |
| `Blob`、`File`、`FormData` | `FormData` 可以直接作为 `fetch` 的正文（multipart 上传） |
| `ReadableStream`、`WritableStream`、`TransformStream`、`TextEncoderStream`、`TextDecoderStream` | 读取器、写入器、`for await`、`pipeTo`、`pipeThrough`、`tee`、`ReadableStream.from` |
| `MessageChannel`、`MessagePort`、`setImmediate`、`performance`、`navigator`、`self` | `performance.now()` 是单调时钟 |
| `Buffer`、`process`（Node） | `Buffer` 是 `Uint8Array` 的子类，支持 utf8、hex、base64、base64url、latin1、ascii、utf16le 与常用读写方法；`process` 只有 `env`、`nextTick`、`hrtime`、`platform` 等。没有 `process.versions.node`，以免库去加载不存在的 Node 模块 |
| `Event`、`EventTarget`、`DOMException` | 可以用来给自己的对象加事件 |
| `queueMicrotask`、`structuredClone` | `structuredClone` 支持循环引用、`Date`、`RegExp`、`Map`、`Set`、`ArrayBuffer`、类型化数组、错误对象；不支持 `transfer` |

```js
const bytes = new TextEncoder().encode("用户:密码");
const basic = "Basic " + btoa(String.fromCharCode(...bytes));          // UTF-8 文本的 Base64

const url = new URL("../v2/items?page=1", "https://api.example.com/v1/");
url.searchParams.set("q", "砚 台");                                      // https://api.example.com/v2/items?page=1&q=%E7%A0%9A+%E5%8F%B0

const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret),
  { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
const signature = new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payload)));
const hex = Array.from(signature, (b) => b.toString(16).padStart(2, "0")).join("");
```

`crypto.subtle` 支持的算法（`main.js` 与面板页面相同）：

| 用途 | 算法 | 密钥格式 |
|---|---|---|
| 摘要 | SHA-1、SHA-256、SHA-384、SHA-512 | — |
| 消息认证 | HMAC | `raw`、`jwk` |
| 对称加密 | AES-GCM（12 字节 iv、128 位 tag）、AES-CBC、AES-CTR | `raw`、`jwk` |
| 密钥派生 | PBKDF2、HKDF | `raw` |
| 签名 | ECDSA（P-256、P-384、P-521）、RSASSA-PKCS1-v1_5、RSA-PSS（saltLength 等于摘要长度）、Ed25519 | `spki`、`pkcs8`、`jwk`；EC 和 Ed25519 公钥另有 `raw` |
| 密钥协商 | ECDH（P-256、P-384、P-521）、X25519 | 同上 |
| 公钥加密 | RSA-OAEP（不支持 label） | `spki`、`pkcs8`、`jwk` |

不支持 AES-KW；不支持的算法返回 `NotSupportedError`。RSA 生成密钥只支持公共指数 65537。常见用法如 JWT 的 HS256/RS256/ES256、加密保存数据、口令派生密钥都可以直接写。

与浏览器的差别：

- 没有 `XMLHttpRequest`、DOM、`URL.createObjectURL`，也没有 Node 的 `fs`、`net` 等模块。读写用户选择的文件用 `toolbox.files`。
- `fetch` 的 `redirect: "manual"` 返回 3xx 响应本身（浏览器返回不透明响应）；`init` 还可以带 `timeout`、`totalTimeout`、`maxBytes`、`cookies`、`proxy`、`tls`，响应另有 `httpVersion`、`redirects`、`timing`。
- 类型声明：这些对象的类型来自 TypeScript 的 `dom` 库（`Buffer`、`process` 来自 `@types/node`），在 `tsconfig.json` 的 `lib` 中加入 `"dom"` 即可。

各 API 可用的位置：

| API | 命令、文本动作、面板处理函数 | 事件处理函数 | 预览器、校验器、悬停、补全 | 格式化器 |
|---|---|---|---|---|
| `storage`、`settings.get/getAll`、`secrets`、`net`/`fetch`、`clipboard`、`files`、`log` | ✅ | ✅ | ✅ | ✅ |
| `editor.setDecorations/clearDecorations`、`languages.setDiagnostics` | ✅ | ✅ | ✅ | ✅ |
| `ui.showMessage`、`statusBar` | ✅ | ✅ | — | — |
| `settings.set`、`editor` 的其余方法、`ui.showInput/showPick/confirm/openExternal`、`executeCommand`、`workspace`、`panels.open` | ✅ | 声明 `documents: "all"` 后 ✅ | — | — |

事件、预览器、校验器、悬停、补全、内联提示、折叠、语义高亮、内联补全、代码透镜和自定义编辑器属于**后台入口**（不由用户直接触发）。联网插件没有声明 `documents: "all"` 时，后台入口在单独的进程（`toolbox.lane === 'background'`）中运行，这个进程里的代码不能联网，也不能调用 `storage.set`、`secrets.set`、`settings.set`、`clipboard.write*`、`files.write`、`context.set`，见[第 21 节](#21-权限网络剪贴板文档与命令)。另一个进程（`'interactive'`）不受此限：main.js 载入时的顶层代码、定时器、`onDeactivate`、导出函数在那里都可以联网和保存数据。

声明了 `documents: "all"` 的插件，事件处理函数以及不属于任何调用的代码（`main.js` 顶层、由它们设置的定时器、连接的回调）可以做命令能做的所有事：修改编辑器、打开面板、弹对话框、执行命令，例如“打字时自动闭合标签”“收到推送时打开面板”。

导出函数（`toolbox.extensions.export`）由另一个插件调用。调用方是用户触发的代码（命令、面板等）时，导出函数也可以用 `ui.showMessage/showInput/showPick/confirm`、`workspace`、`executeCommand`、`panels.open`（例如弹出登录框），但不能读写调用方的文档；`context.caller` 是调用方插件的 id。

---

## 6. 文本动作详解

### 输入与输出

```js
toolbox.registerTextAction("wrapQuotes", (input) => {
  if (!input.text) throw new Error("请先选中文本");
  const lines = input.text.split("\n").map((line) => `"${line}"`);
  return { text: lines.join(",\n"), message: `已处理 ${lines.length} 行` };
});
```

- 返回**字符串**：作为新文本。
- 返回 `{ text, message }`：`message` 显示在编辑器底部的提示条中（缺省为“<标题> 完成”），2 秒后自动消失。
- **抛出异常**：动作失败，`Error.message` 以红色显示在编辑器底部的提示条中（直到用户关闭或执行下一个动作），文档不会被修改。请让错误信息直接告诉用户该怎么做，例如“请输入 owner/repo，例如 apple/swift”。
- 运行期间编辑器底部显示“正在运行插件：<标题>…”和进度指示；联网等耗时操作不需要自己提示。
- 返回与原文相同的文本：文档不变（适合只修改设置的动作，见第 20 节示例）。

### 结果去向

| `resultTarget` | 行为 |
|---|---|
| `replace` | 有选区时只替换选区，否则替换全文；可用 ⌘Z 撤销。 |
| `newTab` | 在新标签打开结果；语言取 `resultLanguage`。 |
| `preview` | 在右侧分屏显示结果，用户可再选择“替换原文”或“在新标签打开”。 |
| 省略 | 跟随用户在检查器中选择的结果去向。 |

### 在处理步骤中使用

用户可以在“处理步骤”里添加 **插件 → 你的动作**，与内置步骤串联。此时：

- `input.text` 是上一步的输出，`hasSelection` 为 `false`，`language`、`fileName` 为空字符串；
- 返回值中的 `message` 会被忽略；
- 处理步骤的输入输出上限为 1 MiB。

---

## 7. 预览器详解

### 何时使用

用户打开一个与 `fileExtensions` 或 `languages` 匹配的文件时，标签顶部出现 **预览 / 源码 / 分屏** 切换条：

- **预览**：只显示你的 HTML；**分屏**：左侧源码、右侧实时预览；**源码**：普通编辑。
- 文本变化后约 150 ms 重新调用你的函数；用户切换到预览/分屏时也会调用；插件存储发生变化时也会重新调用。
- 匹配优先级：内置预览（Markdown、HTML）优先，其次按扩展名匹配的插件，再次按语言匹配的插件；多个插件都匹配时取第一个（按插件名排序）。用户可在 设置 → 插件 → 格式化与预览 中为某个语言或扩展名改选你的预览器，包括替代 Markdown、HTML 的内置预览（见[第 15 节](#15-格式化预览与校验的选择)）。
- 超过 90 万字符的文档或以大文件模式打开的文档不提供预览。

### 返回 HTML

```js
toolbox.registerPreviewer("page", (input) => {
  const lines = input.text.split("\n").length;
  return `<!doctype html>
    <html><head><meta charset="utf-8"><link rel="stylesheet" href="style.css"></head>
    <body><h1>${escapeHTML(input.fileName)}</h1><p>${lines} 行</p></body></html>`;
});
```

- 可返回完整文档或片段；建议返回带 `<meta charset="utf-8">` 的完整文档。
- **一定要转义**用户文本中的 `& < >`，否则文档内容会被当作 HTML 解析。
- 抛出异常时，预览区显示一个错误页，内容为异常信息。
- 预览器在后台进程运行：联网插件需要声明 `documents: "all"` 才能在预览器里联网。

### 页面规则（预览页面与面板页面相同）

| 项目 | 规则 |
|---|---|
| 页面脚本 | 可以运行（`<script>` 内联或引用包内 .js）。预览页面中没有 `toolbox`；面板页面有 `window.toolbox`（第 8 节）。 |
| 相对路径 | 预览页面以**插件包根目录**为基准；面板页面以 **entry 所在目录**为基准。 |
| 允许加载 | 插件包内的文件、`data:`、`blob:`、内联样式与脚本。 |
| 框架 | `<iframe>` 可以加载插件包内的页面、`blob:` 和 `srcdoc`（例如在沙箱 iframe 中显示不可信的 HTML），它们继承同样的规则；不能加载 `data:` 和网络地址。 |
| 禁止加载 | 任何网络地址（http/https/websocket 等）、插件包以外的本地文件。CDN 上的库请下载后放进插件包。 |
| 跳转 | 面板可以在插件包内的页面之间跳转（链接、`location.href`、前进后退、刷新），每个页面都有同样的规则；用户点击 http(s) 链接时在默认浏览器打开；`#锚点` 链接在页内滚动；表单提交和跳到包外都会被阻止。预览页面不跳转。 |
| 深色模式 | 页面跟随系统外观，用 `@media (prefers-color-scheme: dark)` 适配；建议在 `:root` 写 `color-scheme: light dark`。 |
| 安全上下文 | 面板页面是安全上下文（`window.isSecureContext` 为 `true`），`crypto.subtle`、`crypto.randomUUID` 等只在安全上下文提供的浏览器 API 都可以用。 |

---

## 8. 工具面板详解

工具面板是插件自带的 HTML 界面，在独立窗口中打开，适合需要输入框、按钮、列表的工具（查询器、生成器、转换器等）。

### 声明

```json
"contributes": {
  "panels": [
    { "id": "lookup", "title": "GitHub 仓库查询", "entry": "panel/index.html", "width": 520, "height": 460 }
  ]
}
```

用户从 菜单栏 工具 → 插件 → *GitHub 仓库查询…*、命令面板，或插件中心的详情页打开它；`main.js` 也可以用 `toolbox.panels.open(id, { args })` 打开并传参数。面板缺省只有一个窗口（再次打开时把新的 `args` 作为消息 `{ type: "args", args }` 发给已有窗口）；声明 `"multiple": true` 后可以用 `newWindow: true` 打开多个。插件被停用、更新或卸载时，它的面板窗口会自动关闭；面板打开期间，插件进程不会因空闲而结束。

> 面板页面中 `window.alert/confirm/prompt` 不可用，请用 `toolbox.ui.confirm/showInput/showPick`（由应用实现，注明来自哪个插件）。需要跟随编辑器时，在 `main.js` 监听 `textChanged`/`selectionChanged` 事件，再用 `toolbox.panels.post` 推送给页面；自定义编辑器可以使用 `toolbox.editor.onChange`（第 18 节）。

### 页面中的 `window.toolbox`

面板页面加载前，应用会注入 `window.toolbox`，**所有方法都返回 Promise**：

```ts
toolbox.version / has(name)
toolbox.args: any                        // panels.open 传入的参数，没有时为 null
toolbox.instance: string                 // 本窗口的实例 id（panels.post 的目标）
toolbox.theme: { dark, colors, fonts }   // 应用的颜色与字体；也是 CSS 变量 --toolbox-bg、--toolbox-fg、--toolbox-accent、--toolbox-font-mono…
toolbox.onThemeChange(fn) / onDrop(fn: (files: FileHandle[]) => void) / onMessage(fn)   // 返回取消订阅的函数
toolbox.post(message)                    // 单向消息给 main.js 的 toolbox.panels.onMessage，不占用调用
toolbox.invoke(name, payload?, { signal? })   // 调用 registerPanelHandler 注册的函数；signal 中止时 main.js 的 context.signal 也触发
toolbox.panel.setTitle(text) / setEdited(bool) / setSize(width, height) / setAlwaysOnTop(bool) / focus()   // setEdited(true) 时关闭窗口前询问用户
toolbox.close()
toolbox.env                              // 与 main.js 的 toolbox.env 相同（没有 callbackURI、onOpenURI）

toolbox.settings.get / getAll / set / onChange
toolbox.storage.get / set / remove / keys(prefix?) / getMany / setMany / usage / onChange(fn: (keys) => void)
toolbox.editor.getText / replace / replaceRange / applyEdits / insert / openTab / closeTab / getSelection / setSelection
               / reveal / positionAt / offsetAt / listTabs / setDecorations / clearDecorations / onChange
toolbox.ui.showMessage / showInput / showPick / confirm / openExternal / notify
toolbox.workspace.pickFile / pickFiles / pickFolder / saveFile        // 二进制（ArrayBuffer、{ base64 }）、文件令牌都可以保存
toolbox.files.stat / list / readText / readBase64 / readBytes / writeText / writeBytes / dataFolder / remove / mkdir / move / copy / release
toolbox.clipboard.readText / writeText / read / write
toolbox.statusBar.set / clear; toolbox.executeCommand(id, ...args); toolbox.context.set; toolbox.panels.open; toolbox.previews.refresh
```

面板页面没有 `secrets` 和网络，需要时交给 `main.js`。页面可以：

- **接收拖入的文件**：拖到面板上的文件以文件令牌交给 `onDrop`，可以直接 `files.readBytes`，或交给 `main.js` 上传。
- **下载文件**：`<a download>`、`blob:` 链接会弹出保存对话框。
- **显示远程图片**：`<img>`、`<video>` 可以加载插件 `permissions.network` 中的主机。
- **使用 `localStorage`、IndexedDB**：每个插件的页面有自己的存储，其他插件看不到，卸载时删除。

出错时 Promise 被拒绝，`error.message` 是可以直接展示给用户的说明。

### 页面与 main.js 分工

面板页面本身**不能联网**。需要网络或复杂计算时，在 `main.js` 注册处理函数，页面用 `toolbox.invoke` 调用：

```js
// main.js
toolbox.registerPanelHandler("lookup", async (payload, context) => {
  const response = await fetch(`https://api.github.com/repos/${payload.name}`, { signal: context.signal });
  if (!response.ok) throw new Error(`GitHub 返回 ${response.status}`);
  return response.json();                       // 返回值须可 JSON 序列化
});

// 推送：进度、流式响应、WebSocket 消息
toolbox.panels.post("lookup", { type: "progress", done: 3, total: 10 });   // 目标为面板 id（全部窗口）或实例 id
```

```js
// panel/panel.js
const repo = await toolbox.invoke("lookup", { name: "apple/swift" });
```

- `payload` 与返回值都经过 JSON 序列化：可以是对象、数组、字符串、数字、布尔、null；函数、`undefined` 字段、循环引用不能传递（`undefined` 返回值会变成 `null`）。
- 处理函数在 `main.js` 的环境里运行；同一插件的多个调用可以同时进行（一个在等网络时，另一个照常执行）。

### 读取与写回编辑器

`editor.*` 作用于**主编辑器当前选中的标签**：

```js
const { text, hasSelection } = await toolbox.editor.getText();   // 有选区时为选区，否则为全文（最多 limits.transferBytes）
await toolbox.editor.replace(text.toUpperCase());                 // 写回同一位置，可 ⌘Z 撤销
```

- `replace` 写回的是**最近一次 `getText()` 读到的那段**：有选区时替换那段选区，否则替换全文。必须先调用 `getText()`。
- 读取之后如果文档被修改过，`replace` 会拒绝并提示，以免覆盖用户新输入的内容；重新 `getText()` 即可。
- `openTab(text, language)` 在新标签打开文本，`language` 取值同[语言名称](#语言名称)。

---

## 9. 通用命令

文本动作只能“收到文本、返回文本”。**通用命令**没有这个限制：命令函数里可以读写编辑器、弹出输入框或选择列表、读取设置、联网（需权限），可以接收参数、返回任意值。

### 声明

```json
"contributes": {
  "commands": [
    { "id": "insertDate", "title": "插入当前日期", "icon": "calendar", "keywords": "date 日期" },
    { "id": "prefixLines", "title": "给选中的行加前缀…",
      "menus": ["editorContext", "palette"],
      "when": { "selection": true, "languages": ["markdown", "plainText"] } }
  ]
}
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | ✅ | 插件内唯一（与文本动作共用命名空间），`[A-Za-z0-9_.-]`，最长 64。 |
| `title` | ✅ | 菜单中显示的名称。需要用户进一步输入的命令，习惯上以“…”结尾。 |
| `description`、`icon`、`keywords` | | 同文本动作。 |
| `menus` | | 出现在哪里：`editorContext`（编辑器右键 → 插件）、`tools`（菜单栏 工具 → 插件）、`palette`（命令面板）。省略表示三处都出现。 |
| `when` | | 显示条件，全部满足才出现（工具菜单中不满足时显示为灰色）：`languages`（语言列表）、`fileExtensions`（扩展名列表，不带点）、`selection`（`true` 只在有选区时，`false` 只在没有选区时）、`context`（插件自己用 `toolbox.context.set` 设置的状态，如 `"loggedIn && (mode == 'json' || count > 3)"`，支持 `!`、`==`、`!=`、`<`、`<=`、`>`、`>=`、`&&`、`\|\|` 和括号；字符串用引号，引号内可以有任何字符）。 |
| `keybinding` | | 快捷键，如 `"cmd+shift+k"`，必须包含 cmd 或 ctrl。与应用快捷键或其他插件冲突时不生效，原因显示在 设置 → 快捷键。 |

### 注册

```js
toolbox.commands.register("insertDate", async (context, format) => {
  // context: { language, fileName, hasSelection, tab, progress, signal }；后面是调用方传的参数
  // tab 是命令针对的文档：通常是当前标签；从标签右键菜单、代码透镜、行号栏图标运行时是那个标签
  const text = new Date().toISOString().slice(0, 10);
  await toolbox.editor.insert(text);
  return { message: `已插入 ${text}` };      // 可选：成功提示；也可以直接返回字符串或任意可序列化的值
});

const result = await toolbox.executeCommand("com.yourname.tools/insertDate", "YYYY-MM-DD");   // 拿到返回值
```

- 运行时编辑器底部显示“正在运行插件：<标题>…”；结束后显示返回的提示，没有返回时显示“<标题> 完成”；抛出异常时显示红色错误。
- 命令里调用 `toolbox.ui.showMessage(...)` 后，该提示会保留，不会被“完成”覆盖。
- 命令可以运行任意久：底部会显示已运行的时间。等待网络、对话框不占用插件；JavaScript 连续计算超过 15 秒时，应用提示“已连续计算 N 秒”，由用户决定继续等待或停止，不会自动结束。
- 长任务调用 `context.progress(fraction, message)`（`fraction` 为 0–1，`null` 为不确定进度）。用户点“停止”时 `context.signal` 触发；仍在连续计算的脚本会被结束。
- 状态栏项、菜单可以在清单或 `statusBar.set` 中给命令带参数（`args`）；代码透镜和行号栏图标也可以带 `args`，常用来传行号。
- `context.language`、`context.fileName`、`context.hasSelection` 描述的都是 `context.tab` 那个文档。

### 文本动作还是命令？

| 需求 | 用 |
|---|---|
| 把选区/全文转换成另一段文本，可放进“处理步骤” | 文本动作 |
| 需要询问用户、在光标处插入、打开新标签、修改设置、只改某一部分 | 命令 |

---

## 10. 编辑器与交互 API

以下 API 都返回 Promise（在应用主线程完成）。没有时间上限：对话框可以等用户任意久，期间插件的其他调用照常进行。

### `toolbox.editor`

| 方法 | 说明 |
|---|---|
| `getText({ start?, length?, tab? })` | 返回 `{ text, hasSelection, language, fileName, start, length, documentLength, revision, tab, file }`（`file` 是该文档文件的只读令牌，可用 `files.*` 读取或作为语言功能的位置；未保存的新文档为 `null`）：当前标签的选区，没有选区时为全文；传入范围时按范围读取（大文件也可以分块读取）。`tab` 读取其他标签页，需要 `documents: "all"`。一次最多 `limits.transferBytes`。 |
| `replace(text)` | 写回**最近一次 `getText()` 读到的范围**，可 ⌘Z 撤销；读取后文档被改动过时拒绝。 |
| `applyEdits([{ start, length, text }], { tab?, expectedRevision?, undoTitle? })` | 多处修改作为**一个**撤销步骤，按修改前的偏移计算，全部成功或全部不生效。每处原地修改，相隔多远都不会改写中间的文本（大文件模式除外）。`expectedRevision` 与 `getText` 返回的 `revision` 不同时拒绝。返回 `{ revision }`。 |
| `replaceRange(start, length, text, { tab? })` | 单处修改，等同于只有一项的 `applyEdits`。 |
| `getSelection()` / `setSelection(start, length?, { ranges? })` | 选区；`ranges` 为多个选区（多光标）。 |
| `insert(text)` | 在光标处插入；有选区时替换选区。 |
| `openTab(text, { language?, title?, fileName? })` | 在新标签打开文本，返回标签 id，之后可以 `getText({ tab })`、`applyEdits(…, { tab })`、`closeTab(tab)`。 |
| `openFile(file)` | 把用户选择或拖入的文件（令牌）作为真正的文档打开（保存时写回原文件），已打开时切到它的标签；返回标签 id。 |
| `setLanguage(language, { tab? })` | 更改文档的语言。 |
| `setDecorations(key, decorations, { tab? })` | 见第 17 节；`tab` 给其他标签页加装饰（需要 `documents: "all"`）。任何入口都可以调用，校验器和事件里也可以。 |
| `reveal(offset, { tab? })` | 滚动到该位置并闪烁提示。 |
| `positionAt(offset)` / `offsetAt(line, column)` | 偏移与行列（从 1 开始）互转，大文件也可用。 |
| `listTabs()` | 所有标签 `{ id, fileName, title, language, isActive, isLarge, length, isEdited, file }`，需要 `documents: "all"`。 |

`start`、`length` 均为 UTF-16 偏移。写入其他标签页时，该标签会被切到前台。

### `toolbox.ui`

| 方法 | 结果 | 说明 |
|---|---|---|
| `showMessage(text, kind?, { buttons? })` | 无按钮时立即完成；有按钮时为所选按钮文字或 `null` | 编辑器底部提示。`kind`：`info`、`success`、`warning`、`error`。带 `buttons`（最多 4 个）时弹出对话框。 |
| `showInput({ title, prompt, value, placeholder, password?, multiline? })` | 字符串或 `null` | `password` 为密文输入框，`multiline` 为多行。 |
| `showPick(items, { title, prompt, multiple?, matchOnDetail? })` | 选中项（`multiple` 时为数组）或 `null` | 可搜索的列表，最多 10 万项；项目可带 `group`（分组）、`picked`（预先选中）、`value`。 |
| `confirm(text, { title, confirmTitle, destructive? })` | `true` / `false` | `destructive` 时确认按钮显示为危险操作。 |

对话框都会注明“来自插件‘<插件名>’”。**不要用对话框索要其他服务的密码。** 面板页面也可以直接调用这些方法。

```js
toolbox.commands.register("prefixLines", async () => {
  const prefix = await toolbox.ui.showInput({ title: "加前缀", prompt: "每行开头加上：", value: "> " });
  if (prefix === null) return { message: "已取消" };
  const { text } = await toolbox.editor.getText();
  await toolbox.editor.replace(text.split("\n").map((line) => prefix + line).join("\n"));
});
```

### `toolbox.executeCommand(id, ...args)`

执行命令。插件命令（`<插件 id>/<命令 id>`）收到参数并把返回值交回；应用命令返回 `true`/`false`。应用命令和其他插件的命令需要在 `permissions.commands` 中声明（见[第 21 节](#21-权限网络剪贴板文档与命令)）。

### 文件：`toolbox.workspace` 与 `toolbox.files`

用户选择的文件和文件夹以**令牌**表示：插件只能访问用户选过（或拖到面板上）的文件，文件夹令牌只覆盖文件夹之内；令牌在应用运行期间有效。

| 方法 | 结果 | 说明 |
|---|---|---|
| `workspace.pickFile({ title, extensions, maxBytes, encoding, remember })` | `{ token, name, size, type, text? / base64? }` 或 `null` | `encoding`：`"text"`（缺省，UTF-8/UTF-16）、`"base64"`（二进制）、`"none"`（只要令牌，适合大文件）。`remember: true` 时令牌跨重启有效（用户可在插件中心撤销）。 |
| `workspace.pickFiles({ title, extensions, multiple })` | `FileHandle[]` | 多选，只返回令牌。 |
| `workspace.pickFolder({ title, remember })` | `{ token, name, isDirectory: true }` 或 `null` | `remember: true` 时跨重启保留（用户可在插件中心撤销）。 |
| `workspace.saveFile(content, { name, types })` | 保存后的 `FileHandle` 或 `null` | `content` 可以是字符串、`ArrayBuffer`/类型化数组、`{ base64 }`、`{ file: token }`（如下载好的响应）。 |
| `files.stat(token, path?)` / `files.list(token, { path, recursive, limit })` | `{ name, path, size, isDirectory, modified }` | `path` 为文件夹令牌内的相对路径。 |
| `files.readText(token, { path, maxBytes })` | 字符串 | 一次读取整个文件，上限 `limits.fileReadBytes`。 |
| `files.readBase64(token, { path, offset, length })` / `readBytes` | `{ base64, size, eof }` / `Uint8Array` | 分段读取，单段最多 16 MiB，文件大小不限。 |
| `files.writeText` / `writeBytes(token, data, { path, append })` | — | 写入用户选择的文件或文件夹中的文件。 |
| `files.watch(token, fn)` | 取消函数 | 文件夹内文件变化时调用 `fn({ paths })`（约 0.3 秒合并一次）。 |
| `files.dataFolder()` | `FileHandle` | 只属于本插件的文件夹，放缓存、数据库、下载的模型。令牌每次运行都相同，可以保存；更新时保留，卸载时删除。 |
| `files.mkdir(token, path)` / `files.move(token, from, to)` | — | 在文件夹令牌内新建文件夹、移动或改名。 |
| `files.copy(from, to, { fromPath, toPath })` | — | 复制，可跨令牌，例如把 `responseType: "file"` 的临时下载存进 `dataFolder`。 |
| `files.remove(token, { path })` | — | 删除。私有文件夹和临时下载中的文件直接删除，用户文件夹中的文件移到废纸篓。 |
| `files.release(token)` | — | 释放令牌；临时下载的文件同时删除，不必等到退出。 |

### `toolbox.has(name)`

判断某项能力是否可用，返回 `true` 或 `false`：

```js
if (toolbox.has("ui.showPick")) { /* … */ }
```

可检测的名称：

以运行时 `toolbox.has` 的结果为准。常用的有：`net`、`net.stream`、`net.socket`、`net.eventSource`、`fetch`、`files`、`files.watch`、`workspace.pickFolder`、`editor.applyEdits`、`editor.tabs`、`panels.open`、`panels.post`、`extensions`、`context`、`languageFeatures`、`languages.<kind>`、`events.textChanged`、`events.willSave`、`concurrency`、`abort`、`lifecycle`。面板页面另有 `invoke`、`post`、`panel`、`theme`、`drop`、`download`、`panel.args`。

---

## 11. 插件设置

在清单中声明设置项，应用会在插件中心 → 你的插件 → **设置** 标签中自动生成表单，插件用 `toolbox.settings.get(key)` 读取。

```json
"contributes": {
  "configuration": [
    { "key": "dateFormat", "title": "日期格式", "type": "enum",
      "options": ["YYYY-MM-DD", "YYYY/MM/DD"], "default": "YYYY-MM-DD" },
    { "key": "defaultPrefix", "title": "默认行前缀", "type": "string", "default": "> ",
      "description": "输入框里预先填好的内容" },
    { "key": "maxItems", "title": "最多条数", "type": "number", "default": 20 },
    { "key": "announceSave", "title": "保存时提示", "type": "boolean", "default": false }
  ]
}
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `key` | ✅ | 插件内唯一，`[A-Za-z0-9_.-]`。 |
| `title` | ✅ | 表单中的名称。 |
| `type` | ✅ | `string`（文本框）、`text`（多行文本）、`number`（数字框；有 `minimum`/`maximum` 时为滑块）、`boolean`（开关）、`enum`（下拉选择）、`secret`（安全输入框，保存在钥匙串）、`array`（字符串列表，每行一项）、`object`（JSON 对象）、`color`（取色器，`#RRGGBB`）。 |
| `minimum` / `maximum` / `step` | | `number` 的范围与步长。 |
| `pattern` / `minLength` / `maxLength` | | `string`/`text` 必须整体匹配的正则与长度；`array` 的项数。 |
| `properties` | | `object` 允许的字段及类型，如 `{ "host": "string", "port": "number" }`。 |
| `default` | | 缺省值，必须与 `type` 相符；省略时为空字符串、0、false 或第一个选项。 |
| `options` | enum 必需 | 可选值列表。 |
| `description` | | 表单中的说明文字。 |

```js
const format = toolbox.settings.get("dateFormat");   // 用户未修改时返回 default
```

- 可在 `main.js` 的所有函数（包括预览器、事件处理函数）和面板页面（`await toolbox.settings.get(key)`）中读取。读取未声明的 key 会抛出异常。
- 用户修改设置后，使用该插件预览器的标签会自动重新渲染。
- 设置在插件更新时保留，卸载时删除。表单中有“全部恢复默认”。
- 设置用于用户可调整的选项；插件自己记录的数据（历史、缓存）请用 `toolbox.storage`。

### 读写设置并同步

```js
// 面板页面：调用返回 Promise
await toolbox.settings.getAll();              // 不含 secret 类型的设置
await toolbox.settings.set("goal", 2000);     // 按 configuration 校验类型；省略值表示恢复默认
const stop = toolbox.settings.onChange((keys) => { /* 只给键名，需要时再读取 */ });

// main.js：先在 contributes.events 中声明 "settingsChanged"
toolbox.events.on("settingsChanged", ({ keys }) => {
  toolbox.statusBar.set("goal", toolbox.settings.get("label"));
});
```

设置保存后：打开的面板页面收到 `onChange`，插件预览重新渲染，当前文档重新校验，`settingsChanged` 事件通知 `main.js`（连续修改约 250 毫秒内合并为一次）。`settings.set` 只能在用户触发的入口（命令、文本动作、面板）中调用，不能在事件、校验器等后台入口中调用。

---

## 12. 事件

插件可以在文档打开、保存、切换时得到通知，例如“保存时检查”“打开时提示”。

```json
"contributes": { "events": ["documentSaved"] }
```

```js
toolbox.events.on("documentSaved", async (doc) => {
  // doc: { language, fileName, text, truncated, textWithheld, size, tab }
  // 没有声明 permissions.documents = "all" 时 text 为空、textWithheld 为 true（只有元数据）
  if (doc.textWithheld || doc.truncated) return;   // 文档超过 limits.documentBytes 时 truncated 为 true
  if (doc.text.includes("TODO")) await toolbox.ui.showMessage(`${doc.fileName} 还有 TODO`, "info");
});

// 保存时格式化：返回的编辑在写入文件前应用（2 秒内没有结果时照常保存）
toolbox.events.on("willSave", (doc) => doc.text.endsWith("\n") ? [] : [{ start: doc.size, length: 0, text: "\n" }]);
```

| 事件 | 何时 |
|---|---|
| `documentOpened` | 从磁盘打开文件完成后 |
| `documentSaved` | 保存成功后（包括另存为 UTF-8） |
| `documentClosed` | 关闭一个对应文件的标签前；此时还能拿到它的内容 |
| `activeDocumentChanged` | 切换到另一个标签后（快速连续切换时只通知最后停留的标签） |
| `languageChanged` | 当前文档的语言被用户或工具改变后 |
| `settingsChanged` | 本插件的设置改变后，回调参数为 `{ keys }`，只含键名，见第 11 节 |
| `textChanged` | 文本改变后（停止输入约 300 毫秒） |
| `selectionChanged` | 选区移动后（停留约 200 毫秒）；`doc.changes` 为选区列表 `{ start, length }` |
| `willSave` | 保存前；处理函数可以返回编辑列表 `[{ start, length, text }]`，在写入文件前应用 |

- **必须在 `contributes.events` 中声明**，应用只会为声明了该事件的插件加载并运行脚本；没有声明时 `events.on` 注册的函数不会被调用。
- 处理函数在后台运行，不阻塞编辑器；可以是 `async` 函数，事件在它完成后才结束，`await` 之后的代码照常执行。同一事件可以注册多个处理函数，其中一个抛出异常不影响其他，异常写入插件控制台（见第 23 节）。
- 事件处理函数中可以读取设置、使用存储、联网（需权限）、调用 `ui.showMessage`；修改编辑器和弹出对话框需要声明 `documents: "all"`。

---

## 13. 校验器

校验器检查文档，返回问题列表；编辑器在行号栏标出问题、在问题文字下画波浪线，检查器的“问题”列表与底部状态栏显示问题数，按 F8 / ⇧F8 在问题之间跳转。

### 声明

```json
"contributes": {
  "validators": [
    { "id": "check", "title": ".env 检查", "fileExtensions": ["env", "properties"], "runOn": "change" }
  ]
}
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `id`、`title` | ✅ | 标识与名称；名称会显示为问题的来源。 |
| `fileExtensions` / `languages` | 二选一 | 适用的文件（扩展名或语言任一匹配即可）。 |
| `runOn` | | `change`（缺省）：打开、切换到、保存文档时，以及停止输入约 0.7 秒后运行；`save`：只在保存后运行；`manual`：只在用户执行“运行校验器”时运行。 |

**主动推送问题**：校验器只在编辑器请求时运行。插件自己发现的问题（后台分析、远程检查、监听文件变化后）可以随时推送，任何入口都可以调用：

```js
await toolbox.languages.setDiagnostics("remote-lint", problems, { tab });   // 与校验器返回的问题格式相同；替换这个 key 之前的问题
await toolbox.languages.clearDiagnostics("remote-lint", { tab });
```

不写 `tab` 时为当前文档；其他标签页需要 `documents: "all"`。插件停用时它推送的问题一起清除。

用户也可以随时通过 菜单栏 工具 → 插件 → 运行校验器（或命令面板）手动运行全部适用的校验器，包括应用内置的 JSON、XML、YAML、SQL 校验器，结果会显示在编辑器底部。

### 注册

```js
toolbox.registerValidator("check", (input) => {
  // input: { text, language, fileName, tab }，text 为全文（文档超过 limits.documentBytes 时不运行）
  const problems = [];
  input.text.split("\n").forEach((line, index) => {
    if (line.trim() && !line.includes("=")) {
      problems.push({ line: index + 1, message: "缺少“=”", severity: "error" });
    }
  });
  return problems;      // 没有问题时返回 []
});
```

每个问题：

| 字段 | 必需 | 说明 |
|---|---|---|
| `line` | ✅ | 行号，从 1 开始。 |
| `message` | ✅ | 问题说明，显示在提示、问题列表中。 |
| `severity` | | `error`（缺省，红色）、`warning`（橙色）、`info`（蓝色）。 |
| `column` | | 起始列，从 1 开始（按 UTF-16 计，中文、普通字符都算 1，emoji 算 2）；省略时标出整行。 |
| `endLine`、`endColumn` | | 结束位置（`endColumn` 不包含该列）；省略时到行尾。 |
| `fixes` | | 快速修复，见下方[快速修复](#快速修复)。 |

- 缺少 `line` 或 `message` 的项会被忽略；最多显示 1000 个问题；超出文档的行号会被限制在文档范围内。
- 用户修改文本后，旧问题变暗显示，直到校验器给出新结果；校验期间文本又变了时，这次结果会被丢弃，不会覆盖新内容。
- 每个校验器的问题单独管理：插件被停用或卸载时，它的问题会自动清除。
- 校验器不能修改编辑器或弹出对话框，其他 API 的可用范围见第 5 节的表格。
- 校验器出错时只写日志（手动运行时会显示错误），不影响编辑。

### 快速修复

问题可以带 `fixes`，检查器的问题列表会显示修复按钮。一个修复的所有编辑作为一次撤销；编辑不能重叠。

```js
toolbox.registerValidator("whitespace", (input) => [{
  line: 2, column: 4, endColumn: 6, message: "行尾有多余空白", severity: "warning",
  fixes: [{ title: "删除行尾空白", edits: [{ line: 2, column: 4, endColumn: 6, text: "" }] }]
}]);
```

---

## 14. 格式化器

格式化器接入“按当前语言格式化”（⇧⌘F，菜单栏 工具），为应用不支持的格式提供格式化，或为特定扩展名提供专门的格式化。

```json
"contributes": {
  "formatters": [ { "id": "tidy", "title": ".env 整理", "fileExtensions": ["env", "properties"] } ]
}
```

```js
toolbox.registerFormatter("tidy", (input) => {
  // input: { text, hasSelection, language, fileName, indentWidth }
  // 有选区时 text 为选区，否则为全文；indentWidth 为用户设置的缩进宽度
  return input.text.split("\n").map((line) => line.replace(/\s*=\s*/, "=")).join("\n");
});
```

- 返回字符串或 `{ text, message }`；结果直接替换原文（可撤销），运行状态显示在编辑器底部。
- **何时使用插件格式化器**：自动选择的顺序是 按**扩展名**匹配的插件 → 内置格式化器（JSON、XML、YAML、Markdown、SQL 的结构化格式化，JavaScript/TypeScript/CSS/HTML 等的 Prettier）→ 按**语言**匹配的插件 → 通用格式化。所以只按语言匹配时，应用对该语言没有专门的格式化器才会用到插件。
- 用户可在 设置 → 插件 → 格式化与预览 中为某个语言或扩展名改选你的格式化器（见[第 15 节](#15-格式化预览与校验的选择)）。
- 多个插件都匹配时取第一个（按插件名排序）。

---

## 15. 格式化、预览与校验的选择

插件提供的格式化器、预览器和校验器与应用内置的功能并列，按同一套规则选用：

| 服务 | 自动选择顺序 | 用户选择 |
|---|---|---|
| 格式化 | 扩展名匹配的插件 → 内置 → 语言匹配的插件 → 通用格式化 | 设置 → 插件 → 格式化与预览，按语言或扩展名 |
| 预览 | 内置（Markdown、HTML）→ 扩展名匹配的插件 → 语言匹配的插件 | 同上 |
| 校验 | 全部运行：插件校验器按各自的 `runOn`；内置的 JSON、XML、YAML、SQL 校验器在“运行校验器”时运行 | — |

- 按扩展名的选择比按语言的选择更具体：用户给 `.yml` 选了某个格式化器，`.yml` 文件就用它，其余 YAML 文件仍按 YAML 的选择。
- 设置里只列出真正有多个可选项的语言和扩展名；扩展名一行与该扩展名打开时的语言的提供者一起比较。
- 被选中的插件被停用或卸载后，选择保留但不生效，恢复自动顺序；设置里显示为“不可用”。

---

## 16. 扩展名关联语言

让应用把某种扩展名的文件按已有语言打开（语法高亮、折叠、工具都按该语言）：

```json
"contributes": {
  "languageAssociations": { "jsonc": "json", "env": "ini", "properties": "ini", "mdx": "markdown" }
}
```

- 键为扩展名（不带点，不区分大小写）；值为[语言名称](#语言名称)。
- 以点开头、没有其他扩展名的文件（如 `.env`、`.babelrc`），点后面的名字视为扩展名：`"env"` 也匹配名为 `.env` 的文件。同样适用于预览器、格式化器、校验器和命令的 `fileExtensions`。
- 在打开文件时生效；已打开的标签不会改变。用户手动选择过语言的文件保持用户的选择。

---

## 17. 编辑器增强：状态栏、装饰、悬停、补全、检查器分区

### 状态栏

```json
"statusItems": [{ "id": "todos", "tooltip": "TODO 数量", "command": "highlightTodos", "alignment": "left" }]
```

```js
toolbox.statusBar.set("todos", { text: "TODO 3", command: "highlightTodos" });
toolbox.statusBar.clear("todos");
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | ✅ | `[A-Za-z0-9_.-]`，最长 64。 |
| `text` | | 初始文字；运行时用 `statusBar.set` 更新。 |
| `tooltip` | | 鼠标提示。 |
| `command` | | 点击时运行的命令 id；本插件的命令直接写 id。 |
| `alignment` | | `left` 或 `right`。 |
| `priority` | | 同侧排序用的整数。 |

`statusBar.set` 可在命令、文本动作、面板处理函数、面板页面和事件中调用。

### 装饰

```js
toolbox.editor.setDecorations("todos", [{ start: 10, length: 4, background: "#ffd60a66", underline: "single", tooltip: "待办" }]);
toolbox.editor.clearDecorations("todos");
```

| 字段 | 说明 |
|---|---|
| `start`、`length` | 范围，UTF-16 偏移。 |
| `background`、`underlineColor` | 颜色：`#RRGGBB`、`#RRGGBBAA` 或 `red`、`yellow`、`green`、`blue`。 |
| `underline` | `single`、`double`、`wavy`。 |
| `tooltip` | 鼠标提示。 |
| `gutter` | 行号栏图标（在 `start` 所在的行）：`{ symbol, tooltip?, color?, command?, args? }`。`symbol` 是 SF Symbol 名称，无效时调用会报错；`command` 点击时运行，规则同 `codeLens`，命令的 `context.tab` 是这个文档。 |

`key` 用来区分同一插件的不同组装饰。装饰不改变文本，**文本一改范围类装饰就会被清除**，需要时再设置（例如在事件或命令中）。`gutter` 图标按行记录，不随输入清除：在行内输入不影响它，增删行时下方的图标跟着移动，被删掉的行上的图标一起消失；用同一个 `key` 再次设置（或 `clearDecorations`）即可更新。大文件模式下不可用。

```js
// 断点：点击图标时命令收到行号
toolbox.editor.setDecorations("breakpoints", [
  { start: lineStart, length: 0, gutter: { symbol: "circle.fill", color: "red", tooltip: "断点", command: "toggleBreakpoint", args: [line] } },
]);
```

#### 行号栏图标 `gutter`

- **位置**：图标画在 `start` 所在行的行号左边，诊断圆点的右边。一个标签第一次出现图标时行号栏变宽约 20 点，之后一直保持这个宽度，插件重新设置图标时正文不会左右跳动。
- **符号**：`symbol` 是 SF Symbol 名称（可在 Apple 的“SF Symbols”应用中查），如 `circle.fill`（断点）、`plus.square.fill` / `minus.square.fill` / `square.fill`（Git 新增、删除、修改）、`bookmark.fill`、`exclamationmark.triangle.fill`。名称无效时 `setDecorations` 抛出错误。`color` 与其他装饰相同，不写时为次要文字色。
- **提示与点击**：鼠标停留显示 `tooltip`；有 `command` 时点击图标运行它，`args` 作为命令的参数，命令的 `context.tab` 是图标所在的文档。没有 `command` 的图标点击无效果，点击行号栏其他位置照常（折叠、选行）。
- **同一行多个图标**：同一插件同一 `key` 中先出现的生效；多个插件或多个 `key` 都给同一行设置时，按 `<插件id>/<key>` 的字母顺序取第一个。需要组合显示时，在一个 `key` 里自行决定这一行画哪个符号。
- **随编辑移动**：图标按行记录。在行内输入不影响它；回车、删除换行符等增删行的编辑，会让下方的图标跟着上下移动，被删掉的行上的图标一起消失。折叠代码后图标仍在原来的行上。整篇替换（格式化、`editor.replace`）后行号可能变化，用 `textChanged` 事件重新设置即可。
- **清除**：`clearDecorations(key)` 或用同一 `key` 设置空数组；插件停用或卸载、标签关闭时自动清除。
- 只给行号栏画图标时，`length` 写 0，不要加 `background` 等字段，这样它不会被文字修改清掉。

```js
// Git 标记：textChanged 事件里比较文档与已保存版本，给改动的行画色块
toolbox.events.on("textChanged", async (doc) => {
  const marks = diffLines(saved, doc.text).map(({ start, kind }) => ({
    start, length: 0,
    gutter: { symbol: "square.fill", color: kind === "added" ? "green" : kind === "removed" ? "red" : "blue", tooltip: kind === "added" ? "新增" : "修改" },
  }));
  await toolbox.editor.setDecorations("git", marks, { tab: doc.tab });
});
```

### 悬停与补全

```json
"hoverProviders": [{ "id": "color", "title": "颜色值", "languages": ["css"] }],
"completionProviders": [{ "id": "words", "title": "文档单词", "languages": ["markdown"], "triggerCharacters": ["@"] }]
```

```js
// input: { text, language, fileName, offset, line, column, word }（补全时 word 换成 prefix）
toolbox.registerHoverProvider("color", (input) => input.word.length === 6 ? "颜色值" : null);
toolbox.registerCompletionProvider("words", (input) => [{ label: "alpha", insertText: "alpha()", detail: "函数" }]);
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `id`、`title` | ✅ | 标识与名称。 |
| `fileExtensions` / `languages` | 二选一 | 适用的文件。 |
| `triggerCharacters` | | 补全的触发字符。 |

鼠标在文字上停留约 0.6 秒显示悬停提示，返回字符串、`{ contents }` 或 `null`（不显示）。补全通过 ⌥⎋ 或输入触发字符打开系统补全列表，返回字符串或补全项数组：`{ label, insertText?, detail?, kind?, documentation?, sortText?, filterText?, range?: { start, length }, snippet? }`（`range` 为要替换的范围；`snippet` 为 `true` 时 `${1:名称}` 等占位符展开为文字）。两者都是后台入口，联网需要 `documents: "all"`。编辑器最多等 5 秒，过时的请求会通过 `context.signal` 取消，插件进程不受影响。文档超过 `limits.documentBytes` 时，`text` 是光标附近的片段，`textOffset` 是它在文档中的起点，`offset` 仍是文档中的偏移。

### 语言功能 `languageFeatures`

在清单中声明，在 `main.js` 用 `toolbox.languages.register(kind, id, fn)` 实现：

```json
"languageFeatures": [
  { "id": "def", "title": "Zig 定义", "kind": "definition", "languages": ["zig"] },
  { "id": "outline", "title": "Zig 大纲", "kind": "symbols", "languages": ["zig"] },
  { "id": "fold", "title": "Zig 折叠", "kind": "folding", "fileExtensions": ["zig"] }
]
```

| kind | 何时调用 | 返回 |
|---|---|---|
| `definition` | 前往 → 转到定义 | 一个位置，或位置数组（让用户选），`null` 表示没有 |
| `symbols` | 前往 → 转到符号…（可搜索列表） | `[{ name, detail?, kind?, ...位置 }]`；位置可以在其他文档中，用来做工作区符号 |
| `references` | 前往 → 查找所有引用… | 位置数组，可带 `text`（显示的代码行）、`detail`；按文档分组显示，选中后跳转 |
| `semanticTokens` | 打开、切到前台、停止输入约 0.3 秒后（自动） | 装饰数组（与 `setDecorations` 相同，常用 `color`），画在语法高亮之上，最多 20 万项 |
| `codeActions` | 工具 → 代码操作… | `[{ title, edits?: TextEdit[], command?, args? }]`，与错误无关的操作（提取变量、排序导入…） |
| `rename` | 工具 → 重命名符号…（`input.args` 含 `newName`、`oldName`） | `TextEdit[]`，一次撤销 |
| `rangeFormat` | 工具 → 格式化选区 | 新文本，或 `TextEdit[]` |
| `signatureHelp` | 输入 `(` 或 `,` 时自动弹出（字符可用 `triggerCharacters` 改），也可用 工具 → 参数提示 | 字符串、`{ label, documentation?, parameters?, activeParameter? }`，或 LSP 的 `{ signatures, activeSignature?, activeParameter? }`；显示在光标上方，当前参数加粗 |
| `inlayHints` | 停止输入约 0.4 秒后（自动） | `[{ offset \| line+column, text, color? }]`，显示在文字后面 |
| `folding` | 停止输入约 0.6 秒后（自动） | `[{ startLine, endLine, placeholder? }]`（从 1 开始），与语言自带的折叠合并 |
| `inlineCompletion` | 停止输入约 0.3 秒后（自动） | 字符串、`{ text, range? }`，或它们的数组（取第一个可用的）。在光标处显示灰色文字，**Tab** 接受、Esc 取消；继续输入建议里的内容时建议保留，其他输入或移动光标时消失。多行建议会让下面的行让位。`range: { start, length }` 必须覆盖光标，光标前的部分必须是 `text` 的开头（已输入的内容不会重复插入），光标后的部分会被替换 |
| `codeLens` | 停止输入约 0.4 秒后（自动） | `[{ line \| offset, title, command?, args?, tooltip?, below? }]`（`line` 从 1 开始）。在该行上方（`below: true` 时下方）显示小字，点击运行 `command`（本插件的命令 id，或已在 `permissions.commands` 声明的 `<插件id>/<命令id>`，否则只显示文字）；新答案到来前旧的保留，文字不会随每次按键跳动 |
| `inspect` | 用户按住 ⌘ 指向文字、⌘ + 点击，或 工具 → 识别内容（⌃⌘I） | 结果或结果数组：`{ start, length, title, confidence?, value?, detail?, rows?, swatch?, actions? }`，`null` 表示认不出。见下方[识别内容](#识别内容-inspect) |

**位置**是 `{ offset | start | line+column, length?, tab?, file? }`：不带 `tab`、`file` 时在当前文档；`tab` 是 `editor.listTabs()` 的标签 id；`file` 是文件令牌（用户选择的文件或文件夹中的文件，或 `editor.getText()` 返回的 `file`），跳转时在编辑器中打开该文件。

输入与悬停相同（`text`、`offset`、`line`、`column`、`word`），另有 `input.args`（JSON）中的 `selection: { start, length }`；`signatureHelp` 的 `args` 还有 `trigger`（触发的字符，菜单打开时为空）、`callStart`（调用的 `(` 的位置）和 `activeParameter`（光标在第几个参数，从 0 开始）。

参数提示弹出后跟随光标：移到别的参数时加粗随之改变，离开括号、输入 `)` 或按 Esc 时关闭；它不抢键盘焦点，可以继续输入。`inlayHints`、`folding`、`semanticTokens`、`inlineCompletion`、`codeLens` 是后台入口，其余是用户触发的入口。`inlayHints`、`folding`、`semanticTokens`、`codeLens` 会询问所有提供者并合并结果，一个插件返回空不影响其他插件。

#### 内联补全 `inlineCompletion`（AI 补全）

停止输入约 0.3 秒后，编辑器问提供者“光标处接下来写什么”，把答案以灰色文字显示在光标后面：

- **Tab** 接受，作为一个撤销步骤插入；**Esc**、移动光标、点击别处或切走焦点时消失。
- 继续输入与建议开头相同的字符时，建议保留并缩短，不会重新请求；输入别的字符时消失，停顿后重新请求。
- 光标在行中间时，建议插在光标处，原来的后半行显示在建议之后（接受前不改文档）。
- 多行建议会让下面的行暂时下移；最多显示 24 行（其余以“…”表示，Tab 仍插入全部）。自动换行时光标不在段落最后一行的话，只显示第一行。
- 有选区、正在用输入法输入、多光标、编辑器没有焦点时不请求，也不显示。

返回值：字符串（从光标处插入），或 `{ text, range?: { start, length } }`，或它们的数组（取第一个可用的），`null` 表示没有。`range` 用文档中的偏移，必须包住光标：光标前的部分必须是 `text` 的开头（例如已经输入了 `con`，`range` 从 `c` 开始，`text` 为 `console.log()`），光标后的部分在接受时被替换（例如替换自动补上的右括号）。不满足这些条件的答案不显示。

```json
"permissions": { "network": ["api.example.com"], "documents": "all" },
"contributes": {
  "languageFeatures": [{ "id": "ai", "title": "AI 补全", "kind": "inlineCompletion", "languages": ["javascript", "typescript", "python"] }]
}
```

```js
toolbox.languages.register("inlineCompletion", "ai", async (input, context) => {
  const prefix = input.text.slice(0, input.offset - (input.textOffset ?? 0));   // 光标前的文字
  if (prefix.trim().length < 3) return null;
  const response = await fetch("https://api.example.com/complete", {
    method: "POST",
    headers: { "content-type": "application/json", authorization: "Bearer " + toolbox.secrets.get("token") },
    body: JSON.stringify({ prefix, suffix: input.text.slice(prefix.length), language: input.language }),
    signal: context.signal,            // 用户继续输入时上一次请求会被取消
  });
  const { completion } = await response.json();
  return completion || null;
});
```

- 每次停顿只请求一次；新的请求开始时，上一次的 `context.signal` 触发，请把它传给 `fetch`，节省用量。编辑器最多等 30 秒。
- 内联补全是后台入口：要联网（调用 AI 服务）就必须声明 `documents: "all"`，见[第 21 节](#21-权限网络剪贴板文档与命令)。
- 多个插件为同一语言提供时，按插件顺序问，用第一个给出答案的。
- 文档超过插件的 `limits.documentBytes` 时，`text` 只是光标附近的片段，`input.textOffset` 是片段在文档中的起点，`offset` 和 `range` 仍按整篇文档计算。
- 大文件模式下以及超过 400 万字符的文档不请求。

#### 代码透镜 `codeLens`

停止输入约 0.4 秒后（以及打开、切换到文档时）请求，在指定行的上方显示一行小字，常用于“运行测试 | 调试”“3 个引用”“最后修改：张三”。

返回 `[{ line | offset, title, command?, args?, tooltip?, below? }]`：

- `line` 从 1 开始；也可以用 `offset`（该行任意位置的偏移）。同一行可以有多项，从左到右排列，与该行的缩进对齐。文档以换行结尾时，最后那个空行也可以挂透镜（`line` 为总行数，或 `offset` 等于文本长度），适合把按钮放在最后一段内容的下方。
- `below: true` 把这一项显示在该行**下方**而不是上方，适合放在一段内容（例如嵌入的 JSON）之后的按钮。它不依赖下一行存在：内容在最后一行、文档不以换行结尾时同样显示；之后在行尾继续输入或回车，按钮仍留在这一行下方。不要用“挂到下一行上方”来模拟，那样在最后一行会无处可挂。
- 有 `command` 的项是可点击的（鼠标变成手形，点击运行命令，`args` 作为参数，`context.tab` 是这个文档）；`command` 写本插件的命令 id，或已在 `permissions.commands` 声明的 `<插件id>/<命令id>`，否则只显示文字。没有 `command` 的项显示为更淡的说明文字。
- 最多 2000 项（所有插件合计）。返回 `[]` 或 `null` 清除本插件的透镜；插件停用时自动清除。
- 多个插件为同一文档提供透镜时，每个插件都会被询问，结果合在一起显示；同一行按插件顺序排列。一个插件返回空不影响其他插件。启用、导入或更新插件后，当前文档会立即重新请求，不必等下一次编辑。
- 新答案到来之前旧的透镜保留，并随文本移动（上方插入行时跟着下移），打字时正文不会一跳一跳。

```js
toolbox.languages.register("codeLens", "tests", (input) => {
  const lenses = [];
  input.text.split("\n").forEach((line, index) => {
    const match = /^\s*(?:it|test)\(["'](.+?)["']/.exec(line);
    if (match) {
      lenses.push({ line: index + 1, title: "▶ 运行", command: "runTest", args: [match[1]], tooltip: "运行这个测试" });
      lenses.push({ line: index + 1, title: "调试", command: "debugTest", args: [match[1]] });
    }
  });
  return lenses;
});
toolbox.commands.register("runTest", async (context, name) => { /* context.tab 是测试所在的文档 */ });
```

代码透镜也是后台入口，联网需要 `documents: "all"`。大文件模式下以及超过 400 万字符的文档不请求。

#### 识别内容 `inspect`

用户按住 **⌘** 移动鼠标时，编辑器问提供者“指针下的文字是什么”。认得出就给范围加下划线，停留约 0.3 秒弹出卡片；**⌘ + 点击** 时，有“转到定义”的答案优先跳转，否则弹出并固定卡片；选中文字后按 **⌃⌘I**（工具 → 识别内容）识别选区。不按 ⌘ 时什么都不显示，所以这里适合放“解码、换算、解释”这类按需查看的功能，而不是常驻装饰。

```json
"languageFeatures": [{ "id": "inspect", "title": "内容识别", "kind": "inspect", "languages": ["*"] }]
```

`languages: ["*"]` 表示所有文档（任何语言功能都可以这样写）。

输入除了通用的 `text`、`offset`、`line`、`column`，还有：

| 字段 | 说明 |
|---|---|
| `trigger` | `pointer`（⌘ 指向）、`click`（⌘ + 点击）、`keyboard`（菜单命令） |
| `selection` | `{ start, length }` |
| `candidates` | 编辑器按指针位置算好的候选范围，由小到大：`{ kind, start, length, text }`。`kind` 为 `selection`（指针在选区内时只有它）、`part`（`key=value&a=b`、`a,b;c` 这类词中指针所在的一段；`=` 后面还是 `=` 或在末尾时算 Base64 填充，不切开）、`token`（连续非空白字符，已去掉两边的引号和标点；指针在 ASCII 字符上时不跨入中文）、`string`（引号内）、`bracket`（最内层配对括号，`(` 前的名字一并带上，如 `rgb(…)`）、`line`（整行，去掉首尾空白）、`block`（连续非空行，多于一行时） |

返回值的每一项：

| 字段 | 说明 |
|---|---|
| `start`、`length` | 文档中的范围，通常直接用某个候选的；必须包住指针（`keyboard` 除外） |
| `title` | 卡片标题，如“Unix 时间戳（秒）” |
| `confidence` | 0–1，缺省 0.75。**低于 0.5 不显示**。没把握就不要回答：普通文本按住 ⌘ 应该什么都不出现 |
| `value` | 主要结果（等宽字体，可选中），最长 2 万字符 |
| `rows` | `[{ label, value }]` 明细，最多 40 行 |
| `detail` | 一句补充说明 |
| `swatch` | 颜色（`#RRGGBB` 或 `#RRGGBBAA`），显示为色块 |
| `actions` | 按钮，最多 8 个：`{ kind: "copy", title, value }` 复制；`{ kind: "replace", title, value }` 把范围替换为 `value`（原文已变时拒绝，可撤销）；`{ kind: "command", title, command, args? }` 运行命令（规则同 `codeLens`） |

多个答案按置信度、再按范围大小排序，第一个显示在卡片上，其余列在“其他解释”中，点击可切换（下划线跟着变）。所有提供者的答案合在一起排序。编辑器每个范围只问一次，同一次按住 ⌘ 期间结果会被缓存；单次请求最多等 3 秒。大文件模式下不可用。

```js
toolbox.languages.register("inspect", "inspect", (input) => {
  const token = input.candidates.find((c) => c.kind === "token");
  if (!token || !/^\d{10}$/.test(token.text)) return null;
  const date = new Date(Number(token.text) * 1000);
  return {
    start: token.start, length: token.length, confidence: 0.7,
    title: "Unix 时间戳（秒）", value: date.toISOString(),
    actions: [{ kind: "replace", title: "替换为 ISO 8601", value: date.toISOString() }],
  };
});
```

测试识别功能时，打开一份含示例数据的文档，按住 ⌘ 将指针移到匹配文本上，再检查卡片内容及点击动作。

### 检查器分区

把面板页面嵌入编辑器右侧的检查器，规则与面板页面相同：

```json
"panels": [{ "id": "outline", "title": "TODO 列表", "entry": "panel/index.html" }],
"inspectorSections": [{ "id": "todos", "title": "TODO", "panel": "outline", "height": 160, "languages": ["markdown"] }]
```

`id`、`title`、`panel`（本插件的面板 id）必需；`height` 为高度，`languages` 限定显示的语言。分区由应用自动显示，读写文档需要 `documents: "all"`。

---

## 18. 界面集成：菜单、工作区工具、粘贴识别、设置页、自定义编辑器

以下贡献点都写在 `contributes` 中。菜单项和粘贴动作指向应用命令时，需要在 `permissions.commands` 中声明（第 21 节）。

### 菜单 `menus`

```json
"menus": [
  { "menu": "menubar/tools", "command": "insertDate", "group": 1, "order": 10 },
  { "menu": "editor/context", "command": "prefixLines", "when": { "selection": true } },
  { "menu": "tab/context", "command": "copyPath", "when": { "fileExtensions": ["md"] } },
  { "menu": "menubar/tools", "command": "publish", "enablement": "loggedIn && hasSelection && language == 'Markdown'" }
]
```

| 字段 | 说明 |
|---|---|
| `menu` ✅ | 位置：`menubar/file`、`menubar/split`、`menubar/find`、`menubar/go`、`menubar/selection`、`menubar/tools`、`toolbar`、`editor/context`、`tab/context`、`palette`，或某个子菜单的 id。 |
| `command`、`submenu`、`text` | 三选一：运行的命令、子菜单的 id、一行说明文字。 |
| `title` | 显示名称。 |
| `group`、`order` | 分组（组间显示分隔线）与组内顺序。 |
| `enablement` | 启用条件，不满足时显示为灰色。写法同 `when.context`（`!`、`&&`、`\|\|`、比较、括号）。可用的名字：`contentReady`、`hasDiagnostics`、`hasSelection`、`language`（与 `context.language` 相同）、`fileExtension`，其余是本插件用 `toolbox.context.set` 设置的键（不能覆盖前面这些）。例如 `"hasSelection && loggedIn && mode != 'readonly'"`。无法解析的条件在安装时报错。 |
| `when` | 显示条件，同命令的 `when`。 |

`tab/context` 的命令里，`context.tab`、`context.language`、`context.fileName`、`context.hasSelection` 都是**被右键点击的标签页**，`enablement` 与 `when` 也按它判断（它不一定是当前标签页）。用 `toolbox.editor.getText({ tab: context.tab })` 读写非当前标签页需要 `documents: "all"`。

```js
toolbox.commands.register("copyPath", async (context) => {
  const { file, fileName } = await toolbox.editor.getText({ tab: context.tab, length: 0 });   // 非当前标签需要 documents: "all"
  await toolbox.ui.showMessage(file ? `右键的是 ${fileName}` : "这个标签还没有保存");
});

// enablement 里的 loggedIn 来自插件自己设置的上下文键，改变后菜单立即更新
toolbox.commands.register("login", async () => {
  await signIn();
  await toolbox.context.set("loggedIn", true);
});
```

**`enablement` 与 `when` 的区别**：在 `menus` 的一项里，两者不满足时都让这一项显示为灰色。`when` 用 `languages`、`fileExtensions`、`selection` 这几个字段，外加一个只读插件上下文键的 `context` 表达式；`enablement` 是一个表达式，可以同时读编辑器状态（`hasSelection`、`language` 等）和插件的上下文键。另外，命令自身的 `when`（`contributes.commands[].when`，第 9 节）决定命令是否出现在编辑器右键 → 插件、命令面板等列表里，与这里的 `menus` 是两回事。菜单栏和工具栏的启用状态跟随当前标签的选区、语言、扩展名和插件上下文键实时更新。

表达式的写法：

| 写法 | 含义 |
|---|---|
| `loggedIn` | 值为真（非空字符串、非零数字、`true`、对象或数组） |
| `!readonly` | 取反 |
| `a && b`、`a \|\| b`、`(a \|\| b) && c` | 与、或、括号；`&&` 先于 `\|\|` |
| `mode == 'json'`、`mode != json` | 相等、不等；右边不带引号的单词也当字符串 |
| `count > 3`、`version >= 2`、`name < 'm'` | 数字或字符串比较 |
| `language == 'JSON'` | `language` 的值与 `context.language` 相同 |

### 工作区工具 `workspaceTools`

把面板作为工作区的一个工具。不声明时，面板也会自动出现在工作区侧栏的“插件”分类；需要自定义标题、位置或搜索词时才声明。

```json
"workspaceTools": [{ "id": "lookup", "title": "仓库查询", "subtitle": "GitHub", "panel": "lookup", "icon": "magnifyingglass", "aliases": "github repo" }]
```

| 字段 | 说明 |
|---|---|
| `id`、`title`、`panel` ✅ | 标识、名称、本插件的面板 id。 |
| `subtitle`、`icon`、`aliases` | 副标题、SF Symbols 图标、搜索词。 |
| `category`、`order` | 侧栏分类（缺省 `plugins`）与顺序。 |
| `acceptsInput` | 可以接收编辑器发送的文本。页面用 `window.toolboxInitialText` 取初始文本。 |
| `usesNetwork` | 标记此工具会联网。 |
| `window` | 独立窗口的最小尺寸 `{ minWidth, minHeight }`。 |

### 粘贴识别 `pasteDetectors`

粘贴的文本匹配 `pattern` 时，向用户提供动作。文本超过 64 KB 时不匹配。

```json
"pasteDetectors": [{ "id": "jwt", "label": "JWT", "pattern": "^eyJ[\\w-]+\\.[\\w-]+\\.[\\w-]+$", "actions": [{ "command": "decodeJWT" }] }]
```

| 字段 | 说明 |
|---|---|
| `id`、`label` ✅ | 标识、显示名称。 |
| `pattern` | 匹配粘贴文本的正则。 |
| `order` | 顺序。 |
| `actions` | 提供的动作，每项为 `{ command }`（运行命令）、`{ tool }`（打开工作区工具）或 `{ transform, action }`（运行文本工具分类中的动作）。 |

### 设置页 `settingsPages`

在设置窗口左侧增加一页，显示本插件的面板：

```json
"settingsPages": [{ "id": "general", "title": "我的插件", "panel": "settingsPanel", "icon": "gearshape", "detail": "账户与同步" }]
```

`id`、`title`、`panel` 必需；`icon`、`detail`、`order` 可选。设置页由应用自动显示，读写文档需要 `documents: "all"`。

### 自定义编辑器 `customEditors`

用面板显示并编辑匹配的文档，选择规则与预览器相同：

```json
"customEditors": [{ "id": "kanban", "title": "看板", "panel": "board", "fileExtensions": ["kanban"] }]
```

`id`、`title`、`panel` 必需，`languages`、`fileExtensions` 指定匹配的文档。

可选的 `contentCondition: "jsonObjectArray"` 要求 JSON 文档内至少有一个非空对象数组（可以在根节点或嵌套层级）。砚会在文本变化后重新检查。条件不满足时，该面板不参与预览选择；若没有其他匹配的预览器，文档只显示源码。

- 页面中的 `toolbox.editor.*` 固定作用于页面所属的标签，`getText()` 取整篇。
- 文档变化时 `toolbox.editor.onChange(fn)` 回调，收到后重新读取。
- 该标签不在前台时可以读取和写回（写回会切到该标签），不能使用光标和选区。
- 编辑器自动显示它时属于后台入口：联网插件需要 `documents: "all"` 才能联网和保存数据，页面也不能弹对话框。**用户在页面中点击或按键后 5 秒内**发起的调用（`invoke`、对话框、存储等）算作用户触发，与对文档运行命令相同：可以联网、保存数据、弹对话框。只有真实的鼠标和键盘操作算数，脚本合成的事件不算。

---

## 19. 插件中心：详情页与自定义页面

每个已安装的插件在插件中心（设置 → 插件 中内嵌；按 ⇧⌘X 或选应用菜单的“插件中心…”在独立窗口打开）都有独立的详情页：概览、功能、设置、自定义页面、更新记录、权限、控制台。

### 详情页信息

以下字段写在 `plugin.json` 顶层，均可省略：

| 字段 | 说明 |
| --- | --- |
| `icon` | SF Symbol 名称，或包内的 png、jpg、heic 图片 |
| `readme` | 包内 Markdown，显示在“概览”；省略时使用 `README.md`；都没有时由清单生成 |
| `changelog` | 包内 Markdown，显示在“更新记录”；省略时使用 `CHANGELOG.md` |
| `repository` | http(s) 链接 |
| `license` | 许可证名称 |
| `categories` | 分类名称数组，可用于搜索 |

说明文档不执行脚本，只显示包内图片；外部链接在浏览器中打开。

### 自定义页面 `pages`

页面使用本插件 `contributes.panels` 中的面板，能力与面板相同：

```json
"pages": [
  { "id": "settings", "title": "设置", "panel": "settingsPanel", "role": "settings" },
  { "id": "stats", "title": "统计", "icon": "chart.bar", "panel": "statsPanel" }
]
```

`role: "settings"` 的页面（最多一个）显示在“设置”标签，用户可以切换到由 `configuration` 生成的标准表单；其余页面各占一个标签。

---

## 20. 插件存储与秘密

`toolbox.storage` 是每个插件独立的键值存储，在文本动作、预览器、面板处理函数和面板页面中都可以使用：

```js
const usesHeader = () => toolbox.storage.get("headerRow", true);   // 第二个参数是缺省值

toolbox.registerTextAction("toggleHeader", (input) => {
  const next = !usesHeader();
  toolbox.storage.set("headerRow", next);
  return { text: input.text, message: next ? "首行作为表头" : "首行作为数据" };
});
```

- 值可以是任意**可 JSON 序列化**的数据（数字、字符串、布尔、数组、对象、null）；`set(key, undefined)` 等同于删除。
- 键必须是非空字符串。
- 写入立即保存；面板页面通过 `toolbox.storage.onChange` 得到改变的键。预览不会因写存储重新渲染，需要时调用 `toolbox.previews.refresh()`。
- 每个插件总计上限缺省 **16 MiB**，可在清单 `limits.storageBytes` 中申请到 1 GiB（见[资源上限](#资源上限)）；超出时 `set` 抛出异常、原数据不变。数据只在读取时从磁盘载入，不常驻应用内存。
- `keys(prefix)` 按前缀列出键；`getMany`/`setMany` 一次读写多个键（`setMany` 全部成功或全部不写）；`usage()` 返回 `{ bytes, keys, limit }`。
- 每个键单独保存，写入的开销只与这个键的值有关。数据多时，把它们拆到多个键中，不要反复改写一个大对象。
- **更新插件时保留**数据；**卸载插件时删除**数据。
- 不同插件之间互相看不到对方的数据。
- **不要存放密码、令牌等敏感信息**：数据以普通 JSON 文件保存在应用数据目录。

### 秘密：`toolbox.secrets`

令牌、密码等敏感信息请保存在钥匙串中：

```js
toolbox.secrets.set("token", "…");
toolbox.secrets.get("token");       // 字符串，不存在时为 null
toolbox.secrets.delete("token");
```

只能在 `main.js` 中使用，面板页面需要时通过 `toolbox.invoke` 调用。卸载插件时删除。需要用户填写时，也可以声明 `secret` 类型的设置项（第 11 节）。

---

## 21. 权限：网络、剪贴板、文档与命令

### 网络：`fetch` 与 `toolbox.net`

在 `plugin.json` 中声明要访问的主机（写法见[第 4 节](#permissions)）：

```json
"permissions": { "network": ["api.github.com", "*.example.com", "localhost:8080", "192.168.0.0/16"] }
```

需要访问用户指定的任意地址（例如通用 API 调试）时，可以申请 `["*"]`，见下方[访问所有网站](#访问所有网站)。

```js
// 常用写法：与浏览器相同
const response = await fetch("https://api.github.com/repos/apple/swift", {
  headers: { Accept: "application/vnd.github+json" }, signal: context.signal,
});
const repo = await response.json();
// 标准 Response：二进制用 arrayBuffer()/blob()，大响应用 response.body 边收边读
const image = new Uint8Array(await (await fetch(avatarURL)).arrayBuffer());
const form = new FormData(); form.append("file", new Blob([bytes], { type: "image/png" }), "a.png");
await fetch(uploadURL, { method: "POST", body: form });               // multipart 上传

// 完整能力
const r = await toolbox.net.request({
  url, method: "POST",
  headers: [["X-A", "1"], ["X-A", "2"]],          // 数组形式可以重复同名请求头；也可以是对象
  body: { multipart: [{ name: "file", file: token }, { name: "note", value: "…" }] },
        // 也可以是字符串、ArrayBuffer、{ base64 }、{ file: token }、{ form: [[k, v]] }、URLSearchParams、对象（按 JSON 发送）
  redirect: "manual",                             // follow（缺省）| manual（拿到 3xx 本身）| error
  responseType: "base64",                         // text（缺省）| base64（二进制）| stream（边收边读）| file（存到临时文件）
  timeout: 120,                                   // 连接空闲多少秒算超时，缺省 60，0 为不限
  totalTimeout: 0,                                // 总时长上限，缺省不限
  maxBytes: 8 * 1024 * 1024,                      // 超过时截断（truncated 为 true），而不是失败
  cookies: "plugin",                              // 使用插件自己的 Cookie（缺省 none）
  proxy: "http://user:pass@127.0.0.1:8888",       // 代理也必须在 network 名单中；可带用户名密码（http、socks5）
  tls: { allowSelfSigned: true },                 // 本机和局域网直接生效，其他主机由用户逐个同意；clientIdentity: "钥匙串中证书的名称"（用户逐个同意）
  signal: context.signal,
  onProgress: ({ received, total }) => {},
});
r.status; r.statusText; r.ok; r.url; r.redirected; r.httpVersion;   // "h2"、"http/1.1"
r.headers.get("content-type"); r.headers.getSetCookie();            // 同名响应头不会合并
r.redirects;                                     // 每一跳的状态、地址、响应头
r.timing;                                        // { dns, connect, tls, firstByte, download, total }（毫秒）
r.size; r.truncated; r.file;                     // responseType "file" 时为文件令牌，可交给 workspace.saveFile
await r.text(); await r.json(); await r.bytes(); await r.base64(); await r.arrayBuffer();
for await (const chunk of r.body) { /* responseType "stream"：Uint8Array */ }

// WebSocket 与 Server-Sent Events：连接保持期间插件进程不会因空闲结束
const ws = new WebSocket("wss://echo.example.com", ["chat"]);         // 浏览器写法；EventSource 同理
ws.onmessage = (event) => console.log(event.data);
const socket = toolbox.net.socket("wss://echo.example.com", { protocols: ["chat"], cookies: "plugin", tls: { allowSelfSigned: true } });
socket.on("open", () => socket.send("hi"));
socket.on("message", ({ data }) => { /* 文本，或二进制时为 Uint8Array */ });
socket.on("close", ({ code, reason }) => {});
const events = toolbox.net.eventSource("https://api.example.com/v1/chat", {   // 可以用 POST（大模型流式接口）
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ stream: true }),
});
events.on("message", ({ data, event, id }) => {});
```

规则：

| 项目 | 规则 |
|---|---|
| 协议 | `http`、`https`；WebSocket 为 `ws`、`wss`。 |
| 主机 | 必须在 `permissions.network` 中（按主机和端口检查），或声明了 `["*"]`；否则抛出 `NotAllowedError`，请求不会发出。 |
| 用户开关 | 用户关闭网络访问后，任何请求都抛出异常，已打开的连接也会关闭。 |
| 重定向 | `follow` 时每一跳的目标都必须在名单中；`manual` 时 3xx 交给插件，`Location` 只是数据，再次请求时重新检查。 |
| 状态码 | 4xx/5xx **不会**抛出异常，请检查 `status` / `ok`。网络错误、超时（`TimeoutError`）、取消（`AbortError`）会抛出。 |
| 等待 | 没有固定上限：慢接口、大文件下载、长轮询都可以，只受 `timeout`（连接空闲）与 `totalTimeout` 控制；等待期间插件的其他调用照常进行。 |
| 响应大小 | `maxBytes` 可截断响应；`text` 和 `base64` 同时受 `limits.responseBytes` 约束。大数据使用 `stream` 或 `file`，临时下载计入 `limits.privateDiskBytes`，用完可调用 `files.release`。 |
| Cookie | 缺省不保存、不发送；`cookies: "plugin"`（`fetch` 中为 `credentials: "include"`）使用插件自己的 Cookie 存储（与系统、其他插件隔离，卸载时删除；`clearCookies()` 清空）。 |
| 连接复用 | 同一插件、相同代理和 TLS 设置的请求共用连接（keep-alive、HTTP/2），批量请求不必每次握手。 |
| WebSocket、SSE | 与请求相同：主机名单、`cookies`、`proxy`、`tls`；SSE 的每一跳重定向也要在名单中。缺省不因安静而断开，`timeout` 可设置空闲秒数。SSE 单行或单个事件不能超过 `limits.transferBytes`。 |
| 原始 TCP | `toolbox.net.tcp(host, port, { tls })`：`permissions.network` 中要有这个主机（写端口时按端口）。事件与 WebSocket 相同（`open`、`message`、`close`、`error`），`message` 的 `data` 是 `Uint8Array`。 |
| 流式读取 | 读取跟不上时应用会暂停接收，内存中最多积压约 16 MiB；读完后继续。 |
| 顺序 | 同一进程中不等待结果连续发出的 `socket.send`、`panels.post`、`files.write`、`statusBar.set`、`setDecorations` 按调用顺序执行；页面的 `toolbox.post` 按发送顺序到达。 |
| User-Agent | 缺省为 `Yan-Plugin/<插件 id>`，可以自行覆盖。 |

面板页面和预览页面自己不能联网（`fetch` 被拦截），但可以显示 `network` 名单中主机的图片和音视频。

### 剪贴板：`toolbox.clipboard`

```json
"permissions": { "clipboard": true }
```

```js
const text = toolbox.clipboard.readText();     // main.js：同步
toolbox.clipboard.writeText("内容");
await toolbox.clipboard.write([{ type: "text/html", data: "<b>粗体</b>" }, { type: "text/plain", data: "粗体" }]);
const items = await toolbox.clipboard.read({ types: ["image/png", "files"] });   // 图片为 base64，文件为令牌
```

`"clipboard": "write"` 只允许写入；读取需要 `true`。支持 `text/plain`、`text/html`、`text/rtf`、`image/png`、`image/tiff` 和文件。没有声明权限时调用会抛出异常。

### 用户看到什么

安装确认框会列出“⚠️ 此插件申请以下权限”，例如“访问网络：api.github.com”“读取和写入剪贴板”，并提醒联网插件可以把文本发送到这些主机。插件中心里每个插件的“权限”标签也会显示它的权限。**只申请真正需要的主机**，范围越小越容易获得用户信任。

### 访问所有网站

`"network": ["*"]` 表示不受域名限制。规则如下：

- `"*"` 必须是数组里唯一的一项，不能和其他主机混写；这与只匹配子域的 `*.example.com` 不同。
- 响应大小、时限等限制不变。
- 可以访问任意 http 或 https 地址，包括 IP、本机和局域网地址。
- 后台悬停、补全和自动语言功能可单独申请 [后台语言服务联网](#后台语言服务联网)。校验器和事件等其他后台入口的联网规则见 [文档权限](#文档permissionsdocuments)。

只有目标地址事先确实无法确定时才申请 `*`；地址固定的插件请列出具体主机，范围越小越容易获得用户信任。

用户必须明确同意，否则插件无法使用这项权限：

| 场景 | 用户看到什么 | 未同意时 |
|---|---|---|
| 首次安装 | 严重警告，按钮为“允许访问所有网站并安装” | 不安装 |
| 更新时从固定主机改为 `*` | 严重警告，按钮为“允许访问所有网站并更新”，并列出新增权限 | 不更新，继续使用旧版本 |
| 链接开发文件夹，或把已链接插件的清单改成 `*` | 严重警告，询问“允许访问所有网站？” | 插件可以运行，但所有请求被拦截；可在“权限”页点“查看并允许…”补上同意 |

开发文件夹的同意会一直保留，从清单移除 `*` 或取消链接后失效，再次申请时重新询问。

### 网络开关

插件中心里每个插件的“权限”标签都有“允许访问网络”开关，默认开启，用户可以随时关闭或重新开启，重启应用后保留。未申请网络权限的插件，开关为灰色不可操作。

关闭后请求抛出异常、已打开的连接被关闭。开关不会改变插件申请的权限。插件应当捕获异常并给出提示，不要假设网络一定可用：

```js
try {
  const response = await fetch(url);
  return await response.text();
} catch (error) {
  // 网络错误、超时、用户关闭网络访问都会走到这里
  toolbox.ui.showMessage(`请求失败：${error.message}`, "error");
  return input.text;
}
```

### 文档：`permissions.documents`

```json
"permissions": { "documents": "all" }
```

取值为 `"active"`（缺省）或 `"all"`。安装确认框会明确提示 `all`。声明 `all` 后：

- 事件收到文档内容（否则 `text` 为空，`textWithheld` 为 `true`）；
- 预览器、校验器、事件、悬停、补全、自定义编辑器中可以联网（不声明时，这些后台入口所在的进程不能联网，用户触发的进程不受影响）；
- 检查器分区和设置页可以读写文档；
- 可以调用 `toolbox.editor.listTabs()`；
- 事件处理函数、定时器等自动运行的代码可以修改编辑器、打开面板、弹对话框、执行命令（第 5 节）。

没有声明 `all` 的联网插件，在后台入口（预览器、校验器、事件、悬停、补全、语言功能中的自动项、自定义编辑器）中不能调用 `storage.set`、`secrets.set`、`settings.set`、`clipboard.write*`、`files.write`、`context.set`；它的后台入口也总在单独的进程中运行（不能用 `singleProcess`）。这样可以防止插件把自动读到的内容保存或藏在全局变量里，之后再发送出去。

### 后台语言服务联网

```json
"permissions": {
  "network": ["api.example.com"],
  "backgroundLanguageNetwork": true
}
```

这项授权允许悬停、补全和自动语言功能在 `toolbox.lane === "remoteLanguage"` 的进程中联网。输入是当前调用的文档快照或光标附近的窗口，使用 `limits.documentBytes` 控制输入大小。网络仍执行主机名单和重定向检查。跨标签页读取、编辑写入、文件持久化及后台交互沿用各自的限制。插件中心可以单独关闭这项授权并断开正在进行的后台语言连接。开发目录需要在插件中心手动开启。已有 `documents: "all"` 清单沿用原有授权。

### 应用命令：`permissions.commands`

```json
"permissions": { "commands": ["file.save", "tools.*"] }
```

允许 `toolbox.executeCommand` 执行列出的应用命令，可用通配。执行本插件自己的命令不需要声明。菜单、快捷键、文本工具、粘贴动作和状态栏项指向其他命令时适用同一规则；未声明的条目不生效，并在插件详情页列出原因。

---

## 22. 运行环境与限制

### 语言与环境

- 引擎为 macOS 自带的 JavaScriptCore，支持现代 JavaScript（`let/const`、箭头函数、`class`、`async/await`、`for await`、`Map/Set`、正则命名分组等）。
- **可以拆成多个文件**：`main.js` 中出现 `import`/`export` 时按 ES 模块加载，否则按普通脚本运行（顶层函数是全局的，与以前相同）。
  - ES 模块：`import x from "./a.js"`、`import { a as b }`、`import * as ns`、`import "./side.js"`、`import data from "./data.json" with { type: "json" }`、`export` 的各种写法、`export * from`、动态 `import()`、`import.meta.url`、顶层 `await`、循环引用。
  - CommonJS：ES 模块可以 `import` CommonJS 文件；CommonJS 文件里有 `require`、`module.exports`、`__dirname`。`.mjs` 总是 ES 模块，`.cjs` 总是 CommonJS，`.js` 看有没有 `import`/`export`。`require()` 不能加载 ES 模块（与 Node 相同），请改用 `import`。
  - 路径：`./`、`../`、以 `/` 开头（插件包根目录），可以省略 `.js`、`.mjs`、`.cjs`、`.json` 和 `/index.js`。包名到 `node_modules` 中找，按 `package.json` 的 `exports`（条件依次为 `toolbox`、`browser`、`import` 或 `require`、`module`、`default`）、`module`、`main`。只能加载插件包里的文件；Node 的内置模块（`node:fs` 等）不存在。
  - 与浏览器的差别：导入的绑定在模块开始运行时取值，导出方之后重新赋值不会反映到 `import { x }`（用 `import * as ns` 后读 `ns.x` 可以看到最新值）；循环引用中尚未初始化的绑定读作 `undefined`。
  - 也可以继续用打包工具合并成一个文件，例如 `npx esbuild src/index.js --bundle --format=iife --target=safari15 --outfile=main.js`。
- **插件包里的其他文件**：`toolbox.bundle.readText(path)`、`toolbox.bundle.readBytes(path)`（同步，只读，路径相对于插件包根目录）。
- **WebAssembly** 可用：`WebAssembly.instantiate(toolbox.bundle.readBytes("lib/parser.wasm"), imports)`，以及 `compile`、`Module`、`Instance`、`Memory`、`instantiateStreaming`（接受 `fetch` 的响应）。JavaScript 和 WebAssembly 都启用即时编译，计算密集的代码接近浏览器的速度；内存计入插件的 `limits.memoryBytes`。
- 有 `fetch`、`Response`、`Blob`、`FormData`、`ReadableStream`、`WebSocket`、`EventSource`、`TextEncoder`、`URL`、`crypto`、`AbortController`、`structuredClone`、`performance` 等 Web 标准对象，以及 Node 的 `Buffer` 和简化的 `process`，见[第 5 节](#mainjs-中的-web-标准全局对象)。没有 DOM、`XMLHttpRequest`、Node 内置模块。
- `setTimeout`/`setInterval` 在调用之间继续运行：可以做心跳、轮询、去抖。

### 进程与并发

- 每个插件在**独立的进程**中运行。缺省有两个进程：用户触发的代码（命令、文本动作、面板处理函数、格式化器、面板消息、语言功能中的用户操作）一个，自动运行的代码（预览器、校验器、事件、悬停、补全、内联提示、折叠）一个，这样一个长时间计算的命令不会拖慢预览和补全。两个进程的全局变量不共享；需要共享时用 `toolbox.storage`，或在清单中声明 `"singleProcess": true` 让所有代码共用一个进程。`toolbox.lane` 告诉代码自己在哪个进程（`'interactive'` 或 `'background'`）：每个进程都会载入 main.js。开启单独授权的后台语言功能使用第三个进程 `'remoteLanguage'`。长连接、轮询这类常驻工作应在 `'interactive'` 中启动。导出函数（供其他插件调用）在用户触发的进程中运行。
- **同一进程中的调用可以同时进行**：JavaScript 仍是单线程，但一个调用在等网络、对话框或定时器时，其他调用照常执行。校验器、悬停、补全有更新的请求时，旧请求的 `context.signal` 会触发。
- **调用之间可以互相等待**：命令可以返回一个 Promise，等面板发来的消息、另一个命令或事件来完成它（例如“打开面板，等用户在面板里提交”）。用户触发的调用会一直等到完成或用户停止；自动运行的调用（预览器、校验器、悬停、补全、事件）在没有任何进行中的调用、定时器和连接、因而不可能再完成时结束，返回“插件没有返回结果”。
- 进程在空闲 10 分钟后结束（面板打开、有连接或声明了 `permissions.background` 时不会）；插件更新、停用、卸载时也会结束。结束前会调用 `toolbox.lifecycle.onDeactivate` 注册的函数（最多 2 秒），可以在这里保存状态、关闭连接。

### 长时间运行

应用不会因为“运行太久”结束插件，只区分两种情况：

| 情况 | 应用怎么做 |
|---|---|
| 在**等待**（网络、对话框、定时器、长连接） | 没有时间上限，不占 CPU。命令运行时底部显示已运行的时间和停止按钮。 |
| JavaScript **连续计算**不返回（如死循环、灾难性回溯） | 超过 15 秒时，所有窗口提示“插件 X 已连续计算 N 秒”，用户可以“停止插件”或“继续等待”。用户触发的代码不会被自动结束；**自动运行**的代码超过 `limits.busySeconds`（缺省 120 秒）时被结束，并提示原因。 |
| 调用方不再需要结果（悬停已移开、面板关闭、用户点停止） | 只触发该调用的 `context.signal`，进程和其他调用不受影响。 |

计算量大的工作请分段进行（例如每处理一批数据 `await new Promise((r) => setTimeout(r, 0))`），这样插件的其他调用和取消都能及时响应。

### 限制一览

| 项目 | 缺省 | 可申请到 |
|---|---|---|
| 等待网络、对话框、定时器 | 不限 | — |
| 用户触发的代码连续计算 | 不自动停止（15 秒后提示用户） | — |
| 自动运行的代码连续计算（`busySeconds`） | 120 秒 | 3600 秒 |
| 进程内存（`memoryBytes`） | 2 GiB | 16 GiB |
| 一次传递的数据（`transferBytes`） | 64 MiB | 512 MiB |
| 内存中的网络响应（`responseBytes`） | 64 MiB | 1 GiB |
| 私有文件和临时下载（`privateDiskBytes`） | 4 GiB | 64 GiB |
| 同时进行的网络连接（`networkConnections`） | 64 | 512 |
| 一次整体读取的文件（`fileReadBytes`；分段读取不限） | 64 MiB | 1 GiB |
| 交给语言功能和事件的整篇文档（`documentBytes`） | 8 MiB | 128 MiB |
| 插件存储（`storageBytes`） | 16 MiB | 1 GiB |
| 网络主机名单 | 100 项 | — |
| 插件包 | 256 MiB、10000 个文件、不含符号链接 | — |
| 第三方正则（语法、`shebang`、`contentRules`、`pasteDetectors`） | 不能嵌套重复（如 `(a+)+`）；单次匹配超时的模式停用并显示诊断 | — |
| 内联补全等待 | 30 秒；只显示最近一次停顿的答案，多行最多显示 24 行 | — |
| 代码透镜 | 每个文档 2000 项，等待 10 秒 | — |
| 内联提示 / 语义高亮 | 2000 项 / 20 万项 | — |
| 装饰（`setDecorations`） | 每次 5000 项 | — |

编写自动运行的语言功能时请注意：

- 内联提示、折叠、语义高亮、内联补全、代码透镜都在用户停止输入后才请求；用户继续输入时，上一次请求的 `context.signal` 会触发，请及时放弃。
- 大文件模式下，装饰、行号栏图标、内联补全、代码透镜都不可用；超过 400 万字符的文档也不请求内联补全和代码透镜。

---

## 23. 调试

1. **看错误信息**：脚本语法错误会在第一次运行时提示“加载插件脚本失败：…”；运行时异常显示在编辑器错误区、预览错误页，或面板中被拒绝的 Promise。
2. **打日志**：`toolbox.log(...)` / `console.log(...)`（`main.js` 中）显示在插件中心 → 你的插件 → **控制台** 标签，运行错误带 `main.js:行:列` 和堆栈；同时写入系统日志，可在终端实时查看：
   ```bash
   log stream --level info --predicate 'category == "Plugins"'
   ```
   每条日志带有插件 id 前缀，例如 `[com.yourname.reverse-lines] 处理了 12 行`。也可以打开“控制台”应用，搜索 `Plugins`。面板页面的 `console.*`、未捕获的错误和被拒绝的 Promise 也显示在同一个控制台。
3. **迭代**：用插件中心的 **＋ → 链接开发文件夹…** 载入源文件夹，保存文件后自动重新载入；也可以重新“导入插件…”选择同一文件夹，无需卸载。已打开的面板会自动关闭，重新打开即为新版本。
4. **断点调试**：在面板页面右键 → 检查元素，打开 Web Inspector。`main.js` 在 Safari 的“开发”菜单 → 这台 Mac 下列出（名称为插件名，两个进程各一项，需要先在 Safari 设置中开启“开发”菜单），可以下断点、看变量、在控制台执行。

---

## 24. 打包、分发与更新

### 打包

插件包就是把插件文件夹的内容压缩成 zip，再把扩展名改为 `.toolboxplugin`：

```bash
cd my-plugin
zip -r ../my-plugin.toolboxplugin . -x '.*'
```

或者在 Finder 里压缩文件夹，再把 `.zip` 改名为 `.toolboxplugin`。

### 分发

- 应用**不提供**插件市场或下载功能。请把 `.toolboxplugin` 文件放在你的网站、Git 仓库的 Releases 等位置，由用户自行下载。
- 用户安装方式：双击 `.toolboxplugin`；把 `.toolboxplugin`、含插件的 `.zip` 或含有效 `plugin.json` 的文件夹拖到应用窗口；或在插件中心的 **＋ → 导入插件…** 选择它们。
- 安装前会显示确认框：名称、版本、作者、来源文件、提供的动作、预览和面板，以及申请的权限。

### 更新

- 发布新版时**保持 `id` 不变**并增大 `version`；用户导入后确认框显示“版本：旧 → 新”，新增的权限会单独列出，确认即覆盖。
- 更新时，如果作者或主页与已安装的版本不同，确认框会警告用户。
- 插件存储的数据在更新时保留。修改了存储结构时请自行兼容旧数据（例如存一个 `schemaVersion`）。
- 插件需要特定版本以上的应用时，设置 `minAppVersion`，版本不够的应用会拒绝导入并提示用户更新。

---

### 回调链接（OAuth 登录）

`toolbox.env.callbackURI(path)` 生成 `yanplugin://<插件 id>/<path>`，系统打开这个链接时运行 `toolbox.env.onOpenURI` 注册的函数（在交互进程中，可以联网和弹对话框）：

```js
toolbox.commands.register("login", async () => {
  await toolbox.ui.openExternal(`https://example.com/oauth?redirect_uri=${encodeURIComponent(toolbox.env.callbackURI("auth"))}`);
});
toolbox.env.onOpenURI(async ({ path, query }) => {
  if (path === "/auth") toolbox.secrets.set("token", await exchange(query.code));
});
```

链接可以被任何网页或应用打开，请校验 `state` 等参数。

---

## 25. 常见错误对照表

| 提示 | 原因与处理 |
|---|---|
| 没有找到 plugin.json / 插件包里没有 plugin.json | zip 结构不对：plugin.json 必须在根目录或唯一的顶层文件夹里。 |
| plugin.json 格式不正确：缺少字段 … | 必需字段漏写或拼错；JSON 不能有注释和结尾逗号。 |
| 插件 id 只能包含字母、数字、点和连字符… | 修改 `id`。 |
| 插件没有提供任何功能… | `contributes` 中除 `configuration` 外至少提供一种。 |
| 预览器“…”需要指定 fileExtensions 或 languages | 预览器必须限定适用范围。 |
| 预览器“…”的扩展名“.csv”无效（不要带点） | 写 `csv`，不要写 `.csv`。 |
| …的语言“…”无法识别 | 见[语言名称](#语言名称)。 |
| 面板“…”的 entry 应为 .html 文件 / 无法以 UTF-8 读取面板页面 | 检查 `entry` 路径与文件编码。 |
| 此插件申请了当前版本还不支持的权限（…） | `permissions` 中可声明 `network`、`clipboard`、`documents`、`commands`、`background`、`backgroundLanguageNetwork`。 |
| network 权限只能列出域名或 IP… | 去掉 `http://`、`https://` 和路径，例如写 `api.github.com`、`localhost:8080` 或 `192.168.0.0/16`。 |
| network 权限使用 "*" 时不能再列出其他主机 | 只保留 `["*"]`，或去掉 `"*"` 并列出具体主机。 |
| 此插件需要应用 X 或更高版本 | 降低 `minAppVersion` 或请用户更新应用。 |
| 此插件需要插件 API X，当前应用支持到 Y | 降低 `apiVersion` 或请用户更新应用。 |
| 加载插件脚本失败：SyntaxError… | `main.js` 语法错误。 |
| 插件没有注册动作 / 预览器 / 面板处理函数 xxx | 清单中的 id 与 `register…` 的 id 不一致，或面板 `invoke` 的名称拼错。 |
| 插件返回值无效 | 文本动作应返回字符串或 `{ text }`；预览器应返回字符串或 `{ html }`。 |
| 插件没有返回结果（Promise 没有完成…） | 返回的 Promise 既没有完成，也没有待运行的定时器。 |
| 插件没有访问 xxx 的权限… | 在 `permissions.network` 中加入该主机。 |
| 此插件的网络访问已被关闭… | 用户关闭了开关，到插件中心的“权限”页重新开启。 |
| 此开发插件申请访问所有网站，尚未获得同意… | 在弹框中允许，或到插件中心的“权限”页点“查看并允许…”。 |
| 只支持 http、https 地址 | 地址要以 `http://` 或 `https://` 开头（WebSocket 为 `ws://`、`wss://`）。 |
| 请求被重定向到未声明的主机 xxx，已拦截 | 把重定向目标主机也加入 `permissions.network`。 |
| 插件没有剪贴板权限… | 在 `permissions` 中加入 `"clipboard": true`（只写入时 `"write"`）。 |
| 请先调用 toolbox.editor.getText()，再写回结果 | 面板中 `replace` 之前必须 `getText`。 |
| 原文稿已修改，未覆盖新内容… | 读取后文档变了；重新 `getText()` 后再写回。 |
| 插件已连续计算 N 秒 | 脚本在死循环或长时间计算。用户可以停止；自动运行的代码超过 `limits.busySeconds` 会被结束。把大计算分段（`await` 一个 0 毫秒的定时器）。 |
| 等待插件结果超时；插件已收到取消信号 | 悬停、补全等调用方只等几秒；用 `context.signal` 及时放弃过时的工作。 |
| 响应超过 N MiB… | 用 `responseType: "stream"`/`"file"`、`maxBytes` 截断，或申请更大的 `limits.responseBytes`。 |
| …中不能联网：需要…“documents”: “all” | 预览器、校验器、事件、自定义编辑器、内联补全、代码透镜中联网需要 `documents: "all"` 权限。 |
| gutter 的 symbol“…”不是可用的 SF Symbol | 装饰的 `gutter.symbol` 写错了；在“SF Symbols”应用中查准确的名称。 |
| 插件没有执行“…”的权限：请在 plugin.json 的 permissions.commands 中声明 | 行号栏图标、状态栏、菜单指向其他插件或应用的命令时，先在 `permissions.commands` 中声明。代码透镜指向未声明的命令时不报错，只显示文字。 |
| 菜单项的条件“…”无法解析 | `menus[].enablement` 或 `when.context` 的表达式有语法错误（括号不配对、`&&` 后面缺内容、引号没闭合）。 |
| 灰色建议不出现 | 检查：`languageFeatures` 的 `kind` 是否为 `inlineCompletion` 且语言匹配；光标处没有选区、编辑器有焦点；`main.js` 是否用同一个 `kind` 和 `id` 注册；联网的提供者是否声明了 `documents: "all"`；控制台里有没有错误。 |
| 插件 id 不能使用保留前缀 builtin. | `builtin.*` 留给随应用提供的扩展，换一个反向域名 id。 |
| 插件数据将达到 X，超过上限 Y，未保存 | 减少存储内容，或在 `limits.storageBytes` 中申请更大的上限。 |
| “文件名”有 X，超过此插件可以读取的 Y | 在 `limits.fileReadBytes` 中申请更大的上限。 |
| limits 中的“…”无法识别 / limits.… 应为 1 到 … 之间的整数 | `limits` 只能写 `storageBytes`、`fileReadBytes`，值为字节数。 |
| 插件动作“…”不可用：插件未安装或已停用 | 处理步骤引用的插件被卸载或停用。 |

---

## 26. 完整示例

下面几个示例覆盖最常见的插件形态，代码可以直接复制到你的插件里使用。

### 示例：JSON 键排序（文本动作）

```js
function sortDeep(value) {
  if (Array.isArray(value)) return value.map(sortDeep);
  if (value && typeof value === "object") {
    const sorted = {};
    for (const key of Object.keys(value).sort()) sorted[key] = sortDeep(value[key]);
    return sorted;
  }
  return value;
}

toolbox.registerTextAction("sortKeysDeep", (input) => {
  let value;
  try { value = JSON.parse(input.text); }
  catch (error) { throw new Error("不是有效的 JSON：" + error.message); }
  return { text: JSON.stringify(sortDeep(value), null, 2), message: "已递归排序所有键" };
});
```

### 示例：CSV 表格（预览器 + 存储）

```js
const usesHeader = () => toolbox.storage.get("headerRow", true);

toolbox.registerPreviewer("table", (input) => {
  const rows = parse(input.text, delimiterFor(input));
  const header = usesHeader() && rows.length ? rows.shift() : null;
  // …拼出 <table>，单元格内容先 escapeHTML…
  return `<!doctype html><html><head><meta charset="utf-8">
    <link rel="stylesheet" href="style.css"></head><body>…</body></html>`;
});
```

### 示例：GitHub 仓库查询（面板 + 网络）

`plugin.json`（节选）：

```json
"permissions": { "network": ["api.github.com"], "clipboard": true },
"contributes": {
  "panels": [ { "id": "lookup", "title": "GitHub 仓库查询", "entry": "panel/index.html", "width": 520, "height": 460 } ]
}
```

`main.js`（节选）：

```js
toolbox.registerPanelHandler("lookup", async (payload, context) => {
  const response = await fetch(`https://api.github.com/repos/${payload.name}`, {
    headers: { Accept: "application/vnd.github+json" }, signal: context.signal,
  });
  if (!response.ok) throw new Error(`GitHub 返回 ${response.status}`);
  const repo = await response.json();
  return { name: repo.full_name, url: repo.html_url, stars: repo.stargazers_count };
});
```

`panel/panel.js`（节选）：

```js
const repo = await toolbox.invoke("lookup", { name: input.value });
await toolbox.clipboard.writeText(`[${repo.name}](${repo.url})`);

await toolbox.editor.getText();                       // 确定写回位置
await toolbox.editor.replace(`[${repo.name}](${repo.url})`);
```

---

## 27. 常见问题

**能不能访问网络？**
可以，在 `permissions.network` 中声明主机（或声明 `["*"]` 并经用户同意）后，在 `main.js` 里用 `fetch` 或 `toolbox.net.request`（另有 WebSocket、SSE）。页面（预览、面板）本身不能联网，需要时通过 `toolbox.invoke` 调用 `main.js`，用 `toolbox.panels.post` 推送实时数据。

**能不能读写本地文件？**
可以读写用户选择的文件和文件夹：`toolbox.workspace.pickFile/pickFiles/pickFolder` 返回文件令牌，再用 `toolbox.files` 分段读取二进制、写入、列目录、监听变化；`pickFolder({ remember: true })` 可以跨重启记住文件夹。插件不能访问用户没有选择的路径。

**能不能用 npm 包？**
可以，只要它不依赖 Node 的 API 或 DOM（`fetch`、`TextEncoder`、`URL`、`crypto.subtle`、`WebAssembly` 等都有）。把包放进插件的 `node_modules` 后直接 `import`，或用 esbuild 等工具打包成一个 `main.js`（发布时更小，见第 22 节）。给页面用的前端库（如图表库）可以放进插件包，在 HTML 中用 `<script src="lib/chart.js">` 引用。

**能不能给 Markdown 或 HTML 文件做预览器？**
可以。默认使用内置预览；用户可以在 设置 → 插件 → 格式化与预览 中为 Markdown 或 HTML 改选你的预览器（见第 15 节）。

**为什么我的预览器没出现？**
检查：文件扩展名或语言是否匹配；插件是否启用；文档是否超过 90 万字符或以大文件模式打开；同一文件是否已有其他插件的预览器排在前面。

**面板里怎么保存 API 令牌？**
用 `toolbox.secrets`（`main.js` 中，保存在钥匙串，卸载时删除；页面通过 `toolbox.invoke` 调用，见第 20 节），或声明 `secret` 类型的设置项，由用户在设置表单中填写。不要放进 `toolbox.storage`，它是普通 JSON 文件。

**插件能不能自动更新？**
不能。应用不会下载插件。发布新版后，请告知用户下载并重新导入。

**用户的文本会不会被插件发送出去？**
没有网络权限的插件不能联网。有网络权限的插件只能把数据发往它在清单中声明、且用户同意过的主机；声明了 `["*"]` 的插件在用户明确同意后可以发往任意 http 或 https 地址。用户可以随时用“允许访问网络”开关切断插件的网络。页面的网络请求一律被拦截。

**怎么做 AI 补全？**
声明 `kind` 为 `inlineCompletion` 的语言功能，在函数里调用 AI 服务，返回光标后的文字（见第 17 节“内联补全”）。用 `permissions.network` 声明服务的主机，并设置 `backgroundLanguageNetwork: true`；令牌放在 `toolbox.secrets`；把 `context.signal` 传给 `fetch`，用户继续输入时旧请求会被取消。

**怎么做断点、Git 改动标记？**
用 `toolbox.editor.setDecorations` 的 `gutter` 字段在行号栏画图标，点击运行你的命令（`args` 里放行号）。图标随增删行移动；整篇替换后在 `textChanged` 事件里重新设置（见第 17 节“行号栏图标”）。

**标签右键菜单里的命令怎么知道点的是哪个标签？**
用 `context.tab`。从标签右键菜单运行时它是被点击的标签，不一定是当前标签；读写它需要 `documents: "all"`（见第 18 节）。

**菜单项能不能按我自己的状态启用？**
可以。用 `toolbox.context.set(key, value)` 保存状态，在菜单项的 `enablement` 里写表达式，如 `"loggedIn && hasSelection"`，状态改变后菜单立即更新（见第 18 节）。

**怎么卸载？**
插件中心 → 你的插件 → 卸载…。插件文件和它存储的数据都会被删除；引用它的处理步骤运行时会报错。
