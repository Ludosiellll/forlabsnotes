---
description: Common XML generation pitfalls for 1C metadata and managed forms (`TabularSection` `LineNumber`, `PagesGroupExtInfo` typo, `Page.enabled`, UID uniqueness, post-edit validation). Load when authoring or fixing metadata XML or `Form.xml` by hand.
alwaysApply: false
category: metadata
---

# Common XML Generation Pitfalls (Metadata and Forms)

Concrete recurring mistakes when generating or editing 1C metadata XML / MDO and managed-form XML by hand or with scripts. Apply when authoring metadata XML directly (rather than via the `1c-metadata-manage` skill).

> **Hand-editing is the exception, not a parallel path.** Mutating metadata XML goes through the `1c-metadata-manage` skill or the `1c-metadata-manager` subagent (see `content/agents/metadata-manager.md`) — hard gate per `AGENTS.md → Skills and Subagents`. This file applies only inside the documented exceptions (`content/skills/1c-metadata-manage/SKILL.md → Hard rule`: one-line fix, skill unavailable) and for reviewing existing files.

> **Never use hand-editing to get around a support refusal.** If the skill's tools refused the edit because the object belongs to a typical configuration on vendor support and is locked ("на замке"), that refusal holds here too: a direct XML edit silently breaks future vendor updates. The answer is an extension (`cfe-borrow` / `cfe-patch-method`) or a deliberate support-state change via `support-edit` — canon: `content/skills/1c-metadata-manage/docs/support-manage.md`. A configuration on support is recognizable by `Ext/ParentConfigurations.bin` next to `Configuration.xml`.

---

## 1. TabularSections — no `LineNumber` standard attribute

Tabular sections (`табличные части`) **must not** contain a `<standardAttributes>` block with `LineNumber`. The platform adds it automatically; an explicit copy will cause a load error or duplication.

```xml
<!-- WRONG — remove this block from <tabularSections> -->
<standardAttributes>
  <dataHistory>Use</dataHistory>
  <name>LineNumber</name>
  <fillValue xsi:type="core:UndefinedValue"/>
  <fullTextSearch>Use</fullTextSearch>
  <minValue xsi:type="core:UndefinedValue"/>
  <maxValue xsi:type="core:UndefinedValue"/>
</standardAttributes>
```

The same rule applies to MDO (EDT format) `*.mdo` files — do not add a `LineNumber` standardAttribute to tabular sections; the EDT toolchain provides it implicitly.

---

## 2. `Pages` group — correct extInfo type name

The extInfo type is `PagesGroupExtInfo` (with letter "**s**"), not `PageGroupExtInfo`:

```xml
<!-- CORRECT -->
<type>Pages</type>
<extInfo xsi:type="form:PagesGroupExtInfo">
  <pagesRepresentation>Auto</pagesRepresentation>
  <currentRowUse>Auto</currentRowUse>
</extInfo>
```

A misspelled `PageGroupExtInfo` will silently break the form — the page group will not load in Designer / EDT.

---

## 3. `Page` element — must include `<enabled>true</enabled>`

For each `Page` element inside a `Pages` group, the `<enabled>` flag is required. Without it, Designer treats the page as disabled (or the form fails validation).

```xml
<type>Page</type>
<enabled>true</enabled>
```

---

## 4. UID / UUID — must be globally unique

All UIDs and UUIDs of new metadata objects, attributes, tabular sections must be **globally unique** across the configuration.

- Generate each UUID separately via `[guid]::NewGuid()` (PowerShell) or `uuid.uuid4()` (Python).
- Never reuse a UUID by copy-paste.
- Never use placeholder / sequential UUIDs (`a1b2c3d4...`, `b2c3d4e5...`).
- After bulk metadata generation, run a duplicate-UUID check across the source tree.

When adding metadata objects — also update `Configuration.xml` (`<childObjects>` ordering matters).

---

## 5. `ChildItems` — NEVER leave as empty self-closing stub

