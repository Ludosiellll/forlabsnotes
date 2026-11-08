import subprocess, os

epf_bsl = """&НаКлиенте
Процедура ПриОткрытии(Отказ)
    ПроверитьДокументыНаСервере();
    ЗавершитьРаботуСистемы(Ложь);
КонецПроцедуры

&НаСервере
Процедура ПроверитьДокументыНаСервере()
    Лог = Новый ЗаписьТекста("d:\\1c_docs_status.txt", КодировкаТекста.UTF8);
    
    Для Каждого МетаДок Из Метаданные.Документы Цикл
        ИмяДок = МетаДок.Имя;
        Менеджер = Документы[ИмяДок];
        Выборка = Менеджер.Выбрать();
        Всего = 0;
        Проведено = 0;
        НеПроведено = 0;
        Пока Выборка.Следующий() Цикл
            Всего = Всего + 1;
            Если Выборка.Проведен Тогда
                Проведено = Проведено + 1;
            Иначе
                НеПроведено = НеПроведено + 1;
            КонецЕсли;
        КонецЦикла;
        Лог.ЗаписатьСтроку(ИмяДок + ": Всего=" + Строка(Всего) + ", Проведено=" + Строка(Проведено) + ", НеПроведено=" + Строка(НеПроведено));
    КонецЦикла;
    
    Лог.Закрыть();
КонецПроцедуры
"""

with open(r'd:\1с лабы\1С_ЛР5_Файлы\epf_post_src\ЗаполнениеЛР4\Forms\Форма\Ext\Form\Module.bsl', 'w', encoding='utf-8') as f:
    f.write(epf_bsl)

subprocess.run(['subst', 'W:', '/D'], stderr=subprocess.DEVNULL)
subprocess.run(['subst', 'W:', r'd:\1с лабы\1С_ЛР5_Файлы'], check=True)

try:
    cmd_b = [
        r'D:\1c_app\8.3.27.1508\bin\1cv8t.exe',
        'DESIGNER', '/F', r'W:\Base1C',
        '/LoadExternalDataProcessorOrReportFromFiles',
        r'W:\epf_post_src\ЗаполнениеЛР4.xml', r'W:\ЗаполнениеЛР4.epf'
    ]
    subprocess.run(cmd_b, check=True)
    
    cmd_r = [
        r'D:\1c_app\8.3.27.1508\bin\1cv8t.exe',
        'ENTERPRISE', '/F', r'W:\Base1C',
        '/Execute', r'W:\ЗаполнениеЛР4.epf',
        '/DisableStartupMessages'
    ]
    subprocess.run(cmd_r, check=True)
    
    if os.path.exists(r'd:\1c_docs_status.txt'):
        with open(r'd:\1c_docs_status.txt', 'r', encoding='utf-8') as f:
            print('DOCUMENT POST STATUS:\n' + f.read())
finally:
    subprocess.run(['subst', 'W:', '/D'], check=True)
