/**
 * Лабораторная работа №5 по дисциплине "Современные системы программирования"
 * Задание №1: Исследование базовых методов класса String
 * Студент: Лабынцев Денис Янушевич, группа РС02-23
 */
public class StringOperations {

    /**
     * Метод, выполняющий комплексную обработку переданной строки
     * согласно требованиям пунктов 1-9 Задания №1.
     * 
     * @param str входная строка (например, ФИО студента)
     */
    public static void processString(String str) {
        System.out.println("Исходная строка: \"" + str + "\"");
        System.out.println("--------------------------------------------------");

        // 2. Распечатать последний символ строки
        if (str != null && str.length() > 0) {
            char lastChar = str.charAt(str.length() - 1);
            System.out.println("2. Последний символ строки: '" + lastChar + "'");
        } else {
            System.out.println("2. Строка пуста или равна null");
            return;
        }

        // 3. Проверить, заканчивается ли строка подстрокой "..."
        boolean endsWithDots = str.endsWith("...");
        System.out.println("3. Заканчивается ли подстрокой \"...\": " + endsWithDots);
        boolean endsWithVich = str.endsWith("вич");
        System.out.println("   (дополнительно: заканчивается ли на \"вич\": " + endsWithVich + ")");

        // 4. Проверить, начинается ли строка подстрокой "Фамилия"
        boolean startsWithFam = str.startsWith("Фамилия");
        System.out.println("4. Начинается ли подстрокой \"Фамилия\": " + startsWithFam);
        boolean startsWithLastName = str.startsWith("Лабынцев");
        System.out.println("   (дополнительно: начинается ли на \"Лабынцев\": " + startsWithLastName + ")");

        // 5. Проверить, содержит ли строка подстроку "Имя"
        boolean containsName = str.contains("Имя");
        System.out.println("5. Содержит ли подстроку \"Имя\": " + containsName);
        boolean containsDenis = str.contains("Денис");
        System.out.println("   (дополнительно: содержит ли подстроку \"Денис\": " + containsDenis + ")");

        // 6. Найти позицию подстроки "Имя" / фактического имени в строке
        int posName = str.indexOf("Имя");
        System.out.println("6. Позиция подстроки \"Имя\": " + posName);
        int posDenis = str.indexOf("Денис");
        System.out.println("   Позиция подстроки \"Денис\": " + posDenis);

        // 7. Заменить все символы 'а' на 'о'
        String replaced = str.replace('а', 'о').replace('А', 'О');
        System.out.println("7. Результат замены всех символов 'а' на 'о': \"" + replaced + "\"");

        // 8. Преобразовать строку к верхнему регистру
        String upper = str.toUpperCase();
        System.out.println("8. Преобразование к верхнему регистру: \"" + upper + "\"");

        // 9. Преобразовать строку к нижнему регистру
        String lower = str.toLowerCase();
        System.out.println("9. Преобразование к нижнему регистру: \"" + lower + "\"");
        System.out.println("==================================================");
    }

    public static void main(String[] args) {
        System.out.println("Демонстрация выполнения Задания №1 (класс StringOperations)");
        System.out.println("==================================================");

        // 1. Вызов метода для строки с ФИО студента
        String myFullName = "Лабынцев Денис Янушевич";
        processString(myFullName);

        // Демонстрация для контрольной строки с литералами "Фамилия Имя ..."
        System.out.println("Демонстрация для строки с литералами заданий:");
        String testStr = "Фамилия Имя Отчество...";
        processString(testStr);
    }
}
