package main

import "fmt"

// Лабораторная работа №7 по дисциплине "Современные системы программирования"
// Задание 1: Работа с примитивными типами данных и арифметическими операциями в Go
// Группа: РС02-23
func main() {
	fmt.Println("=== Пункт 1. Объявление переменных всех примитивных типов данных ===")

	// Целочисленные типы со знаком
	var vInt8 int8 = -45
	var vInt16 int16 = -12500
	var vInt32 int32 = 1500000
	var vInt64 int64 = 9000000000
	var vInt int = 2026

	// Целочисленные беззнаковые типы и синонимы
	var vUint8 uint8 = 200
	var vUint16 uint16 = 45000
	var vUint32 uint32 = 3000000000
	var vUint64 uint64 = 15000000000
	var vUint uint = 1024
	var vByte byte = 255
	var vRune rune = 'Я'

	// Числа с плавающей точкой и комплексные числа
	var vFloat32 float32 = 3.14159
	var vFloat64 float64 = 2.718281828459045
	var vComplex64 complex64 = 2 + 3i
	var vComplex128 complex128 = 5.5 - 1.25i

	// Логический и строковый типы
	var vBool bool = true
	var vString string = "Привет, Golang!"

	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vInt8, vInt8)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vInt16, vInt16)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vInt32, vInt32)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vInt64, vInt64)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vInt, vInt)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vUint8, vUint8)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vUint16, vUint16)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vUint32, vUint32)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vUint64, vUint64)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vUint, vUint)
	fmt.Printf("Значение: %-20v | Тип данных: byte (%T)\n", vByte, vByte)
	fmt.Printf("Значение: %-20c | Тип данных: rune (%T)\n", vRune, vRune)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vFloat32, vFloat32)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vFloat64, vFloat64)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vComplex64, vComplex64)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vComplex128, vComplex128)
	fmt.Printf("Значение: %-20v | Тип данных: %T\n", vBool, vBool)
	fmt.Printf("Значение: %-20q | Тип данных: %T\n", vString, vString)

	fmt.Println("\n=== Пункт 2. Все арифметические операции с 3 переменными ===")
	var x int = 25
	var y int = 7
	var z float64 = 4.0

	fmt.Printf("Исходные переменные: x = %d, y = %d, z = %.1f\n", x, y, z)
	fmt.Printf("Сложение (x + y):               %d + %d = %d\n", x, y, x+y)
	fmt.Printf("Вычитание (x - y):              %d - %d = %d\n", x, y, x-y)
	fmt.Printf("Умножение (x * y):              %d * %d = %d\n", x, y, x*y)
	fmt.Printf("Целочисленное деление (x / y):  %d / %d = %d\n", x, y, x/y)
	fmt.Printf("Вещественное деление (x / z):   %d / %.1f = %.2f\n", x, z, float64(x)/z)
	fmt.Printf("Остаток от деления (x %% y):     %d %% %d = %d\n", x, y, x%y)

	x++
	fmt.Printf("Постфиксный инкремент (x++):    x = %d\n", x)
	y--
	fmt.Printf("Постфиксный декремент (y--):    y = %d\n", y)

	fmt.Println("\n=== Пункт 3. Вычисление трех связанных переменных типа int ===")
	var a int = 12
	var b int = a + 3
	var c int = a + b

	fmt.Printf("Первая переменная (a):          %d\n", a)
	fmt.Printf("Вторая переменная (b = a + 3):  %d\n", b)
	fmt.Printf("Третья переменная (c = a + b):  %d\n", c)
}
