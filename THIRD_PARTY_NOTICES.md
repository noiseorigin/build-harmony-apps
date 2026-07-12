# Third-party notices

This plugin is independently authored and is not an official Huawei or OpenAI product.

## OpenAI Build iOS Apps

The plugin's task-oriented skill layout, progressive-disclosure structure, evidence gates, and code-first/runtime-evidence split are adapted from OpenAI's `build-ios-apps` plugin version `0.1.2`, distributed under the MIT License. No Apple-specific code or assets are included.

Source: https://github.com/openai/plugins

## DevEco CodeGenie skills

The project-creation, ArkTS grammar, compiler-triage, and crash-evidence workflows are adapted from DevEco CodeGenie's open-source skills at commit `2a9a5193c122798a451520cf6a4a5a0553e62f93`.

Repository: https://gitcode.com/southbridge/codegenie_cli

The repository root carries the MIT License (copyright 2025 opencode). Individual runtime scripts in that source may carry Huawei Device Co., Ltd. Apache-2.0 headers. This plugin does not vendor those scripts; its Python utilities are independent implementations.

## Official HarmonyOS samples and documentation

API workflows link to, but do not vendor, Huawei Developer documentation and HarmonyOS sample repositories. In particular, the Intents Kit workflow is grounded in the official `intents-kit-samplecode-clientdemo-arkts` sample.

Source: https://gitcode.com/HarmonyOS_Samples/intents-kit-samplecode-clientdemo-arkts

## HarmonyOS AI Skill knowledge pack (DengShiyingA)

Knowledge content across skill references (platform baseline, ArkUI component/state/performance patterns, Kit integration, permissions, testing) is adapted from `DengShiyingA/harmonyos-ai-skill`, distributed under the MIT License. Content was curated, restructured into per-skill references, version-labeled, and cross-checked against official documentation at adaptation time.

Source: https://github.com/DengShiyingA/harmonyos-ai-skill

## HarmonyOS practice skills (chen_jeff)

Production pitfall knowledge (ArkUI state-tracking chains, service-card refresh/transparency/image passing, atomic-service constraints, signing and AppGallery submission, IAP integration) is adapted from `chen_jeff/harmony-os-skill`. Its LICENSE file carries the Mulan PSL v2 while the README states MIT. This project conservatively treats the repository LICENSE file (MulanPSL-2.0) as authoritative, records the inconsistency, and does not vendor upstream files verbatim. Community release/compliance observations are labeled as operational evidence and require current official verification.

Source: https://gitee.com/chen_jeff/harmony-os-skill

## DevEco CLI

The `devecocli` command surface referenced by the debugger, project-creation, error-fixing, and multi-device skills is the openharmony-sig DevEco CLI, distributed under the MIT License. This plugin documents and invokes the tool; it does not vendor its code.

Source: https://gitcode.com/openharmony-sig/deveco-cli

## Community references

Workflow ideas were reviewed from Eclipse Oniro `agent-skills`, Midscene `midscene-skills`, and other public HarmonyOS skill repositories. They are references only; no source code or assets from those repositories are included.
