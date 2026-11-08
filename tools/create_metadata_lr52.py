# -*- coding: utf-8 -*-
"""
tools/create_metadata_lr52.py
Генератор объектов метаданных для Лабораторной работы №5.2:
1. DataProcessor.РаботаСДокументами (Задания 1, 2, 3, 4)
2. DataProcessor.ЛичныеДанные (Дополнительное задание 1)
3. DataProcessor.ИзменениеДокумента (Дополнительное задание 2)
"""

import os
import uuid
import re

SRC_DIR = r"d:\1с лабы\1С_ЛР5.2_Файлы\src"
DP_DIR = os.path.join(SRC_DIR, "DataProcessors")
os.makedirs(DP_DIR, exist_ok=True)

def gen_uuid():
    return str(uuid.uuid4())

# ==============================================================================
# 1. DataProcessor.РаботаСДокументами
# ==============================================================================
def create_dp_rabota_s_dokumentami():
    name = "РаботаСДокументами"
    synonym = "Работа с документами"
    dp_uuid = gen_uuid()
    obj_uuid = gen_uuid()
    val_uuid = gen_uuid()
    mgr_uuid = gen_uuid()
    mgr_val_uuid = gen_uuid()
    form_uuid = gen_uuid()

    # 1.1 Метаданные обработки
    dp_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<DataProcessor uuid="{dp_uuid}">
		<InternalInfo>
			<xr:GeneratedType name="DataProcessorObject.{name}" category="Object">
				<xr:TypeId>{obj_uuid}</xr:TypeId>
				<xr:ValueId>{val_uuid}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DataProcessorManager.{name}" category="Manager">
				<xr:TypeId>{mgr_uuid}</xr:TypeId>
				<xr:ValueId>{mgr_val_uuid}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>{name}</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>{synonym}</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<UseStandardCommands>true</UseStandardCommands>
			<DefaultForm>DataProcessor.{name}.Form.Форма</DefaultForm>
			<AuxiliaryForm/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<ExtendedPresentation/>
			<Explanation/>
		</Properties>
		<ChildObjects>
			<Form>Форма</Form>
		</ChildObjects>
	</DataProcessor>
