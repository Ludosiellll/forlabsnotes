import java.util.Scanner;

public class Task3_Rectangles {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Введите сторону a: ");
        double a = scanner.nextDouble();
        System.out.print("Введите сторону b: ");
        double b = scanner.nextDouble();

        System.out.print("Введите сторону c: ");
        double c = scanner.nextDouble();
        System.out.print("Введите сторону d: ");
        double d = scanner.nextDouble();

        if (a <= 0 || b <= 0 || c <= 0 || d <= 0) {
            System.out.println("Стороны должны быть положительными");
            scanner.close();
            return;
        }

        if ((a <= c && b <= d) || (a <= d && b <= c)) {
            System.out.println("Прямоугольник помещается");
        } else {
            System.out.println("Прямоугольник не помещается");
        }

        scanner.close();
    }
}
