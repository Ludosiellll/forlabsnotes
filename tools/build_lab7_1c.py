# -*- coding: utf-8 -*-
"""
Builder and seeder for 1C Lab 7:
«Разработка конфигурации для учета доходов от продаж товаров»
(В сборнике лабораторных работ — Лабораторная работа №15, стр. 315-350)
Студент: Лабынцев Денис Янушевич, группа РС02-23
"""

import os
import uuid
import subprocess
import shutil
import time

BASE_DIR = r"d:\1с лабы\1С_ЛР7_Файлы"
SRC_DIR = os.path.join(BASE_DIR, "src")
IB_DIR = os.path.join(BASE_DIR, "Base1C")
BIN_1CV8T = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
BIN_1CV8CT = r"D:\1c_app\8.3.27.1508\bin\1cv8ct.exe"

def uid():
    return str(uuid.uuid4())

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def build_src_tree():
    print("Generating XML source metadata...")
    os.makedirs(SRC_DIR, exist_ok=True)

    # 1. Configuration.xml
    conf_uuid = uid()
    conf_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Configuration uuid="{conf_uuid}">
		<InternalInfo>
			<xr:ContainedObject>
				<xr:ClassId>9cd510cd-abfc-11d4-9434-004095e12fc7</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:ContainedObject>
				<xr:ClassId>9fcd25a0-4822-11d4-9414-008048da11f9</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:ContainedObject>
				<xr:ClassId>e3687481-0a87-462c-a166-9f34594f9bba</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:ContainedObject>
				<xr:ClassId>9de14907-ec23-4a07-96f0-85521cb6b53b</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:ContainedObject>
				<xr:ClassId>51f2d5d8-ea4d-4064-8892-82951750031e</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:ContainedObject>
				<xr:ClassId>e68182ea-4237-4383-967f-90c1e3370bc7</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
			<xr:ContainedObject>
				<xr:ClassId>fb282519-d103-4dd3-bc12-cb271d631dfc</xr:ClassId>
				<xr:ObjectId>{uid()}</xr:ObjectId>
			</xr:ContainedObject>
		</InternalInfo>
		<Properties>
			<Name>Лабынцев</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Учет доходов от продаж товаров (Лабынцев)</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<NamePrefix/>
			<ConfigurationExtensionCompatibilityMode>Version8_3_27</ConfigurationExtensionCompatibilityMode>
			<DefaultRunMode>ManagedApplication</DefaultRunMode>
			<UsePurposes>
				<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
			</UsePurposes>
			<ScriptVariant>Russian</ScriptVariant>
			<DefaultRoles/>
			<Vendor/>
			<Version/>
			<UpdateCatalogAddress/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<UseManagedFormInOrdinaryApplication>false</UseManagedFormInOrdinaryApplication>
			<UseOrdinaryFormInManagedApplication>false</UseOrdinaryFormInManagedApplication>
			<AdditionalFullTextSearchDictionaries/>
			<CommonSettingsStorage/>
			<ReportsUserSettingsStorage/>
			<ReportsVariantsStorage/>
			<FormDataSettingsStorage/>
			<DynamicListsUserSettingsStorage/>
			<URLExternalDataStorage/>
			<Content/>
			<DefaultReportForm/>
			<DefaultReportVariantForm/>
			<DefaultReportSettingsForm/>
			<DefaultReportAppearanceTemplate/>
			<DefaultDynamicListSettingsForm/>
			<DefaultSearchForm/>
			<DefaultDataHistoryChangeHistoryForm/>
			<DefaultDataHistoryVersionDataForm/>
			<DefaultDataHistoryVersionDifferencesForm/>
			<DefaultCollaborationSystemUsersChoiceForm/>
			<RequiredMobileApplicationPermissions/>
			<UsedMobileApplicationFunctionalities>
				<app:functionality>
					<app:functionality>Biometrics</app:functionality>
					<app:use>true</app:use>
				</app:functionality>
				<app:functionality>
					<app:functionality>OSBackup</app:functionality>
					<app:use>true</app:use>
				</app:functionality>
			</UsedMobileApplicationFunctionalities>
			<StandaloneConfigurationRestrictionRoles/>
			<MobileApplicationURLs/>
			<AllowedIncomingShareRequestTypes/>
			<MainClientApplicationWindowMode>Normal</MainClientApplicationWindowMode>
			<DefaultInterface/>
			<DefaultStyle/>
			<DefaultLanguage>Language.Русский</DefaultLanguage>
			<BriefInformation/>
			<DetailedInformation/>
			<Copyright/>
			<VendorInformationAddress/>
			<ConfigurationInformationAddress/>
			<DataLockControlMode>Managed</DataLockControlMode>
			<ObjectAutonumerationMode>NotAutoFree</ObjectAutonumerationMode>
			<ModalityUseMode>Use</ModalityUseMode>
			<SynchronousPlatformExtensionAndAddInCallUseMode>Use</SynchronousPlatformExtensionAndAddInCallUseMode>
			<InterfaceCompatibilityMode>Taxi</InterfaceCompatibilityMode>
			<DatabaseTablespacesUseMode>DontUse</DatabaseTablespacesUseMode>
			<CompatibilityMode>Version8_3_27</CompatibilityMode>
			<DefaultConstantsForm/>
		</Properties>
		<ChildObjects>
			<Language>Русский</Language>
			<Subsystem>Справочники</Subsystem>
			<Subsystem>Документы</Subsystem>
			<Subsystem>Регистры</Subsystem>
			<Subsystem>Отчёты</Subsystem>
			<Subsystem>Сервис</Subsystem>
			<Constant>ВестиМноговалютныйУчёт</Constant>
			<FunctionalOption>ВестиМноговалютныйУчёт</FunctionalOption>
			<Catalog>Номенклатура</Catalog>
			<Catalog>Контрагенты</Catalog>
			<Catalog>Валюты</Catalog>
			<Document>Продажи</Document>
			<Report>Продажи</Report>
			<InformationRegister>КурсыВалют</InformationRegister>
			<AccumulationRegister>Продажи</AccumulationRegister>
		</ChildObjects>
	</Configuration>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Configuration.xml"), conf_xml)

    # 2. Languages/Русский.xml
    lang_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Language uuid="{uid()}">
		<Properties>
			<Name>Русский</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Русский</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<LanguageCode>ru</LanguageCode>
		</Properties>
	</Language>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Languages", "Русский.xml"), lang_xml)

    # 3. Subsystems
    subsystems = [
        ("Справочники", ["Catalog.Номенклатура", "Catalog.Контрагенты", "Catalog.Валюты"]),
        ("Документы", ["Document.Продажи"]),
        ("Регистры", ["InformationRegister.КурсыВалют", "AccumulationRegister.Продажи"]),
        ("Отчёты", ["Report.Продажи"]),
        ("Сервис", ["Constant.ВестиМноговалютныйУчёт", "FunctionalOption.ВестиМноговалютныйУчёт"])
    ]
    for sub_name, items in subsystems:
        content_items = "\n".join([f"\t\t\t\t<xr:Item xsi:type=\"xr:MDObjectRef\">{it}</xr:Item>" for it in items])
        sub_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Subsystem uuid="{uid()}">
		<Properties>
			<Name>{sub_name}</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>{sub_name}</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<IncludeInCommandInterface>true</IncludeInCommandInterface>
			<UseOneCommand>false</UseOneCommand>
			<Explanation/>
			<Picture/>
			<Content>
{content_items}
			</Content>
		</Properties>
		<ChildObjects/>
	</Subsystem>
