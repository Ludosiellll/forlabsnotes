import os

dirs = [
    r"d:\1с лабы\КПИЯП_ЛР10_Файлы",
    r"d:\1с лабы\КПИЯП_ЛР11_Файлы",
    r"d:\1с лабы\КПИЯП_ЛР12_Файлы"
]

clean_csproj = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>disable</ImplicitUsings>
    <Nullable>disable</Nullable>
  </PropertyGroup>

</Project>
"""

for base in dirs:
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(".csproj"):
                p = os.path.join(root, f)
                with open(p, "w", encoding="utf-8") as out:
                    out.write(clean_csproj)
                print("Updated to net10.0:", p)

print("All projects updated to net10.0.")
