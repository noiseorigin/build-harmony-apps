# Build Harmony Apps

支持 Codex 与 Claude Code 双平台的 HarmonyOS 开发插件，参考 OpenAI `Build iOS Apps` 的任务型结构，优先复用华为 DevEco CodeGenie 官方能力，并整合 OpenHarmony SIG DevEco CLI 与社区实战知识。

详细使用说明（17 个 Skill 的触发方式与工作流程、工具链、排障 FAQ）见 [docs/USAGE.md](docs/USAGE.md)；iOS 应用迁移见 [docs/IOS-MIGRATION.md](docs/IOS-MIGRATION.md)。

## 能力

- 构建、启动、UI 树、交互、截图与日志调试(CodeGenie MCP + devecocli 工具阶梯)
- ArkUI 原生设计、组件模式、状态管理踩坑诊断、性能审查、重构与多设备适配
- 60+ HarmonyOS Kit 集成(相机/音频/推送/地图/账号/支付/服务卡片/元服务等)+ 权限完整流程
- 签名打包、AppGallery 提审、IAP 内购、备案合规
- DevEco Profiler trace 和内存快照分析
- HarmonyOS Intents Kit、Hypium 测试分诊
- ArkTS 项目创建、语法、编译错误与运行崩溃处理

插件包含 17 个独立 Skill，并固定使用：

```text
@deveco-codegenie/mcp@1.1.11
```

可选增强：安装 [OpenHarmony SIG DevEco CLI](https://gitcode.com/openharmony-sig/deveco-cli)(`npm i -g @deveco/deveco-cli`)后,skill 会自动利用其本地文档检索(`devecocli docs search`)、模拟器状态注入(折叠/传感器/GPS)与脚手架能力。

## 安装

将仓库放入个人插件目录：

```bash
git clone https://github.com/noiseorigin/build-harmony-apps.git ~/plugins/build-harmony-apps
```

### Codex

在 `~/.agents/plugins/marketplace.json` 中添加本地插件条目，并启用 `build-harmony-apps@personal`。更新后重新安装插件并新开 Codex 任务，确保 Skill 与 MCP 使用同一版本。

### Claude Code

仓库根目录包含 Claude 插件清单与 Marketplace 清单。正式安装：

```bash
claude plugin marketplace add noiseorigin/build-harmony-apps
claude plugin install build-harmony-apps@build-harmony-apps-marketplace
```

本地开发验证无需安装 Marketplace：

```bash
claude --plugin-dir ~/plugins/build-harmony-apps
# 修改后在会话中运行 /reload-plugins
```

安装后问 "What skills are available?" 应列出 17 个 skill(harmony-debugger-agent、arkui-ui-patterns、harmony-kit-integration、harmony-release-compliance 等)。

## 验证

```bash
python3 scripts/validate_bundle.py      # 结构校验:frontmatter/路由用例覆盖/引用断链/双清单一致性
python3 -m unittest discover -s tests -v
python3 scripts/evaluate_routing_results.py path/to/agent-results.json  # 校验真实 Agent 运行记录
python3 scripts/smoke_codegenie_mcp.py  # 需要网络拉取 MCP,CI 中为手动触发
```

CI(`.github/workflows/validate.yml`)在 push/PR 时自动跑前两项。`evals/cases.json` 是路由与答案断言用例，不等同于真实 Agent 运行结果；发布前应在目标 Agent 中抽样执行新增高风险用例。

已在 DevEco Studio 26 / HarmonyOS API 26 Beta1 环境验证 ArkTS 编译和 unsigned HAP 打包。

## 参考的开源项目

本插件的结构、工具链与知识内容改编自以下开源项目(完整来源与许可证见 `THIRD_PARTY_NOTICES.md` 和 `upstreams.json`):

| 项目 | 许可证 | 借鉴内容 |
|---|---|---|
| [OpenAI Build iOS Apps](https://github.com/openai/plugins)(v0.1.2) | MIT | 任务型 skill 结构、渐进式 references、证据门控工作流 |
| [DevEco CodeGenie skills](https://gitcode.com/southbridge/codegenie_cli) | MIT(部分脚本 Apache-2.0) | 项目创建、ArkTS 语法/编译分诊、崩溃证据工作流(固定快照改编,未拷贝脚本) |
| [DengShiyingA/harmonyos-ai-skill](https://github.com/DengShiyingA/harmonyos-ai-skill) | MIT | 平台版本基线、ArkUI 组件/状态管理/性能、60+ Kit 集成、权限流程等知识内容(精选改编并对照官方文档) |
| [chen_jeff/harmony-os-skill](https://gitee.com/chen_jeff/harmony-os-skill) | 以 LICENSE 的木兰 PSL v2 为准(README 的 MIT 声明不一致) | 已上架应用沉淀的实战踩坑:状态追踪断链、服务卡片刷新/透明/跨进程图片、元服务约束、签名提审、IAP;发布与合规结论需再核对官方现行规则 |
| [openharmony-sig/deveco-cli](https://gitcode.com/openharmony-sig/deveco-cli) | MIT | 官方统一 CLI 作为工具阶梯的一环:build/run/log、模拟器状态注入、本地文档检索、MCP 语法诊断(仅引用命令面,未 vendor 代码) |
| [HarmonyOS Intents Kit sample](https://gitcode.com/HarmonyOS_Samples/intents-kit-samplecode-clientdemo-arkts) | — | Intents Kit 工作流的官方参考样例(仅链接) |
| [openharmonyinsight/openharmony-skills](https://gitcode.com/openharmonyinsight/openharmony-skills) | 未明确 | 质量维度与 eval 设计参考(仅参考,未收录内容) |

## 说明

这是独立社区项目，并非华为或 OpenAI 官方产品。
