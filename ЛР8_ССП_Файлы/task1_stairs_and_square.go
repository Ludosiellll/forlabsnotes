package main

import "fmt"

// Лабораторная работа №8 по дисциплине "Современные системы программирования"
// Задание 1:
// 1. По данному натуральному n <= 30 вывести лесенку из n ступенек:
//    1
//    2 2
//    3 3 3 и т.д.
// 2. Найти квадрат числа n по формуле n^2 = 1 + 3 + 5 + ... + (2*n - 1) с выводом текущей суммы.
// Группа: РС02-23
func main() {
    var n int
    fmt.Print("Введите натуральное число n (n <= 30) для вывода лесенки: ")
    fmt.Scan(&n)

    if n < 1 || n > 30 {
        fmt.Println("Ошибка: число n должно быть в диапазоне от 1 до 30!")
        return
    }

    fmt.Printf("\n=== 1. Лесенка из %d ступенек ===\n", n)
    stairs := make([][]int, n)
    for i := 0; i < n; i++ {
        val := i + 1
        stairs[i] = make([]int, val)
        for j := 0; j < val; j++ {
            stairs[i][j] = val
            if j > 0 {
                fmt.Print(" ")
            }
            fmt.Print(stairs[i][j])
        }
        fmt.Println()
    }

    var k int
    fmt.Print("\nВведите целое положительное число n для вычисления квадрата: ")
    fmt.Scan(&k)

    if k <= 0 {
        fmt.Println("Ошибка: введите положительное целое число!")
        return
    }

    fmt.Printf("\n=== 2. Вычисление квадрата числа %d по формуле суммы нечетных чисел ===\n", k)
    sum := 0
    for i := 1; i <= k; i++ {
        oddTerm := 2*i - 1
        sum += oddTerm
        fmt.Printf("Шаг %d: прибавлено слагаемое %2d -> текущая сумма = %d\n", i, oddTerm, sum)
    }

    fmt.Printf("Итоговый квадрат числа %d^2 = %d\n", k, sum)
}