**CRITICAL.** A `Form.xml` with `<ChildItems/>` (self-closing, no child elements) is **syntactically valid XML** and will **pass `verify_xml` / XSD validation**, but the resulting form will be **completely blank** — no input fields, no tables, no buttons. The user opens the document and sees an empty white window.

The platform treats an explicitly created form as authoritative: if `<DefaultObjectForm>` points to a form with empty `<ChildItems/>`, the platform will NOT auto-generate UI — it shows the empty form as-is.

```xml
<!-- WRONG — renders as blank white form -->
<ChildItems/>

<!-- CORRECT — has actual UI elements -->
<ChildItems>
    <InputField name="Склад" id="1">
        <DataPath>Объект.Склад</DataPath>
        ...
    </InputField>
    ...
</ChildItems>
```

**How this happens:**
- The `form-add.ps1` scaffold script (lines 393, 418, 465) intentionally creates empty `<ChildItems/>` — it is a *scaffold*, not a finished form.
- If the agent stops after `form-add` without running `form-compile -FromObject`, the form stays blank.
- The script refuses to overwrite an existing `Form.xml` (`[SKIP] Form.xml already exists`), so re-running `form-compile` later won't help unless the empty file is deleted first.

**Mandatory rule:**
1. After `form-add` → always run `form-compile -FromObject` to populate `<ChildItems>` with data-bound elements.
2. If `form-compile` is unavailable — **do not create a custom form at all**: remove the `<DefaultObjectForm>` / `<DefaultChoiceForm>` entries from the object XML and let the platform auto-generate the form.
3. Never hand-write a `<ChildItems/>` stub and leave it.

---

## 6. Validation hook

Whenever editing metadata XML by hand, after the change run:

- `verify_xml` from `1c-code-metadata-mcp` against the appropriate XSD (`get_xsd_schema` first if unsure of the type).
- Then a sanity load via `1c-metadata-manage/tools/1c-meta-validate/scripts/meta-validate.ps1`.

This catches structural issues (missing required elements, wrong type names, broken references) before they reach the platform.

> **Note:** `verify_xml` does NOT catch semantically broken forms (empty `<ChildItems/>`, missing data bindings). Always visually verify forms in 1C:Enterprise mode after creation.

---

## 7. Общие нумераторы (`DocumentNumerators`) — строгое совпадение типа и длины

При подключении документа к общему нумератору:
```xml
<numerator>DocumentNumerator.ИмяНумератора</numerator>
```
Параметры номера документа (`<numberType>` и `<numberLength>`) **обязаны строго совпадать** с параметрами нумератора. Если у нумератора тип `Number` и длина `5`, а у документа указан тип `String` или длина `9`, Конфигуратор 1С откажется загружать конфигурацию с фатальной ошибкой.

---

## 8. Квалификаторы чисел (`NumberQualifiers`) — масштаб и точность

В 1С точность `<scale>` (число знаков дробной части) **не может превышать** `<precision>` (общую длину числа):
- Стандарт для сумм/цен: `precision = 15`, `scale = 2`.
- Стандарт для количества: `precision = 10..15`, `scale = 3` (или `scale = 0` для целых/штучных).
- Осторожно с `<nonNegative>true</nonNegative>`: при включенном флаге любая операция сторно/корректировки остатка в минус вызовет аварийную ошибку транзакции платформы.

---

## 9. Форматы дат в XML и модулях BSL

- **В файлах метаданных и выгрузках XML**: строго формат ISO 8601 (`ГГГГ-ММ-ДДTЧЧ:ММ:СС`), например `2026-09-16T00:00:00`.
- **Пустая дата в XML**: `0001-01-01T00:00:00`.
- **В модулях 1С (BSL)**: строковый литерал даты пишется в одинарных кавычках без дефисов: `'20260916'` или `'20260916180000'`. Пустая дата: `'00010101'`.
- **Состав даты (`dateFractions`)**: для документов всегда использовать `DateTime`. Значение `Date` обрезает время до `00:00:00`, что ломает хронологический порядок проведения документов в один день!