</MetaDataObject>'''
        write_file(os.path.join(SRC_DIR, "Subsystems", f"{sub_name}.xml"), sub_xml)

    # 4. Catalog: Номенклатура (with attribute ЭтоУслуга)
    cat_nom_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Catalog uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="CatalogObject.Номенклатура" category="Object">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogRef.Номенклатура" category="Ref">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogSelection.Номенклатура" category="Selection">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogList.Номенклатура" category="List">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogManager.Номенклатура" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>Номенклатура</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Номенклатура</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<Hierarchical>false</Hierarchical>
			<HierarchyType>HierarchyFoldersAndItems</HierarchyType>
			<LimitLevelCount>false</LimitLevelCount>
			<LevelCount>2</LevelCount>
			<FoldersOnTop>true</FoldersOnTop>
			<UseStandardCommands>true</UseStandardCommands>
			<Owners/>
			<SubordinationUse>ToItems</SubordinationUse>
			<CodeLength>9</CodeLength>
			<DescriptionLength>50</DescriptionLength>
			<CodeType>String</CodeType>
			<CodeAllowedLength>Variable</CodeAllowedLength>
			<CodeSeries>WholeCatalog</CodeSeries>
			<CheckUnique>true</CheckUnique>
			<Autonumbering>true</Autonumbering>
			<DefaultPresentation>AsDescription</DefaultPresentation>
			<Characteristics/>
			<PredefinedDataUpdate>Auto</PredefinedDataUpdate>
			<EditType>InDialog</EditType>
			<QuickChoice>false</QuickChoice>
			<ChoiceMode>BothWays</ChoiceMode>
			<InputByString>
				<xr:Field>Catalog.Номенклатура.StandardAttribute.Description</xr:Field>
				<xr:Field>Catalog.Номенклатура.StandardAttribute.Code</xr:Field>
			</InputByString>
			<SearchStringModeOnInputByString>Begin</SearchStringModeOnInputByString>
			<FullTextSearchOnInputByString>DontUse</FullTextSearchOnInputByString>
			<ChoiceDataGetModeOnInputByString>Directly</ChoiceDataGetModeOnInputByString>
			<DefaultObjectForm/>
			<DefaultFolderForm/>
			<DefaultListForm/>
			<DefaultChoiceForm/>
			<DefaultFolderChoiceForm/>
			<AuxiliaryObjectForm/>
			<AuxiliaryFolderForm/>
			<AuxiliaryListForm/>
			<AuxiliaryChoiceForm/>
			<AuxiliaryFolderChoiceForm/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<BasedOn/>
			<DataLockFields/>
			<DataLockControlMode>Managed</DataLockControlMode>
			<FullTextSearch>Use</FullTextSearch>
			<ObjectPresentation/>
			<ExtendedObjectPresentation/>
			<ListPresentation/>
			<ExtendedListPresentation/>
			<Explanation/>
			<CreateOnInput>Use</CreateOnInput>
			<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
			<DataHistory>DontUse</DataHistory>
			<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
			<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
		</Properties>
		<ChildObjects>
			<Attribute uuid="{uid()}">
				<Properties>
					<Name>ЭтоУслуга</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Это услуга</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type>xs:boolean</v8:Type>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillFromFillingValue>false</FillFromFillingValue>
					<FillValue xsi:type="xs:boolean">false</FillValue>
					<FillChecking>DontCheck</FillChecking>
					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
					<ChoiceParameterLinks/>
					<ChoiceParameters/>
					<QuickChoice>Auto</QuickChoice>
					<CreateOnInput>Auto</CreateOnInput>
					<ChoiceForm/>
					<LinkByType/>
					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<DataHistory>Use</DataHistory>
				</Properties>
			</Attribute>
		</ChildObjects>
	</Catalog>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Catalogs", "Номенклатура.xml"), cat_nom_xml)
    write_file(os.path.join(SRC_DIR, "Catalogs", "Номенклатура", "Ext", "Predefined.xml"), '''<?xml version="1.0" encoding="UTF-8"?>
