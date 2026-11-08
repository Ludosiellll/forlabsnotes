package main

import (
	"fmt"
)

// generateSquares последовательно вычисляет квадраты чисел от 1 до n и отправляет их в канал
func generateSquares(n int, ch chan int) {
	defer close(ch)
	for i := 1; i <= n; i++ {
		ch <- i * i
	}
}

func main() {
	var n int
	fmt.Print("Введите натуральное число n: ")
	_, err := fmt.Scan(&n)
	if err != nil || n <= 0 {
		fmt.Println("Ошибка: число n должно быть натуральным (n > 0)!")
		return
	}

	// Создание канала для потока квадратов чисел
	squareChan := make(chan int)

	// Запуск горутины генерации квадратов чисел
	go generateSquares(n, squareChan)

	totalSum := 0
	step := 1

	fmt.Println("--------------------------------------------------")
	fmt.Println("Пошаговое получение квадратов чисел из канала:")

	// Чтение данных из канала до его закрытия
	for sq := range squareChan {
		fmt.Printf("Шаг %d: квадрат числа %d = %d\n", step, step, sq)
		totalSum += sq
		step++
	}

	fmt.Println("--------------------------------------------------")
	fmt.Printf("Итоговая сумма квадратов чисел от 1 до %d: %d\n", n, totalSum)
}
