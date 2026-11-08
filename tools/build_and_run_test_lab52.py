# -*- coding: utf-8 -*-
"""
tools/build_and_run_test_lab52.py
Создает, собирает и запускает тестовую внешнюю обработку в 1С:Предприятие
для автоматической проверки и выполнения всех заданий ЛР 5.2.
"""

import os
import subprocess
import uuid

BASE_DIR = r"d:\1с лабы\1С_ЛР5.2_Файлы\Base1C"
ONE_C = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
TARGET_DIR = r"d:\1с лабы\1С_ЛР5.2_Файлы"
EPF_SRC_DIR = os.path.join(TARGET_DIR, "epf_test_src")
EPF_FILE = os.path.join(TARGET_DIR, "ТестЛР52.epf")
AUDIT_LOG = os.path.join(TARGET_DIR, "audit_lab52.log")

def gen_uuid():
    return str(uuid.uuid4())

def prepare_epf_src():
    os.makedirs(os.path.join(EPF_SRC_DIR, "ТестЛР52", "Forms", "Форма", "Ext", "Form"), exist_ok=True)
    
    # 1. ТестЛР52.xml
    epf_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<ExternalDataProcessor uuid="{gen_uuid()}">
		<InternalInfo>
			<xr:ContainedObject>
				<xr:ClassId>c3831ec8-d8d5-4f93-8a22-f9bfae07327f</xr:ClassId>
				<xr:ObjectId>{gen_uuid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:GeneratedType name="ExternalDataProcessorObject.ТестЛР52" category="Object">
				<xr:TypeId>{gen_uuid()}</xr:TypeId>
				<xr:ValueId>{gen_uuid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>ТестЛР52</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Тест ЛР 5.2</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<DefaultForm>ExternalDataProcessor.ТестЛР52.Form.Форма</DefaultForm>
			<AuxiliaryForm/>
		</Properties>
		<ChildObjects>
			<Form>Форма</Form>
		</ChildObjects>
	</ExternalDataProcessor>
</MetaDataObject>
'''
    with open(os.path.join(EPF_SRC_DIR, "ТестЛР52.xml"), "w", encoding="utf-8") as f:
        f.write(epf_xml)

    # 2. Форма.xml
    form_meta = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Form uuid="{gen_uuid()}">
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
    with open(os.path.join(EPF_SRC_DIR, "ТестЛР52", "Forms", "Форма.xml"), "w", encoding="utf-8") as f:
        f.write(form_meta)

    # 3. Form.xml
    form_layout = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Title>
		<v8:item>
			<v8:lang>ru</v8:lang>
			<v8:content>Тест ЛР 5.2</v8:content>
		</v8:item>
	</Title>
	<AutoTitle>false</AutoTitle>
	<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
	<Events>
		<Event name="OnOpen">ПриОткрытии</Event>
	</Events>
	<ChildItems>
		<LabelField name="Инфо" id="1">
			<DataPath>Инфо</DataPath>
			<ContextMenu name="ИнфоКонтекстноеМеню" id="2"/>
			<ExtendedTooltip name="ИнфоРасширеннаяПодсказка" id="3"/>
		</LabelField>
	</ChildItems>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:ExternalDataProcessorObject.ТестЛР52</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
		</Attribute>
		<Attribute name="Инфо" id="2">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Инфо</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:string</v8:Type>
				<v8:StringQualifiers>
					<v8:Length>0</v8:Length>
					<v8:AllowedLength>Variable</v8:AllowedLength>
				</v8:StringQualifiers>
			</Type>
		</Attribute>
	</Attributes>
</Form>
'''
    with open(os.path.join(EPF_SRC_DIR, "ТестЛР52", "Forms", "Форма", "Ext", "Form.xml"), "w", encoding="utf-8") as f:
        f.write(form_layout)

    # 4. Module.bsl (Тестирование и проведение всех документов)
    log_path_escaped = AUDIT_LOG.replace("\\", "\\\\")
    module_bsl = f'''&НаКлиенте
Процедура ПриОткрытии(Отказ)
	ВыполнитьТест();
	ЗавершитьРаботуСистемы(Ложь);
КонецПроцедуры

&НаСервере
Процедура ВыполнитьТест()
	Лог = Новый ЗаписьТекста("{log_path_escaped}", КодировкаТекста.UTF8);
	Лог.ЗаписатьСтроку("=== АУДИТ И ВЫПОЛНЕНИЕ ЛАБОРАТОРНОЙ РАБОТЫ №5.2 ===");
	
	// 1. Проверка созданных обработок в метаданных
	Лог.ЗаписатьСтроку("--- ОБРАБОТКИ В МЕТАДАННЫХ ---");
	Для Каждого Мета Из Метаданные.Обработки Цикл
		Лог.ЗаписатьСтроку("Обработка: " + Мета.Имя + " (" + Мета.Синоним + ")");
	КонецЦикла;
	
	// 2. Тестирование Задания 1: Создание документа через ПриходнаяНакладная
	Лог.ЗаписатьСтроку("--- ТЕСТ ЗАДАНИЯ 1: СоздатьДокумент ---");
	Попытка
		НовыйДок = Документы.ПриходнаяНакладная.СоздатьДокумент();
		НовыйДок.Дата = ТекущаяДата();
		
		Пост = Справочники.Поставщики.НайтиПоНаименованию("ОАО ""Азот""");
		Если Пост.Пустая() Тогда
			ВыбП = Справочники.Поставщики.Выбрать();
			Если ВыбП.Следующий() Тогда
				Пост = ВыбП.Ссылка;
			КонецЕсли;
		КонецЕсли;
		НовыйДок.Поставщик = Пост;
		
		Скл = Справочники.Склады.НайтиПоКоду("000000001");
		Если Скл.Пустая() Тогда
			Скл = Справочники.Склады.НайтиПоНаименованию("Основной");
		КонецЕсли;
		НовыйДок.Склад = Скл;
		
		НовыйДок.Комментарий = "#Документ создан автоматически обработкой";
		
		СтрТЧ = НовыйДок.Материалы.Добавить();
		Ном = Справочники.Номенклатура.НайтиПоНаименованию("Транзистор Philips");
		Если Ном.Пустая() Тогда
			ВыбН = Справочники.Номенклатура.Выбрать();
			Если ВыбН.Следующий() Тогда
				Ном = ВыбН.Ссылка;
			КонецЕсли;
		КонецЕсли;
		СтрТЧ.Наименование = Ном;
		СтрТЧ.Количество = 10;
		СтрТЧ.Цена = 97.10;
		СтрТЧ.Сумма = СтрТЧ.Количество * СтрТЧ.Цена;
		Попытка
			СтрТЧ.Наценка = -3.5;
			СтрТЧ.СуммаСНаценкой = ((СтрТЧ.Сумма * СтрТЧ.Наценка) / 100 + СтрТЧ.Сумма);
			СтрТЧ.Отклонение = СтрТЧ.Сумма - СтрТЧ.СуммаСНаценкой;
		Исключение
		КонецПопытки;
		
		НовыйДок.Записать(РежимЗаписиДокумента.Запись);
		НовыйДок.Записать(РежимЗаписиДокумента.Проведение);
		Лог.ЗаписатьСтроку("[OK] Документ создан и проведен: " + Строка(НовыйДок.Ссылка) + " Номер: " + НовыйДок.Номер);
	Исключение
		Лог.ЗаписатьСтроку("[ERR] Ошибка создания документа: " + ОписаниеОшибки());
	КонецПопытки;
	
	// 3. Тестирование Задания 2: Копия документа
	Лог.ЗаписатьСтроку("--- ТЕСТ ЗАДАНИЯ 2: КопияДокумента ---");
	Попытка
		Выб = Документы.ПриходнаяНакладная.Выбрать();
		Если Выб.Следующий() Тогда
			Исходный = Выб.Ссылка;
			Копия = Исходный.Скопировать();
			Копия.Дата = ТекущаяДата();
			Копия.Комментарий = "КОПИЯ " + Строка(Исходный);
			Копия.Записать(РежимЗаписиДокумента.Проведение);
			Лог.ЗаписатьСтроку("[OK] Копия документа создана и проведена: " + Строка(Копия.Ссылка));
		КонецЕсли;
	Исключение
		Лог.ЗаписатьСтроку("[ERR] Ошибка копирования: " + ОписаниеОшибки());
	КонецПопытки;
	
	// 4. Тестирование Доп. задания 2: Изменение документа
	Лог.ЗаписатьСтроку("--- ТЕСТ ДОП. ЗАДАНИЯ 2: Изменение документа ---");
	Попытка
		Выб = Документы.ПриходнаяНакладная.Выбрать();
		Если Выб.Следующий() Тогда
			Док = Выб.Ссылка.ПолучитьОбъект();
			СклРозн = Справочники.Склады.НайтиПоНаименованию("Розничный");
			Если Не СклРозн.Пустая() Тогда
				Док.Склад = СклРозн;
			КонецЕсли;
			Док.Комментарий = "Склад изменен при помощи обработки";
			Док.Записать(РежимЗаписиДокумента.Проведение);
			Лог.ЗаписатьСтроку("[OK] Документ изменен и проведен со складом: " + Строка(Док.Склад));
		КонецЕсли;
	Исключение
		Лог.ЗаписатьСтроку("[ERR] Ошибка изменения документа: " + ОписаниеОшибки());
	КонецПопытки;
	
	// 5. ЖЕЛЕЗНОЕ ПРАВИЛО: ПРОВЕДЕНИЕ 100% УЧЕТНЫХ ДОКУМЕНТОВ
	Лог.ЗаписатьСтроку("--- ПРОВЕРКА И ПРОВЕДЕНИЕ ВСЕХ ДОКУМЕНТОВ ---");
	ВсегоДок = 0;
	ПроведеноДок = 0;
	НеПроведеноДок = 0;
	
	Для Каждого Мета Из Метаданные.Документы Цикл
		Менеджер = Документы[Мета.Имя];
		Выборка = Менеджер.Выбрать();
		Пока Выборка.Следующий() Цикл
			ВсегоДок = ВсегоДок + 1;
			Если Выборка.Проведен Тогда
				ПроведеноДок = ПроведеноДок + 1;
			Иначе
				// Принудительно проводим!
				Попытка
					ОбъектДок = Выборка.ПолучитьОбъект();
					ОбъектДок.Записать(РежимЗаписиДокумента.Проведение);
					ПроведеноДок = ПроведеноДок + 1;
					Лог.ЗаписатьСтроку("Проведен непроведенный: " + Строка(Выборка.Ссылка));
				Исключение
					НеПроведеноДок = НеПроведеноДок + 1;
					Лог.ЗаписатьСтроку("[WARN] Не удалось провести: " + Строка(Выборка.Ссылка) + " - " + ОписаниеОшибки());
				КонецПопытки;
			КонецЕсли;
		КонецЦикла;
	КонецЦикла;
	
	Лог.ЗаписатьСтроку("ИТОГО ДОКУМЕНТОВ: " + Строка(ВсегоДок));
	Лог.ЗаписатьСтроку("ИЗ НИХ ПРОВЕДЕНО: " + Строка(ПроведеноДок));
	Лог.ЗаписатьСтроку("НЕ ПРОВЕДЕНО: " + Строка(НеПроведеноДок));
	
	Лог.Закрыть();
КонецПроцедуры
'''
    with open(os.path.join(EPF_SRC_DIR, "ТестЛР52", "Forms", "Форма", "Ext", "Form", "Module.bsl"), "w", encoding="utf-8") as f:
        f.write(module_bsl)
    print("[OK] Исходники EPF подготовлены!")

def build_epf():
    xml_root = os.path.join(EPF_SRC_DIR, "ТестЛР52.xml")
    log_f = os.path.join(TARGET_DIR, "epf_build.log")
    cmd = [
        ONE_C, "DESIGNER",
        "/F", BASE_DIR,
        "/LoadExternalDataProcessorOrReportFromFiles", xml_root, EPF_FILE,
        "/Out", log_f
    ]
    print("[*] Сборка EPF ТестЛР52...")
    res = subprocess.run(cmd, capture_output=True)
    print("EPF build exit code:", res.returncode)

def run_enterprise():
    log_f = os.path.join(TARGET_DIR, "enterprise_test.log")
    cmd = [
        ONE_C, "ENTERPRISE",
        "/F", BASE_DIR,
        "/Execute", EPF_FILE,
        "/Out", log_f
    ]
    print("[*] Запуск 1С:Предприятие для выполнения теста...")
    res = subprocess.run(cmd, capture_output=True)
    print("Enterprise exit code:", res.returncode)

def main():
    prepare_epf_src()
    build_epf()
    run_enterprise()
    
    if os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            print("\n" + "=" * 60)
            print("  РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ ТЕСТА В 1С:ПРЕДПРИЯТИЕ")
            print("=" * 60)
            print(f.read())
            print("=" * 60)
    else:
        print("[ERR] Файл audit_lab52.log не был создан!")

if __name__ == "__main__":
    main()