<PredefinedData xmlns="http://v8.1c.ru/8.3/xcf/predef" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CatalogPredefinedItems" version="2.20"/>''')

    # 5. Catalog: Контрагенты
    cat_kontr_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Catalog uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="CatalogObject.Контрагенты" category="Object">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogRef.Контрагенты" category="Ref">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogSelection.Контрагенты" category="Selection">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogList.Контрагенты" category="List">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogManager.Контрагенты" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>Контрагенты</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Контрагенты</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<Hierarchical>false</Hierarchical>
			<HierarchyType>HierarchyFoldersAndItems</HierarchyType>
			<LimitLevelCount>false</LimitLevelCount>
			<LevelCount>2</LevelCount>
			<FoldersOnTop>true</FoldersOnTop>
			<UseStandardCommands>true</UseStandardCommands>
			<Owners/>
			<SubordinationUse>ToItems</SubordinationUse>
			<CodeLength>9</CodeLength>
			<DescriptionLength>50</DescriptionLength>
			<CodeType>String</CodeType>
			<CodeAllowedLength>Variable</CodeAllowedLength>
			<CodeSeries>WholeCatalog</CodeSeries>
			<CheckUnique>true</CheckUnique>
			<Autonumbering>true</Autonumbering>
			<DefaultPresentation>AsDescription</DefaultPresentation>
			<Characteristics/>
			<PredefinedDataUpdate>Auto</PredefinedDataUpdate>
			<EditType>InDialog</EditType>
			<QuickChoice>false</QuickChoice>
			<ChoiceMode>BothWays</ChoiceMode>
			<InputByString>
				<xr:Field>Catalog.Контрагенты.StandardAttribute.Description</xr:Field>
				<xr:Field>Catalog.Контрагенты.StandardAttribute.Code</xr:Field>
			</InputByString>
			<SearchStringModeOnInputByString>Begin</SearchStringModeOnInputByString>
			<FullTextSearchOnInputByString>DontUse</FullTextSearchOnInputByString>
			<ChoiceDataGetModeOnInputByString>Directly</ChoiceDataGetModeOnInputByString>
			<DefaultObjectForm/>
			<DefaultFolderForm/>
			<DefaultListForm/>
			<DefaultChoiceForm/>
			<DefaultFolderChoiceForm/>
			<AuxiliaryObjectForm/>
			<AuxiliaryFolderForm/>
			<AuxiliaryListForm/>
			<AuxiliaryChoiceForm/>
			<AuxiliaryFolderChoiceForm/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<BasedOn/>
			<DataLockFields/>
			<DataLockControlMode>Managed</DataLockControlMode>
			<FullTextSearch>Use</FullTextSearch>
			<ObjectPresentation/>
			<ExtendedObjectPresentation/>
			<ListPresentation/>
			<ExtendedListPresentation/>
			<Explanation/>
			<CreateOnInput>Use</CreateOnInput>
			<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
			<DataHistory>DontUse</DataHistory>
			<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
			<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
		</Properties>
		<ChildObjects/>
	</Catalog>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Catalogs", "Контрагенты.xml"), cat_kontr_xml)
    write_file(os.path.join(SRC_DIR, "Catalogs", "Контрагенты", "Ext", "Predefined.xml"), '''<?xml version="1.0" encoding="UTF-8"?>
<PredefinedData xmlns="http://v8.1c.ru/8.3/xcf/predef" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CatalogPredefinedItems" version="2.20"/>''')

    # 6. Catalog: Валюты (with Predefined Рубль)
    ruble_id = uid()
    cat_val_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Catalog uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="CatalogObject.Валюты" category="Object">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogRef.Валюты" category="Ref">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogSelection.Валюты" category="Selection">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogList.Валюты" category="List">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="CatalogManager.Валюты" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>Валюты</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Валюты</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<Hierarchical>false</Hierarchical>
			<HierarchyType>HierarchyFoldersAndItems</HierarchyType>
			<LimitLevelCount>false</LimitLevelCount>
			<LevelCount>2</LevelCount>
			<FoldersOnTop>true</FoldersOnTop>
			<UseStandardCommands>true</UseStandardCommands>
			<Owners/>
			<SubordinationUse>ToItems</SubordinationUse>
			<CodeLength>9</CodeLength>
			<DescriptionLength>25</DescriptionLength>
			<CodeType>String</CodeType>
			<CodeAllowedLength>Variable</CodeAllowedLength>
			<CodeSeries>WholeCatalog</CodeSeries>
			<CheckUnique>true</CheckUnique>
			<Autonumbering>true</Autonumbering>
			<DefaultPresentation>AsDescription</DefaultPresentation>
			<Characteristics/>
			<PredefinedDataUpdate>Auto</PredefinedDataUpdate>
			<EditType>InDialog</EditType>
			<QuickChoice>false</QuickChoice>
			<ChoiceMode>BothWays</ChoiceMode>
			<InputByString>
				<xr:Field>Catalog.Валюты.StandardAttribute.Description</xr:Field>
				<xr:Field>Catalog.Валюты.StandardAttribute.Code</xr:Field>
			</InputByString>
			<SearchStringModeOnInputByString>Begin</SearchStringModeOnInputByString>
			<FullTextSearchOnInputByString>DontUse</FullTextSearchOnInputByString>
			<ChoiceDataGetModeOnInputByString>Directly</ChoiceDataGetModeOnInputByString>
			<DefaultObjectForm/>
			<DefaultFolderForm/>
			<DefaultListForm/>
			<DefaultChoiceForm/>
			<DefaultFolderChoiceForm/>
			<AuxiliaryObjectForm/>
			<AuxiliaryFolderForm/>
			<AuxiliaryListForm/>
			<AuxiliaryChoiceForm/>
			<AuxiliaryFolderChoiceForm/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<BasedOn/>
			<DataLockFields/>
			<DataLockControlMode>Managed</DataLockControlMode>
			<FullTextSearch>Use</FullTextSearch>
			<ObjectPresentation/>
			<ExtendedObjectPresentation/>
			<ListPresentation/>
			<ExtendedListPresentation/>
			<Explanation/>
			<CreateOnInput>Use</CreateOnInput>
			<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
			<DataHistory>DontUse</DataHistory>
			<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
			<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
		</Properties>
		<ChildObjects/>
	</Catalog>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Catalogs", "Валюты.xml"), cat_val_xml)
    predef_val_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<PredefinedData xmlns="http://v8.1c.ru/8.3/xcf/predef" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CatalogPredefinedItems" version="2.20">
	<Item id="{ruble_id}">
		<Name>Рубль</Name>
		<Code>000000001</Code>
		<Description>Рубль</Description>
		<IsFolder>false</IsFolder>
	</Item>
