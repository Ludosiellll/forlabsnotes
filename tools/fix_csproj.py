import os

target = r"d:\1с лабы\КПИЯП_ЛР10_Файлы\Индивидуальное задание\Индивидуальное задание.csproj"

content = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>disable</ImplicitUsings>
    <Nullable>disable</Nullable>
  </PropertyGroup>

</Project>
"""

with open(target, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated:", target)