---

## 10. Запрет переопределения стандартных реквизитов

У каждого объекта метаданных платформа 1С автоматически создает стандартные реквизиты:
- Справочники: `Ref` (Ссылка), `DeletionMark` (ПометкаУдаления), `Code` (Код), `Description` (Наименование), `Parent` (Родитель), `Owner` (Владелец).
- Документы: `Ref` (Ссылка), `Date` (Дата), `Number` (Номер), `Posted` (Проведен), `DeletionMark` (ПометкаУдаления).

**Категорически запрещено** создавать в блоке `<attributes>` пользовательские реквизиты с именами `Код`, `Номер`, `Дата`, `Наименование`, `Ссылка`, `ПометкаУдаления`! Это вызывает конфликт имен и ломает структуру объекта.

---

## 11. Дисциплина кодировок (UTF-8 с BOM vs ANSI vs ASCII)

- **PowerShell 5.1**: Скрипты `.ps1` без BOM читаются как Windows-1251. Все `.ps1` файлы с русскими строками **обязаны сохраняться в UTF-8 с BOM**.
- **Модули 1С (`.bsl`)**: Файлы модулей (`Ext/ObjectModule.bsl` и др.) должны быть в кодировке **UTF-8 с BOM**, иначе русские комментарии и строковые литералы превращаются в нечитаемые символы при загрузке Конфигуратором.
- **Батники запуска (`.bat`)**: Консоль `cmd.exe` работает в CP866. В `.bat` файлах **запрещена кириллица** и директива `chcp 65001`. Пути к 1С указывать только через ASCII-junction: `D:\1c_app`.

---

## 12. Специфика Учебной версии платформы (8.3.27.1508)

- **Имена исполняемых файлов**: толстый клиент/конфигуратор — **`1cv8t.exe`**, тонкий клиент — **`1cv8ct.exe`**. Стандартного файла `1cv8.exe` в учебной версии **нет**!
- **Монопольный доступ**: база может быть открыта только в одном сеансе. Перед пакетными выгрузками/загрузками обязательно закрывать все окна 1С.
- **Лимиты данных**: не более 2000 записей в основных таблицах базы данных, не более 1000 записей в табличных частях.
- **Безопасность внешних обработок**: обязательно должна быть прописана директива `DisableUnsafeActionProtection=.*` в `D:\1c_app\8.3.27.1508\bin\conf\conf.cfg`.

---

## 13. Периодичность нумерации (`NumberPeriodicity`) и `НайтиПоНомеру()`

В платформе 1С:Предприятие 8.3 метод `Документы.<Имя>.НайтиПоНомеру(НомерДокумента, [ДатаИнтервала])` работает по-разному в зависимости от свойства `<NumberPeriodicity>` в XML документа:
- Если `<NumberPeriodicity>Year</NumberPeriodicity>` (или `Quarter`, `Month`, `Day`), то вызов `НайтиПоНомеру("00000000004")` **с одним аргументом** (без второго параметра `ДатаИнтервала`) ищет документ в интервале пустой даты `'00010101'` и **всегда возвращает `ПустаяСсылка`**!
- Из-за этого конструкции вида `Если Не КопияДокумента.Пустая() Тогда` молча пропускают весь блок кода и кнопка на форме ничего не делает.

**Обязательное правило:**
1. Если в методичке или коде лабораторной работы используется вызов `НайтиПоНомеру(Номер)` с одним параметром, у документа в XML обязательно должно стоять `<NumberPeriodicity>Nonperiodical</NumberPeriodicity>`.
2. В обработчиках кнопок обработок (`СоздатьДокумент`, `КопияДокумента`, `ОтменаПроведения`, `ИзменениеДокумента`, `БлокировкаДокумента`) всегда добавлять `Сообщить(...)` и на клиенте `ОповеститьОбИзменении(ДокСсылка)`, чтобы пользователь сразу видел результат и открытая форма списка обновлялась автоматически.