</PredefinedData>'''
    write_file(os.path.join(SRC_DIR, "Catalogs", "Валюты", "Ext", "Predefined.xml"), predef_val_xml)

    # 7. InformationRegister: КурсыВалют
    reg_kurs_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<InformationRegister uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="InformationRegisterRecord.КурсыВалют" category="Record">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="InformationRegisterManager.КурсыВалют" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="InformationRegisterSelection.КурсыВалют" category="Selection">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="InformationRegisterList.КурсыВалют" category="List">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="InformationRegisterRecordSet.КурсыВалют" category="RecordSet">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="InformationRegisterRecordKey.КурсыВалют" category="RecordKey">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="InformationRegisterRecordManager.КурсыВалют" category="RecordManager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>КурсыВалют</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Курсы валют</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<UseStandardCommands>true</UseStandardCommands>
			<EditType>InDialog</EditType>
			<DefaultRecordForm/>
			<DefaultListForm/>
			<AuxiliaryRecordForm/>
			<AuxiliaryListForm/>
			<InformationRegisterPeriodicity>Day</InformationRegisterPeriodicity>
			<WriteMode>Independent</WriteMode>
			<MainFilterOnPeriod>true</MainFilterOnPeriod>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<DataLockControlMode>Managed</DataLockControlMode>
			<FullTextSearch>Use</FullTextSearch>
			<EnableTotalsSliceFirst>false</EnableTotalsSliceFirst>
			<EnableTotalsSliceLast>true</EnableTotalsSliceLast>
			<RecordPresentation/>
			<ExtendedRecordPresentation/>
			<ListPresentation/>
			<ExtendedListPresentation/>
			<Explanation/>
			<DataHistory>DontUse</DataHistory>
			<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
			<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
		</Properties>
		<ChildObjects>
			<Resource uuid="{uid()}">
				<Properties>
					<Name>Курс</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Курс</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type>xs:decimal</v8:Type>
						<v8:NumberQualifiers>
							<v8:Digits>10</v8:Digits>
							<v8:FractionDigits>2</v8:FractionDigits>
							<v8:AllowedSign>Nonnegative</v8:AllowedSign>
						</v8:NumberQualifiers>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillFromFillingValue>false</FillFromFillingValue>
					<FillValue xsi:type="xs:decimal">0</FillValue>
					<FillChecking>DontCheck</FillChecking>
					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
					<ChoiceParameterLinks/>
					<ChoiceParameters/>
					<QuickChoice>Auto</QuickChoice>
					<CreateOnInput>Auto</CreateOnInput>
					<ChoiceForm/>
					<LinkByType/>
					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<DataHistory>Use</DataHistory>
				</Properties>
			</Resource>
			<Dimension uuid="{uid()}">
				<Properties>
					<Name>Валюта</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Валюта</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Валюты</v8:Type>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillFromFillingValue>true</FillFromFillingValue>
					<FillValue xsi:nil="true"/>
					<FillChecking>ShowError</FillChecking>
					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
					<ChoiceParameterLinks/>
					<ChoiceParameters/>
					<QuickChoice>Auto</QuickChoice>
					<CreateOnInput>Auto</CreateOnInput>
					<ChoiceForm/>
					<LinkByType/>
					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
					<Master>true</Master>
					<MainFilter>true</MainFilter>
					<DenyIncompleteValues>true</DenyIncompleteValues>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<DataHistory>Use</DataHistory>
					<TypeReductionMode>TransformValues</TypeReductionMode>
				</Properties>
			</Dimension>
		</ChildObjects>
	</InformationRegister>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "InformationRegisters", "КурсыВалют.xml"), reg_kurs_xml)

    # 8. Constant: ВестиМноговалютныйУчёт
    const_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Constant uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="ConstantManager.ВестиМноговалютныйУчёт" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="ConstantValueManager.ВестиМноговалютныйУчёт" category="ValueManager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="ConstantValueKey.ВестиМноговалютныйУчёт" category="ValueKey">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>ВестиМноговалютныйУчёт</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Вести многовалютный учёт</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<Type>
				<v8:Type>xs:boolean</v8:Type>
			</Type>
			<PasswordMode>false</PasswordMode>
			<Format/>
			<EditFormat/>
			<ToolTip/>
			<MarkNegatives>false</MarkNegatives>
			<Mask/>
			<MultiLine>false</MultiLine>
			<ExtendedEdit>false</ExtendedEdit>
			<MinValue xsi:nil="true"/>
			<MaxValue xsi:nil="true"/>
			<FillChecking>DontCheck</FillChecking>
			<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
			<ChoiceParameterLinks/>
			<ChoiceParameters/>
			<QuickChoice>Auto</QuickChoice>
			<ChoiceForm/>
			<LinkByType/>
			<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
			<DataLockControlMode>Managed</DataLockControlMode>
			<DataHistory>DontUse</DataHistory>
			<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
			<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
		</Properties>
	</Constant>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Constants", "ВестиМноговалютныйУчёт.xml"), const_xml)

    # 9. FunctionalOption: ВестиМноговалютныйУчёт
    fo_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<FunctionalOption uuid="{uid()}">
		<Properties>
			<Name>ВестиМноговалютныйУчёт</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Вести многовалютный учёт</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<Location>Constant.ВестиМноговалютныйУчёт</Location>
			<PrivilegedGetMode>true</PrivilegedGetMode>
			<Content>
				<xr:Object>Catalog.Валюты</xr:Object>
				<xr:Object>Document.Продажи.Attribute.Валюта</xr:Object>
				<xr:Object>InformationRegister.КурсыВалют</xr:Object>
			</Content>
		</Properties>
	</FunctionalOption>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "FunctionalOptions", "ВестиМноговалютныйУчёт.xml"), fo_xml)

    # 10. Document: Продажи
    doc_prod_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Document uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="DocumentObject.Продажи" category="Object">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DocumentRef.Продажи" category="Ref">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DocumentSelection.Продажи" category="Selection">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DocumentList.Продажи" category="List">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="DocumentManager.Продажи" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>Продажи</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Продажи</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<UseStandardCommands>true</UseStandardCommands>
			<Numerator/>
			<NumberType>String</NumberType>
			<NumberLength>9</NumberLength>
			<NumberAllowedLength>Variable</NumberAllowedLength>
			<NumberPeriodicity>Nonperiodical</NumberPeriodicity>
			<CheckUnique>true</CheckUnique>
			<Autonumbering>true</Autonumbering>
			<Characteristics/>
			<BasedOn/>
			<InputByString>
				<xr:Field>Document.Продажи.StandardAttribute.Number</xr:Field>
			</InputByString>
			<CreateOnInput>Use</CreateOnInput>
			<SearchStringModeOnInputByString>Begin</SearchStringModeOnInputByString>
			<FullTextSearchOnInputByString>DontUse</FullTextSearchOnInputByString>
			<ChoiceDataGetModeOnInputByString>Directly</ChoiceDataGetModeOnInputByString>
			<DefaultObjectForm/>
			<DefaultListForm/>
			<DefaultChoiceForm/>
			<AuxiliaryObjectForm/>
			<AuxiliaryListForm/>
			<AuxiliaryChoiceForm/>
			<Posting>Allow</Posting>
			<RealTimePosting>Allow</RealTimePosting>
			<RegisterRecordsDeletion>AutoDelete</RegisterRecordsDeletion>
			<RegisterRecordsWritingOnPost>WriteSelected</RegisterRecordsWritingOnPost>
			<SequenceFilling>AutoFill</SequenceFilling>
			<RegisterRecords>
				<xr:Item xsi:type="xr:MDObjectRef">AccumulationRegister.Продажи</xr:Item>
			</RegisterRecords>
			<PostInPrivilegedMode>true</PostInPrivilegedMode>
			<UnpostInPrivilegedMode>true</UnpostInPrivilegedMode>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<DataLockFields/>
			<DataLockControlMode>Managed</DataLockControlMode>
			<FullTextSearch>Use</FullTextSearch>
			<ObjectPresentation/>
			<ExtendedObjectPresentation/>
			<ListPresentation/>
			<ExtendedListPresentation/>
			<Explanation/>
			<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
			<DataHistory>DontUse</DataHistory>
			<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>
			<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>
		</Properties>
		<ChildObjects>
			<Attribute uuid="{uid()}">
				<Properties>
					<Name>Покупатель</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Покупатель</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Контрагенты</v8:Type>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillFromFillingValue>false</FillFromFillingValue>
					<FillValue xsi:nil="true"/>
					<FillChecking>DontCheck</FillChecking>
					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
					<ChoiceParameterLinks/>
					<ChoiceParameters/>
					<QuickChoice>Auto</QuickChoice>
					<CreateOnInput>Auto</CreateOnInput>
					<ChoiceForm/>
					<LinkByType/>
					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<DataHistory>Use</DataHistory>
				</Properties>
			</Attribute>
			<Attribute uuid="{uid()}">
				<Properties>
					<Name>Валюта</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Валюта</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Валюты</v8:Type>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillFromFillingValue>true</FillFromFillingValue>
					<FillValue xmlns:d6p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d6p1:CatalogRef.Валюты">d6p1:Catalog.Валюты.Рубль</FillValue>
					<FillChecking>DontCheck</FillChecking>
					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
					<ChoiceParameterLinks/>
					<ChoiceParameters/>
					<QuickChoice>Auto</QuickChoice>
					<CreateOnInput>Auto</CreateOnInput>
					<ChoiceForm/>
					<LinkByType/>
					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<DataHistory>Use</DataHistory>
				</Properties>
			</Attribute>
			<Attribute uuid="{uid()}">
				<Properties>
					<Name>ВсегоКОплате</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Всего к оплате</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type>xs:decimal</v8:Type>
						<v8:NumberQualifiers>
							<v8:Digits>10</v8:Digits>
							<v8:FractionDigits>2</v8:FractionDigits>
							<v8:AllowedSign>Nonnegative</v8:AllowedSign>
						</v8:NumberQualifiers>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillFromFillingValue>false</FillFromFillingValue>
					<FillValue xsi:type="xs:decimal">0</FillValue>
					<FillChecking>DontCheck</FillChecking>
					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
					<ChoiceParameterLinks/>
					<ChoiceParameters/>
					<QuickChoice>Auto</QuickChoice>
					<CreateOnInput>Auto</CreateOnInput>
					<ChoiceForm/>
					<LinkByType/>
					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<DataHistory>Use</DataHistory>
				</Properties>
			</Attribute>
			<TabularSection uuid="{uid()}">
				<InternalInfo>
					<xr:GeneratedType name="DocumentTabularSection.Продажи.СписокТоваров" category="TabularSection">
						<xr:TypeId>{uid()}</xr:TypeId>
						<xr:ValueId>{uid()}</xr:ValueId>
					</xr:GeneratedType>
					<xr:GeneratedType name="DocumentTabularSectionRow.Продажи.СписокТоваров" category="TabularSectionRow">
						<xr:TypeId>{uid()}</xr:TypeId>
						<xr:ValueId>{uid()}</xr:ValueId>
					</xr:GeneratedType>
				</InternalInfo>
				<Properties>
					<Name>СписокТоваров</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Список товаров</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<ToolTip/>
					<FillChecking>DontCheck</FillChecking>
					<StandardAttributes>
						<xr:StandardAttribute name="LineNumber">
							<xr:LinkByType/>
							<xr:FillChecking>DontCheck</xr:FillChecking>
							<xr:MultiLine>false</xr:MultiLine>
							<xr:FillFromFillingValue>false</xr:FillFromFillingValue>
							<xr:CreateOnInput>Auto</xr:CreateOnInput>
							<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>
							<xr:MaxValue xsi:nil="true"/>
							<xr:ToolTip/>
							<xr:ExtendedEdit>false</xr:ExtendedEdit>
							<xr:Format/>
							<xr:ChoiceForm/>
							<xr:QuickChoice>Auto</xr:QuickChoice>
							<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>
							<xr:EditFormat/>
							<xr:PasswordMode>false</xr:PasswordMode>
							<xr:DataHistory>Use</xr:DataHistory>
							<xr:MarkNegatives>false</xr:MarkNegatives>
							<xr:MinValue xsi:nil="true"/>
							<xr:Synonym/>
							<xr:Comment/>
							<xr:FullTextSearch>Use</xr:FullTextSearch>
							<xr:ChoiceParameterLinks/>
							<xr:FillValue xsi:nil="true"/>
							<xr:Mask/>
							<xr:ChoiceParameters/>
						</xr:StandardAttribute>
					</StandardAttributes>
				</Properties>
				<ChildObjects>
					<Attribute uuid="{uid()}">
						<Properties>
							<Name>Товар</Name>
							<Synonym>
								<v8:item>
									<v8:lang>ru</v8:lang>
									<v8:content>Товар</v8:content>
								</v8:item>
							</Synonym>
							<Comment/>
							<Type>
								<v8:Type xmlns:d7p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d7p1:CatalogRef.Номенклатура</v8:Type>
							</Type>
							<PasswordMode>false</PasswordMode>
							<Format/>
							<EditFormat/>
							<ToolTip/>
							<MarkNegatives>false</MarkNegatives>
							<Mask/>
							<MultiLine>false</MultiLine>
							<ExtendedEdit>false</ExtendedEdit>
							<MinValue xsi:nil="true"/>
							<MaxValue xsi:nil="true"/>
							<FillChecking>DontCheck</FillChecking>
							<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
							<ChoiceParameterLinks/>
							<ChoiceParameters>
								<app:item name="Отбор.ЭтоУслуга">
									<app:value xsi:type="xs:boolean">false</app:value>
								</app:item>
							</ChoiceParameters>
							<QuickChoice>Auto</QuickChoice>
							<CreateOnInput>Auto</CreateOnInput>
							<ChoiceForm/>
							<LinkByType/>
							<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
							<Indexing>DontIndex</Indexing>
							<FullTextSearch>Use</FullTextSearch>
							<DataHistory>Use</DataHistory>
						</Properties>
					</Attribute>
					<Attribute uuid="{uid()}">
						<Properties>
							<Name>Сумма</Name>
							<Synonym>
								<v8:item>
									<v8:lang>ru</v8:lang>
									<v8:content>Сумма</v8:content>
								</v8:item>
							</Synonym>
							<Comment/>
							<Type>
								<v8:Type>xs:decimal</v8:Type>
								<v8:NumberQualifiers>
									<v8:Digits>10</v8:Digits>
									<v8:FractionDigits>2</v8:FractionDigits>
									<v8:AllowedSign>Nonnegative</v8:AllowedSign>
								</v8:NumberQualifiers>
							</Type>
							<PasswordMode>false</PasswordMode>
							<Format/>
							<EditFormat/>
							<ToolTip/>
							<MarkNegatives>false</MarkNegatives>
							<Mask/>
							<MultiLine>false</MultiLine>
							<ExtendedEdit>false</ExtendedEdit>
							<MinValue xsi:nil="true"/>
							<MaxValue xsi:nil="true"/>
							<FillChecking>DontCheck</FillChecking>
							<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
							<ChoiceParameterLinks/>
							<ChoiceParameters/>
							<QuickChoice>Auto</QuickChoice>
							<CreateOnInput>Auto</CreateOnInput>
							<ChoiceForm/>
							<LinkByType/>
							<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
							<Indexing>DontIndex</Indexing>
							<FullTextSearch>Use</FullTextSearch>
							<DataHistory>Use</DataHistory>
						</Properties>
					</Attribute>
				</ChildObjects>
			</TabularSection>
			<TabularSection uuid="{uid()}">
				<InternalInfo>
					<xr:GeneratedType name="DocumentTabularSection.Продажи.СписокУслуг" category="TabularSection">
						<xr:TypeId>{uid()}</xr:TypeId>
						<xr:ValueId>{uid()}</xr:ValueId>
					</xr:GeneratedType>
					<xr:GeneratedType name="DocumentTabularSectionRow.Продажи.СписокУслуг" category="TabularSectionRow">
						<xr:TypeId>{uid()}</xr:TypeId>
						<xr:ValueId>{uid()}</xr:ValueId>
					</xr:GeneratedType>
				</InternalInfo>
				<Properties>
					<Name>СписокУслуг</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Список услуг</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<ToolTip/>
					<FillChecking>DontCheck</FillChecking>
					<StandardAttributes>
						<xr:StandardAttribute name="LineNumber">
							<xr:LinkByType/>
							<xr:FillChecking>DontCheck</xr:FillChecking>
							<xr:MultiLine>false</xr:MultiLine>
							<xr:FillFromFillingValue>false</xr:FillFromFillingValue>
							<xr:CreateOnInput>Auto</xr:CreateOnInput>
							<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>
							<xr:MaxValue xsi:nil="true"/>
							<xr:ToolTip/>
							<xr:ExtendedEdit>false</xr:ExtendedEdit>
							<xr:Format/>
							<xr:ChoiceForm/>
							<xr:QuickChoice>Auto</xr:QuickChoice>
							<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>
							<xr:EditFormat/>
							<xr:PasswordMode>false</xr:PasswordMode>
							<xr:DataHistory>Use</xr:DataHistory>
							<xr:MarkNegatives>false</xr:MarkNegatives>
							<xr:MinValue xsi:nil="true"/>
							<xr:Synonym/>
							<xr:Comment/>
							<xr:FullTextSearch>Use</xr:FullTextSearch>
							<xr:ChoiceParameterLinks/>
							<xr:FillValue xsi:nil="true"/>
							<xr:Mask/>
							<xr:ChoiceParameters/>
						</xr:StandardAttribute>
					</StandardAttributes>
				</Properties>
				<ChildObjects>
					<Attribute uuid="{uid()}">
						<Properties>
							<Name>Услуга</Name>
							<Synonym>
								<v8:item>
									<v8:lang>ru</v8:lang>
									<v8:content>Услуга</v8:content>
								</v8:item>
							</Synonym>
							<Comment/>
							<Type>
								<v8:Type xmlns:d7p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d7p1:CatalogRef.Номенклатура</v8:Type>
							</Type>
							<PasswordMode>false</PasswordMode>
							<Format/>
							<EditFormat/>
							<ToolTip/>
							<MarkNegatives>false</MarkNegatives>
							<Mask/>
							<MultiLine>false</MultiLine>
							<ExtendedEdit>false</ExtendedEdit>
							<MinValue xsi:nil="true"/>
							<MaxValue xsi:nil="true"/>
							<FillChecking>DontCheck</FillChecking>
							<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
							<ChoiceParameterLinks/>
							<ChoiceParameters>
								<app:item name="Отбор.ЭтоУслуга">
									<app:value xsi:type="xs:boolean">true</app:value>
								</app:item>
							</ChoiceParameters>
							<QuickChoice>Auto</QuickChoice>
							<CreateOnInput>Auto</CreateOnInput>
							<ChoiceForm/>
							<LinkByType/>
							<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
							<Indexing>DontIndex</Indexing>
							<FullTextSearch>Use</FullTextSearch>
							<DataHistory>Use</DataHistory>
						</Properties>
					</Attribute>
					<Attribute uuid="{uid()}">
						<Properties>
							<Name>Сумма</Name>
							<Synonym>
								<v8:item>
									<v8:lang>ru</v8:lang>
									<v8:content>Сумма</v8:content>
								</v8:item>
							</Synonym>
							<Comment/>
							<Type>
								<v8:Type>xs:decimal</v8:Type>
								<v8:NumberQualifiers>
									<v8:Digits>10</v8:Digits>
									<v8:FractionDigits>2</v8:FractionDigits>
									<v8:AllowedSign>Nonnegative</v8:AllowedSign>
								</v8:NumberQualifiers>
							</Type>
							<PasswordMode>false</PasswordMode>
							<Format/>
							<EditFormat/>
							<ToolTip/>
							<MarkNegatives>false</MarkNegatives>
							<Mask/>
							<MultiLine>false</MultiLine>
							<ExtendedEdit>false</ExtendedEdit>
							<MinValue xsi:nil="true"/>
							<MaxValue xsi:nil="true"/>
							<FillChecking>DontCheck</FillChecking>
							<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
							<ChoiceParameterLinks/>
							<ChoiceParameters/>
							<QuickChoice>Auto</QuickChoice>
							<CreateOnInput>Auto</CreateOnInput>
							<ChoiceForm/>
							<LinkByType/>
							<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
							<Indexing>DontIndex</Indexing>
							<FullTextSearch>Use</FullTextSearch>
							<DataHistory>Use</DataHistory>
						</Properties>
					</Attribute>
				</ChildObjects>
			</TabularSection>
		</ChildObjects>
	</Document>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Documents", "Продажи.xml"), doc_prod_xml)

    # Document ObjectModule.bsl
    doc_bsl = '''Процедура ПередЗаписью(Отказ, РежимЗаписи, РежимПроведения)
	
	ВсегоКОплате = СписокТоваров.Итог("Сумма") + СписокУслуг.Итог("Сумма");
	
