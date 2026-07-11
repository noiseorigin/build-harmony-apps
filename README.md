# Build Harmony Apps

面向 Codex 的 HarmonyOS 开发插件，参考 OpenAI `Build iOS Apps` 的任务型结构，并优先复用华为 DevEco CodeGenie 官方能力。

## 能力

- 构建、启动、UI 树、交互、截图与日志调试
- ArkUI 原生设计、组件模式、性能审查、重构与多设备适配
- DevEco Profiler trace 和内存快照分析
- HarmonyOS Intents Kit、Hypium 测试分诊
- ArkTS 项目创建、语法、编译错误与运行崩溃处理

插件包含 15 个独立 Skill，并固定使用：

```text
@deveco-codegenie/mcp@1.1.11
```

## 安装

将仓库放入个人插件目录：

```bash
git clone https://github.com/noiseorigin/build-harmony-apps.git ~/plugins/build-harmony-apps
```

在 `~/.agents/plugins/marketplace.json` 中添加本地插件条目，并启用 `build-harmony-apps@personal`。重新打开 Codex 任务后生效。

## 验证

```bash
python3 scripts/validate_bundle.py
python3 -m unittest discover -s tests -v
python3 scripts/smoke_codegenie_mcp.py
```

已在 DevEco Studio 26 / HarmonyOS API 26 Beta1 环境验证 ArkTS 编译和 unsigned HAP 打包。

## 说明

这是独立社区项目，并非华为或 OpenAI 官方产品。上游来源与许可证见 `THIRD_PARTY_NOTICES.md` 和 `upstreams.json`。