</MetaDataObject>
'''
    with open(os.path.join(DP_DIR, f"{name}.xml"), "w", encoding="utf-8") as f:
        f.write(dp_xml)

    # 1.2 Папка формы
    form_base = os.path.join(DP_DIR, name, "Forms", "Форма")
    os.makedirs(os.path.join(form_base, "Ext", "Form"), exist_ok=True)

    form_meta = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Form uuid="{form_uuid}">
		<Properties>
			<Name>Форма</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Форма</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<FormType>Managed</FormType>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<UsePurposes>
				<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
				<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
			</UsePurposes>
		</Properties>
	</Form>
</MetaDataObject>
'''
    with open(os.path.join(DP_DIR, name, "Forms", "Форма.xml"), "w", encoding="utf-8") as f:
        f.write(form_meta)

    # 1.3 Form.xml (полная разметка интерфейса с кнопками)
    form_layout = f'''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Title>
		<v8:item>
			<v8:lang>ru</v8:lang>
			<v8:content>{synonym}</v8:content>
		</v8:item>
	</Title>
	<AutoTitle>false</AutoTitle>
	<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
	<ChildItems>
		<Button name="СоздатьДокумент" id="1">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.СоздатьДокумент</CommandName>
			<ExtendedTooltip name="СоздатьДокументРасширеннаяПодсказка" id="2"/>
		</Button>
		<Button name="ОтменаПроведения" id="3">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.ОтменаПроведения</CommandName>
			<ExtendedTooltip name="ОтменаПроведенияРасширеннаяПодсказка" id="4"/>
		</Button>
		<Button name="КопияДокумента" id="5">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.КопияДокумента</CommandName>
			<ExtendedTooltip name="КопияДокументаРасширеннаяПодсказка" id="6"/>
		</Button>
		<Button name="ИзменениеДокумента" id="7">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.ИзменениеДокумента</CommandName>
			<ExtendedTooltip name="ИзменениеДокументаРасширеннаяПодсказка" id="8"/>
		</Button>
		<Button name="ОткрытьФормуДокумента" id="9">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.ОткрытьФормуДокумента</CommandName>
			<ExtendedTooltip name="ОткрытьФормуДокументаРасширеннаяПодсказка" id="10"/>
		</Button>
		<Button name="ОткрытиеФормыСписка" id="11">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.ОткрытиеФормыСписка</CommandName>
			<ExtendedTooltip name="ОткрытиеФормыСпискаРасширеннаяПодсказка" id="12"/>
		</Button>
		<Button name="БлокировкаДокумента" id="13">
			<Type>UsualButton</Type>
			<CommandName>Form.Command.БлокировкаДокумента</CommandName>
			<ExtendedTooltip name="БлокировкаДокументаРасширеннаяПодсказка" id="14"/>
		</Button>
	</ChildItems>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:DataProcessorObject.{name}</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
		</Attribute>
	</Attributes>
	<Commands>
		<Command name="СоздатьДокумент" id="1">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Создать документ</v8:content>
				</v8:item>
			</Title>
			<Action>СоздатьДокумент</Action>
		</Command>
		<Command name="ОтменаПроведения" id="2">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Отмена проведения</v8:content>
				</v8:item>
			</Title>
			<Action>ОтменаПроведения</Action>
		</Command>
		<Command name="КопияДокумента" id="3">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Копия документа</v8:content>
				</v8:item>
			</Title>
			<Action>КопияДокумента</Action>
		</Command>
		<Command name="ИзменениеДокумента" id="4">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Изменение документа</v8:content>
				</v8:item>
			</Title>
			<Action>ИзменениеДокумента</Action>
		</Command>
		<Command name="ОткрытьФормуДокумента" id="5">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Открыть форму документа</v8:content>
				</v8:item>
			</Title>
			<Action>ОткрытьФормуДокумента</Action>
		</Command>
		<Command name="ОткрытиеФормыСписка" id="6">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Открыть форму списка</v8:content>
				</v8:item>
			</Title>
			<Action>ОткрытиеФормыСписка</Action>
		</Command>
		<Command name="БлокировкаДокумента" id="7">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Блокировка документа</v8:content>
				</v8:item>
			</Title>
			<Action>БлокировкаДокумента</Action>
		</Command>
	</Commands>
</Form>
'''
    with open(os.path.join(form_base, "Ext", "Form.xml"), "w", encoding="utf-8") as f:
        f.write(form_layout)

    # 1.4 Module.bsl (код всех обработчиков строго по методичке)
    module_bsl = '''&НаСервере
Процедура СоздатьДокументНаСервере()
	Поступление = Документы.ПриходнаяНакладная.СоздатьДокумент();
	
	// Заполнение шапки документа
	Поступление.Дата = ТекущаяДата();
	
	ПоставщикОбъект = Справочники.Поставщики.НайтиПоНаименованию("ОАО ""Азот""");
	Если ПоставщикОбъект.Пустая() Тогда
		// Fallback если точного названия нет
		ВыборкаПост = Справочники.Поставщики.Выбрать();
		Если ВыборкаПост.Следующий() Тогда
			ПоставщикОбъект = ВыборкаПост.Ссылка;
		КонецЕсли;
	КонецЕсли;
	Поступление.Поставщик = ПоставщикОбъект;
	
	СкладОбъект = Справочники.Склады.НайтиПоКоду("000000001");
	Если СкладОбъект.Пустая() Тогда
		СкладОбъект = Справочники.Склады.НайтиПоНаименованию("Основной");
	КонецЕсли;
	Поступление.Склад = СкладОбъект;
	
	Поступление.Комментарий = "#Документ создан автоматически обработкой";
	
	// Табличная часть Материалы
	НоваяСтрока = Поступление.Материалы.Добавить();
	
	НоменклатураОбъект = Справочники.Номенклатура.НайтиПоНаименованию("Транзистор Philips");
	Если НоменклатураОбъект.Пустая() Тогда
		ВыборкаНом = Справочники.Номенклатура.Выбрать();
		Если ВыборкаНом.Следующий() Тогда
			НоменклатураОбъект = ВыборкаНом.Ссылка;
		КонецЕсли;
	КонецЕсли;
	НоваяСтрока.Наименование = НоменклатураОбъект;
	
	НоваяСтрока.Количество = 10;
	НоваяСтрока.Цена = 97.10;
	НоваяСтрока.Сумма = НоваяСтрока.Количество * НоваяСтрока.Цена;
	
	// Дополнительные реквизиты ТЧ если есть в метаданных
	Попытка
		НоваяСтрока.Наценка = -3.5;
		НоваяСтрока.СуммаСНаценкой = ((НоваяСтрока.Сумма * НоваяСтрока.Наценка) / 100 + НоваяСтрока.Сумма);
		НоваяСтрока.Отклонение = НоваяСтрока.Сумма - НоваяСтрока.СуммаСНаценкой;
	Исключение
	КонецПопытки;
	
	Поступление.Записать(РежимЗаписиДокумента.Запись);
	Поступление.Записать(РежимЗаписиДокумента.Проведение);
	
	Сообщить("Документ " + Строка(Поступление.Ссылка) + " успешно создан и проведен!");
КонецПроцедуры

&НаКлиенте
Процедура СоздатьДокумент(Команда)
	СоздатьДокументНаСервере();
КонецПроцедуры

// -----------------------------------------------------------------------------
// Задание 2.1: Отмена проведения документа
// -----------------------------------------------------------------------------
&НаСервере
Процедура ОтменаПроведенияНаСервере()
	СсылкаНаПриход = Документы.ПриходнаяНакладная.НайтиПоНомеру("00000000004");
	Если СсылкаНаПриход.Пустая() Тогда
		СсылкаНаПриход = Документы.ПриходнаяНакладная.НайтиПоНомеру("00004");
	КонецЕсли;
	Если СсылкаНаПриход.Пустая() Тогда
		Выборка = Документы.ПриходнаяНакладная.Выбрать();
		Если Выборка.Следующий() Тогда
			СсылкаНаПриход = Выборка.Ссылка;
		КонецЕсли;
	КонецЕсли;
	
	Если Не СсылкаНаПриход.Пустая() Тогда
		ДокОбъект = СсылкаНаПриход.ПолучитьОбъект();
		ДокОбъект.Записать(РежимЗаписиДокумента.ОтменаПроведения);
		Сообщить("Отменено проведение документа: " + Строка(СсылкаНаПриход));
	Иначе
		Сообщить("Документ Приходная накладная не найден для отмены проведения!");
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура ОтменаПроведения(Команда)
	ОтменаПроведенияНаСервере();
КонецПроцедуры

// -----------------------------------------------------------------------------
// Задание 2.2: Копия документа
// -----------------------------------------------------------------------------
&НаСервере
Процедура КопияДокументаНаСервере()
	КопияДокумента = Документы.ПриходнаяНакладная.НайтиПоНомеру("00000000004");
	Если КопияДокумента.Пустая() Тогда
		КопияДокумента = Документы.ПриходнаяНакладная.НайтиПоНомеру("00004");
	КонецЕсли;
	Если КопияДокумента.Пустая() Тогда
		Выборка = Документы.ПриходнаяНакладная.Выбрать();
		Если Выборка.Следующий() Тогда
			КопияДокумента = Выборка.Ссылка;
		КонецЕсли;
	КонецЕсли;
	
	Если Не КопияДокумента.Пустая() Тогда
		Копия = КопияДокумента.Скопировать();
		Копия.Дата = ТекущаяДата();
		Копия.Комментарий = "КОПИЯ " + Строка(КопияДокумента);
		Копия.Записать(РежимЗаписиДокумента.Проведение);
		Сообщить("Создана проведенная копия документа: " + Строка(Копия.Ссылка));
	Иначе
		Сообщить("Документ для копирования не найден!");
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура КопияДокумента(Команда)
	КопияДокументаНаСервере();
КонецПроцедуры

// -----------------------------------------------------------------------------
// Задание 3: Изменение документа
// -----------------------------------------------------------------------------
&НаСервере
Процедура ИзменениеДокументаНаСервере()
	СсылкаНаДокумент = Документы.ПриходнаяНакладная.НайтиПоНомеру("00000000005");
	Если СсылкаНаДокумент.Пустая() Тогда
		СсылкаНаДокумент = Документы.ПриходнаяНакладная.НайтиПоНомеру("00005");
	КонецЕсли;
	Если СсылкаНаДокумент.Пустая() Тогда
		Выборка = Документы.ПриходнаяНакладная.Выбрать();
		Если Выборка.Следующий() Тогда
			СсылкаНаДокумент = Выборка.Ссылка;
		КонецЕсли;
	КонецЕсли;
	
	Если СсылкаНаДокумент.Пустая() Тогда
		Сообщить("Документ не найден");
	Иначе
		Приход = СсылкаНаДокумент.ПолучитьОбъект();
		ПоставщикНовый = Справочники.Поставщики.НайтиПоНаименованию("Петров Пётр Иванович");
		Если ПоставщикНовый.Пустая() Тогда
			ПоставщикНовый = Справочники.Поставщики.НайтиПоНаименованию("ОАО ""Азот""");
		КонецЕсли;
		Если Не ПоставщикНовый.Пустая() Тогда
			Приход.Поставщик = ПоставщикНовый;
		КонецЕсли;
		Приход.Комментарий = "Изменен обработкой: " + ТекущаяДата();
		Приход.Записать(РежимЗаписиДокумента.Проведение);
		Сообщить("Документ " + Строка(СсылкаНаДокумент) + " успешно изменен и проведен!");
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура ИзменениеДокумента(Команда)
	ИзменениеДокументаНаСервере();
КонецПроцедуры

// -----------------------------------------------------------------------------
// Задание 4.1: Открытие формы документа
// -----------------------------------------------------------------------------
&НаСервере
Функция ОткрытьФормуДокументаНаСервере(НомерДокумента)
	ОказаниеУслуг = Документы.ОказаниеУслуг.НайтиПоНомеру("00000000003");
	Если ОказаниеУслуг.Пустая() Тогда
		ОказаниеУслуг = Документы.ОказаниеУслуг.НайтиПоНомеру("00003");
	КонецЕсли;
	Если ОказаниеУслуг.Пустая() Тогда
		ОказаниеУслуг = Документы.ОказаниеУслуг.НайтиПоНомеру(Строка(НомерДокумента));
	КонецЕсли;
	Если ОказаниеУслуг.Пустая() Тогда
		Выборка = Документы.ОказаниеУслуг.Выбрать();
		Если Выборка.Следующий() Тогда
			ОказаниеУслуг = Выборка.Ссылка;
		КонецЕсли;
	КонецЕсли;
	Возврат ОказаниеУслуг;
КонецФункции

&НаКлиенте
Процедура ОткрытьФормуДокумента(Команда)
	СсылкаНаДокумент = ОткрытьФормуДокументаНаСервере(3);
	Если Не ЗначениеЗаполнено(СсылкаНаДокумент) Тогда
		ПоказатьПредупреждение(, "Документ Оказание услуг не найден!");
		Возврат;
	КонецЕсли;
	ПараметрыФормы = Новый Структура("Ключ", СсылкаНаДокумент);
	ОткрытьФорму("Документ.ОказаниеУслуг.ФормаОбъекта", ПараметрыФормы);
КонецПроцедуры

// -----------------------------------------------------------------------------
// Задание 4.2: Открытие формы списка документа с отбором
// -----------------------------------------------------------------------------
&НаСервере
Функция ОткрытиеФормыСпискаНаСервере(ПоставщикИмя)
	ПоставщикСсылка = Справочники.Поставщики.НайтиПоНаименованию(ПоставщикИмя);
	Если ПоставщикСсылка.Пустая() Тогда
		Выборка = Справочники.Поставщики.Выбрать();
		Если Выборка.Следующий() Тогда
			ПоставщикСсылка = Выборка.Ссылка;
		КонецЕсли;
	КонецЕсли;
	Возврат ПоставщикСсылка;
КонецФункции

&НаКлиенте
Процедура ОткрытиеФормыСписка(Команда)
	Поставщик = ОткрытиеФормыСпискаНаСервере("ОАО ""Азот""");
	ПараметрПоставщика = Новый Структура;
	ПараметрПоставщика.Вставить("Поставщик", Поставщик);
	
	ПараметрОтбора = Новый Структура;
	ПараметрОтбора.Вставить("Отбор", ПараметрПоставщика);
	
	ОткрытьФорму("Документ.ПриходнаяНакладная.ФормаСписка", ПараметрОтбора);
КонецПроцедуры

// -----------------------------------------------------------------------------
// Задание 4.3: Блокировка документа
// -----------------------------------------------------------------------------
&НаСервере
Процедура БлокировкаДокументаНаСервере(НовыйМассив)
	СсылкаНаДокумент = Документы.ПриходнаяНакладная.НайтиПоНомеру("00000000006");
	Если СсылкаНаДокумент.Пустая() Тогда
		СсылкаНаДокумент = Документы.ПриходнаяНакладная.НайтиПоНомеру("00006");
	КонецЕсли;
	Если СсылкаНаДокумент.Пустая() Тогда
		Выборка = Документы.ПриходнаяНакладная.Выбрать();
		Если Выборка.Следующий() Тогда
			СсылкаНаДокумент = Выборка.Ссылка;
		КонецЕсли;
	КонецЕсли;
	
	Если СсылкаНаДокумент.Пустая() Тогда
		Сообщить("Документ для блокировки не найден!");
		Возврат;
	КонецЕсли;
	
	Продажа = СсылкаНаДокумент.ПолучитьОбъект();
	
	Если Не Продажа.Заблокирован() Тогда
		Продажа.Заблокировать();
		
		Для Каждого ТекСтрока Из НовыйМассив Цикл
			НоваяСтрока = Продажа.Материалы.Добавить();
			Ном = Справочники.Номенклатура.НайтиПоНаименованию(ТекСтрока[0]);
			Если Ном.Пустая() Тогда
				Выб = Справочники.Номенклатура.Выбрать();
				Если Выб.Следующий() Тогда
					Ном = Выб.Ссылка;
				КонецЕсли;
			КонецЕсли;
			НоваяСтрока.Наименование = Ном;
			НоваяСтрока.Количество = ТекСтрока[1];
			НоваяСтрока.Цена = ТекСтрока[2];
			НоваяСтрока.Сумма = НоваяСтрока.Количество * НоваяСтрока.Цена;
			Попытка
				НоваяСтрока.Наценка = ТекСтрока[3];
				НоваяСтрока.СуммаСНаценкой = ((НоваяСтрока.Сумма * НоваяСтрока.Наценка) / 100 + НоваяСтрока.Сумма);
				НоваяСтрока.Отклонение = НоваяСтрока.Сумма - НоваяСтрока.СуммаСНаценкой;
			Исключение
			КонецПопытки;
		КонецЦикла;
		
		Продажа.Комментарий = "Документ изменён " + ТекущаяДата();
		Продажа.Записать(РежимЗаписиДокумента.Проведение);
		Продажа.Разблокировать();
		Сообщить("Документ успешно заблокирован, заполнен новыми данными и разблокирован!");
	Иначе
		Сообщить("Документ уже заблокирован другим процессом!");
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура БлокировкаДокумента(Команда)
	ЧислоНовыхСтрок = 1;
	
	НовыйМассив = Новый Массив(ЧислоНовыхСтрок, 4);
	НовыйМассив[0][0] = "Транзистор Philips";
	НовыйМассив[0][1] = 5;
	НовыйМассив[0][2] = 120.00;
	НовыйМассив[0][3] = 5.0;
	
	Для Каждого Строка Из НовыйМассив Цикл
		Для Каждого Элемент Из Строка Цикл
			Сообщить("Элемент ввода: " + Строка(Элемент));
		КонецЦикла;
	КонецЦикла;
	
	БлокировкаДокументаНаСервере(НовыйМассив);
КонецПроцедуры
'''
    with open(os.path.join(form_base, "Ext", "Form", "Module.bsl"), "w", encoding="utf-8") as f:
        f.write(module_bsl)
    print(f"[OK] Обработка {name} создана успешно!")

