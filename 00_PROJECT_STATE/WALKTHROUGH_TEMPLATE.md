# WALKTHROUGH — <phase_id> — <YYYY-MM-DD>
status: done | partial | blocked
scope: <одна строка>

## files_changed        # путь — назначение в 1 строку
- <path> — <purpose>

## commands_run          # только state-changing/ключевые
- <cmd> — <result 1 строка>

## acceptance            # критерий: PASS|FAIL [+заметка]
- <criterion>: PASS|FAIL

## deltas_vs_plan         # отличия от ТЗ и причина (пусто, если нет)
- <delta> — <reason>

## project_state_snapshot # зеркало 00_PROJECT_STATE
phase: <id>
completed: [...]
in_progress: [...]
blocked: [...]
open_questions: [...]

## decisions_logged       # новые DEC за этот прогон
- DEC-<n>: <решение> — <причина>

## next_recommended       # 1–3 пункта, предложение агента
- <item>
