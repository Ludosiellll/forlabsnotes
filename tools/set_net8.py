import os

dirs = [r"d:\1с лабы\КПИЯП_ЛР10_Файлы", r"d:\1с лабы\КПИЯП_ЛР11_Файлы"]

clean_csproj = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
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
                print("Updated csproj to net8.0:", p)

print("All projects updated to net8.0.")