# ==============================================================================
# 2. DataProcessor.ЛичныеДанные (Доп. задание 1)
# ==============================================================================
def create_dp_lichnye_dannye():
    name = "ЛичныеДанные"
    synonym = "Личные данные"
    dp_uuid = gen_uuid()
    obj_uuid = gen_uuid()
    val_uuid = gen_uuid()
    mgr_uuid = gen_uuid()
    mgr_val_uuid = gen_uuid()
    form_uuid = gen_uuid()

    # 2.1 Метаданные
    dp_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<DataProcessor uuid="{dp_uuid}">
		<InternalInfo>
			<xr:GeneratedType name="DataProcessorObject.{name}" category="Object">
				<xr:TypeId>{obj_uuid}</xr:TypeId>
				<xr:ValueId>{val_uuid}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DataProcessorManager.{name}" category="Manager">
				<xr:TypeId>{mgr_uuid}</xr:TypeId>
				<xr:ValueId>{mgr_val_uuid}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>{name}</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>{synonym}</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<UseStandardCommands>true</UseStandardCommands>
			<DefaultForm>DataProcessor.{name}.Form.Форма</DefaultForm>
			<AuxiliaryForm/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<ExtendedPresentation/>
			<Explanation/>
		</Properties>
		<ChildObjects>
			<Form>Форма</Form>
		</ChildObjects>
	</DataProcessor>
