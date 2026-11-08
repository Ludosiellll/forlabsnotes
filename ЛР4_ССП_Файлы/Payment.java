import java.util.ArrayList;
import java.util.List;

/**
 * Лабораторная работа №4 по дисциплине "Современные системы программирования"
 * Задание №1 (Приложение А, Вариант 2):
 * Создать класс Payment (покупка) с внутренним классом, с помощью объектов
 * которого можно сформировать покупку из нескольких товаров.
 */
public class Payment {
    private String orderNumber;
    private String customerName;
    private String date;
    private List<Item> items;

    /**
     * Внутренний (inner) класс, представляющий товарную позицию в чеке покупки.
     * Имеет прямой доступ к контексту внешней покупки.
     */
    public class Item {
        private String name;
        private double price;
        private int quantity;

        public Item(String name, double price, int quantity) {
            this.name = name;
            this.price = price;
            this.quantity = quantity;
        }

        public double getCost() {
            return price * quantity;
        }

        public String getName() {
            return name;
        }

        public double getPrice() {
            return price;
        }

        public int getQuantity() {
            return quantity;
        }

        @Override
        public String toString() {
            return String.format("%-26s %8.2f руб. x %2d шт. = %9.2f руб.", 
                    name, price, quantity, getCost());
        }
    }

    public Payment(String orderNumber, String customerName, String date) {
        this.orderNumber = orderNumber;
        this.customerName = customerName;
        this.date = date;
        this.items = new ArrayList<>();
    }

    // Добавление товара через создание объекта внутреннего класса
    public void addItem(String name, double price, int quantity) {
        Item newItem = new Item(name, price, quantity);
        items.add(newItem);
    }

    // Расчет общей суммы покупки
    public double calculateTotal() {
        double total = 0.0;
        for (Item item : items) {
            total += item.getCost();
        }
        return total;
    }

    // Печать детализированного кассового чека
    public void printReceipt() {
        System.out.println("==================================================================");
        System.out.println("                       КАССОВЫЙ ЧЕК ПОКУПКИ                       ");
        System.out.println("==================================================================");
        System.out.println("Номер заказа: " + orderNumber);
        System.out.println("Покупатель:   " + customerName);
        System.out.println("Дата покупки: " + date);
        System.out.println("------------------------------------------------------------------");
        System.out.println("№   Наименование товара            Цена       Кол-во    Стоимость");
        System.out.println("------------------------------------------------------------------");
        for (int i = 0; i < items.size(); i++) {
            System.out.printf("%2d. %s\n", (i + 1), items.get(i).toString());
        }
        System.out.println("------------------------------------------------------------------");
        System.out.printf("ИТОГО К ОПЛАТЕ:                                     %9.2f руб.\n", calculateTotal());
        System.out.println("==================================================================");
    }

    public static void main(String[] args) {
        System.out.println("Лабораторная работа №4. Задание №1 (Приложение А, Вариант 2)");
        System.out.println("Демонстрация работы класса Payment с внутренним классом Item:\n");

        Payment payment = new Payment("ЧЕК-2026/09-014", "Лабынцев Денис Янушевич", "16.09.2026 14:30");

        // Формирование покупки из нескольких товаров
        payment.addItem("Ноутбук ASUS Vivobook", 2450.00, 1);
        payment.addItem("Беспроводная мышь Logitech", 65.50, 2);
        payment.addItem("Механическая клавиатура", 180.00, 1);
        payment.addItem("Флеш-накопитель USB 64GB", 32.20, 3);
        payment.addItem("Коврик для мыши XL", 25.00, 1);

        // Вывод чека в консоль
        payment.printReceipt();
    }
}
