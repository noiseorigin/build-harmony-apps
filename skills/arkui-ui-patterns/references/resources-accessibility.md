# Resources and accessibility

## Resources

- Put localizable text, theme color, shared dimensions, and reusable media in resources according to project conventions.
- Preserve placeholders/plurals and avoid string concatenation that breaks translation.
- Verify light/dark variants, locale fallback, right-to-left behavior where supported, and image semantics.
- Do not put secrets, environment URLs, or machine paths in resources committed as UI data.

## Accessibility

- Supply meaningful names, roles, states, values, and actions for interactive/custom elements.
- Keep reading/focus order aligned with visual and task order.
- Avoid redundant labels on decorative children.
- Do not rely on color, motion, or position alone to communicate state.
- Verify enlarged text, localization expansion, touch targets, keyboard/pointer focus, contrast, and reduced motion requirements applicable to the project.

Use current HarmonyOS accessibility APIs from the installed SDK; API names and supported attributes may change.