</MetaDataObject>
'''
    with open(os.path.join(DP_DIR, f"{name}.xml"), "w", encoding="utf-8") as f:
        f.write(dp_xml)

    # 2.2 Форма
    form_base = os.path.join(DP_DIR, name, "Forms", "Форма")
    os.makedirs(os.path.join(form_base, "Ext", "Form"), exist_ok=True)

    form_meta = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Form uuid="{form_uuid}">
		<Properties>
			<Name>Форма</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Форма</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<FormType>Managed</FormType>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<UsePurposes>
				<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
				<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
			</UsePurposes>
		</Properties>
	</Form>
</MetaDataObject>
'''
    with open(os.path.join(DP_DIR, name, "Forms", "Форма.xml"), "w", encoding="utf-8") as f:
        f.write(form_meta)

    # 2.3 Form.xml с полями: Фамилия, Имя, Отчество, Кнопка Создать ФИО, ФИО, Дата рождения
    form_layout = f'''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Title>
		<v8:item>
			<v8:lang>ru</v8:lang>
			<v8:content>{synonym}</v8:content>
		</v8:item>
	</Title>
	<AutoTitle>false</AutoTitle>
	<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
	<ChildItems>
		<InputField name="Фамилия" id="1">
			<DataPath>Фамилия</DataPath>
			<ContextMenu name="ФамилияКонтекстноеМеню" id="2"/>
			<ExtendedTooltip name="ФамилияРасширеннаяПодсказка" id="3"/>
		</InputField>
		<InputField name="Имя" id="4">
			<DataPath>Имя</DataPath>
			<ContextMenu name="ИмяКонтекстноеМеню" id="5"/>
			<ExtendedTooltip name="ИмяРасширеннаяПодсказка" id="6"/>
		</InputField>
		<InputField name="Отчество" id="7">
			<DataPath>Отчество</DataPath>
			<ContextMenu name="ОтчествоКонтекстноеМеню" id="8"/>
			<ExtendedTooltip name="ОтчествоРасширеннаяПодсказка" id="9"/>
		</InputField>
		<Button name="СоздатьФИО" id="10">
			<Type>UsualButton</Type>
			<DefaultButton>true</DefaultButton>
			<CommandName>Form.Command.СоздатьФИО</CommandName>
			<ExtendedTooltip name="СоздатьФИОРасширеннаяПодсказка" id="11"/>
		</Button>
		<InputField name="ФИО" id="12">
			<DataPath>ФИО</DataPath>
			<ContextMenu name="ФИОКонтекстноеМеню" id="13"/>
			<ExtendedTooltip name="ФИОРасширеннаяПодсказка" id="14"/>
		</InputField>
		<InputField name="ДатаРождения" id="15">
			<DataPath>ДатаРождения</DataPath>
			<ContextMenu name="ДатаРожденияКонтекстноеМеню" id="16"/>
			<ExtendedTooltip name="ДатаРожденияРасширеннаяПодсказка" id="17"/>
		</InputField>
	</ChildItems>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:DataProcessorObject.{name}</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
		</Attribute>
		<Attribute name="Фамилия" id="2">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Фамилия</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:string</v8:Type>
				<v8:StringQualifiers>
					<v8:Length>50</v8:Length>
					<v8:AllowedLength>Variable</v8:AllowedLength>
				</v8:StringQualifiers>
			</Type>
		</Attribute>
		<Attribute name="Имя" id="3">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Имя</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:string</v8:Type>
				<v8:StringQualifiers>
					<v8:Length>50</v8:Length>
					<v8:AllowedLength>Variable</v8:AllowedLength>
				</v8:StringQualifiers>
			</Type>
		</Attribute>
		<Attribute name="Отчество" id="4">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Отчество</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:string</v8:Type>
				<v8:StringQualifiers>
					<v8:Length>50</v8:Length>
					<v8:AllowedLength>Variable</v8:AllowedLength>
				</v8:StringQualifiers>
			</Type>
		</Attribute>
		<Attribute name="ФИО" id="5">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>ФИО</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:string</v8:Type>
				<v8:StringQualifiers>
					<v8:Length>150</v8:Length>
					<v8:AllowedLength>Variable</v8:AllowedLength>
				</v8:StringQualifiers>
			</Type>
		</Attribute>
		<Attribute name="ДатаРождения" id="6">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Дата рождения</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:dateTime</v8:Type>
				<v8:DateQualifiers>
					<v8:DateFractions>Date</v8:DateFractions>
				</v8:DateQualifiers>
			</Type>
		</Attribute>
	</Attributes>
	<Commands>
		<Command name="СоздатьФИО" id="1">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Создать ФИО</v8:content>
				</v8:item>
			</Title>
			<Action>СоздатьФИО</Action>
		</Command>
	</Commands>
</Form>
'''
    with open(os.path.join(form_base, "Ext", "Form.xml"), "w", encoding="utf-8") as f:
        f.write(form_layout)

    # 2.4 Module.bsl
    module_bsl = '''&НаКлиенте
Процедура СоздатьФИО(Команда)
	СтрДата = "";
	Если ЗначениеЗаполнено(ДатаРождения) Тогда
		СтрДата = ", д.р. " + Формат(ДатаРождения, "ДФ=dd.MM.yyyy");
	КонецЕсли;
	
	ФИО = СокрЛП(Фамилия) + " " + СокрЛП(Имя) + " " + СокрЛП(Отчество) + СтрДата;
	
	ПоказатьПредупреждение(, "Введенная информация:" + Символы.ПС + ФИО);
КонецПроцедуры
'''
    with open(os.path.join(form_base, "Ext", "Form", "Module.bsl"), "w", encoding="utf-8") as f:
        f.write(module_bsl)
    print(f"[OK] Обработка {name} создана успешно!")

