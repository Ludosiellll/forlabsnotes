---
type: decision
status: accepted
updated: 2026-09-23
tags:
  - decision
  - 1c
  - managed-forms
  - conditional-appearance
---

# 1C Managed Forms Conditional Appearance Activation Rule

## Summary

In 1C:Enterprise managed forms, programmatic conditional appearance (`УсловноеОформление`) created in server context (e.g. `ПриСозданииНаСервере`) silently fails to apply unless the activation flag `ПолеОформления.Использование = Истина` and `ЭлементОформления.Использование = Истина` are explicitly set.

## Context

During Lab 5 ("Работа с формами и модулями"), Task 5 required highlighting the `Сумма` cell in `ПриходнаяНакладная` with a light green background. The programmatic appearance element was created and `УстановитьЗначениеПараметра("ЦветФона", WebЦвета.СветлоЗеленый)` was called, but the column remained white in the 1C client.

Investigation revealed that in 1C's Data Composition System (DCS), newly instantiated items in collection `Поля` have `Использование = Ложь` by default. Without explicit `Использование = Истина`, the platform ignores the field and does not render the styling.

## Decision

All programmatic conditional appearance in 1C managed forms must follow the canonical pattern:

```bsl
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    
    ЭлементОформления = УсловноеОформление.Элементы.Добавить();
    ЭлементОформления.Использование = Истина;
    
    // Оформление
    ЭлементОформления.Оформление.УстановитьЗначениеПараметра("ЦветФона", WebЦвета.СветлоЗеленый);
    
    // Оформляемое поле (ОБЯЗАТЕЛЬНО Использование = Истина!)
    ПолеОформления = ЭлементОформления.Поля.Элементы.Добавить();
    ПолеОформления.Поле = Новый ПолеКомпоновкиДанных("МатериалыСумма");
    ПолеОформления.Использование = Истина;
    
КонецПроцедуры
```

## Consequences

- Prevents silent styling failures in all future 1C lab assignments and configurations.
- Durable rule codified in `.agents/rules/form-module.md`, cognitive memory `mind_learn`, and knowledge graph `mind_fact`.

## Links

- [[40_Decisions/Decision_Log]]
- [[30_Tech/Codebase_Map]]
