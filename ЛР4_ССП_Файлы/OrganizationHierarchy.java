/**
 * Лабораторная работа №4 по дисциплине "Современные системы программирования"
 * Задание №2 (Приложение Б, Вариант 14 - "Организация"):
 * Построить иерархию классов.
 * В методе Main:
 * 1) описать массив объектов базового класса;
 * 2) занести в этот массив объекты дочерних классов;
 * 3) продемонстрировать работу методов класса у всех элементов этого массива.
 */

// Базовый класс иерархии "Организация"
class Organization {
    private String name;
    private String unp;
    private String city;
    private int foundationYear;

    public Organization(String name, String unp, String city, int foundationYear) {
        this.name = name;
        this.unp = unp;
        this.city = city;
        this.foundationYear = foundationYear;
    }

    public String getName() {
        return name;
    }

    public String getUnp() {
        return unp;
    }

    public String getCity() {
        return city;
    }

    public int getFoundationYear() {
        return foundationYear;
    }

    public String getOrganizationType() {
        return "Базовая организация";
    }

    // Полиморфный метод расчета налоговых отчислений
    public double calculateTax() {
        return 0.0;
    }

    // Полиморфный метод выполнения уставной деятельности
    public void performActivity() {
        System.out.println("  Деятельность: общая уставная деятельность юридического лица");
    }

    // Метод отображения общих реквизитов организации
    public void displayInfo() {
        System.out.println("  Организация:   " + name);
        System.out.println("  УНП:           " + unp);
        System.out.println("  Город:         " + city + " (Основана в " + foundationYear + " г.)");
    }
}

// Дочерний класс 1: Коммерческая организация
class CommercialOrganization extends Organization {
    private double annualRevenue;  // Годовая выручка (руб.)
    private double profitTaxRate;   // Ставка налога на прибыль (%)
    private String directorName;    // Руководитель

    public CommercialOrganization(String name, String unp, String city, int foundationYear,
                                  double annualRevenue, double profitTaxRate, String directorName) {
        super(name, unp, city, foundationYear);
        this.annualRevenue = annualRevenue;
        this.profitTaxRate = profitTaxRate;
        this.directorName = directorName;
    }

    @Override
    public String getOrganizationType() {
        return "Коммерческая организация (ОАО / ООО)";
    }

    @Override
    public double calculateTax() {
        // Расчет налога на прибыль от годовой выручки (с учетом условной рентабельности)
        return annualRevenue * 0.15 * (profitTaxRate / 100.0);
    }

    @Override
    public void performActivity() {
        System.out.println("  Деятельность: производство промышленной продукции и оптово-розничная торговля");
    }

    @Override
    public void displayInfo() {
        super.displayInfo();
        System.out.println("  Руководитель:  " + directorName);
        System.out.printf("  Годовая выручка:  %,.2f руб. (Ставка налога: %.1f%%)\n", annualRevenue, profitTaxRate);
    }
}

// Дочерний класс 2: Некоммерческая организация
class NonProfitOrganization extends Organization {
    private double budgetFinancing; // Целевое финансирование / гранты (руб.)
    private int volunteerCount;     // Количество волонтеров
    private String mission;         // Общественная миссия

    public NonProfitOrganization(String name, String unp, String city, int foundationYear,
                                 double budgetFinancing, int volunteerCount, String mission) {
        super(name, unp, city, foundationYear);
        this.budgetFinancing = budgetFinancing;
        this.volunteerCount = volunteerCount;
        this.mission = mission;
    }

    @Override
    public String getOrganizationType() {
        return "Некоммерческая организация (Благотворительный фонд / НКО)";
    }

    @Override
    public double calculateTax() {
        // Некоммерческие организации освобождены от налога на прибыль по целевым средствам
        return 0.0;
    }

    @Override
    public void performActivity() {
        System.out.println("  Деятельность: реализация благотворительных и социально значимых программ");
    }

    @Override
    public void displayInfo() {
        super.displayInfo();
        System.out.println("  Социальная миссия: " + mission);
        System.out.printf("  Целевой бюджет:    %,.2f руб. (Волонтеров: %d чел.)\n", budgetFinancing, volunteerCount);
    }
}

// Дочерний класс 3: Образовательное учреждение (подкласс некоммерческой организации)
class EducationalOrganization extends NonProfitOrganization {
    private int studentsCount;           // Количество обучающихся
    private String accreditationLevel;   // Уровень аккредитации

    public EducationalOrganization(String name, String unp, String city, int foundationYear,
                                   double budgetFinancing, int volunteerCount, String mission,
                                   int studentsCount, String accreditationLevel) {
        super(name, unp, city, foundationYear, budgetFinancing, volunteerCount, mission);
        this.studentsCount = studentsCount;
        this.accreditationLevel = accreditationLevel;
    }

    @Override
    public String getOrganizationType() {
        return "Образовательное учреждение (Колледж / Институт)";
    }

    @Override
    public void performActivity() {
        System.out.println("  Деятельность: подготовка квалифицированных специалистов по направлению ИТ");
    }

    @Override
    public void displayInfo() {
        super.displayInfo();
        System.out.println("  Аккредитация:      " + accreditationLevel);
        System.out.println("  Контингент:        " + studentsCount + " учащихся дневного отделения");
    }
}

// Главный класс с методом main для демонстрации полиморфизма
public class OrganizationHierarchy {
    public static void main(String[] args) {
        System.out.println("Лабораторная работа №4. Задание №2 (Приложение Б, Вариант 14 - «Организация»)");
        System.out.println("Демонстрация полиморфизма и работы с массивом базового класса:\n");

        // 1) Описать массив объектов базового класса Organization
        Organization[] organizations = new Organization[4];

        // 2) Занести в этот массив объекты дочерних классов
        organizations[0] = new CommercialOrganization(
                "ОАО «Белшина»", 
                "700016217", 
                "г. Бобруйск", 
                1972, 
                85400000.0, 
                18.0, 
                "Яковлев А.Н."
        );

        organizations[1] = new CommercialOrganization(
                "ООО «Технопарк Бобруйск»", 
                "790934120", 
                "г. Бобруйск", 
                2018, 
                14200000.0, 
                18.0, 
                "Лабынцев Д.Я."
        );

        organizations[2] = new NonProfitOrganization(
                "Благотворительный фонд «Доброе сердце»", 
                "790112445", 
                "г. Бобруйск", 
                2010, 
                450000.0, 
                85, 
                "Помощь детям-сиротам и социальная поддержка"
        );

        organizations[3] = new EducationalOrganization(
                "Бобруйский государственный колледж им. А.Е. Ларина", 
                "700028911", 
                "г. Бобруйск", 
                1968, 
                2800000.0, 
                120, 
                "Подготовка техников-программистов (группа РС02-23)", 
                1250, 
                "Государственная аккредитация I категории"
        );

        // 3) Продемонстрировать работу методов класса у всех элементов этого массива
        for (int i = 0; i < organizations.length; i++) {
            System.out.println("================================================================================");
            System.out.println("ОБЪЕКТ В МАССИВЕ [" + i + "]: " + organizations[i].getOrganizationType());
            System.out.println("--------------------------------------------------------------------------------");
            organizations[i].displayInfo();
            organizations[i].performActivity();
            System.out.printf("  Налог на прибыль к уплате: %,.2f руб.\n", organizations[i].calculateTax());
        }
        System.out.println("================================================================================");
    }
}
