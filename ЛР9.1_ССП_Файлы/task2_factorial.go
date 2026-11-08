package main

import (
	"fmt"
)

// calcFactorial вычисляет факториал заданного числа n и передает результат в канал
func calcFactorial(n int, ch chan uint64) {
	var result uint64 = 1
	for i := 1; i <= n; i++ {
		result *= uint64(i)
	}
	ch <- result
}

func main() {
	var n int
	fmt.Print("Введите целое неотрицательное число n для вычисления факториала: ")
	_, err := fmt.Scan(&n)
	if err != nil || n < 0 {
		fmt.Println("Ошибка: введите корректное неотрицательное целое число!")
		return
	}

	// Инициализация канала для передачи вычисленного значения факториала
	factChan := make(chan uint64)

	// Запуск вычисления факториала в отдельной горутине
	go calcFactorial(n, factChan)

	// Получение результата из канала (блокирующее чтение)
	factorialResult := <-factChan

	fmt.Printf("Факториал числа %d! = %d\n", n, factorialResult)
}
