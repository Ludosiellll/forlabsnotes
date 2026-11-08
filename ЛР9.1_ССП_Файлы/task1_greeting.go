package main

import (
	"fmt"
)

// sendGreeting отправляет персонализированное приветствие в переданный канал строк
func sendGreeting(name string, ch chan string) {
	ch <- fmt.Sprintf("Привет, %s!", name)
}

func main() {
	// Создание небуферизированного канала для передачи строковых данных
	greetingChan := make(chan string)

	// Запуск функции sendGreeting в отдельном параллельном потоке (горутине)
	go sendGreeting("Денис", greetingChan)

	// Ожидание получения данных из канала и блокировка main до момента передачи
	message := <-greetingChan

	// Вывод полученного приветствия в консоль
	fmt.Println(message)
}