КонецПроцедуры

Процедура ОбработкаПроведения(Отказ, Режим)
	
	Движения.Продажи.Записывать = Истина;
	Для Каждого ТекСтрокаСписокТоваров Из СписокТоваров Цикл
		Движение = Движения.Продажи.Добавить();
		Движение.Период = Дата;
		Движение.Номенклатура = ТекСтрокаСписокТоваров.Товар;
		Движение.Сумма = ТекСтрокаСписокТоваров.Сумма * ПолучитьКурсВалюты(Валюта, Дата);
	КонецЦикла;
	
	Движения.Продажи.Записывать = Истина;
	Для Каждого ТекСтрокаСписокУслуг Из СписокУслуг Цикл
		Движение = Движения.Продажи.Добавить();
		Движение.Период = Дата;
		Движение.Номенклатура = ТекСтрокаСписокУслуг.Услуга;
		Движение.Сумма = ТекСтрокаСписокУслуг.Сумма * ПолучитьКурсВалюты(Валюта, Дата);
	КонецЦикла;
	
КонецПроцедуры

Функция ПолучитьКурсВалюты(Валюта, Дата)
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
		"ВЫБРАТЬ
		|	КурсыВалютСрезПоследних.Валюта КАК Валюта,
		|	КурсыВалютСрезПоследних.Курс КАК Курс
		|ИЗ
		|	РегистрСведений.КурсыВалют.СрезПоследних(&Период, Валюта = &Валюта) КАК КурсыВалютСрезПоследних";
	Запрос.УстановитьПараметр("Валюта", Валюта);
	Запрос.УстановитьПараметр("Период", НачалоДня(Дата));
	РезультатЗапроса = Запрос.Выполнить();
	ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
	Если ВыборкаДетальныеЗаписи.Следующий() Тогда
		Возврат ВыборкаДетальныеЗаписи.Курс;
	Иначе
		Возврат 1;
	КонецЕсли;
	