# ==============================================================================
# 3. DataProcessor.ИзменениеДокумента (Доп. задание 2)
# ==============================================================================
def create_dp_izmenenie_dokumenta():
    name = "ИзменениеДокумента"
    synonym = "Изменение документа"
    dp_uuid = gen_uuid()
    obj_uuid = gen_uuid()
    val_uuid = gen_uuid()
    mgr_uuid = gen_uuid()
    mgr_val_uuid = gen_uuid()
    form_uuid = gen_uuid()

    # 3.1 Метаданные
    dp_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<DataProcessor uuid="{dp_uuid}">
		<InternalInfo>
			<xr:GeneratedType name="DataProcessorObject.{name}" category="Object">
				<xr:TypeId>{obj_uuid}</xr:TypeId>
				<xr:ValueId>{val_uuid}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DataProcessorManager.{name}" category="Manager">
				<xr:TypeId>{mgr_uuid}</xr:TypeId>
				<xr:ValueId>{mgr_val_uuid}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>{name}</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>{synonym}</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<UseStandardCommands>true</UseStandardCommands>
			<DefaultForm>DataProcessor.{name}.Form.Форма</DefaultForm>
			<AuxiliaryForm/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<ExtendedPresentation/>
			<Explanation/>
		</Properties>
		<ChildObjects>
			<Form>Форма</Form>
		</ChildObjects>
	</DataProcessor>
