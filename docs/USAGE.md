# Build Harmony Apps 使用说明

面向使用者的完整手册：安装配置、快速上手、17 个 Skill 的触发方式与工作流程、工具链说明、排障与 FAQ。开发与贡献相关内容（结构校验、evals、CI）见 [README.md](../README.md#验证)。

## 目录

- [1. 简介](#1-简介)
- [2. 环境要求](#2-环境要求)
- [3. 安装与配置](#3-安装与配置)
- [4. 快速上手](#4-快速上手)
- [5. 工具链说明](#5-工具链说明)
- [6. Skill 参考](#6-skill-参考)
  - [6.1 核心构建与调试](#61-核心构建与调试)
  - [6.2 ArkTS 语言](#62-arkts-语言)
  - [6.3 ArkUI 界面](#63-arkui-界面)
  - [6.4 集成、发布、测试与诊断](#64-集成发布测试与诊断)
- [7. 排障与 FAQ](#7-排障与-faq)
- [8. 附录](#8-附录)

---

## 1. 简介

Build Harmony Apps 是一个支持 **Claude Code 与 Codex 双平台**的 HarmonyOS（鸿蒙）应用开发插件。它把 HarmonyOS 开发中的常见任务拆分为 17 个独立 Skill——从创建项目、写 ArkUI 界面、修编译错误和运行崩溃，到集成系统 Kit、性能与内存分析、签名打包和 AppGallery 提审——由 AI Agent 根据你的提问自动路由到对应 Skill。

**适用人群**：使用 Claude Code 或 Codex 进行 HarmonyOS / ArkTS 应用开发的开发者。

**核心设计理念：证据门控（evidence-gated）工作流。** 每个 Skill 都要求 Agent 用真实证据支撑结论，而不是凭模型记忆下判断：

- 构建失败立即停下修复，不带着错误继续后面的步骤；
- 应用"启动成功"必须用 UI 树或截图证明，`start_app` 调用返回成功不算数；
- UI 交互之后必须重新读取 UI 树 / 截图确认效果，不复用过期坐标；
- 性能与内存结论需要 DevEco Profiler trace / 快照的前后对比数据；
- 工程配置文件（如 `build-profile.json5`、`module.json5`）不凭记忆重写，以项目现状和已安装 SDK 为准。

这意味着插件在多数任务里会实际驱动构建、设备/模拟器和 UI 自动化，而不只是给出代码建议。

## 2. 环境要求

### 必需

| 依赖 | 说明 |
|---|---|
| DevEco Studio | HarmonyOS 官方 IDE，提供 SDK、Hvigor、HDC 等底层工具链。插件已在 **DevEco Studio 26 / HarmonyOS API 26 Beta1** 环境验证 ArkTS 编译和 unsigned HAP 打包 |
| Node.js + npm | 用于通过 `npx` 自动拉取 CodeGenie MCP（无需手动安装该包） |
| Claude Code 或 Codex | 插件的宿主 Agent |

涉及运行时的任务（启动应用、UI 自动化、截图取证）需要至少一个可用目标：真机（HDC 可连接）或 DevEco 模拟器；纯视觉预览也可以用 DevEco Previewer。完全没有设备时，创建项目、语法/编译诊断、代码评审、日志与 trace 文件分析仍可正常工作，Skill 会把运行时验证明确标注为"待完成"。

### 可选增强：OpenHarmony SIG DevEco CLI

```bash
npm i -g @deveco/deveco-cli
```

要求 Node ≥ 18、已安装 DevEco Studio ≥ 6.1，仅支持 macOS/Windows。安装后各 Skill 会**自动检测并利用**（通过 `devecocli --version` 探测），获得以下增强能力：

- **本地官方文档检索**：`devecocli docs search <关键词>`，查 API 签名、组件用法时不再依赖联网搜索；
- **模拟器状态注入**：折叠/展开、旋转、GPS 坐标、电量、传感器——CodeGenie MCP 不具备的能力；
- **官方脚手架**：`devecocli create` 使用华为当前官方模板创建项目（优先于插件内置模板）；
- **LSP 语法诊断**：`devecocli serve mcp` 提供不经完整构建的 `check_ets_files` / `check_cpp_files`（需按项目配置，见 [5.3](#53-可选devecocli-增强)）。

不安装也完全可用，只是相应能力回退到 CodeGenie MCP 与内置方案。

## 3. 安装与配置

### 3.1 Claude Code

正式安装（通过 Marketplace）：

```bash
claude plugin marketplace add noiseorigin/build-harmony-apps
claude plugin install build-harmony-apps@build-harmony-apps-marketplace
```

本地开发/试用（无需 Marketplace）：

```bash
git clone https://github.com/noiseorigin/build-harmony-apps.git ~/plugins/build-harmony-apps
claude --plugin-dir ~/plugins/build-harmony-apps
# 修改插件文件后在会话中运行 /reload-plugins 生效
```

### 3.2 Codex

将仓库放入个人插件目录（如 `~/plugins/build-harmony-apps`），在 `~/.agents/plugins/marketplace.json` 中添加本地插件条目并启用 `build-harmony-apps@personal`。更新插件后需要重新安装并**新开 Codex 任务**，确保 Skill 与 MCP 使用同一版本。

### 3.3 CodeGenie MCP

插件根目录的 `.mcp.json` 已声明官方 DevEco CodeGenie MCP，安装插件后由宿主 Agent 自动加载：

```json
{
  "mcpServers": {
    "deveco-codegenie": {
      "command": "npx",
      "args": ["-y", "@deveco-codegenie/mcp@1.1.11"]
    }
  }
}
```

版本被**固定为 `1.1.11`**（npm stable 版），首次使用时 `npx` 会自动下载，需要能访问 npm registry（见 [7.1 排障](#71-mcp-拉取失败或超时)）。无需手动安装或全局安装该包。

### 3.4 验证安装

在会话中问：

> What skills are available?

应列出 17 个 Skill（`harmony-debugger-agent`、`arkui-ui-patterns`、`harmony-kit-integration`、`harmony-release-compliance` 等）。再让 Agent 构建任意一个 HarmonyOS 工程，能看到它调用 `deveco-codegenie` 的 `init_project_path` / `build_project` 即说明 MCP 连接正常。

## 4. 快速上手

### 4.1 第一次使用

在一个 HarmonyOS 工程根目录（包含 `build-profile.json5` 的目录）启动 Claude Code / Codex，直接用自然语言描述任务：

> 构建并在模拟器上启动这个应用，截图给我看首页

Agent 会自动路由到 `harmony-debugger-agent`：初始化项目路径 → 构建 → 启动 → 读取 UI 树 / 截图作为启动证据。

还没有工程？直接说：

> 帮我创建一个叫 MyNotes 的鸿蒙应用项目

会路由到 `deveco-create-project`，脚手架完成后自动做一次干净构建验证。

### 4.2 Skill 的触发机制

**不需要记住任何 Skill 名字。** 每个 Skill 通过描述中的触发场景自动匹配，你只需要像描述 bug 或需求一样说话：

| 你说的话 | 触发的 Skill |
|---|---|
| "编译报错了，帮我修" | [arkts-error-fixes](#arkts-error-fixes) |
| "应用一打开就闪退" | [arkts-runtime-fix](#arkts-runtime-fix) |
| "列表滑动很卡" | [arkui-performance-audit](#arkui-performance-audit) |
| "加一个相机拍照功能" | [harmony-kit-integration](#harmony-kit-integration) |
| "准备上架 AppGallery" | [harmony-release-compliance](#harmony-release-compliance) |

症状式、意图式的描述最容易命中。如果想强制使用某个 Skill，也可以直接点名（如"用 harmony-memory-leaks 查一下内存"）。

## 5. 工具链说明

### 5.1 CodeGenie MCP 的 10 个工具

插件的核心运行时能力来自官方 `deveco-codegenie` MCP：

| 工具 | 用途 |
|---|---|
| `init_project_path` | 设置 HarmonyOS 项目根目录（其余项目工具的前置） |
| `build_project` | 构建 app/模块，可选 clean、product、build mode |
| `start_app` | 在模拟器或真机上安装并启动已构建的应用 |
| `get_app_ui_tree` | 读取当前 UI 层级树（JSON），用作启动/交互证据 |
| `perform_ui_action` | 点击、滑动、输入文本、按键、截图 |
| `verify_ui` | 执行一段有边界的自然语言 UI 验证场景，返回 verification id |
| `save_ui_screenshot` | 保存某次 verify 运行的截图（需 verification id） |
| `get_ui_verification_log` | 获取某次 verify 运行的执行日志（需 verification id） |
| `check_ets_files` | 聚焦的 ArkTS/ETS 诊断，比完整构建快 |
| `check_cpp_files` | 聚焦的原生 C/C++ 源码诊断 |

**已知能力边界**（1.1.11 版）：不提供设备列表查询、连续 hilog 日志流、任意文件拉取、DevEco Profiler trace 捕获、实时画面镜像。这些场景 Skill 会自动降级到下面的工具阶梯。

### 5.2 工具阶梯

每类能力按"官方封装优先"排列，前一级不可用或不覆盖时才降级：

| 能力 | 首选 | 次选 | 兜底 |
|---|---|---|---|
| 构建 / 安装 / 启动 / 日志 | CodeGenie MCP | `devecocli build/run/log` | 原始 hvigor + hdc |
| UI 树 / 点击 / 输入 | CodeGenie MCP（唯一） | — | `devecocli ui screenshot` 仅作截图证据 |
| ArkTS 语法诊断 | CodeGenie / devecocli 的 `check_ets_files`（免完整构建） | 完整构建 | — |
| 项目脚手架 | `devecocli create` | 插件内置模板脚本 | DevEco Studio 新建向导 |
| 文档检索 | `devecocli docs search/read`（本地官方文档） | 联网搜索官方文档 | — |
| 模拟器状态注入（折叠/传感器/GPS/电量） | `devecocli emulator …`（唯一） | — | — |

降级到原始 hvigor + hdc 时，Skill 会先用环境探测脚本（`detect_harmony_env.py`）解析 `DEVECO_SDK_HOME`、`JAVA_HOME` 和 hdc 路径，并且**不会把机器路径写进项目文件**；多设备连接时所有命令强制指定 `-t <设备>`。

### 5.3 可选：devecocli 增强

安装方法见 [第 2 节](#2-环境要求)。两点补充说明：

- **LSP 语法诊断需按项目初始化**：`devecocli serve mcp` 依赖项目级环境变量（`PROJECT_PATH`），所以它不在插件全局 `.mcp.json` 里，需要在目标项目中运行 `devecocli init --mcp --agent <agent> --project <path>` 后才可用。
- 部分 emulator 子命令有硬性限制（license 接受需要交互式终端、镜像下载耗时 30 分钟以上不可自动重试等），遇到时 Skill 会把命令交给你手动执行，这是预期行为而非故障。

## 6. Skill 参考

17 个 Skill 按 4 类分组。每个条目包含：用途、何时触发（含示例提问）、工作流程、依赖与产物。速查：

| 分组 | Skill | 用途 |
|---|---|---|
| 核心构建与调试 | [harmony-debugger-agent](#harmony-debugger-agent) | 构建/启动/UI 自动化/调试总入口 |
| | [deveco-create-project](#deveco-create-project) | 创建最小 Stage-model 项目 |
| | [harmony-runtime-preview](#harmony-runtime-preview) | 渲染与对比界面、生成截图证据 |
| ArkTS 语言 | [arkts-grammar-standards](#arkts-grammar-standards) | 语法规则与 TS→ArkTS 迁移 |
| | [arkts-error-fixes](#arkts-error-fixes) | 修编译/类型/资源/装饰器错误 |
| | [arkts-runtime-fix](#arkts-runtime-fix) | 修运行时崩溃与白屏 |
| ArkUI 界面 | [arkui-ui-patterns](#arkui-ui-patterns) | 组件/导航/状态/列表/表单模式 |
| | [arkui-native-design](#arkui-native-design) | 原生外观与交互、设计评审 |
| | [arkui-multidevice](#arkui-multidevice) | 手机/平板/折叠屏适配 |
| | [arkui-performance-audit](#arkui-performance-audit) | 卡顿与渲染性能审查 |
| | [arkui-view-refactor](#arkui-view-refactor) | 大组件拆分与 V1→V2 迁移 |
| 集成、发布、测试与诊断 | [harmony-kit-integration](#harmony-kit-integration) | 60+ Kit 集成与权限流程 |
| | [harmony-app-intents](#harmony-app-intents) | Intents Kit / 小艺系统入口 |
| | [harmony-release-compliance](#harmony-release-compliance) | 签名打包、提审、备案、IAP |
| | [harmony-test-triage](#harmony-test-triage) | 单元/集成/Hypium UI 测试分诊 |
| | [harmony-profiler-trace](#harmony-profiler-trace) | Profiler trace 分析 |
| | [harmony-memory-leaks](#harmony-memory-leaks) | 内存增长与泄漏取证 |

### 6.1 核心构建与调试

#### harmony-debugger-agent

**用途**：构建、安装、启动、UI 检查、UI 自动化与运行时调试的总入口，编排 CodeGenie MCP + Hvigor + HDC。

**何时触发**：编译或运行应用、选择设备/模拟器、查看 UI 树、点击输入截图、读 hilog、诊断运行时行为。

> - "构建并启动这个应用"
> - "在真机上跑起来，点一下登录按钮看看会发生什么"
> - "帮我抓一下这个页面的 hilog"

**工作流程**：解析并保持会话上下文（项目根、模块、product、构建模式、UIAbility、bundle、设备）→ `init_project_path` → `build_project`（构建失败即停，转 arkts-error-fixes）→ `start_app` → 用 UI 树或截图证明启动 → 交互后重新读树 → 需要断言的场景用 `verify_ui` 并保存截图与验证日志。

**依赖与产物**：需要 CodeGenie MCP；环境不明时运行 `../skills/harmony-debugger-agent/scripts/detect_harmony_env.py` 探测 SDK/hdc/devecocli。多个设备连接且目标不明确时会先询问；点名真机时不会静默换成模拟器；不会顺手卸载应用、清数据或重启设备。产物：构建结果、启动证据（UI 树/截图）、verification id、相关日志片段。

#### deveco-create-project

**用途**：创建最小 HarmonyOS Stage-model ArkTS 应用项目。

**何时触发**：新建应用脚手架、初始化空目录。

> - "创建一个叫 MyNotes 的鸿蒙项目，包名 com.example.mynotes"
> - "在这个空目录初始化一个 HarmonyOS 工程"

**工作流程**：脚手架优先级为官方 `devecocli create` → 插件内置确定性模板脚本（`../skills/deveco-create-project/scripts/create_project.py`，离线可用，读取已安装 DevEco SDK 元数据做替换）→ 超出最小 Stage-model 范围（元服务、HAR/HSP、C++、签名等）改用 DevEco Studio 官方新建向导。生成后校验完整性并通过 harmony-debugger-agent 做一次干净构建。

**依赖与产物**：需要已安装 DevEco SDK（不猜 API level）；不覆盖非空目录、不发明签名材料。产物：可构建的完整 Stage-model 工程（AppScope、entry 模块、EntryAbility、Index 页面等）。

#### harmony-runtime-preview

**用途**：在 Previewer、模拟器或真机上渲染、检查、对比 ArkUI 界面。

**何时触发**：想"看到"某个页面、迭代 UI、对比手机/平板/折叠屏布局、为视觉改动生成截图证据。

> - "改完这个页面后截图给我看效果"
> - "对比一下这个页面在手机和折叠屏上的样子"
> - "把这几个状态的截图做成一个网页画廊"

**工作流程**：按场景选择模式（Previewer 快速迭代 / 运行中应用抓真实运行时 / Hvigor 热重载 / 截图画廊）→ 先构建 → 抓基线截图与 UI 树 → 做一次聚焦的 UI 修改 → 重新捕获同一状态对比 → 多图时用 `../skills/harmony-runtime-preview/scripts/build_preview_gallery.py` 生成本地 HTML 画廊。

**依赖与产物**：交互类验证需要 CodeGenie MCP 与设备/模拟器。产物：带设备/主题/状态标注的截图、HTML 画廊。注意截图画廊是静态证据，插件不提供模拟器实时画面镜像。

### 6.2 ArkTS 语言

#### arkts-grammar-standards

**用途**：ArkTS 语法规则、静态限制、TypeScript→ArkTS 差异、Sendable 约束的解释与合规评审。

**何时触发**：写/评审 ArkTS、解释某段语法为什么被拒绝、移植 TS/JS 代码、选择合法的类型化改写。

> - "为什么 ArkTS 不让我写这种解构？"
> - "把这段 TypeScript 改成合法的 ArkTS"
> - "这个类要跨线程传，Sendable 该怎么写？"

**工作流程**：优先采信已安装编译器与现行规范而非模型记忆；区分证据来源（编译器诊断 / 官方规范 / linter 策略 / 迁移指南），给出最小的编译器可接受改写；涉及代码改动时用 `check_ets_files` 或构建验证。

**依赖与产物**：无硬性设备要求。产物：规则出处标注 + 最小改写。不用 `any`/`ESObject`/强断言来压制诊断。

#### arkts-error-fixes

**用途**：诊断并修复 ArkTS 编译器、类型检查、linter、资源、模块、ArkUI 装饰器类错误。

**何时触发**：构建或 ETS 检查刚失败、用户贴出 ArkTS 诊断信息要求修复。

> - "构建报了这个错：Property 'xxx' does not exist…"
> - "帮我把这一堆编译错误清掉"

**工作流程**：保留首个编译错误的完整上下文 → 用 `check_ets_files` 做聚焦诊断（比完整构建快）→ 用最窄的构建任务复现，先修最早的因果错误、忽略级联 → 分类（语言限制/装饰器/API 可用性/模块导入/资源/Hvigor 配置/原生桥/生成代码）→ 最小语义修复 → 重跑聚焦检查再重建。不熟悉的 `@kit.*` API 用 `devecocli docs search` 或官方文档核对签名。

**依赖与产物**：需要可用的构建工具链；CodeGenie 的 `check_ets_files` 用于加速诊断，devecocli 可选（本地文档检索）。产物：因果诊断、分类、最小改动、聚焦检查与完整构建结果。"旧错误消失但出现更早的新错误"不算完成。

#### arkts-runtime-fix

**用途**：解析、分诊、修复并验证运行时崩溃——jscrash、未捕获异常、白屏、启动后闪退。

**何时触发**：构建通过但运行失败；用户提供 TypeError / ReferenceError / BusinessError / faultlogger / hilog / 栈信息。

> - "应用一点这个按钮就闪退，这是崩溃日志"
> - "启动白屏，帮我查"

**工作流程**：已有日志则用 `../skills/arkts-runtime-fix/scripts/parse_crash.py` 解析出错误类型、可疑文件、栈顶帧和下一步动作；没有日志则先锁定一台设备 → 复现一次 → 优先查 faultlogger，不够再做有边界的 hilog 抓取。修复从第一个应用自有栈帧和确切错误消息入手，做最小根因修复（不用重试/延时/空值兜底掩盖），然后构建、跑相同流程、证明原崩溃签名消失。

**依赖与产物**：日志解析可离线；复现与验证需要设备。产物：结构化崩溃解析（markdown）、根因修复、修复后运行验证。

### 6.3 ArkUI 界面

#### arkui-ui-patterns

**用途**：用 HarmonyOS 原生模式构建/重构 ArkUI 页面——组件、导航、浮层、状态管理、异步、列表、表单、无障碍、资源。

**何时触发**：实现新页面或新功能、选组件和状态归属、接导航或弹窗、需要示例驱动的 ArkTS UI 指导。

> - "做一个带搜索的设置页"
> - "这个页面的状态该用 @State 还是 @ObservedV2？"
> - "给这个列表加下拉刷新和空态"

**工作流程**：识别功能形态（列表/详情、表单、设置、Tabs、搜索等）→ 检查项目的 SDK 基线与 V1/V2 状态管理代际 → 先定状态归属再选装饰器 → 从组件索引选原生组件与模式 → 实现 loading/内容/空态/错误/重试等状态 → 结构骨架和行为接线后各构建一次 → 用 CodeGenie 渲染并驱动主路径。全新项目会先经 deveco-create-project 搭脚手架，确立单一应用外壳、导航所有者、资源层与服务组合根之后再铺功能页。

**依赖与产物**：内置 10 个参考文档，从组件索引（`components-index`）路由到匹配的模式文档，按需加载。硬规则：不在一个组件里混用 V1/V2 装饰器；`build()` 保持声明式无副作用。

#### arkui-native-design

**用途**：让界面符合 HarmonyOS 原生外观与交互模型——层级、色彩、字体、形状、动效、深色模式、系统栏与避让区。

**何时触发**：应用 HarmonyOS 设计规范、评审视觉质量、替换"网页感/iOS 感"的界面。

> - "这个页面看起来像网页，帮我改成鸿蒙原生风格"
> - "按 HarmonyOS 设计规范评审一下这个页面"
> - "适配深色模式和大字体"

**工作流程**：检查目标设备类型、设计 token 与 ArkUI 代际 → 先理信息层级再动视觉 → 优先官方原生组件 → 用语义化 token 而非一次性字面值 → 刻意处理系统面（状态栏、避让区、键盘、返回、弹窗）→ 补全交互状态（pressed/focused/disabled/loading/空态/错误）→ 验证深色模式、文本缩放、本地化、读屏、触控目标 → 用 harmony-runtime-preview 渲染确认。

**依赖与产物**：视觉结论必须基于至少一个真实渲染状态；不发明"HarmonyOS 标准"像素值或断点。

#### arkui-multidevice

**用途**：跨手机/平板/折叠屏/窗口尺寸/横竖屏/键鼠输入的布局适配与验证（一次开发多端部署）。

**何时触发**：响应式/自适应布局、折叠态变化、避让区与键盘、自由窗口、鼠标键盘焦点、SysCap 能力检查。

> - "让这个页面在平板上左右分栏"
> - "折叠屏展开时布局乱了"
> - "适配键盘弹出时的避让"

**工作流程**：记录支持的设备类型、窗口行为、输入方式 → 场景分类（尺寸/折叠/避让/输入/方向/硬件能力/复合）→ 以窗口与能力证据决定布局（不按 phone/tablet 标签猜）→ 保持语义结构稳定、只变排布与密度 → 处理运行时过渡（resize/旋转/折叠/键盘）→ 可选硬件路径加能力检查与回退 → 用 harmony-runtime-preview 渲染矩阵并在每个差异布局里驱动主操作。

**依赖与产物**："支持手机平板折叠屏"这类宣称需要每个差异布局类 + 至少一个过渡态的证据，单张截图不算多设备证明。

#### arkui-performance-audit

**用途**：ArkUI 运行时性能审查——代码优先，量化结论要求 Profiler 证据。

**何时触发**：首帧慢、卡顿、列表滑动掉帧、组件更新风暴、布局抖动、CPU 高、图片内存压力。

> - "列表滑动很卡，帮我查原因"
> - "这个页面打开要两秒，优化一下"

**工作流程**：记录确切的页面、交互、设备、数据规模与症状 → 识别 V1/V2 代际（不拿 V1 建议套 V2 代码）→ 追踪状态扇出到渲染子树 → 检查列表 identity、`build()` 内重复分配、UI 线程同步工作、布局深度、图片解码、动画范围 → 按用户影响与证据强度排序（代码确认/推测/trace 支持）→ 最小针对性修复 → 构建复跑；量化结论升级到 harmony-profiler-trace 抓可比 trace。

**依赖与产物**：代码审查可离线；量化结论需要 Profiler。不接受"更少行数/懒加载/加缓存必然更快"的无证据断言。

#### arkui-view-refactor

**用途**：把大而脆的 ArkUI 组件重构为清晰稳定可测的结构，保持行为不变；规划安全的 V1→V2 状态管理迁移。

**何时触发**：拆分超长 `.ets` 页面、收紧状态归属、抽子组件、清理 `build()` 副作用、V1→V2 迁移。

> - "这个 800 行的页面帮我拆一下"
> - "把这个组件从 @State/@Link 迁到 V2"

**工作流程**：先构建并记录必须保持不变的流程与渲染状态 → 摸清当前状态归属、参数、事件、生命周期 → 把副作用移出 `build()`、领域逻辑移入 service → 按职责抽取子组件（窄类型输入 + 事件）→ 状态放在最窄的 owner → V1/V2 迁移与普通抽取分开做 → 每个结构切片后构建，重构后对比记录的流程与渲染状态。

**依赖与产物**：验证需要构建与运行对比。"文件变短"不等于重构成功。

### 6.4 集成、发布、测试与诊断

#### harmony-kit-integration

**用途**：集成 HarmonyOS 系统 Kit——相机、音频/AVPlayer/AVSession、扫码、账号登录、支付、推送、地图、定位、通知、OCR、服务卡片、元服务、Share Kit、App Linking、数据持久化、网络、后台任务、ArkWeb 等 60+ 能力，以及完整的权限申请流程。

**何时触发**：添加任何 Kit 能力、申请权限（相机/定位/麦克风）、后台播放被静音、服务卡片不刷新、push token 报错、不确定某能力该用哪个 Kit。

> - "加一个扫码功能"
> - "切到后台音乐就停了"
> - "服务卡片不刷新怎么办"
> - "接入华为账号一键登录"

**工作流程**：先通过 Kit 索引把能力解析到具体 Kit（有免权限的系统面如 CameraPicker 就优先用，少要敏感权限）→ 对照项目基线检查可用性（SDK、deviceTypes、**部分 Kit 仅中国大陆可用**、Release/preview 状态）→ 按三步权限流程声明与请求（`module.json5` 声明 → 运行时检查 → `requestPermissionsFromUser` → 设置页兜底，绝不重复弹已拒绝的框）→ 最小集成、Kit 调用放 service 层 → 真机/模拟器上驱动实际流程（授权弹窗、拍摄、播放、加卡片）取证。

**依赖与产物**：内置 13 个 Kit 分簇参考文档，从 Kit 索引路由后只读匹配的簇。硬规则：AGC 后端类 Kit（账号/推送/支付/地图）没有控制台配置必然失败，会先指出 AGC 前置而不是空转调试客户端；后台执行必须配对正确的后台任务类型，媒体播放还需 AVSession；**编译通过不等于集成成功**，每个 Kit 都需要设备证据。

#### harmony-app-intents

**用途**：Intents Kit 集成——把应用功能/内容暴露给小艺（Celia）建议、语音调用、本地搜索等系统入口；`insight_intent.json` 配置与 `InsightIntentExecutor` 实现。

**何时触发**：让应用功能可被系统外部调用、添加 insight_intent 配置、处理系统 intent 调用、评审 Intents Kit 集成。

> - "让用户能用小艺语音打开我的播放页"
> - "评审一下这个 InsightIntentExecutor 实现"

**工作流程**：选 1–3 个高价值动词（不镜像整个导航树）→ 确认目标垂直域/意图名当前开放且满足准入（SID、设备、系统、SDK）→ 定义窄参数/结果契约 → 按现行官方 schema 更新 `insight_intent.json` → 实现薄 executor（校验参数、委托现有 service、返回明确结果）→ 本地测试后做真机/系统面验证与验收。

**依赖与产物**：结果按四级证据严格标注——已实现（编译通过）/ 本地验证 / 系统验证（真机系统入口实际调起）/ 已验收（通过华为审核）。绝不凭编译结果宣称"小艺里可用"。部分能力要求华为标准系统真机，模拟器不支持。

#### harmony-release-compliance

**用途**：签名、打包、AppGallery 提审与驳回分诊——证书与 Profile、真机包验证、`assembleApp` 产物、AGC 提交清单、IAP 内购审核要求、APP 备案与 ICP 备案边界。

**何时触发**：签名验证失败（含错误码 **9568322**）、包或版本被驳回、Profile 缺 entitlement、准备上架/提审、虚拟商品需要内购/买断/订阅。

> - "安装报 9568322"
> - "准备提审 AppGallery，帮我过一遍清单"
> - "应用被驳回了，这是审核意见"

**工作流程**：按当前所处的门逐个走——签名配置（.p12/CSR、AGC 证书 + Profile 匹配）→ 本地能力验证（手动 Profile + hdc 安装）→ 商店打包（项目级 `assembleApp` 出签名 `.app`）→ 提交材料清单（隐私政策、截图、versionCode 递增、能力勾选）→ 资质判断（备案是否适用按实际情况，**不把 APP 备案/ICP 备案/软著当无条件通用规则**）→ 需要内购时走 IAP → 驳回分诊映射到清单行。

**依赖与产物**：不发明签名材料、不把证书/机器路径提交进版本控制。要点：9568322 是"签名/Profile/设备信任不匹配"的一类症状而非单一原因；AGC 开放能力需要"已申请、已批准、**且在 Profile 中勾选**"三态齐全；商店政策变化快，references 是门的地图，现行要求以 AGC/官方文档为准。

#### harmony-test-triage

**用途**：发现、运行、缩小和诊断 ArkTS 单元/集成/Hypium UI 测试问题。

**何时触发**：测试失败、挂起、flaky、发现不了用例、需要设备才能跑、改代码后要回归。

> - "单元测试跑不起来"
> - "这个 UI 测试时好时坏"
> - "改完这块代码帮我跑一遍相关测试"

**工作流程**：用项目自己的测试配置与 Hvigor 任务图（跑 `tasks`/`taskTree` 发现命令，不硬编码别的版本的任务名）→ 复现最小失败用例 → 按失败分类学归类（发现/编译/环境/夹具/时序/断言/框架）→ 最小范围修根因（不为了变绿弱化有效断言）→ 窄用例重跑 + 所在套件 + 适度回归。flaky 判定需要同条件重复运行记录，不凭一次通过一次失败下结论；用确定性就绪条件替代加长 sleep。

**依赖与产物**：设备测试通过 harmony-debugger-agent 锁定单一目标。产物：发现的命令、失败分类、证据、改动、窄重跑与回归结果。

#### harmony-profiler-trace

**用途**：捕获、转换、检查、对比 DevEco Profiler 的 htrace/bytrace 性能证据。

**何时触发**：剖析启动、UI 冻结、滑动卡顿、CPU 高、慢交互，或性能审查需要 trace 实证。

> - "抓一段启动 trace 分析冷启动慢在哪"
> - "这是导出的 htrace 文件，帮我分析"

**工作流程**：每条 trace 只覆盖一个聚焦流程（明确起点、动作、停止条件）→ 记录版本、设备、构建模式、冷/热启动 → 构建并启动确切产物 → DevEco Profiler 抓取对应 lane → 导出 `.htrace`/SQLite 后先保留原始产物 → 用 `../skills/harmony-profiler-trace/scripts/analyze_htrace.py` 转换汇总（借助 DevEco 自带 `trace_streamer`）→ 把热点映射回应用自有代码 → 最小修复后同条件重抓对比。

**依赖与产物**：trace 捕获需在 DevEco Profiler 中手动进行（CodeGenie MCP 不提供捕获），Skill 会引导操作并从导出文件继续。噪声大的延迟结论要求至少 3 次可比运行，报告中位数与逐次值。

#### harmony-memory-leaks

**用途**：排查内存增长、ArkTS/原生对象泄漏、页面不释放、图片内存压力，产出前后对比的泄漏证据。

**何时触发**：内存随流程持续上涨、页面退出不回收、应用在内存压力下被杀、泄漏修复需要证明。

> - "反复进出这个页面内存一直涨"
> - "怀疑这个监听器泄漏了，帮我证实并修掉"

**工作流程**：先定义可疑对象的预期生命周期（进程/会话/页面/组件/请求）→ 稳定态抓基线快照 → 固定次数执行"创建-使用-释放"流程后回到同一稳定态 → 同模式抓 post 快照 → 归一化为 `type,count,shallow_size,retained_size` 后用 `../skills/harmony-memory-leaks/scripts/compare_memory_snapshots.py` 出增量报告 → 在 Profiler 中查增长最大的应用自有类型的引用链 → 修最小的持有边/清理遗漏/监听器/timer/native 句柄 → 重复相同流程验证该类型/路径的增量消失。

**依赖与产物**：快照在 DevEco Profiler 中捕获导出。证据标准严格："总内存变小"不算修复证明；只有增长而无引用链或可重复性证据时，结论写"疑似增长"而非"确认泄漏"。

## 7. 排障与 FAQ

### 7.1 MCP 拉取失败或超时

`npx -y @deveco-codegenie/mcp@1.1.11` 首次运行要从 npm registry 下载包。若卡住或失败：

- 检查网络与 npm registry 可达性；国内环境可配置镜像：`npm config set registry https://registry.npmmirror.com`；
- 手动预热一次：`npx -y @deveco-codegenie/mcp@1.1.11 --help`（下载完成后 Agent 再启动即走缓存）；
- 确认 Node/npm 可用：`node -v && npm -v`。

### 7.2 Skill 没有出现 / 没触发预期的 Skill

- 安装后问 "What skills are available?"，若不足 17 个：Claude Code 本地模式确认 `--plugin-dir` 路径正确并运行过 `/reload-plugins`；Codex 确认 marketplace 条目已启用且**新开了任务**；
- 提问太宽泛时可能路由到别的 Skill——用症状式描述（说"应用一打开就闪退"而不是"应用有点问题"），或直接点名 Skill；
- Codex 会把插件安装到以版本号命名的缓存目录，旧版结构校验脚本曾因此误判插件名不一致——当前 0.2.0 已修复，更新插件即可。

### 7.3 构建失败

这是预期的门控行为：Skill 会停在构建失败处并路由到 `arkts-error-fixes` 修复，而不是带病继续。常见环境侧原因：

- `DEVECO_SDK_HOME` / `JAVA_HOME` 未配置——Skill 会用 `detect_harmony_env.py` 从已安装的 DevEco Studio 解析，无需手动写入项目文件；
- SDK 版本与项目 `build-profile.json5` 声明不匹配——按提示对齐已安装 SDK；
- hvigor 任务名不存在——插件不猜任务名，会先跑 `hvigorw tasks` 检查，跟着它的结论走。

### 7.4 设备与模拟器

- **hdc 连不上真机**：检查 USB 调试授权；多设备时所有命令必须 `-t <设备号>`，Skill 在目标不明确时会先询问而不是随机选一台；
- **签名后安装报 install sign info inconsistent**：换过签名 key 导致，`devecocli run --uninstall` 或先卸载旧包再装；
- **模拟器 license / 镜像下载**：`devecocli emulator license accept` 需要交互式终端、镜像下载 30 分钟起——Skill 会把这些命令交给你手动执行，属预期行为；
- **权限弹窗、多数 Kit 在 Previewer 里不工作**：这是平台限制，需用模拟器或真机验证。

### 7.5 CodeGenie MCP 能力边界

以下能力 1.1.11 版 MCP 不提供，Skill 会自动走替代路径，无需报障：

| 缺失能力 | 替代路径 |
|---|---|
| 设备列表 | `devecocli device list` 或 hdc |
| 连续 hilog 流 | `devecocli log --follow` 或 `hdc -t <设备> hilog` |
| Profiler trace / 内存快照捕获 | DevEco Profiler 手动捕获导出，脚本接力分析 |
| 模拟器状态注入 | `devecocli emulator fold/rotate/geolocation/battery` |
| 实时画面镜像 | 截图 + HTML 画廊（harmony-runtime-preview） |

### 7.6 其他常见问题

**Q：没有连接任何设备能用吗？**

能。创建项目、语法/编译诊断、代码评审、重构、崩溃日志解析、trace/快照文件分析都不需要设备；需要运行时的步骤会明确标注"运行时验证待完成"。

**Q：会不会乱动我的设备或工程？**

Skill 有明确边界：不顺手卸载应用、清数据、重启设备；不覆盖非空目录；不把机器路径和签名材料写入版本控制；多目标时先问再动。

**Q：插件给出的上架/备案结论可靠吗？**

签名、提审、备案类 references 按官方范围收敛过，但商店与合规政策变化快——插件把它们当作"门的地图"，最终以 AGC 控制台与官方文档现行要求为准，Skill 本身也会这样提示。

## 8. 附录

### 版本信息

| 项 | 值 |
|---|---|
| 插件版本 | 0.2.0 |
| CodeGenie MCP | `@deveco-codegenie/mcp@1.1.11`（固定；npm stable，2026-07 评审） |
| 验证环境 | DevEco Studio 26 / HarmonyOS API 26 Beta1 |
| 可选 devecocli | `@deveco/deveco-cli`（评审时为 1.0.0，以安装版 `--help` 为准） |
| 许可证 | MIT |

### 来源与许可证

插件的结构、工具链与知识内容改编自多个开源项目，完整来源表见 [README.md](../README.md#参考的开源项目)，许可证细节见 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) 与 [upstreams.json](../upstreams.json)。

本插件是独立社区项目，并非华为或 OpenAI 官方产品。
