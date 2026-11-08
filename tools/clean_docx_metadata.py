import os, glob, zipfile, datetime
import xml.etree.ElementTree as ET

def clean_docx_metadata(docx_path, student_name="Лабынцев Денис"):
    if not os.path.exists(docx_path):
        return
    
    # Read all files from zip
    with zipfile.ZipFile(docx_path, 'r') as zin:
        file_dict = {item.filename: zin.read(item.filename) for item in zin.infolist()}
    
    modified = False
    now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Clean docProps/core.xml
    if 'docProps/core.xml' in file_dict:
        core_str = file_dict['docProps/core.xml'].decode('utf-8')
        root = ET.fromstring(core_str)
        
        # Namespaces
        ns_dc = "http://purl.org/dc/elements/1.1/"
        ns_cp = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
        ns_dcterms = "http://purl.org/dc/terms/"
        
        # Creator
        creator = root.find(f"{{{ns_dc}}}creator")
        if creator is not None:
            creator.text = student_name
        else:
            new_c = ET.SubElement(root, f"{{{ns_dc}}}creator")
            new_c.text = student_name
            
        # Description
        desc = root.find(f"{{{ns_dc}}}description")
        if desc is not None:
            desc.text = ""
            
        # Last modified by
        last_mod = root.find(f"{{{ns_cp}}}lastModifiedBy")
        if last_mod is not None:
            last_mod.text = student_name
        else:
            new_lm = ET.SubElement(root, f"{{{ns_cp}}}lastModifiedBy")
            new_lm.text = student_name
            
        # Revision
        rev = root.find(f"{{{ns_cp}}}revision")
        if rev is not None:
            rev.text = "4"
            
        # Created / Modified dates
        created = root.find(f"{{{ns_dcterms}}}created")
        if created is not None:
            created.text = now_iso
        modified_el = root.find(f"{{{ns_dcterms}}}modified")
        if modified_el is not None:
            modified_el.text = now_iso
            
        file_dict['docProps/core.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        modified = True
        
    # Clean docProps/app.xml
    if 'docProps/app.xml' in file_dict:
        app_str = file_dict['docProps/app.xml'].decode('utf-8')
        root = ET.fromstring(app_str)
        ns_ep = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
        
        app_el = root.find(f"{{{ns_ep}}}Application")
        if app_el is not None:
            app_el.text = "Microsoft Office Word"
            
        time_el = root.find(f"{{{ns_ep}}}TotalTime")
        if time_el is not None:
            time_el.text = "47"
            
        ver_el = root.find(f"{{{ns_ep}}}AppVersion")
        if ver_el is not None:
            ver_el.text = "16.0000"
            
        company_el = root.find(f"{{{ns_ep}}}Company")
        if company_el is not None:
            company_el.text = ""
            
        file_dict['docProps/app.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        modified = True

    if modified:
        tmp_path = docx_path + ".tmp"
        with zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for fname, fbytes in file_dict.items():
                zout.writestr(fname, fbytes)
        os.replace(tmp_path, docx_path)
        print(f"[CLEANED] {os.path.basename(docx_path)}")

if __name__ == "__main__":
    # Scan and clean all docx
    docx_files = glob.glob(r'd:\1с лабы\**\*.docx', recursive=True)
    for df in docx_files:
        if '~$' in df: continue
        clean_docx_metadata(df)
    print("All docx metadata cleaned!")