КонецФункции // ПолучитьКурсВалюты()
'''
    write_file(os.path.join(SRC_DIR, "Documents", "Продажи", "Ext", "ObjectModule.bsl"), doc_bsl)

    # 11. AccumulationRegister: Продажи
    reg_acc_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<AccumulationRegister uuid="{uid()}">
		<InternalInfo>
			<xr:GeneratedType name="AccumulationRegisterRecord.Продажи" category="Record">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="AccumulationRegisterManager.Продажи" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="AccumulationRegisterSelection.Продажи" category="Selection">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="AccumulationRegisterList.Продажи" category="List">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="AccumulationRegisterRecordSet.Продажи" category="RecordSet">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="AccumulationRegisterRecordKey.Продажи" category="RecordKey">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>Продажи</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Продажи</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<RegisterType>Turnovers</RegisterType>
			<DefaultListForm/>
			<AuxiliaryListForm/>
			<UseStandardCommands>true</UseStandardCommands>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<DataLockControlMode>Managed</DataLockControlMode>
			<FullTextSearch>Use</FullTextSearch>
			<EnableTotalsSplitting>true</EnableTotalsSplitting>
			<ListPresentation/>
			<ExtendedListPresentation/>
			<Explanation/>
		</Properties>
		<ChildObjects>
			<Resource uuid="{uid()}">
				<Properties>
					<Name>Сумма</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Сумма</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type>xs:decimal</v8:Type>
						<v8:NumberQualifiers>
							<v8:Digits>10</v8:Digits>
							<v8:FractionDigits>2</v8:FractionDigits>
							<v8:AllowedSign>Nonnegative</v8:AllowedSign>
						</v8:NumberQualifiers>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillChecking>DontCheck</FillChecking>
					<FullTextSearch>Use</FullTextSearch>
				</Properties>
			</Resource>
			<Dimension uuid="{uid()}">
				<Properties>
					<Name>Номенклатура</Name>
					<Synonym>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Номенклатура</v8:content>
						</v8:item>
					</Synonym>
					<Comment/>
					<Type>
						<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Номенклатура</v8:Type>
					</Type>
					<PasswordMode>false</PasswordMode>
					<Format/>
					<EditFormat/>
					<ToolTip/>
					<MarkNegatives>false</MarkNegatives>
					<Mask/>
					<MultiLine>false</MultiLine>
					<ExtendedEdit>false</ExtendedEdit>
					<MinValue xsi:nil="true"/>
					<MaxValue xsi:nil="true"/>
					<FillChecking>ShowError</FillChecking>
					<DenyIncompleteValues>true</DenyIncompleteValues>
					<Indexing>DontIndex</Indexing>
					<FullTextSearch>Use</FullTextSearch>
					<UseInTotals>true</UseInTotals>
				</Properties>
			</Dimension>
		</ChildObjects>
	</AccumulationRegister>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "AccumulationRegisters", "Продажи.xml"), reg_acc_xml)

    # 12. Report: Продажи (with Data Composition Schema)
    rep_uuid = uid()
    rep_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Report uuid="{rep_uuid}">
		<InternalInfo>
			<xr:GeneratedType name="ReportObject.Продажи" category="Object">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
			<xr:GeneratedType name="ReportManager.Продажи" category="Manager">
				<xr:TypeId>{uid()}</xr:TypeId>
				<xr:ValueId>{uid()}</xr:ValueId>
			</xr:GeneratedType>
		</InternalInfo>
		<Properties>
			<Name>Продажи</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Продажи</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<UseStandardCommands>true</UseStandardCommands>
			<DefaultForm/>
			<AuxiliaryForm/>
			<MainDataCompositionSchema>Report.Продажи.Template.ОсновнаяСхемаКомпоновкиДанных</MainDataCompositionSchema>
			<DefaultSettingsForm/>
			<AuxiliarySettingsForm/>
			<DefaultVariantForm/>
			<VariantsStorage/>
			<SettingsStorage/>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<ExtendedPresentation/>
			<Explanation/>
		</Properties>
		<ChildObjects>
			<Template>ОсновнаяСхемаКомпоновкиДанных</Template>
		</ChildObjects>
	</Report>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Reports", "Продажи.xml"), rep_xml)
    write_file(os.path.join(SRC_DIR, "Reports", "Продажи", "Ext", "ObjectModule.bsl"), "")
    write_file(os.path.join(SRC_DIR, "Reports", "Продажи", "Ext", "ManagerModule.bsl"), "")

    rep_tpl_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Template uuid="{uid()}">
		<Properties>
			<Name>ОсновнаяСхемаКомпоновкиДанных</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Основная схема компоновки данных</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<TemplateType>DataCompositionSchema</TemplateType>
		</Properties>
	</Template>
</MetaDataObject>'''
    write_file(os.path.join(SRC_DIR, "Reports", "Продажи", "Templates", "ОсновнаяСхемаКомпоновкиДанных.xml"), rep_tpl_xml)

    skd_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<DataCompositionSchema xmlns="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcscom="http://v8.1c.ru/8.1/data-composition-system/common" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<dataSource>
		<name>ИсточникДанных1</name>
		<dataSourceType>Local</dataSourceType>
	</dataSource>
	<dataSet xsi:type="DataSetQuery">
		<name>НаборДанных1</name>
		<field xsi:type="DataSetFieldField">
			<dataPath>Номенклатура</dataPath>
			<field>Номенклатура</field>
			<role>
				<dcscom:dimension>true</dcscom:dimension>
			</role>
			<valueType>
				<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Номенклатура</v8:Type>
			</valueType>
		</field>
		<field xsi:type="DataSetFieldField">
			<dataPath>Сумма</dataPath>
			<field>Сумма</field>
			<title xsi:type="v8:LocalStringType">
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Сумма</v8:content>
				</v8:item>
			</title>
			<valueType>
				<v8:Type>xs:decimal</v8:Type>
				<v8:NumberQualifiers>
					<v8:Digits>10</v8:Digits>
					<v8:FractionDigits>2</v8:FractionDigits>
					<v8:AllowedSign>Any</v8:AllowedSign>
				</v8:NumberQualifiers>
			</valueType>
		</field>
		<dataSource>ИсточникДанных1</dataSource>
		<query>ВЫБРАТЬ
	ПродажиОбороты.Номенклатура КАК Номенклатура,
	ПродажиОбороты.СуммаОборот КАК Сумма
