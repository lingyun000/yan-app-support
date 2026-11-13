# 扩展开发手册

> 砚 1.0.4 及后续版本支持插件。

> 本手册讲**声明式贡献**：语言、语法高亮、主题、快捷键、文本工具与分类、工作区工具，以及格式化/预览/校验的裁决规则。用 JavaScript 实现的功能（命令、文本动作、预览器、面板、校验器、格式化器、悬停、补全、状态栏……）见 [插件开发手册](plugin-guide.md)。
>
> 清单格式有 JSON Schema：[schemas/plugin.schema.json](schemas/plugin.schema.json)（插件）、[schemas/extension.schema.json](schemas/extension.schema.json)（内置扩展）、[schemas/contributions.schema.json](schemas/contributions.schema.json)（两者共用的条目）。

## 目录

1. [概念](#1-概念)
2. [五分钟上手：一个纯声明式插件](#2-五分钟上手一个纯声明式插件)
3. [清单](#3-清单)
4. [加载、冲突与生效](#4-加载冲突与生效)
5. [语言 `languages`、`languageGroups`](#5-语言-languageslanguagegroups)
6. [语法高亮 `grammars`](#6-语法高亮-grammars)
7. [主题 `themes`](#7-主题-themes)
8. [快捷键 `keybindings`](#8-快捷键-keybindings)
9. [文本工具 `textTools`、`toolCategories`](#9-文本工具-texttoolstoolcategories)
10. [工作区工具](#10-工作区工具)
11. [格式化、预览与校验](#11-格式化预览与校验)
12. [诊断与排错](#12-诊断与排错)
13. [发布须知](#13-发布须知)
14. [内置扩展一览](#14-内置扩展一览)

---

## 1. 概念

应用本身只有**扩展内核**、编辑器引擎和窗口外壳。语言、语法、主题、快捷键、文本工具、工作区工具、格式化器、预览器、校验器都是**扩展**提供的**贡献**；应用自带的这些功能是随应用打包的**内置扩展**，与第三方插件走同一套贡献点。

| 名词 | 含义 |
|---|---|
| 扩展 | 一组贡献加上元数据（id、版本、兼容范围）。内置扩展的清单是 `extension.json`，第三方插件的清单是 `plugin.json`。 |
| 贡献点 | 一种可扩展的能力，对应清单 `contributes` 下的一个键，如 `languages`、`grammars`、`themes`。 |
| 声明式贡献 | 纯数据，由应用内的引擎执行（语法由声明式语法引擎着色），不运行插件代码，不影响输入和滚动性能。 |
| 脚本贡献 | 由插件的 `main.js` 实现，在独立进程中运行。 |

一个插件可以只有声明式贡献（不需要 `main.js`，不启动进程），也可以两者兼有。

## 2. 五分钟上手：一个纯声明式插件

下面的示例 为应用新增 Zig 语言：识别 `.zig` 文件、语法高亮、折叠和注释结构。整个插件只有一个 `plugin.json`：

```json
{
  "$schema": "https://lingyun000.github.io/yan-app-support/docs/schemas/plugin.schema.json",
  "id": "com.example.zig-language",
  "name": "Zig 语言支持",
  "version": "1.0.0",
  "contributes": {
    "languages": [ { "id": "Zig", "name": "Zig", "group": "系统语言", "keywords": ["fn", "const", "pub"],
                     "detection": { "extensions": ["zig", "zon"] },
                     "syntax": { "strings": { "double": { "escapes": true } }, "lineComments": ["//"] } } ],
    "grammars": [ { "language": "Zig",
                    "multiline": { "scanner": "code", "strings": { "double": { "escapes": true } }, "lineComments": ["//"] },
                    "protected": [ { "pattern": "\"(?:\\\\.|[^\"\\\\\\n])*\"", "scope": "string" },
                                   { "pattern": "(?m://.*$)", "scope": "comment" } ],
                    "rules": [ { "keywords": true, "scope": "key", "skipProtected": true } ] } ]
  }
}
```

1. 建一个文件夹，放入 `plugin.json`。
2. 设置 → 插件，点插件列表上方的 **＋ → 链接开发文件夹…**，选择这个文件夹。保存文件后自动重新载入，不需要重启。
3. 打开一个 `.zig` 文件：语言菜单里出现 Zig，代码按语法着色。
4. 条目有错时（正则写错、颜色格式不对），插件中心该插件的详情页以橙色列出被拒绝的条目和原因；其余条目照常生效。

**`$schema`**：写上它，VS Code 等支持 JSON Schema 的编辑器就能补全字段、提示取值并标出错误。可以直接使用上面的地址（应用不读取 `$schema`）。

## 3. 清单

第三方扩展一律使用 `plugin.json`，完整字段见 [插件开发手册第 4 节](plugin-guide.md#4-pluginjson-完整参考)。与本手册相关的要点：

| 字段 | 说明 |
|---|---|
| `id` | 反向域名，2–128 个字符，发布后不要改。插件的工具、快捷键等标识会以它为前缀。 |
| `version` | 数字版本号，如 `1.0.0`。 |
| `apiVersion` | 编写时使用的 API 版本（`toolbox.version`），可省略。比应用支持的新时拒绝安装。 |
| `main` | 脚本入口。**只有声明式贡献时省略**。提供了 `textActions`、`commands`、`previewers`、`events`、`formatters`、`validators`、`hoverProviders`、`completionProviders` 时必须有。 |
| `contributes` | 本手册的贡献点：`languages`、`languageGroups`、`grammars`、`themes`、`keybindings`、`textTools`、`toolCategories`；以及插件手册中的脚本贡献点。至少提供一种。 |

清单字符串可以写成 `"%key%"`，从插件包的 `nls.json`、`nls.<语言>.json` 取本地化文本。

## 4. 加载、冲突与生效

- **即时生效**：安装、启用、停用、卸载插件，或开发文件夹中的文件变化，贡献立即增减，界面随之刷新，不需要重启。停用一个内置扩展（插件中心的“内置”分组，标记“核心”的除外）同理。
- **逐条校验**：每个条目单独解码和校验；有错的条目被拒绝并记录原因，同一扩展的其他条目照常生效。
- **合并方式**：每个贡献点有固定的合并方式：
  - 唯一（`languages`、`languageGroups`、`grammars`、`themes`、`textTools`、`toolCategories`、工作区工具）：同一标识只有一个生效。依次比较：用户的选择 → 内置优先 → 先加载者。所以**插件不能用同一 id 替换内置的语言、语法或主题**；请使用新的 id，或用“扩展条目”给已有项追加内容。
  - 扩展条目：`languages` 和 `toolCategories` 中**只有 `id`、没有 `name`** 的条目不定义新项，而是给已有项追加内容（扩展名、文件名、关键字、识别规则；分类的动作、分组、语言）。
  - 并存（`keybindings` 等）：都保留，由各自的规则裁决（见第 8 节）。
- **命名空间**：插件的文本工具、工作区工具、快捷键命令自动以插件 id 为前缀（`com.example.x/tool`），清单里写短 id 即可；引用本插件的工具时也写短 id。

## 5. 语言 `languages`、`languageGroups`

语言 id（如 `"Zig"`）会存入会话和设置，**发布后不要改**。`aliases` 用于在清单和插件 API 中指代该语言（不区分大小写）。

| 字段 | 说明 |
|---|---|
| `id` ✅ | 语言 id。与已有语言相同且不写 `name` 时，本条目是扩展条目。 |
| `name` | 显示名称。 |
| `aliases` | 别名。 |
| `group` | 语言菜单分组的 id（见 `languageGroups`；内置分组有 `数据与文档`、`Web`、`应用开发`、`系统语言`、`脚本语言`、`配置与 DevOps`、`其他`）。 |
| `icon`、`order` | SF Symbols 图标；菜单顺序。 |
| `formattingStyle` | 没有格式化器时的通用格式化方式：`braces`、`indentation`、`markup`、`whitespace`、`structuredTool`。 |
| `preferredExtension` | 另存为时的扩展名，缺省为 `detection.extensions` 的第一个。 |
| `keywords` | 关键字。语法规则 `{ "keywords": true }` 用它生成匹配。 |
| `markup`、`slashComments`、`backtickStrings` | 标记语言；`//` 与 `/* */` 注释；反引号字符串。 |
| `folding` | 折叠策略，按顺序组合：`brackets`、`markup`、`embeddedMarkup`、`headings`、`indentation`、`sections`。缺省 `["brackets"]`。 |
| `syntax` | 词法结构，供折叠、括号匹配、注释切换、重排使用（**不决定颜色**，颜色由 `grammars` 决定）：`strings`（`double`/`single`/`backtick`，值为 `true`、`false` 或 `{ "escapes": true, "doubled": false }`）、`lineComments`、`blockComments`（`[["/*", "*/"]]`）、`foldBrackets`。 |
| `detection` | 如何识别这种文件，见下。 |

**识别**（`detection`）：打开文件时先看文件名，再看内容，得分最高的语言胜出。

| 字段 | 说明 |
|---|---|
| `extensions` | 扩展名（不含点）。插件声明的扩展名优先于内置语言。 |
| `weakExtensions` | 弱扩展名：只在内容不指向其他语言时采用（如 `.txt`）。 |
| `fileNames` | 完整文件名与得分，如 `{ "name": "Dockerfile", "score": 20 }`。 |
| `fileNamePrefixes` | 文件名前缀。 |
| `shebang` | 首行 `#!` 的正则。 |
| `contentRules` | `{ "score": 20, "patterns": [...], "requiresLiteral": "@import" }`：`patterns` 全部匹配才得分；`requiresLiteral` 是先做的廉价检查，不出现时跳过正则。识别在打开文件的路径上运行，正则要简单。 |
| `combinations` | 多种语言同时得分时的加分：`{ "requires": { "HTML": 10 }, "score": 5 }`。 |
| `authoritativeFileName` | 文件名匹配即决定语言（缺省 `true`）。 |

**扩展已有语言**：只写 `id` 和要追加的内容，例如让 `.jsonl` 按 JSON 打开：

```json
"languages": [ { "id": "JSON", "detection": { "extensions": ["jsonl"] } } ]
```

（插件手册中的 `languageAssociations` 是它的简写。）

**分组** `languageGroups`：`{ "id": "我的语言", "name": "我的语言", "order": 90 }`。

## 6. 语法高亮 `grammars`

一个语法为一种语言着色。着色在应用主进程由声明式引擎执行，大文件和虚拟编辑器中同样生效。

```json
{
  "language": "Zig",
  "multiline": { "scanner": "code", "strings": { "double": { "escapes": true } }, "lineComments": ["//"] },
  "protected": [ { "pattern": "\"(?:\\\\.|[^\"\\\\\\n])*\"", "scope": "string" },
                 { "pattern": "(?m://.*$)", "scope": "comment" } ],
  "protectedOptions": [],
  "rules": [ { "keywords": true, "scope": "key", "skipProtected": true },
             { "pattern": "@[A-Za-z_]\\w*", "scope": "tag", "skipProtected": true },
             { "pattern": "\\b(\\w+)\\s*\\(", "group": 1, "scope": "attribute", "skipProtected": true } ]
}
```

**执行顺序**

1. `protected`（受保护区域，通常是字符串和注释）：所有条目合成一个按顺序的选择分支，从左到右找最早的匹配并着色。
2. `rules`：每条规则在整个范围内匹配并着色；`skipProtected: true` 的规则不在受保护区域里着色（关键字不会在字符串里变色）。后面的规则覆盖前面的。

**规则字段**：`pattern`（ICU 正则）或 `keywords: true`（用语言的 `keywords`）；`scope`（类别）；`group`（只给某个捕获组着色，缺省 0 即整个匹配）；`options`（`anchorsMatchLines`、`caseInsensitive`、`dotMatchesLineSeparators`）。

**类别**（`scope`）决定颜色，由主题配色：

| 类别 | 用途 |
|---|---|
| `key` | 关键字、键名 |
| `string` | 字符串 |
| `number` | 数字 |
| `literal` | `true`、`false`、`null` 等 |
| `punctuation` | 运算符、括号 |
| `comment` | 注释 |
| `attribute` | 类型、属性、装饰器 |
| `tag` | 标签、函数名、内建调用 |
| `xmlDeclaration`、`xmlTag`、`xmlAttribute`、`xmlValue`、`xmlNumber`、`xmlBoolean`、`xmlCDATA`、`xmlComment`、`xmlEntity`、`xmlNamespace`、`xmlError`、`xmlSymbol` | XML 系语言（使用原生 XML 词法器时） |

**`multiline`：跨行构造**

编辑时只重新着色改动附近的行，需要知道从哪一行起状态是干净的。`multiline` 告诉增量扫描器**本语法**中哪些构造会跨行：

| 字段 | 说明 |
|---|---|
| `scanner` | `code`（按下面的字符串和注释设置）、`xml`、`markdown`、`make`、`none`（没有跨行构造）。 |
| `strings` | `double`、`single`、`backtick`：`{ "escapes": true, "doubled": false }`。 |
| `tripleQuotes` | `"""` 与 `'''` 字符串。 |
| `blockComments` | `"/*"`、`"--[["`。 |
| `lineComments` | 行注释标记。 |

**只声明语法确实着色的构造**：如果声明了块注释而 `protected` 中没有对应的模式，重启点会与着色结果不一致，表现为编辑后颜色错位。

**写法与性能**

- `protected` 的模式**不要用捕获组包裹整体**：ICU 在很长的匹配（几百 KB 的字符串）位于捕获组中时会放弃匹配。需要多行的块注释写成 `(?s:/\*.*?\*/)` 这样的非捕获组。
- 不要写可能灾难性回溯的正则（嵌套量词 `(a+)+`）。
- 正则错误、未知类别、未知选项会让这条语法被拒绝，并在设置中显示原因；该语言此时按纯文本显示。
- 内置的 45 种语言的语法都在内置扩展 `builtin.grammars` 中。

## 7. 主题 `themes`

```json
"themes": [ {
  "id": "我的主题", "name": "我的主题", "subtitle": "青灰与暖白", "icon": "paintpalette",
  "light": { "accent": "#236C70", "toolbar": "#E6ECEB", "chrome": "#EDF1F0", "inspector": "#F1F4F2", "sidebar": "#E8EEEB",
             "status": "#E6ECEB", "editor": "#FAFBF8", "control": "#DCE5E1", "border": "#A8B9B2",
             "selection": "#80AAA3", "caret": "#236C70", "editorText": "#243832", "caretWidth": 2 },
  "dark": { ... },
  "syntax": { "light": { "key": "#8A3B6E", "string": "#2F6B3A", "comment": "#7A8A86" }, "dark": { ... } }
} ]
```

主题 id 会存入设置，发布后不要改。主题被移除后，正在使用它的用户回退为“系统原生”。

| 配色键 | 位置 |
|---|---|
| `accent` ✅ | 强调色（按钮、选中项） |
| `toolbar`、`chrome`、`inspector`、`sidebar`、`status` ✅ | 工具栏、窗口框架、检查器、侧栏、状态栏背景 |
| `editor` ✅ | 编辑区背景 |
| `control` ✅ | 控件背景 |
| `border` ✅ | 分隔线 |
| `matchingRange` | 匹配括号、查找结果 |
| `selection`、`caret`、`caretWidth` | 选区、插入点颜色与宽度（缺省 1.5） |
| `editorText` | 正文颜色 |

`light` 与 `dark` 都必须给出；颜色写 `#RRGGBB`。`syntax` 按外观给出类别颜色（类别见第 6 节），未给出的类别使用应用默认色；外观切换时自动换色。内置的 15 个主题（`builtin.themes`）可作参考。

## 8. 快捷键 `keybindings`

```json
"keybindings": [ { "command": "format", "key": "cmd+shift+l", "title": "格式化" } ]
```

- 插件只能为**自己的命令**绑定快捷键（`command` 写短 id），等同于命令上的 `keybinding` 字段。快捷键必须包含 `cmd` 或 `ctrl`。
- 裁决：用户在 设置 → 快捷键 中的选择 → 内置绑定 → 插件按顺序。已被占用或属于系统的快捷键不会分配给插件，设置中显示原因。
- 用户可以在同一页修改、清空、恢复任何快捷键，修改后菜单立即更新。

## 9. 文本工具 `textTools`、`toolCategories`

文本工具是检查器、菜单、命令面板和处理步骤里的一个动作。插件的文本工具由它的**文本动作**实现：

```json
"textActions": [ { "id": "sortKeys", "title": "按键排序" } ],
"textTools": [ { "id": "sortKeys", "title": "按键排序", "icon": "arrow.up.arrow.down", "tint": "purple",
                 "aliases": "sort keys 排序", "handler": { "plugin": "sortKeys" } } ],
"toolCategories": [ { "id": "JSON", "actions": ["sortKeys"] } ]
```

- 只声明 `textActions` 时，应用自动为每个动作生成文本工具，并放在以插件命名的分类中。要自己决定图标、颜色或位置时才写 `textTools`。
- `toolCategories` 的扩展条目（只有 `id`）把工具放进已有分类，例如上面把“按键排序”加入 JSON 分类；也可以新建分类（写 `name`、`icon`、`languages` 等）。
- 文本工具字段：`title`、`icon`、`tint`（`blue`、`orange`、`red`、`green`、`purple`、`teal`）、`aliases`（搜索词）、`report`（结果在分屏显示，不替换原文）、`conversionTitle`（检查器“转换”中的短标题）、`selectionTransform`（作为选区变换时的顺序）。
- 分类字段：`name`、`icon`、`subtitle`、`order`、`languages`（以该分类打开的语言）、`editorLanguage`（选中分类时把文档切换为的语言）、`actions`、`groups`（`{ title, icon, actions }`）、`primaryActions`、`general`、`fallback`。

处理步骤和历史记录按工具 id 保存；插件工具的 id 是 `<插件 id>/<工具 id>`，改名会让已保存的步骤找不到它。

## 10. 工作区工具

插件的每个**面板**（`contributes.panels`）自动成为工作区侧栏“插件”分类下的一页，也可以在独立窗口中打开，不需要另外声明。面板写法见插件手册第 8 节。

需要自定义标题、分类或搜索词时声明 `workspaceTools`，见 [插件开发手册第 18 节](plugin-guide.md#18-界面集成菜单工作区工具粘贴识别设置页自定义编辑器)。

## 11. 格式化、预览与校验

插件的 `formatters`、`previewers`、`validators` 与应用内置的功能按同一规则选用：

| 服务 | 自动顺序 |
|---|---|
| 格式化 | 按扩展名匹配的插件 → 内置 → 按语言匹配的插件 → 通用格式化 |
| 预览 | 内置（Markdown、HTML）→ 按扩展名匹配的插件 → 按语言匹配的插件 |
| 校验 | 全部运行 |

用户可在 设置 → 插件 → 格式化与预览 中为某个语言或扩展名改选提供者，详见 [插件开发手册第 15 节](plugin-guide.md#15-格式化预览与校验的选择)。为新语言提供格式化器时，按语言匹配即可，不会与内置冲突。

## 12. 诊断与排错

| 现象 | 去哪看 |
|---|---|
| 插件无法安装 | 导入时的错误提示（清单格式、缺少 `main`、`apiVersion` 过高等）。 |
| 某个条目没有生效 | 插件中心，该插件详情页的橙色条目：`<插件 id> · <贡献点> · <原因>`。 |
| 编辑清单时就想发现错误 | 在 `plugin.json` 中写 `$schema`，用支持 JSON Schema 的编辑器打开。 |
| 脚本错误 | 插件中心的“控制台”标签（插件手册第 23 节）。 |

常见错误：

- `grammars`：`invalid pattern`（正则无法编译，注意 JSON 中反斜杠要写两次）、`scope xxx`（类别不存在）、`unknown regex option`。
- `themes`：`<键> (#RRGGBB)`（颜色格式或缺少必需的键）。
- `textTools`：`handler must name a plugin action`（插件的工具必须由文本动作实现）。
- `languages`：`invalid pattern`（识别规则的正则）、`formattingStyle`（取值不对）。

## 13. 发布须知

- 存入用户数据的标识（语言 id、主题 id、工具 id、命令 id）是插件的公开接口，发布后不要改。
- 应用不认识的 `contributes` 键会被忽略，并在插件详情页以橙色提示。发布前请用 `$schema` 检查拼写。

## 14. 内置扩展一览

应用自带的功能也是扩展，可在插件中心的“内置”分组中查看。

| 扩展 | 内容 |
|---|---|
| `builtin.languages` | 45 种语言与菜单分组，含识别规则 |
| `builtin.grammars` | 45 种语言的语法（XML 系使用原生词法器 `tokenizer: "xml"`） |
| `builtin.text-tools` | 文本工具与分类（格式化、转换、编码、校验……） |
| `builtin.workspace-tools` | 27 个工作区工具及侧栏分类 |
| `builtin.themes` | 15 个预设主题 |
| `builtin.keybindings` | 菜单默认快捷键（命令 id 如 `edit.undo`） |
| `builtin.language-services` | 内置格式化器（含 Prettier 的解析器表）、Markdown/HTML 预览、JSON/XML/YAML/SQL 校验器 |
