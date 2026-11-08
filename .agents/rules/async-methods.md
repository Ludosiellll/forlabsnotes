---
description: 1C asynchronous methods (`Асинх` / `Ждать` / `Обещание`) — patterns and pitfalls for platform 8.3.18+. Load when writing or reviewing client-side async code.
alwaysApply: false
category: forms
---

# Asynchronous Methods in 1C (Асинх / Ждать / Обещание)

Rules for using the asynchronous mechanism introduced in platform 8.3.18+.

Applies to: client-side code with asynchronous calls (`&НаКлиенте`).

Authoritative reference: `standards(name="dev-standards-architecture") §3 → "Async and Modality"`. This file gives the practical patterns and the pitfalls.

> **College Lab Exception (РС02-23)**: Do NOT apply enterprise async callbacks (`ОписаниеОповещения`, `ПоказатьВводЧисла`, `ПоказатьПредупреждение`, `Асинх`/`Ждать`) in student laboratory works (`1С_ЛР*`). Student labs use `<ModalityUseMode>Use</ModalityUseMode>` in `Configuration.xml` and classic synchronous calls (`ВвестиЧисло`, `ВвестиСтроку`, `Предупреждение`) matching college methodology.

---

<!-- help-mcp-router -->

> **Retrieve through MCP only.** Call `standards(name="async-methods")` on `1C-docs-mcp` before applying this standard. Retrieval, paging, and unavailable-server policy: `content/rules/help-corpus-retrieval.md`. Headings below are retrieval targets, not summaries.

## Core principles

## Old vs new method correspondence

## Return values (result of `Ждать`)

## Basic template

## Critical rules

### 1. Without `Ждать`, exceptions are silently lost

### 2. `Асинх` in form event handlers does NOT block

### 3. Command handlers — async is allowed

## Pattern: question on form open

## Pattern: question on form close

## Pattern: file workflow

## HTTP methods (platform 8.3.21+)