ИЗ
	РегистрНакопления.Продажи.Обороты КАК ПродажиОбороты</query>
	</dataSet>
	<totalField>
		<dataPath>Сумма</dataPath>
		<expression>Сумма(Сумма)</expression>
	</totalField>
	<parameter>
		<name>НачалоПериода</name>
		<title xsi:type="v8:LocalStringType">
			<v8:item>
				<v8:lang>ru</v8:lang>
				<v8:content>Начало периода</v8:content>
			</v8:item>
		</title>
		<valueType>
			<v8:Type>xs:dateTime</v8:Type>
			<v8:DateQualifiers>
				<v8:DateFractions>DateTime</v8:DateFractions>
			</v8:DateQualifiers>
		</valueType>
		<value xsi:type="xs:dateTime">0001-01-01T00:00:00</value>
		<useRestriction>false</useRestriction>
	</parameter>
	<parameter>
		<name>КонецПериода</name>
		<title xsi:type="v8:LocalStringType">
			<v8:item>
				<v8:lang>ru</v8:lang>
				<v8:content>Конец периода</v8:content>
			</v8:item>
		</title>
		<valueType>
			<v8:Type>xs:dateTime</v8:Type>
			<v8:DateQualifiers>
				<v8:DateFractions>DateTime</v8:DateFractions>
			</v8:DateQualifiers>
		</valueType>
		<value xsi:type="xs:dateTime">0001-01-01T00:00:00</value>
		<useRestriction>false</useRestriction>
	</parameter>
	<settingsVariant>
		<dcsset:name>Основной</dcsset:name>
		<dcsset:presentation xsi:type="v8:LocalStringType">
			<v8:item>
				<v8:lang>ru</v8:lang>
				<v8:content>Основной</v8:content>
			</v8:item>
		</dcsset:presentation>
		<dcsset:settings xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows">
			<dcsset:selection>
				<dcsset:item xsi:type="dcsset:SelectedItemField">
					<dcsset:field>Номенклатура</dcsset:field>
				</dcsset:item>
				<dcsset:item xsi:type="dcsset:SelectedItemField">
					<dcsset:field>Сумма</dcsset:field>
				</dcsset:item>
			</dcsset:selection>
			<dcsset:order>
				<dcsset:item xsi:type="dcsset:OrderItemField">
					<dcsset:field>Сумма</dcsset:field>
					<dcsset:orderType>Desc</dcsset:orderType>
				</dcsset:item>
			</dcsset:order>
			<dcsset:item xsi:type="dcsset:StructureItemGroup">
				<dcsset:order>
					<dcsset:item xsi:type="dcsset:OrderItemAuto"/>
				</dcsset:order>
				<dcsset:selection>
					<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>
				</dcsset:selection>
			</dcsset:item>
		</dcsset:settings>
	</settingsVariant>
</DataCompositionSchema>'''
    write_file(os.path.join(SRC_DIR, "Reports", "Продажи", "Templates", "ОсновнаяСхемаКомпоновкиДанных", "Ext", "Template.xml"), skd_xml)

    print("XML source metadata generated successfully.")

if __name__ == "__main__":
    build_src_tree()