</MetaDataObject>
'''
    with open(os.path.join(DP_DIR, f"{name}.xml"), "w", encoding="utf-8") as f:
        f.write(dp_xml)

    # 3.2 Форма
    form_base = os.path.join(DP_DIR, name, "Forms", "Форма")
    os.makedirs(os.path.join(form_base, "Ext", "Form"), exist_ok=True)

    form_meta = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Form uuid="{form_uuid}">
		<Properties>
			<Name>Форма</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Форма</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<FormType>Managed</FormType>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<UsePurposes>
				<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
				<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
			</UsePurposes>
		</Properties>
	</Form>
</MetaDataObject>
'''
    with open(os.path.join(DP_DIR, name, "Forms", "Форма.xml"), "w", encoding="utf-8") as f:
        f.write(form_meta)

    # 3.3 Form.xml (по Рисунку из методички: Приходная накладная, Склад новый, кнопка Изменить приходную накладную)
    form_layout = f'''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Title>
		<v8:item>
			<v8:lang>ru</v8:lang>
			<v8:content>{synonym}</v8:content>
		</v8:item>
	</Title>
	<AutoTitle>false</AutoTitle>
	<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
	<ChildItems>
		<InputField name="ПриходнаяНакладная" id="1">
			<DataPath>ПриходнаяНакладная</DataPath>
			<ContextMenu name="ПриходнаяНакладнаяКонтекстноеМеню" id="2"/>
			<ExtendedTooltip name="ПриходнаяНакладнаяРасширеннаяПодсказка" id="3"/>
		</InputField>
		<InputField name="СкладНовый" id="4">
			<DataPath>СкладНовый</DataPath>
			<ContextMenu name="СкладНовыйКонтекстноеМеню" id="5"/>
			<ExtendedTooltip name="СкладНовыйРасширеннаяПодсказка" id="6"/>
		</InputField>
		<Button name="ИзменитьПриходнуюНакладную" id="7">
			<Type>UsualButton</Type>
			<DefaultButton>true</DefaultButton>
			<CommandName>Form.Command.ИзменитьПриходнуюНакладную</CommandName>
			<ExtendedTooltip name="ИзменитьПриходнуюНакладнуюРасширеннаяПодсказка" id="8"/>
		</Button>
	</ChildItems>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:DataProcessorObject.{name}</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
		</Attribute>
		<Attribute name="ПриходнаяНакладная" id="2">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Приходная накладная</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:DocumentRef.ПриходнаяНакладная</v8:Type>
			</Type>
		</Attribute>
		<Attribute name="СкладНовый" id="3">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Склад новый</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Склады</v8:Type>
			</Type>
		</Attribute>
	</Attributes>
	<Commands>
		<Command name="ИзменитьПриходнуюНакладную" id="1">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Изменить приходную накладную</v8:content>
				</v8:item>
			</Title>
			<Action>ИзменитьПриходнуюНакладную</Action>
		</Command>
	</Commands>
</Form>
'''
    with open(os.path.join(form_base, "Ext", "Form.xml"), "w", encoding="utf-8") as f:
        f.write(form_layout)

    # 3.4 Module.bsl
    module_bsl = '''&НаСервере
Процедура ИзменитьПриходнуюНакладнуюНаСервере()
	Если Не ЗначениеЗаполнено(ПриходнаяНакладная) Тогда
		ВызватьИсключение "Не выбран документ Приходная накладная!";
	КонецЕсли;
	
	ДокОбъект = ПриходнаяНакладная.ПолучитьОбъект();
	Если ЗначениеЗаполнено(СкладНовый) Тогда
		ДокОбъект.Склад = СкладНовый;
	КонецЕсли;
	
	ДокОбъект.Комментарий = "Склад изменен при помощи обработки";
	ДокОбъект.Записать(РежимЗаписиДокумента.Проведение);
	Сообщить("Документ " + Строка(ПриходнаяНакладная) + " успешно обновлен!");
КонецПроцедуры

&НаКлиенте
Процедура ИзменитьПриходнуюНакладную(Команда)
	Если Не ЗначениеЗаполнено(ПриходнаяНакладная) Тогда
		ПоказатьПредупреждение(, "Пожалуйста, выберите документ Приходная накладная!");
		Возврат;
	КонецЕсли;
	
	ИзменитьПриходнуюНакладнуюНаСервере();
	
	// Открываем форму документа с измененными данными
	ПараметрыФормы = Новый Структура("Ключ", ПриходнаяНакладная);
	ОткрытьФорму("Документ.ПриходнаяНакладная.ФормаОбъекта", ПараметрыФормы);
КонецПроцедуры
'''
    with open(os.path.join(form_base, "Ext", "Form", "Module.bsl"), "w", encoding="utf-8") as f:
        f.write(module_bsl)
    print(f"[OK] Обработка {name} создана успешно!")

