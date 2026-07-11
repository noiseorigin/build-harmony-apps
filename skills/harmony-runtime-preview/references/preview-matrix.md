# Preview matrix

Choose only dimensions that materially affect the requested UI, but do not omit an explicitly supported class.

## Baseline dimensions

- device/window class and exact viewport
- portrait/landscape or resize state
- light/dark theme
- default and enlarged text
- primary locale plus one expansion-prone locale when localization is in scope
- loading, content, empty, error, disabled, and selected states that exist in the feature
- keyboard shown/hidden for input pages
- touch versus pointer/keyboard focus when both are supported

## Artifact names

Use stable, sortable names:

`<flow>__<device-or-width>__<theme>__<locale>__<state>__<build>.png`

Keep a small manifest beside the images containing project revision, module/product/build, system version, viewport, capture time, and expected assertion.

## Minimum proof

- A focused visual change: before/after on one representative device plus affected edge states.
- A responsive change: each materially different layout class and one resize/fold/orientation transition.
- A theme/resource change: light/dark and localization/text-scale states affected.
- An interactive change: initial frame, post-action frame, and assertion/log for the action.
