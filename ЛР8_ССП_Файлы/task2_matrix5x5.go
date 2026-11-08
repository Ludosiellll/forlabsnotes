package main

import (
    "fmt"
    "math/rand"
    "time"
)

// Лабораторная работа №8 по дисциплине "Современные системы программирования"
// Задание 2 (Приложение А, Вариант 14):
// Создать двумерный массив 5 х 5. Написать функцию, которая заполнит его случайными числами от 30 до 60.
// Создать еще две функции, которые находят максимальный и минимальный элементы этого двумерного массива.
// Группа: РС02-23

// Функция заполнения двумерного массива 5x5 случайными числами в диапазоне [30, 60]
func fillMatrix() [5][5]int {
    var matrix [5][5]int
    for i := 0; i < 5; i++ {
        for j := 0; j < 5; j++ {
            matrix[i][j] = rand.Intn(31) + 30
        }
    }
    return matrix
}

// Функция поиска максимального элемента двумерного массива 5x5
func findMax(matrix [5][5]int) (int, int, int) {
    maxVal := matrix[0][0]
    maxRow, maxCol := 0, 0
    for i, row := range matrix {
        for j, val := range row {
            if val > maxVal {
                maxVal = val
                maxRow = i
                maxCol = j
            }
        }
    }
    return maxVal, maxRow, maxCol
}

// Функция поиска минимального элемента двумерного массива 5x5
func findMin(matrix [5][5]int) (int, int, int) {
    minVal := matrix[0][0]
    minRow, minCol := 0, 0
    for i, row := range matrix {
        for j, val := range row {
            if val < minVal {
                minVal = val
                minRow = i
                minCol = j
            }
        }
    }
    return minVal, minRow, minCol
}

func main() {
    rand.Seed(time.Now().UnixNano())

    fmt.Println("=== Заполнение двумерного массива 5 x 5 случайными числами [30..60] ===")
    matrix := fillMatrix()

    for i := 0; i < 5; i++ {
        for j := 0; j < 5; j++ {
            fmt.Printf("%4d", matrix[i][j])
        }
        fmt.Println()
    }

    maxVal, maxR, maxC := findMax(matrix)
    minVal, minR, minC := findMin(matrix)

    fmt.Println("-----------------------------------------------------------------------")
    fmt.Printf("Максимальный элемент массива: %d (строка %d, столбец %d)\n", maxVal, maxR+1, maxC+1)
    fmt.Printf("Минимальный элемент массива:  %d (строка %d, столбец %d)\n", minVal, minR+1, minC+1)
}
