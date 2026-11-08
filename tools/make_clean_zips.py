import os
import zipfile

targets = [
    (r"d:\1с лабы\КПИЯП_ЛР10_Файлы", r"d:\1с лабы\КПИЯП_ЛР10_Файлы.zip"),
    (r"d:\1с лабы\КПИЯП_ЛР11_Файлы", r"d:\1с лабы\КПИЯП_ЛР11_Файлы.zip"),
    (r"d:\1с лабы\КПИЯП_ЛР12_Файлы", r"d:\1с лабы\КПИЯП_ЛР12_Файлы.zip")
]

# First, clean any *.py files directly inside the lab folders
for src_dir, _ in targets:
    for f in os.listdir(src_dir):
        if f.endswith(".py"):
            p = os.path.join(src_dir, f)
            os.remove(p)
            print("Removed from folder:", p)

# Now create clean zip archives
for src_dir, zip_dest in targets:
    base_name = os.path.basename(src_dir)
    print(f"Creating {zip_dest} from {src_dir}...")
    with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                # Strictly ignore python scripts or temp files
                if file.endswith(".py") or file.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.path.dirname(src_dir))
                zf.write(full_path, rel_path)
    print(f"Created: {zip_dest} ({os.path.getsize(zip_dest)} bytes)")

print("All zip archives created successfully.")
