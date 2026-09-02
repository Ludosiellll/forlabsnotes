---
type: resource
status: stable
updated: 2026-07-12
tags:
  - ai/template
  - ai/onboarding
---

# Прочти меня первым / Read me first

## Что это за архив

Этот ZIP — прозрачный ручной вариант AI OS для Windows. Обычному пользователю проще запустить `AI_OS_Setup_v{{KIT_VERSION}}_x64.exe`: он создаёт новые среды, переиспользует общие компоненты и сам запускает проверки.

Архив нужен, если нативный Setup недоступен, если вы хотите проверить содержимое до установки или настроить рабочую среду вручную.

## Что внутри

- `AI_OS_TEMPLATE_v0_1/` — отдельная рабочая среда одного проекта: заметки, правила для ИИ, skills, проверки и Control Center;
- `memory-tool/` — официальный бинарный файл локальной смысловой памяти с лицензией и инструкцией;
- `KIT_MANIFEST.json` и `SHA256SUMS.txt` — версия комплекта, происхождение компонентов и контрольные суммы.

## Установка вручную

1. Распакуйте ZIP в обычную папку, например в `Документы`.
2. Скопируйте `AI_OS_TEMPLATE_v0_1` и переименуйте копию под свой проект. Одна такая папка должна относиться только к одному проекту.
3. Откройте Claude Code, Codex, Cursor или другой поддерживаемый агент прямо в этой папке.
4. Напишите: **«Настрой эту рабочую среду полностью. Следуй `TEMPLATE_SETUP.md`, ничего не пропускай и в конце запусти проверки».**
5. Ответьте на вопросы о названии проекта, своём имени и краткой цели проекта.

Rust, Python, Node.js и MCP-серверы вручную устанавливать не требуется. Obsidian и Git полезны, но сама папка остаётся обычным набором Markdown-файлов и работает без них.

## Новый проект

Для второго проекта сделайте новую чистую копию `AI_OS_TEMPLATE_v0_1`. Не складывайте несвязанные проекты в одну среду: их заметки, решения и память должны оставаться раздельными.

## Безопасность

- Ничего не отправляется автору автоматически.
- Не записывайте пароли, токены и клиентские секреты в заметки.
- Перед запуском бинарных файлов сверяйте `SHA256SUMS.txt`.
- Локальная память помогает найти заметку, но источником правды остаются Markdown, код и первичные документы.

## English (short)

This ZIP is the transparent Windows fallback. Prefer the native `AI_OS_Setup_v{{KIT_VERSION}}_x64.exe` for normal installation. For manual setup, copy `AI_OS_TEMPLATE_v0_1` for one project, open your AI coding agent in that folder, and ask it to follow `TEMPLATE_SETUP.md` completely and run the final checks. Verify bundled binaries with `SHA256SUMS.txt`.

Template author: Denis Labyntsev · @Ludosiel

## Links

- [[TEMPLATE_SETUP]]
- [[70_Resources/Template_Memory_Tool_Install_Note]]
- [[70_Resources/Agent_Workflow_Protocol]]