# ==============================================================================
# 4. Обновление Configuration.xml и Subsystems\Обработки.xml
# ==============================================================================
def update_configuration_and_subsystem():
    cfg_file = os.path.join(SRC_DIR, "Configuration.xml")
    with open(cfg_file, "r", encoding="utf-8") as f:
        content = f.read()

    new_dps = [
        "DataProcessor.РаботаСДокументами",
        "DataProcessor.ЛичныеДанные",
        "DataProcessor.ИзменениеДокумента"
    ]

    for dp_full in new_dps:
        dp_name = dp_full.split(".")[1]
        elem = f"<DataProcessor>{dp_name}</DataProcessor>"
        if elem not in content:
            # Вставляем после <DataProcessor>РаботаСоСправочниками</DataProcessor>
            ref_pos = content.find("<DataProcessor>РаботаСоСправочниками</DataProcessor>")
            if ref_pos != -1:
                end_pos = ref_pos + len("<DataProcessor>РаботаСоСправочниками</DataProcessor>")
                content = content[:end_pos] + "\n\t\t\t" + elem + content[end_pos:]
            else:
                # Вставляем перед </ChildObjects> конфигурации
                co_pos = content.find("</ChildObjects>")
                if co_pos != -1:
                    content = content[:co_pos] + f"\t\t\t{elem}\n\t\t" + content[co_pos:]

    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Configuration.xml обновлен!")

    # Обновление подсистемы Обработки
    sub_file = os.path.join(SRC_DIR, "Subsystems", "Обработки.xml")
    with open(sub_file, "r", encoding="utf-8") as f:
        sub_content = f.read()

    for dp_full in new_dps:
        item = f'<xr:Item xsi:type="xr:MDObjectRef">{dp_full}</xr:Item>'
        if item not in sub_content:
            c_pos = sub_content.find("</Content>")
            if c_pos != -1:
                sub_content = sub_content[:c_pos] + f"\t\t\t\t{item}\n\t\t\t" + sub_content[c_pos:]

    with open(sub_file, "w", encoding="utf-8") as f:
        f.write(sub_content)
    print("[OK] Subsystems/Обработки.xml обновлен!")

def main():
    print("=" * 60)
    print("  Создание объектов метаданных ЛР 5.2")
    print("=" * 60)
    create_dp_rabota_s_dokumentami()
    create_dp_lichnye_dannye()
    create_dp_izmenenie_dokumenta()
    update_configuration_and_subsystem()
    print("=" * 60)
    print("  Все объекты метаданных и формы успешно созданы!")
    print("=" * 60)

if __name__ == "__main__":
    main()
