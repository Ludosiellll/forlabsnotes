# -*- coding: utf-8 -*-
"""
Seeding script for 1C Lab 7:
Populates:
- Валюты: Рубль (000000001), Доллар (000000002)
- Контрагенты: ООО "Василёк" (000000001), ООО "Мак" (000000002)
- Номенклатура: Телефон (000000001, Ложь), Компьютер (000000002, Ложь), Доставка (000000003, Истина), Настройка (000000004, Истина)
- КурсыВалют:
  01.01.2020: Рубль = 1.00
  01.01.2020: Доллар = 60.00
  15.01.2020: Доллар = 70.00
- Константа: ВестиМноговалютныйУчёт = Истина
- Продажи (4 документа):
  000000001 от 05.01.2020 21:18:08 (Василёк, Рубль, Компьютер 55000 + Доставка 3000 = 58000)
  000000002 от 01.01.2020 21:09:55 (Василёк, Доллар, Компьютер 800 + Доставка 200 = 1000)
  000000003 от 01.01.2020 21:18:07 (Мак, Рубль, Компьютер 80000 + Телефон 45000 + Доставка 5000 = 130000)
  000000004 от 16.01.2020 21:18:09 (Василёк, Доллар, Компьютер 800 + Доставка 200 = 1000)
- Проверяет обороты регистра Продажи:
  Компьютер: 239 000,00
  Телефон: 45 000,00
  Доставка: 34 000,00
  Итого: 318 000,00
"""

import os
import uuid
import subprocess
import shutil

SCRATCH_DIR = r"C:\Users\denis\.gemini\antigravity\brain\683daffc-c22c-4e09-aadd-6db28d5a41f9\scratch\epf_lr7"
EPF_SRC = os.path.join(SCRATCH_DIR, "src")
EPF_FILE = os.path.join(SCRATCH_DIR, "ЗаполнениеДанных.epf")
STATUS_FILE = os.path.join(SCRATCH_DIR, "seed_status.txt")

BIN_1CV8T = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
BIN_1CV8CT = r"D:\1c_app\8.3.27.1508\bin\1cv8ct.exe"

def uid():
    return str(uuid.uuid4())

