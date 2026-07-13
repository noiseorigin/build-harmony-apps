# iOS 应用迁移 HarmonyOS 指南

面向 iOS 开发者：如何用 Build Harmony Apps 插件把一个 Swift/SwiftUI/UIKit 应用迁移到 HarmonyOS（Stage 模型 + ArkTS/ArkUI），按阶段给出对应 Skill、示例提问和完成标准。插件本身不含 iOS 专属 Skill，本指南补充了迁移所需的概念映射、依赖替换、数据迁移等内容，并标注了哪些是插件能力、哪些是指南补充。

基础使用（安装、Skill 触发机制、工具链）见 [USAGE.md](USAGE.md)，先读它再读本文。

## 目录

- [1. 迁移前提与心智模型](#1-迁移前提与心智模型)
- [2. 阶段总览与 Skill 映射](#2-阶段总览与-skill-映射)
- [3. 阶段 0：评估与盘点](#3-阶段-0评估与盘点)
- [4. 阶段 1：工程与应用骨架](#4-阶段-1工程与应用骨架)
- [5. 阶段 2：语言与业务逻辑](#5-阶段-2语言与业务逻辑)
- [6. 阶段 3：UI 迁移](#6-阶段-3ui-迁移)
- [7. 阶段 4：系统能力迁移](#7-阶段-4系统能力迁移)
- [8. 阶段 5：数据与账号迁移](#8-阶段-5数据与账号迁移)
- [9. 阶段 6：测试、性能与调试](#9-阶段-6测试性能与调试)
- [10. 阶段 7：签名与上架](#10-阶段-7签名与上架)
- [11. 端到端最小验证路径](#11-端到端最小验证路径)
- [12. 迁移常见坑速查](#12-迁移常见坑速查)

---

## 1. 迁移前提与心智模型

**没有自动转换器。** iOS → HarmonyOS 是按目标平台习惯重写，不是转译。能平移的是：产品逻辑与信息架构、领域模型设计、服务端契约、C/C++ 核心库（经 NAPI 复用）、测试用例设计。需要重写的是：全部 Swift/Objective-C 代码、全部 UI、系统能力接入。

好消息是两个平台的形态高度相似，iOS 经验大部分可以直接换算：

| 维度 | iOS | HarmonyOS | 相似度 |
|---|---|---|---|
| 语言 | Swift | ArkTS（TypeScript 严格超集，静态类型） | 中：都是现代静态类型语言 |
| UI 框架 | SwiftUI（声明式） | ArkUI（声明式） | 高：结构几乎同构 |
| 原生扩展 | C/C++/ObjC 直接混编 | C/C++ 经 NAPI | 中 |
| IDE | Xcode | DevEco Studio | 高 |
| 构建 | xcodebuild | Hvigor（`hvigorw`） | — |
| 包管理 | SPM / CocoaPods | ohpm（`oh-package.json5`） | 高 |
| 设备调试 | devicectl / 模拟器 | HDC / DevEco 模拟器 | 高 |
| 测试 | XCTest / XCUITest | Hypium（单元 + UiTest） | 高 |
| 分发 | App Store Connect | AppGallery Connect（AGC） | 高：证书/Profile 概念直接对应 |

UIKit 时代的命令式经验也能用，但 ArkUI 只有声明式一条路——从 SwiftUI 出发映射最顺。

**版本基线**：生产默认 **API 24（HarmonyOS 6.1.1 Release）**；API 26 是开发者预览（Beta1），不要按 Beta 能力做上线承诺。细节见 [platform-baseline.md](../skills/deveco-create-project/references/platform-baseline.md)。

## 2. 阶段总览与 Skill 映射

| 阶段 | 内容 | 主用 Skill | 覆盖情况 |
|---|---|---|---|
| 0 评估与盘点 | 功能/能力/依赖/数据清单，基线决策 | —（Agent 通用能力） | 指南补充（[§3](#3-阶段-0评估与盘点)） |
| 1 工程与骨架 | 脚手架、外壳、导航骨架 | deveco-create-project、arkui-ui-patterns | 已覆盖 + 结构/生命周期映射表 |
| 2 语言与逻辑 | Swift→ArkTS、C/C++ 复用 | arkts-grammar-standards、arkts-error-fixes | 部分覆盖（TS→ArkTS 有 reference；Swift 映射为指南补充） |
| 3 UI 迁移 | 页面重写、设计语言、多设备 | arkui-ui-patterns、arkui-native-design、arkui-multidevice、harmony-runtime-preview | 已覆盖 + SwiftUI/UIKit 映射表 |
| 4 系统能力 | Kit 接入、权限、Widget/Siri 等 | harmony-kit-integration、harmony-app-intents | 已覆盖 + iOS framework→Kit 映射表 |
| 5 数据与账号 | 存储 API、用户数据跨端迁移 | harmony-kit-integration（存储簇） | API 已覆盖；跨端迁移策略为指南补充 |
| 6 测试与性能 | 测试迁移、性能基线 | harmony-test-triage、arkui-performance-audit、harmony-profiler-trace、harmony-memory-leaks | 已覆盖 |
| 7 发布 | 签名、提审、备案、IAP | harmony-release-compliance | 已覆盖 + 签名概念对照表 |
| 全程 | 构建/启动/取证/修错 | harmony-debugger-agent、arkts-runtime-fix | 已覆盖 |

**关键实操技巧：把 iOS 工程放进同一工作区。** Agent 能直接读 Swift 源码，把它当迁移蓝本：

```text
workspace/
├── MyApp-iOS/        # 原 Xcode 工程（只读参照）
└── MyApp-Harmony/    # 新 DevEco 工程（迁移目标）
```

之后的提问都可以是"照着 `../MyApp-iOS/Features/Login/LoginView.swift` 用 ArkUI 重写登录页"——比口头描述需求准确得多。这是通用 Agent 能力，不依赖任何 Skill。

**迁移顺序采用"骨架先行 + 垂直切片"**：先让一条最小用户路径端到端跑通（阶段 0–1），再按功能逐条迁移（每条都走"实现 → 构建 → 运行取证"），最后统一处理测试、性能、发布。不要横向地"先转完所有模型层再转所有 UI"——插件的证据门控在垂直切片下才能发挥作用（每个切片都可构建、可运行、可截图）。

## 3. 阶段 0：评估与盘点

插件没有专门的评估 Skill，用 Agent 通用能力扫描 iOS 工程即可。示例提问：

> 读一下 ../MyApp-iOS，输出迁移盘点：1) 页面清单和导航结构；2) 用到的系统 framework 和 entitlements（从 project.pbxproj / Info.plist / *.entitlements 提取）；3) SPM/CocoaPods 依赖列表；4) 本地存储用了什么（CoreData/UserDefaults/Keychain/文件）；5) 有没有 C/C++/纯逻辑模块可以复用

盘点结果对照后续章节的映射表，形成四张清单：

1. **功能清单** → 排迁移优先级，选出首个垂直切片（通常是"启动 → 登录/主列表 → 详情"）；
2. **系统能力清单** → 逐项查 [§7 的 framework→Kit 映射表](#71-ios-framework--harmonyos-kit-映射)，标出三类：有对应、有对应但有前置（AGC/资质/地域）、无对应（要产品决策）；
3. **依赖清单** → 逐项查 [§5.4](#54-第三方依赖替换指南补充)，分为"官方 Kit 内置""ohpm 有移植版""需要自研/降级"；
4. **数据清单** → 进入 [§8](#8-阶段-5数据与账号迁移) 的迁移策略决策。

**基线决策**：除非明确只面向预览用户，`compileSdkVersion`/`compatibleSdkVersion` 选 API 24（生产 Release 基线）。这个决定影响后面每个 Kit 和 ArkUI API 的可用性判断。

## 4. 阶段 1：工程与应用骨架

### 4.1 创建工程

> 创建一个叫 MyApp 的鸿蒙项目，包名 com.example.myapp

`deveco-create-project` 会用官方模板/内置模板生成 Stage 模型工程并完成一次干净构建。工程结构与 Xcode 概念对照（结构详情见 [stage-model.md](../skills/deveco-create-project/references/stage-model.md)）：

| Xcode | DevEco | 说明 |
|---|---|---|
| `.xcodeproj` / project settings | 项目级 `build-profile.json5` | products、签名配置、SDK 版本 |
| target | module（entry/feature）+ product | 主应用是 entry 模块 |
| `Info.plist` | `module.json5` + `AppScope/app.json5` | 权限、Ability、设备类型在 module.json5 |
| Bundle Identifier | `bundleName`（app.json5） | |
| `.entitlements` | 签名 Profile 中的能力勾选 | 见 [§10](#10-阶段-7签名与上架) |
| SPM `Package.swift` / Podfile | `oh-package.json5` | ohpm 管理 |
| Asset Catalog（.xcassets） | `resources/base/media` + `element` | 引用方式 `$r('app.media.x')` |
| `InfoPlist.strings` 本地化 | `resources/<locale>/element/string.json` | |
| framework/静态库产物 | HAR（静态）/ HSP（动态共享） | |

### 4.2 应用外壳与生命周期

iOS 的 AppDelegate/SceneDelegate 职责由三层承接：AbilityStage（模块级）、UIAbility（任务级，≈ Scene）、WindowStage（窗口）：

| iOS | HarmonyOS | 触发时机 |
|---|---|---|
| `application(_:didFinishLaunchingWithOptions:)` | `AbilityStage.onCreate` / `UIAbility.onCreate` | 冷启动 |
| `scene(_:willConnectTo:)` + 设 rootViewController | `onWindowStageCreate` + `windowStage.loadContent('pages/Index')` | 窗口就绪 |
| `sceneDidBecomeActive` | `onForeground` | 回前台 |
| `sceneDidEnterBackground` | `onBackground` | 进后台 |
| `applicationWillTerminate` | `onDestroy` | 销毁 |
| `application(_:open:)` / universal link 回调 | `onCreate`/`onNewWant` 里的 `Want` 参数 | 外部拉起 |
| singleton 场景再次拉起 | `onNewWant`（代替 `onCreate`） | launchType: singleton |

冷启动顺序：`onCreate → onWindowStageCreate → onForeground`。

### 4.3 导航骨架

> 照着 ../MyApp-iOS 的 Tab 结构搭应用骨架：底部 Tabs + 每个 Tab 一个 Navigation 栈，页面先放占位内容，能构建、能启动、能截图

由 `arkui-ui-patterns` 承接。对应关系：`TabView`→`Tabs`+`TabContent`；`NavigationStack`+`path`→`Navigation`+`NavPathStack`（API 23 起可绑定路由栈、以 `NavDestination` 为首页）；`NavigationLink`/`push`→`pathStack.pushPathByName('Detail', param)`。

**阶段完成标准**：骨架工程构建成功 + 启动后有 UI 树/截图证据 + Tab 与页面栈切换正常。这就是后续所有切片的宿主。

## 5. 阶段 2：语言与业务逻辑

### 5.1 Swift → ArkTS 核心映射

以下映射为指南补充的经验对照，最终以已安装编译器与官方文档为准（`arkts-grammar-standards` 会核对现行规范；装了 devecocli 可用 `devecocli docs search` 本地查证）：

| Swift | ArkTS | 注意 |
|---|---|---|
| `T?`、`if let` / `guard let` | `T \| undefined` + 显式判空收窄 | ArkTS 区分 `null`/`undefined`，系统 API 多用 `undefined` |
| `??`、`?.` | `??`、`?.` | 相同 |
| `struct`（值语义） | 无值类型；只有 `class`/`interface`（引用） | 共享可变状态的 bug 源；需要拷贝语义时显式 clone |
| `protocol` | `interface` | protocol extension 的默认实现 → 抽象类或组合 |
| `extension` | 无 | 工具函数或子类 |
| `enum`（关联值） | enum 仅常量成员 | 关联值场景改用类层次或带字面量标签的联合类型 |
| `Codable` | 无反射式 JSON 映射 | 见 [§5.2](#52-codable-的替代) |
| 泛型 / `where` | 泛型 / `extends` 约束 | 相近 |
| 闭包 / `@escaping` | 箭头函数 | 无逃逸概念；注意 `this` 绑定 |
| `guard` | 提前 `return` | |
| `deinit` | 无析构 | 释放动作挂到生命周期回调；`on()` 必须配对 `off()` |
| 字符串插值 `\(x)` | 模板字符串 `${x}` | |
| `KeyPath`、反射、动态派发技巧 | 无 | ArkTS 禁止运行时改对象形状——这是与 TS 最大的差异 |

**并发模型**（差异最大，值得单独记）：

| iOS | HarmonyOS | 说明 |
|---|---|---|
| `DispatchQueue.main.async` | 通常不需要 | ArkTS 是单线程事件循环，async 回调本来就在 UI 线程；更新 @State 即刷新 |
| `DispatchQueue.global().async` / `Task.detached` | `TaskPool` + `@Concurrent` 函数 | 短平快的 CPU 任务 |
| `Thread` / `OperationQueue` 长驻 | `Worker` | 独立线程，消息通信 |
| `actor` / `Sendable` | `Sendable` 类（`@Sendable`） | 跨并发域默认拷贝数据，共享需 Sendable；约束比 Swift 更严，见 [restrictions.md](../skills/arkts-grammar-standards/references/restrictions.md) |
| `async/await` | `async/await` | 语法相同 |
| `NotificationCenter` | `Emitter` / UIAbility 的 `EventHub` | |
| Combine / AsyncSequence | 无直接等价 | 状态装饰器 + 回调/Emitter 组合实现 |

### 5.2 Codable 的替代

ArkTS 禁止运行时反射，`JSON.parse` 的结果不能直接断言成业务类型完事——`arkts-error-fixes` 明确把"类型断言不是修复"列为规则。可靠做法：定义 `interface` 描述载荷 + 写显式的 `fromJson` 工厂（逐字段校验赋值），或让 Agent 按服务端契约生成这层映射代码：

> 这是 iOS 端的 User.swift（Codable）和一份响应样例 JSON，给 ArkTS 生成对应的 interface + 显式解析函数，字段缺失时给出明确错误

### 5.3 C/C++ 核心复用（指南补充）

如果 iOS 工程有纯 C/C++ 核心（算法、协议栈、加密），这是迁移里最大的复用机会：HarmonyOS 通过 NAPI（Node-API）接 C/C++，DevEco 用 CMake 构建 native 模块。要点：

- 新建 native 模块时让 DevEco Studio 的向导生成（Native C++ 模板），不要手搓 CMake 接线；插件的 `deveco-create-project` 内置模板只覆盖纯 ArkTS 最小工程，含 C++ 的骨架属于它明确交回官方向导的场景；
- 桥接层薄封装：C++ 侧暴露稳定 C 接口，NAPI 层只做类型转换，ArkTS 侧包一层 typed service；
- 诊断可用 CodeGenie MCP 的 `check_cpp_files`（原生源码聚焦诊断），构建失败照常走 `arkts-error-fixes`（其分类里含"原生桥"一类）；
- ObjC/Swift 专属依赖（Foundation 类型、GCD）要先从核心库剥离。

### 5.4 第三方依赖替换（指南补充）

在 [ohpm 中心仓](https://ohpm.openharmony.cn) 按名字搜移植版。常见对应（装前以 ohpm 实际收录为准）：

| iOS 常用 | HarmonyOS 替代 |
|---|---|
| Alamofire / URLSession 封装 | 官方 `NetworkKit`（http/webSocket）；社区 `@ohos/axios` |
| Kingfisher / SDWebImage | `Image` 组件内置网络加载与缓存（基础场景够用）；高级需求查 ohpm（如 ImageKnife） |
| Lottie | `@ohos/lottie` |
| MMKV | `@ohos/mmkv`；轻量场景直接用官方 `preferences` |
| KeychainAccess | 官方 `AssetStoreKit`（关键资产） |
| SwiftLint | DevEco 内置 codelinter（ArkTS linter） |
| Firebase 全家桶 | 无整套等价；按能力拆分：推送→Push Kit、分析/崩溃→查各厂商 HarmonyOS SDK 或 AGC 服务 |

原则：**官方 Kit 能覆盖就不引第三方**——`harmony-kit-integration` 的路由第一步就是"解析到官方 Kit"。

### 5.5 工作法

TS→ArkTS 的机械差异（解构、动态属性、结构化对象）有现成参考 [ts-diff.md](../skills/arkts-grammar-standards/references/ts-diff.md)，其中的纪律同样适用于 Swift 迁移：**先证明一个有代表性的连通切片，不要机械转译整个代码库**。每迁一个模块：

> 把 ../MyApp-iOS/Core/OrderService.swift 迁成 ArkTS service，放 entry/src/main/ets/services/，保持接口语义，写完跑一次 ETS 检查和模块构建

编译错误交给 `arkts-error-fixes`（它会用 `check_ets_files` 做免构建的聚焦诊断），语法疑问交给 `arkts-grammar-standards`。

## 6. 阶段 3：UI 迁移

### 6.1 SwiftUI → ArkUI 组件映射

指南补充的经验对照；每个组件的当前用法以 `arkui-ui-patterns` 的组件索引和官方文档为准：

| SwiftUI | ArkUI | 备注 |
|---|---|---|
| `VStack` / `HStack` / `ZStack` | `Column` / `Row` / `Stack` | |
| `Spacer` / `Divider` | `Blank` / `Divider` | |
| `Text` / `Image` / `Button` | `Text` / `Image` / `Button` | |
| `AsyncImage` | `Image(url)` + 占位/错误态 | 内置网络加载 |
| `SF Symbols` | `SymbolGlyph` | HarmonyOS 符号库 |
| `TextField` / `SecureField` | `TextInput` / `TextInput` + `type(InputType.Password)` | 单行输入组件是 TextInput，无 TextField |
| `TextEditor` | `TextArea` | |
| `Toggle` / `Slider` / `Stepper` | `Toggle` / `Slider` / `Counter` | |
| `Picker` / `DatePicker` | `Select`/`TextPicker` / `DatePicker` | |
| `ProgressView` | `Progress` / `LoadingProgress` | |
| `List` + `ForEach` | `List` + `ListItem` + `ForEach`/`LazyForEach` | 大列表必须 LazyForEach + 稳定 key |
| `LazyVGrid` / `LazyHGrid` | `Grid`/`GridItem`，瀑布流用 `WaterFlow` | |
| `ScrollView` | `Scroll`（配 `Scroller` 控制器） | |
| `TabView` | `Tabs` + `TabContent` | |
| `TabView(.page)` | `Swiper` | |
| `NavigationStack` / `NavigationLink` | `Navigation` + `NavPathStack` / `pushPathByName` | |
| `.sheet` | `bindSheet`（半模态） | |
| `.fullScreenCover` | `bindContentCover` | |
| `.alert` / `confirmationDialog` | `AlertDialog` / `ActionSheet`、`promptAction` | |
| `.contextMenu` / `Menu` | `bindContextMenu` / `bindMenu` | |
| `.searchable` | `Search` 组件 | |
| `.refreshable` | `Refresh` 组件 | |
| `.onAppear` / `.onDisappear` | `aboutToAppear`/`aboutToDisappear`（组件）、`onPageShow`/`onPageHide`（页面） | |
| `withAnimation` / `.animation` | `animateTo` / `.animation` | |
| `.transition` / `matchedGeometryEffect` | `transition` / `geometryTransition` | |
| `GeometryReader` | `onAreaChange` 回调、布局约束 | 没有等价的"读几何再布局"；优先约束式布局 |
| view modifier 链 | 属性方法链 `.width().padding().onClick()` | 心智相同 |
| `UIViewRepresentable` | 无（没有第二套 UI 可包） | C++ 自绘走 XComponent |

UIKit 出身的话：`UITableView`→`List`+`LazyForEach`、`UICollectionView`→`Grid`/`WaterFlow`、`UIPageViewController`→`Swiper`、`WKWebView`→`Web`（ArkWeb）、`UIGestureRecognizer`→`gesture(TapGesture()/PanGesture()/…)`、Auto Layout→线性布局/`Flex`/`RelativeContainer`。

### 6.2 状态管理映射

ArkUI 有 V1/V2 两代状态管理，**新迁移的代码统一选一代**（项目基线支持 V2 就直接 V2），不要混用——这是 `arkui-ui-patterns` 的硬规则：

| SwiftUI | ArkUI V1 | ArkUI V2 |
|---|---|---|
| `@State` | `@State` | `@Local` |
| `@Binding` | `@Link` | `@Param` + `@Event` |
| `@StateObject` / `@ObservedObject` | `@Observed` 类 + `@ObjectLink` | `@ObservedV2` 类 + `@Trace` 字段 |
| `@EnvironmentObject` | `@Provide` / `@Consume` | `@Provider` / `@Consumer` |
| `@AppStorage` | `AppStorage` / `PersistentStorage` | 同左 |
| `onChange(of:)` | `@Watch` | `@Monitor` |
| 计算属性驱动视图 | getter | `@Computed` |

拿不准某个页面该怎么建状态，直接问（触发 `arkui-ui-patterns`）：

> 这个页面有筛选条件、分页列表和多选编辑态，照 V2 状态管理该怎么划分状态归属？

### 6.3 设计语言与多设备

**不要复刻 iOS 视觉。** `arkui-native-design` 的触发场景之一就是"替换 iOS 感的界面"。迁移时保留品牌（色彩/图形资产），把系统行为交给平台：返回手势与导航条、系统栏与避让区、弹窗与半模态形态、深色模式、动效节奏。示例提问：

> 这个页面是从 iOS 搬过来的，按 HarmonyOS 设计规范评审一下哪些地方还是 iOS 习惯，给出改造清单

iOS 只需适配 iPhone/iPad，HarmonyOS 多出折叠屏与 2in1。至少在骨架期就决定 `deviceTypes`，核心页面用 `arkui-multidevice` 过一遍：

> 首页在折叠屏展开态和平板横屏下应该怎么排？给出断点方案并渲染对比截图

**每个页面的完成标准**（由 `harmony-runtime-preview` 取证）：构建通过 + 渲染截图 + 与 iOS 原版截图对比确认信息层级一致（视觉允许平台化差异）。

## 7. 阶段 4：系统能力迁移

### 7.1 iOS framework → HarmonyOS Kit 映射

映射目标与 import key 与插件的 [Kit 目录](../skills/harmony-kit-integration/references/kits-index.md) 对齐；接入一律交给 `harmony-kit-integration`（一次一个能力，真机取证）。⚠ 标注硬前置：

| iOS | HarmonyOS Kit | 前置/差异 |
|---|---|---|
| AVFoundation（拍摄） | `CameraKit`；免权限场景用 CameraPicker | CameraPicker 不要相机权限，优先用 |
| AVPlayer / AVAudioSession | `MediaKit`（AVPlayer）/ `AudioKit`（焦点/流） | 名字都叫 AVPlayer，概念平移 |
| 后台音频 + 锁屏控制（MPNowPlayingInfoCenter） | `AVSessionKit` | ⚠ 后台播放**必须**接 AVSession，否则系统静音——iOS 只需 background mode，这里是强制的会话接入 |
| PhotoKit / PHPicker | `MediaLibraryKit`（photoAccessHelper picker） | 旧模块的 PhotoViewPicker 已废弃 |
| AVCaptureMetadataOutput（扫码） | `ScanKit` | 默认 UI 免权限 |
| Vision（OCR/人像分割） | `CoreVisionKit` | ⚠ 仅中国大陆、无模拟器支持 |
| Speech / AVSpeechSynthesizer | `CoreSpeechKit` | ASR 输入要求 PCM 16kHz 单声道 16bit |
| CoreLocation | `LocationKit` | user_grant 权限 |
| MapKit | `MapKit` | ⚠ 需 AGC 配置 + 定位权限 |
| WeatherKit | `WeatherServiceKit` | |
| URLSession | `NetworkKit`（http/webSocket/connection） | |
| 后台 URLSession | `BasicServicesKit` 的 `request.agent` | |
| UserNotifications（本地） | `NotificationKit` | |
| APNs 远程推送 | `PushKit` | ⚠ AGC 必须先开通 Push 服务；token 模式，无 .p8 证书概念 |
| Sign in with Apple | `AccountKit`（华为账号一键登录） | ⚠ 需 AGC client_id |
| Apple Pay（实物） | `PaymentKit` | ⚠ 仅中国大陆 |
| StoreKit IAP（虚拟商品） | IAP Kit | 走发布 Skill 的 [IAP 参考](../skills/harmony-release-compliance/references/iap-integration.md)，审核强制程度与 App Store 同级 |
| WidgetKit | `FormKit`（服务卡片） | ⚠ 卡片跑在受限沙箱进程，可用 ArkUI 子集受限；刷新机制与 Timeline 不同 |
| App Clips | 元服务（atomic service） | 约束见 [atomic-service.md](../skills/harmony-kit-integration/references/atomic-service.md)；有包体与快照专项审核 |
| SiriKit / App Intents | `IntentsKit`（小艺） | 用 `harmony-app-intents`；⚠ 有域开放与验收流程，编译通过≠系统入口可用 |
| Universal Links | App Linking | 同样要域名校验 |
| UIActivityViewController | `ShareKit` | |
| Handoff | `AbilityKit` 的 `onContinue`（跨设备接续） | 仅鸿蒙设备间 |
| BGTaskScheduler / beginBackgroundTask | `BackgroundTasksKit`（短时/长时/延迟任务） | ⚠ 后台执行从不隐式，必须按类型申请；见 [background-tasks.md](../skills/harmony-kit-integration/references/background-tasks.md) |
| Keychain | `AssetStoreKit` | 存 token/密码；别放 preferences |
| CryptoKit / CommonCrypto | `CryptoArchitectureKit` | |
| CoreBluetooth / CoreNFC | `ConnectivityKit` | |
| CoreMotion | Sensor Service Kit | 具体查官方目录 |
| WKWebView | `ArkWeb`（Web 组件） | JS bridge/cookie/拦截见 [arkweb.md](../skills/harmony-kit-integration/references/arkweb.md) |
| HealthKit | Health Service Kit | ⚠ 需申请资质 |
| iCloud / CloudKit | 无直接等价 | 见 [§8.2](#82-用户数据跨端迁移策略指南补充) |
| CallKit / CarPlay | 无一般第三方等价 | 产品层面重新评估 |

### 7.2 权限模型对照

| iOS | HarmonyOS |
|---|---|
| Info.plist 写 usage description，系统首次调用时自动弹窗 | `module.json5` 声明（user_grant 权限必须带 `reason` + `usedScene`）→ 运行时 `checkAccessToken` → `requestPermissionsFromUser` 显式触发弹窗 → 拒绝后引导设置页 |
| 拒绝后再调用不再弹窗 | 同样不会重复弹；**再弹已拒绝的框会被审核打回**，必须走设置页兜底 |

完整三步流程在 [permissions.md](../skills/harmony-kit-integration/references/permissions.md)，`harmony-kit-integration` 接能力时会自动带上。经验法则和 iOS 一致：能用免权限系统面（CameraPicker、Scan 默认 UI、各类 picker）就不要申请敏感权限。

### 7.3 AGC 前置清单

对应 App Store Connect 侧配置的部分，开工前先在 AGC 控制台完成，否则客户端调试是空转（`harmony-kit-integration` 遇到会直接指出）：应用创建与包名一致、Push 服务开通、Account Kit 的 client_id、Map/Payment 等能力开通、IAP 商品配置。

## 8. 阶段 5：数据与账号迁移

### 8.1 存储 API 对照

| iOS | HarmonyOS | 说明 |
|---|---|---|
| UserDefaults | `preferences`（ArkData） | KV，轻量 |
| CoreData / SQLite / GRDB | `relationalStore`（ArkData） | 关系库；无 CoreData 式 ORM 层，schema 与查询手写或封装 |
| Keychain | `AssetStoreKit` | 凭据类 |
| FileManager | `CoreFileKit`（fileIo、picker） | 沙箱路径模型与 iOS 相似 |

接入走 `harmony-kit-integration` 的[存储簇参考](../skills/harmony-kit-integration/references/data-persistence.md)。CoreData 迁移建议：先把 iOS 侧的实体图导出成中立的 schema 描述（让 Agent 从 `.xcdatamodeld` 生成建表 SQL 与 ArkTS DAO），再迁数据访问层。

### 8.2 用户数据跨端迁移策略（指南补充）

**两个生态之间没有设备直迁通道**（没有"从 iPhone 恢复"）。老用户换机时的数据延续只能应用层自己解决，按可靠性排序：

1. **账号 + 服务端同步**（推荐）：数据本来在服务端的，登录即迁移完成。iOS 端若有仅本地的数据（纯 UserDefaults/CoreData），要在 iOS 版本里**提前发版**加上传/同步能力——这是整个迁移里唯一需要动 iOS 代码的地方，越早发越好；
2. **导出/导入**：iOS 端导出加密文件（iCloud Drive/AirDrop/分享），鸿蒙端用 picker 导入解析；适合无账号体系的工具类应用；
3. **扫码接力**：小数据量（配置、令牌）用 iOS 端生成二维码、鸿蒙端 `ScanKit` 扫入。

账号体系本身：Sign in with Apple 的账号在鸿蒙端不可用，需要产品决策——常见做法是服务端账号支持多 IdP 绑定（Apple ID 与华为账号绑到同一账号），或提供手机号作为跨端锚点。

## 9. 阶段 6：测试、性能与调试

| iOS | HarmonyOS | Skill |
|---|---|---|
| XCTest 单元测试 | Hypium（`@ohos/hypium`，ohosTest 目录） | harmony-test-triage |
| XCUITest | Hypium UiTest；轻量场景用插件的 `verify_ui`（自然语言断言 + 截图/日志留证） | harmony-test-triage / harmony-debugger-agent |
| Instruments Time Profiler | DevEco Profiler CPU/启动 lane | harmony-profiler-trace |
| Instruments Allocations / Leaks | DevEco Profiler 内存快照 + 前后对比 | harmony-memory-leaks |
| Core Animation FPS | Profiler 帧率 lane；先做代码级审查 | arkui-performance-audit |

迁移用例设计可平移：让 Agent 照 iOS 测试文件生成 Hypium 版本（"照 OrderServiceTests.swift 给 ArkTS 的 OrderService 写 Hypium 用例"）。**性能要重新测**：拿 iOS 端指标当对照预期而不是结论，两平台渲染管线不同，逐屏在真机/模拟器上建立自己的基线（先 `arkui-performance-audit` 代码审查，量化结论走 trace）。

日常调试循环全程由 `harmony-debugger-agent` 承担（构建/启动/UI 驱动/hilog），运行时崩溃走 `arkts-runtime-fix`（faultlogger ≈ iOS 的 .ips 崩溃报告，有内置解析脚本）。

## 10. 阶段 7：签名与上架

概念几乎一一对应，iOS 发布经验大幅折价复用（全流程由 `harmony-release-compliance` 按"门"推进）：

| App Store | AppGallery | 差异 |
|---|---|---|
| Apple Developer Program | AGC 开发者账号（实名认证） | |
| 开发/发布证书（.p12） | 证书（同样 .p12/CSR 流程） | 概念相同 |
| Provisioning Profile | Profile（.p7b，含设备与能力） | 真机调试同样要注册设备 |
| Entitlements | Profile 能力勾选 | ⚠ 开放能力要"已申请、已批准、**且已勾选**"三态齐全，批准了没勾选会静默失败 |
| TestFlight | AGC 开放式测试/邀请测试 | |
| App Review | AGC 审核 | 驳回分诊：把审核意见原文给 Agent |
| 出口合规/隐私标签 | 隐私政策托管 + 能力声明清单 | |
| 中国区上架 ICP 备案 | APP 备案/ICP 备案按实际业务判断 | 在 App Store 中国区上过架的话对备案不陌生；插件明确**不把备案当无条件通用规则**，按 [filing-icp.md](../skills/harmony-release-compliance/references/filing-icp.md) 判定 |
| Build number 递增 | `versionCode` 严格递增 | 被拒后重传必须递增 |

迁移特有注意：签名报错 9568322 是"证书/Profile/设备信任不匹配"一类症状（对照 iOS 的 provisioning 报错家族）；虚拟商品**必须**走 IAP Kit，规则强度与 App Store 的 IAP 强制一致，别试图用网页支付绕过。

## 11. 端到端最小验证路径

从零到"第一条用户路径在鸿蒙上跑通"的提问序列，可直接照抄（每步末尾是该步的完成证据）：

1. `创建一个叫 MyApp 的鸿蒙项目，包名 com.example.myapp` → 脚手架 JSON `verified: true` + 首次构建成功
2. `读 ../MyApp-iOS 输出迁移盘点（页面/能力/依赖/存储四张清单）` → 盘点文档
3. `照 iOS 工程的 Tab 结构搭骨架：Tabs + Navigation，空页面占位，构建启动截图` → BUILD SUCCESSFUL + 启动截图
4. `迁移 ../MyApp-iOS/.../LoginView.swift 和它的 ViewModel：ArkUI 页面 + ArkTS service，V2 状态管理` → 构建成功
5. `启动应用，输入测试账号走通登录，用 verify_ui 断言进入首页` → verification id + 截图 + 日志
6. `按 HarmonyOS 设计规范评审登录页和首页，改掉 iOS 习惯` → 评审清单 + 修改后对比截图
7. 之后按功能清单逐条重复 4–6，Kit 能力按 [§7](#7-阶段-4系统能力迁移) 接入，每个 Kit 真机取证

**本指南编写时的实测记录**（2026-07，macOS + DevEco Studio 26.0.0 Beta1，hvigor 6.26.1，未连接设备）：第 1 步实际执行通过——内置模板脚手架 `verified: true`（API 26 Beta1，SDK 自动探测），CodeGenie MCP `init_project_path` + `build_project entry@default` 构建 `BUILD SUCCESSFUL`（约 3 秒，未配置签名时跳过 SignHap 属预期）。未连接设备时启动/UI 步骤按门控规则标注"运行时验证待完成"，与 [USAGE.md](USAGE.md) 描述一致。

## 12. 迁移常见坑速查

- **机械整库转译**：先跑通一个连通切片再铺量（ts-diff 纪律）；横向批量转出来的代码没有任何一层能构建取证。
- **把 iOS 视觉当规范**：返回手势、弹窗形态、导航条习惯都要平台化，`arkui-native-design` 专治此项。
- **struct 值语义思维**：ArkTS 全是引用语义，iOS 里安全的"复制一份改改"在这里是共享可变状态 bug。
- **JSON.parse 后直接 as 断言**：没有 Codable，不写显式解析层迟早在运行时爆——而且"类型断言不是修复"是 `arkts-error-fixes` 的红线。
- **V1/V2 装饰器混用**：迁移新代码统一一代；接手混合代码库先看 [v1-v2-boundary.md](../skills/arkui-view-refactor/references/v1-v2-boundary.md)。
- **deinit 思维缺位**：没有析构器；`on()`/`off()`、`init`/`release` 必须在生命周期回调里手动配对，不然就是 `harmony-memory-leaks` 的案源。
- **以为编译通过 = 能力可用**：AGC 前置、权限、地域限制、真机专属能力（Intents、部分 AI Kit）都只有设备证据算数。
- **后台执行当免费午餐**：iOS 勾 background mode 的心智不适用；每类后台工作要申请对应任务类型，后台音频还要 AVSession。
- **在 Previewer 里验证 Kit**：权限弹窗和多数 Kit 在 Previewer 不工作，用模拟器/真机。
- **按 Beta 能力做承诺**：生产基线 API 24；API 26 Beta 的新组件/行为要标注 preview 并给 Release 替代。
- **iOS 端忘了发"数据出口"版本**：账号/导出能力要在迁移完成前提前上到 iOS 线上版本，见 [§8.2](#82-用户数据跨端迁移策略指南补充)。
