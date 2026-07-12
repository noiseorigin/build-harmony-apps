# APP 备案 vs ICP 备案

Checked 2026-07. Regulatory requirements evolve — verify with current MIIT/华为云 guidance before advising.

Two unrelated "filings" that get conflated:

| | APP 备案 | ICP 备案 |
|---|---|---|
| What | MIIT registration of the mobile app itself (2023-07 mandate) | registration of a self-hosted website/domain |
| Scope | Required for an APP that provides internet information services in mainland China; confirm the app/service facts and current platform gate | Depends on the website/domain, hosting location, service type, and access provider rules |
| AGC-hosted privacy URL | Does not replace APP-scope analysis | Usually does not create a developer-operated website filing by itself; verify the current AGC hosting terms and review form |

## Practical path (individual developer)

- For an APP providing internet information services in mainland China, start APP 备案 through the network access provider or distribution platform before the release window; prepare identity, app, domain/IP, and category-specific materials.
- For a privacy policy hosted by AGC, verify the generated URL and current review form before concluding that no separate website filing applies. A self-hosted mainland-China website/domain follows its own ICP rules.
- Treat software copyright as **not universally required and not universally optional**: check the current AppGallery qualification table, app category, ownership proof, and dispute/review context.

Primary regulatory source: MIIT notice 工信部信管〔2023〕105号, especially the scope “在中华人民共和国境内从事互联网信息服务的APP主办者”: https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2023/art_920db564162e4312916a01bed6540ad8.html

Operational experience adapted from chen_jeff/harmony-os-skill (gitee). Verify the current Huawei/AppGallery qualification table before advising.