def write_f(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def create_epf_source():
    if os.path.exists(SCRATCH_DIR):
        shutil.rmtree(SCRATCH_DIR)
    os.makedirs(EPF_SRC, exist_ok=True)

    root_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<ExternalDataProcessor uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="ExternalDataProcessorObject.ЗаполнениеДанных" category="Object">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>ЗаполнениеДанных</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Заполнение данных</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<DefaultForm>ExternalDataProcessor.ЗаполнениеДанных.Form.Форма</DefaultForm>
			<AuxiliaryForm/>
		</Properties>
		<ChildObjects>
			<Form>Форма</Form>
		</ChildObjects>
	</ExternalDataProcessor>
</MetaDataObject>'''
    write_f(os.path.join(EPF_SRC, "ЗаполнениеДанных.xml"), root_xml)
    write_f(os.path.join(EPF_SRC, "ЗаполнениеДанных", "Ext", "ObjectModule.bsl"), "")

    form_desc_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Form uuid="{uid()}">
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
			<ExtendedPresentation/>
		</Properties>
	</Form>
</MetaDataObject>'''
    write_f(os.path.join(EPF_SRC, "ЗаполнениеДанных", "Forms", "Форма.xml"), form_desc_xml)

    form_ui_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Events>
		<Event name="OnOpen">ПриОткрытии</Event>
	</Events>
	<ChildItems>
		<LabelDecoration name="Декорация" id="2">
			<Title formatted="false">
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Заполнение данных ЛР7</v8:content>
				</v8:item>
			</Title>
		</LabelDecoration>
	</ChildItems>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type>cfg:ExternalDataProcessorObject.ЗаполнениеДанных</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
		</Attribute>
	</Attributes>
</Form>'''
    write_f(os.path.join(EPF_SRC, "ЗаполнениеДанных", "Forms", "Форма", "Ext", "Form.xml"), form_ui_xml)

    status_file_escaped = STATUS_FILE.replace('\\', '\\\\')

    bsl_content = f'''&НаКлиенте
Процедура ПриОткрытии(Отказ)
	Попытка
		ЗаполнитьДанныеНаСервере();
	Исключение
		ЗаписьОшибки = Новый ЗаписьТекста("{status_file_escaped}", КодировкаТекста.UTF8);
		ЗаписьОшибки.ЗаписатьСтроку("ERROR: " + ОписаниеОшибки());
		ЗаписьОшибки.Закрыть();
	КонецПопытки;
	ЗавершитьРаботуСистемы(Ложь);
КонецПроцедуры

&НаСервере
Процедура ЗаполнитьДанныеНаСервере()
	
	Лог = Новый Массив;
	Лог.Добавить("START SEEDING");
	
	// 1. Константа ВестиМноговалютныйУчёт
	Константы.ВестиМноговалютныйУчёт.Установить(Истина);
	Лог.Добавить("Константа ВестиМноговалютныйУчёт = Истина");
	
	// 2. Валюты
	// Рубль (предопределенный)
	ВалРубль = Справочники.Валюты.Рубль;
	Если ВалРубль.Пустая() Тогда
		Об = Справочники.Валюты.СоздатьЭлемент();
		Об.Наименование = "Рубль";
		Об.Код = "000000001";
		Об.Записать();
		ВалРубль = Об.Ссылка;
	КонецЕсли;
	
	// Доллар
	ВалДоллар = Справочники.Валюты.НайтиПоНаименованию("Доллар");
	Если ВалДоллар.Пустая() Тогда
		Об = Справочники.Валюты.СоздатьЭлемент();
		Об.Наименование = "Доллар";
		Об.Код = "000000002";
		Об.Записать();
		ВалДоллар = Об.Ссылка;
	КонецЕсли;
	Лог.Добавить("Валюты созданы");
	
	// 3. Контрагенты
	КонтрВасилек = Справочники.Контрагенты.НайтиПоНаименованию("ООО ""Василёк""");
	Если КонтрВасилек.Пустая() Тогда
		Об = Справочники.Контрагенты.СоздатьЭлемент();
		Об.Наименование = "ООО ""Василёк""";
		Об.Код = "000000001";
		Об.Записать();
		КонтрВасилек = Об.Ссылка;
	КонецЕсли;
	
	КонтрМак = Справочники.Контрагенты.НайтиПоНаименованию("ООО ""Мак""");
	Если КонтрМак.Пустая() Тогда
		Об = Справочники.Контрагенты.СоздатьЭлемент();
		Об.Наименование = "ООО ""Мак""";
		Об.Код = "000000002";
		Об.Записать();
		КонтрМак = Об.Ссылка;
	КонецЕсли;
	Лог.Добавить("Контрагенты созданы");
	
	// 4. Номенклатура2
	// Телефон (Ложь)
	НомТелефон = Справочники.Номенклатура2.НайтиПоНаименованию("Телефон");
	Если НомТелефон.Пустая() Тогда
		Об = Справочники.Номенклатура2.СоздатьЭлемент();
		Об.Наименование = "Телефон";
		Об.Код = "000000001";
		Об.ЭтоУслуга = Ложь;
		Об.Записать();
		НомТелефон = Об.Ссылка;
	КонецЕсли;
	
	// Компьютер (Ложь)
	НомКомпьютер = Справочники.Номенклатура2.НайтиПоНаименованию("Компьютер");
	Если НомКомпьютер.Пустая() Тогда
		Об = Справочники.Номенклатура2.СоздатьЭлемент();
		Об.Наименование = "Компьютер";
		Об.Код = "000000002";
		Об.ЭтоУслуга = Ложь;
		Об.Записать();
		НомКомпьютер = Об.Ссылка;
	КонецЕсли;
	
	// Доставка (Истина)
	НомДоставка = Справочники.Номенклатура2.НайтиПоНаименованию("Доставка");
	Если НомДоставка.Пустая() Тогда
		Об = Справочники.Номенклатура2.СоздатьЭлемент();
		Об.Наименование = "Доставка";
		Об.Код = "000000003";
		Об.ЭтоУслуга = Истина;
		Об.Записать();
		НомДоставка = Об.Ссылка;
	КонецЕсли;
	
	// Настройка (Истина)
	НомНастройка = Справочники.Номенклатура2.НайтиПоНаименованию("Настройка");
	Если НомНастройка.Пустая() Тогда
		Об = Справочники.Номенклатура2.СоздатьЭлемент();
		Об.Наименование = "Настройка";
		Об.Код = "000000004";
		Об.ЭтоУслуга = Истина;
		Об.Записать();
		НомНастройка = Об.Ссылка;
	КонецЕсли;
	Лог.Добавить("Номенклатура2 создана");
	
	// 5. КурсыВалют
	// 01.01.2020: Рубль = 1.00
	МЗ = РегистрыСведений.КурсыВалют.СоздатьМенеджерЗаписи();
	МЗ.Период = Дата(2020, 1, 1);
	МЗ.Валюта = ВалРубль;
	МЗ.Курс = 1.00;
	МЗ.Записать(Истина);
	
	// 01.01.2020: Доллар = 60.00
	МЗ = РегистрыСведений.КурсыВалют.СоздатьМенеджерЗаписи();
	МЗ.Период = Дата(2020, 1, 1);
	МЗ.Валюта = ВалДоллар;
	МЗ.Курс = 60.00;
	МЗ.Записать(Истина);
	
	// 15.01.2020: Доллар = 70.00
	МЗ = РегистрыСведений.КурсыВалют.СоздатьМенеджерЗаписи();
	МЗ.Период = Дата(2020, 1, 15);
	МЗ.Валюта = ВалДоллар;
	МЗ.Курс = 70.00;
	МЗ.Записать(Истина);
	Лог.Добавить("Курсы валют записаны");
	
	// Очищаем старые документы Продажи если были
	Выборка = Документы.Продажи.Выбрать();
	Пока Выборка.Следующий() Цикл
		Об = Выборка.ПолучитьОбъект();
		Об.Удалить();
	КонецЦикла;
	
	// 6. Документы Продажи
	// Документ 1: 05.01.2020 21:18:08, Номер 000000001, ООО "Василёк", Рубль
	// Компьютер 55000, Доставка 3000 -> Всего 58000
	Док1 = Документы.Продажи.СоздатьДокумент();
	Док1.Номер = "000000001";
	Док1.Дата = Дата(2020, 1, 5, 21, 18, 8);
	Док1.Покупатель = КонтрВасилек;
	Док1.Валюта = ВалРубль;
	
	СтрТ = Док1.СписокТоваров.Добавить();
	СтрТ.Товар = НомКомпьютер;
	СтрТ.Сумма = 55000.00;
	
	СтрУ = Док1.СписокУслуг.Добавить();
	СтрУ.Услуга = НомДоставка;
	СтрУ.Сумма = 3000.00;
	
	Док1.ВсегоКОплате = 58000.00;
	Док1.Записать(РежимЗаписиДокумента.Проведение);
	
	// Документ 2: 01.01.2020 21:09:55, Номер 000000002, ООО "Василёк", Доллар
	// Компьютер 800, Доставка 200 -> Всего 1000
	Док2 = Документы.Продажи.СоздатьДокумент();
	Док2.Номер = "000000002";
	Док2.Дата = Дата(2020, 1, 1, 21, 9, 55);
	Док2.Покупатель = КонтрВасилек;
	Док2.Валюта = ВалДоллар;
	
	СтрТ = Док2.СписокТоваров.Добавить();
	СтрТ.Товар = НомКомпьютер;
	СтрТ.Сумма = 800.00;
	
	СтрУ = Док2.СписокУслуг.Добавить();
	СтрУ.Услуга = НомДоставка;
	СтрУ.Сумма = 200.00;
	
	Док2.ВсегоКОплате = 1000.00;
	Док2.Записать(РежимЗаписиДокумента.Проведение);
	
	// Документ 3: 01.01.2020 21:18:07, Номер 000000003, ООО "Мак", Рубль
	// Компьютер 80000, Телефон 45000, Доставка 5000 -> Всего 130000
	Док3 = Документы.Продажи.СоздатьДокумент();
	Док3.Номер = "000000003";
	Док3.Дата = Дата(2020, 1, 1, 21, 18, 7);
	Док3.Покупатель = КонтрМак;
	Док3.Валюта = ВалРубль;
	
	СтрТ = Док3.СписокТоваров.Добавить();
	СтрТ.Товар = НомКомпьютер;
	СтрТ.Сумма = 80000.00;
	
	СтрТ = Док3.СписокТоваров.Добавить();
	СтрТ.Товар = НомТелефон;
	СтрТ.Сумма = 45000.00;
	
	СтрУ = Док3.СписокУслуг.Добавить();
	СтрУ.Услуга = НомДоставка;
	СтрУ.Сумма = 5000.00;
	
	Док3.ВсегоКОплате = 130000.00;
	Док3.Записать(РежимЗаписиДокумента.Проведение);
	
	// Документ 4: 16.01.2020 21:18:09, Номер 000000004, ООО "Василёк", Доллар
	// Компьютер 800, Доставка 200 -> Всего 1000
	Док4 = Документы.Продажи.СоздатьДокумент();
	Док4.Номер = "000000004";
	Док4.Дата = Дата(2020, 1, 16, 21, 18, 9);
	Док4.Покупатель = КонтрВасилек;
	Док4.Валюта = ВалДоллар;
	
	СтрТ = Док4.СписокТоваров.Добавить();
	СтрТ.Товар = НомКомпьютер;
	СтрТ.Сумма = 800.00;
	
	СтрУ = Док4.СписокУслуг.Добавить();
	СтрУ.Услуга = НомДоставка;
	СтрУ.Сумма = 200.00;
	
	Док4.ВсегоКОплате = 1000.00;
	Док4.Записать(РежимЗаписиДокумента.Проведение);
	Лог.Добавить("Документы Продажи проведены");
	
	// 7. Проверка оборотов регистра накопления
	Запрос = Новый Запрос;
	Запрос.Текст = 
		"ВЫБРАТЬ
		|	ПродажиОбороты.Номенклатура.Наименование КАК Номенклатура,
		|	ПродажиОбороты.СуммаОборот КАК Сумма
		|ИЗ
		|	РегистрНакопления.Продажи.Обороты(,,, ) КАК ПродажиОбороты
		|УПОРЯДОЧИТЬ ПО
		|	Сумма УБЫВ";
	
	Результат = Запрос.Выполнить();
	Выборка = Результат.Выбрать();
	ИтогСумма = 0;
	Лог.Добавить("--- ОБОРОТЫ РЕГИСТРА ПРОДАЖИ ---");
	Пока Выборка.Следующий() Цикл
		Лог.Добавить(Строка(Выборка.Номенклатура) + ": " + Формат(Выборка.Сумма, "ЧДЦ=2"));
		ИтогСумма = ИтогСумма + Выборка.Сумма;
	КонецЦикла;
	Лог.Добавить("ИТОГО СУММА: " + Формат(ИтогСумма, "ЧДЦ=2"));
	
	// Запись статуса
	ЗаписьСтатуса = Новый ЗаписьТекста("{status_file_escaped}", КодировкаТекста.UTF8);
	Для Каждого СтрЛога Из Лог Цикл
		ЗаписьСтатуса.ЗаписатьСтроку(СтрЛога);
	КонецЦикла;
	ЗаписьСтатуса.Закрыть();
	
КонецПроцедуры
'''
    write_f(os.path.join(EPF_SRC, "ЗаполнениеДанных", "Forms", "Форма", "Ext", "Form", "Module.bsl"), bsl_content)
    print("EPF source files written to:", EPF_SRC)

def run():
    create_epf_source()

    # 1. Mount virtual drive W: for clean ASCII paths
    subprocess.run("subst W: /D", shell=True, capture_output=True)
    subprocess.run(r'subst W: "d:\1с лабы\1С_ЛР7_Файлы"', shell=True, capture_output=True)

    try:
        # Build EPF using Designer
        build_log = os.path.join(SCRATCH_DIR, "build_epf.log")
        xml_root = os.path.join(EPF_SRC, "ЗаполнениеДанных.xml")
        
        print("Compiling EPF...")
        cmd_build = f'"{BIN_1CV8T}" DESIGNER /F "W:\\Base1C" /DisableStartupDialogs /LoadExternalDataProcessorOrReportFromFiles "{xml_root}" "{EPF_FILE}" /Out "{build_log}"'
        res = subprocess.run(cmd_build, shell=True, capture_output=True, text=True)
        print("Build EPF exit code:", res.returncode)
        if os.path.exists(build_log):
            with open(build_log, "r", encoding="cp1251", errors="replace") as f:
                print("Build Log:\n", f.read())

        if not os.path.exists(EPF_FILE):
            print("ERROR: EPF was not built!")
            return

        print("Executing EPF in Thin Client...")
        cmd_exec = f'"{BIN_1CV8CT}" /F "W:\\Base1C" /Execute "{EPF_FILE}" /DisableStartupDialogs'
        res_exec = subprocess.run(cmd_exec, shell=True, capture_output=True, text=True, timeout=45)
        print("Exec exit code:", res_exec.returncode)

        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                print("STATUS FILE CONTENT:\n", content.encode("ascii", errors="backslashreplace").decode("ascii"))
        else:
            print("WARNING: Status file was not created!")

    finally:
        subprocess.run("subst W: /D", shell=True, capture_output=True)
        print("Unmounted W:")

if __name__ == "__main__":
    run()
