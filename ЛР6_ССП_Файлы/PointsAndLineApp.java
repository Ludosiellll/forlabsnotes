import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Stroke;
import java.util.Random;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

/**
 * Лабораторная работа №6 по дисциплине "Современные системы программирования"
 * Задание №2 (Приложение А, Вариант 2):
 * Создать классы Point и Line. Объявить массив из n объектов класса Point
 * и определить в методе, какая из точек находится дальше всех от прямой линии,
 * и пометить ее другим цветом.
 * 
 * Студент: Лабынцев Денис Янушевич, группа РС02-23
 */
public class PointsAndLineApp extends JFrame {

    /**
     * Класс, представляющий двумерную точку на плоскости.
     */
    public static class Point {
        private double x;
        private double y;
        private String name;

        public Point(double x, double y, String name) {
            this.x = x;
            this.y = y;
            this.name = name;
        }

        public double getX() {
            return x;
        }

        public double getY() {
            return y;
        }

        public String getName() {
            return name;
        }

        @Override
        public String toString() {
            return String.format("%s(%.1f, %.1f)", name, x, y);
        }
    }

    /**
     * Класс, представляющий прямую линию, заданную двумя точками A и B.
     */
    public static class Line {
        private Point p1;
        private Point p2;

        public Line(Point p1, Point p2) {
            this.p1 = p1;
            this.p2 = p2;
        }

        public Point getP1() {
            return p1;
        }

        public Point getP2() {
            return p2;
        }

        /**
         * Вычисляет кратчайшее (перпендикулярное) расстояние от заданной точки P до прямой AB.
         * Формула: d = |(y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1| / sqrt((y2 - y1)^2 + (x2 - x1)^2)
         */
        public double distanceTo(Point p) {
            double x0 = p.getX();
            double y0 = p.getY();
            double x1 = p1.getX();
            double y1 = p1.getY();
            double x2 = p2.getX();
            double y2 = p2.getY();

            double numerator = Math.abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1);
            double denominator = Math.hypot(y2 - y1, x2 - x1);

            if (denominator == 0) {
                return Math.hypot(x0 - x1, y0 - y1);
            }
            return numerator / denominator;
        }

        /**
         * Находит основание перпендикуляра от точки P на прямую AB (проекция точки на прямую).
         */
        public Point getProjection(Point p) {
            double x1 = p1.getX(), y1 = p1.getY();
            double x2 = p2.getX(), y2 = p2.getY();
            double dx = x2 - x1;
            double dy = y2 - y1;
            double lenSq = dx * dx + dy * dy;
            if (lenSq == 0) return p1;

            double u = ((p.getX() - x1) * dx + (p.getY() - y1) * dy) / lenSq;
            return new Point(x1 + u * dx, y1 + u * dy, "Proj");
        }
    }

    /**
     * Метод, находящий точку из массива points, наиболее удаленную от прямой line.
     * 
     * @param line   исследуемая прямая линия
     * @param points массив исследуемых точек
     * @return точка, расстояние от которой до прямой максимально
     */
    public static Point findFarthestPoint(Line line, Point[] points) {
        if (points == null || points.length == 0) {
            return null;
        }

        Point farthest = points[0];
        double maxDist = line.distanceTo(farthest);

        for (int i = 1; i < points.length; i++) {
            double d = line.distanceTo(points[i]);
            if (d > maxDist) {
                maxDist = d;
                farthest = points[i];
            }
        }
        return farthest;
    }

    /**
     * Графическая панель Swing для наглядного отображения прямой, точек и выделения наиболее удаленной точки.
     */
    static class GeometryPanel extends JPanel {
        private Line line;
        private Point[] points;
        private Point farthestPoint;

        public GeometryPanel(Line line, Point[] points, Point farthestPoint) {
            this.line = line;
            this.points = points;
            this.farthestPoint = farthestPoint;
            setBackground(new Color(248, 249, 250));
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2d = (Graphics2D) g;
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            int w = getWidth();
            int h = getHeight();

            // 1. Отрисовка координатной сетки
            g2d.setColor(new Color(230, 235, 240));
            for (int x = 40; x < w; x += 40) g2d.drawLine(x, 0, x, h);
            for (int y = 40; y < h; y += 40) g2d.drawLine(0, y, w, y);

            // 2. Отрисовка прямой линии (продлеваем через всю панель)
            double x1 = line.getP1().getX(), y1 = line.getP1().getY();
            double x2 = line.getP2().getX(), y2 = line.getP2().getY();
            double dx = x2 - x1;
            double dy = y2 - y1;

            int drawX1 = (int) (x1 - dx * 4);
            int drawY1 = (int) (y1 - dy * 4);
            int drawX2 = (int) (x2 + dx * 4);
            int drawY2 = (int) (y2 + dy * 4);

            g2d.setColor(new Color(30, 144, 255)); // DodgerBlue
            g2d.setStroke(new BasicStroke(3.0f));
            g2d.drawLine(drawX1, drawY1, drawX2, drawY2);

            // Обозначение прямой
            g2d.setColor(new Color(0, 102, 204));
            g2d.setFont(new Font("Segoe UI", Font.BOLD, 14));
            g2d.drawString("Прямая Line (AB)", (int) x1 - 50, (int) y1 - 15);

            // Опорные точки прямой A и B
            g2d.setColor(new Color(0, 80, 180));
            g2d.fillOval((int) x1 - 5, (int) y1 - 5, 10, 10);
            g2d.drawString("A", (int) x1 + 8, (int) y1 - 4);
            g2d.fillOval((int) x2 - 5, (int) y2 - 5, 10, 10);
            g2d.drawString("B", (int) x2 + 8, (int) y2 - 4);

            // 3. Отрисовка перпендикуляра к наиболее удаленной точке
            if (farthestPoint != null) {
                Point proj = line.getProjection(farthestPoint);
                Stroke dashed = new BasicStroke(2.0f, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL,
                        0, new float[]{6, 4}, 0);
                g2d.setStroke(dashed);
                g2d.setColor(new Color(220, 20, 60)); // Crimson
                g2d.drawLine((int) farthestPoint.getX(), (int) farthestPoint.getY(),
                             (int) proj.getX(), (int) proj.getY());

                // Маркер прямого угла
                g2d.fillOval((int) proj.getX() - 4, (int) proj.getY() - 4, 8, 8);

                // Подпись дистанции
                double dist = line.distanceTo(farthestPoint);
                int midX = (int) ((farthestPoint.getX() + proj.getX()) / 2) + 8;
                int midY = (int) ((farthestPoint.getY() + proj.getY()) / 2);
                g2d.setFont(new Font("Segoe UI", Font.BOLD, 12));
                g2d.drawString(String.format("d_max = %.1f px", dist), midX, midY);
            }

            // 4. Отрисовка массива обычных точек (зеленые круги)
            g2d.setStroke(new BasicStroke(1.5f));
            for (Point p : points) {
                if (p == farthestPoint) continue; // Нарисуем отдельно поверх

                int px = (int) p.getX();
                int py = (int) p.getY();

                // Круг точки
                g2d.setColor(new Color(46, 139, 87)); // SeaGreen
                g2d.fillOval(px - 6, py - 6, 12, 12);
                g2d.setColor(new Color(20, 80, 45));
                g2d.drawOval(px - 6, py - 6, 12, 12);

                // Подпись координат точки
                g2d.setFont(new Font("Consolas", Font.PLAIN, 11));
                g2d.setColor(new Color(40, 40, 40));
                g2d.drawString(String.format("%s (%.0f, %.0f)", p.getName(), p.getX(), p.getY()), px + 8, py - 4);
            }

            // 5. Отрисовка НАИБОЛЕЕ УДАЛЕННОЙ ТОЧКИ (ярко-красный цвет с ореолом)
            if (farthestPoint != null) {
                int fx = (int) farthestPoint.getX();
                int fy = (int) farthestPoint.getY();

                // Внешний полупрозрачный ореол
                g2d.setColor(new Color(255, 0, 0, 70));
                g2d.fillOval(fx - 14, fy - 14, 28, 28);

                // Основной красный маркер точки
                g2d.setColor(new Color(220, 20, 60)); // Crimson Red
                g2d.fillOval(fx - 8, fy - 8, 16, 16);
                g2d.setColor(Color.WHITE);
                g2d.fillOval(fx - 3, fy - 3, 6, 6);
                g2d.setColor(new Color(139, 0, 0));
                g2d.drawOval(fx - 8, fy - 8, 16, 16);

                // Акцентная подпись
                g2d.setFont(new Font("Segoe UI", Font.BOLD, 13));
                g2d.setColor(new Color(178, 34, 34));
                g2d.drawString(String.format("%s [МАКС. УДАЛЕНА: %.1f px]",
                        farthestPoint.getName(), line.distanceTo(farthestPoint)), fx + 12, fy - 8);
            }

            // 6. Информационная плашка с легендой
            g2d.setColor(new Color(255, 255, 255, 230));
            g2d.fillRoundRect(20, 20, 360, 110, 10, 10);
            g2d.setColor(new Color(200, 205, 210));
            g2d.setStroke(new BasicStroke(1.5f));
            g2d.drawRoundRect(20, 20, 360, 110, 10, 10);

            g2d.setFont(new Font("Segoe UI", Font.BOLD, 12));
            g2d.setColor(Color.BLACK);
            g2d.drawString("Легенда графических элементов:", 32, 42);

            g2d.setFont(new Font("Segoe UI", Font.PLAIN, 12));
            g2d.setColor(new Color(30, 144, 255));
            g2d.drawString("— Прямая линия Line", 32, 64);

            g2d.setColor(new Color(46, 139, 87));
            g2d.drawString("● Точки массива Point[]", 32, 84);

            g2d.setColor(new Color(220, 20, 60));
            g2d.drawString("● Наиболее удаленная точка (другой цвет)", 32, 104);
        }
    }

    public PointsAndLineApp(Line line, Point[] points, Point farthest) {
        setTitle("Лабораторная работа №6 — Задание №2 (Вариант 2: Точки и Прямая)");
        setSize(850, 650);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        add(new GeometryPanel(line, points, farthest));
    }

    public static void main(String[] args) {
        System.out.println("Лабораторная работа №6. Задание №2 (Приложение А, Вариант 2)");
        System.out.println("==================================================================");

        // 1. Создание прямой линии AB
        Point a = new Point(120, 480, "A");
        Point b = new Point(680, 180, "B");
        Line line = new Line(a, b);

        System.out.printf("Задана прямая линия через точки %s и %s\n", a, b);

        // 2. Объявление массива из n объектов класса Point
        int n = 8;
        Point[] points = new Point[] {
            new Point(200, 120, "P1"),
            new Point(320, 400, "P2"),
            new Point(450, 280, "P3"),
            new Point(580, 490, "P4"),
            new Point(180, 360, "P5"),
            new Point(640, 350, "P6"),
            new Point(140, 80,  "P7"), // Заведомо удаленная точка
            new Point(500, 140, "P8")
        };

        // 3. Вычисление расстояний для всех точек
        System.out.println("------------------------------------------------------------------");
        System.out.println("№    Точка        Координаты (X, Y)    Расстояние до прямой (px)");
        System.out.println("------------------------------------------------------------------");

        for (int i = 0; i < points.length; i++) {
            double d = line.distanceTo(points[i]);
            System.out.printf("%-4d %-10s   (%-5.1f; %-5.1f)      %7.2f px\n",
                    (i + 1), points[i].getName(), points[i].getX(), points[i].getY(), d);
        }

        // 4. Поиск наиболее удаленной точки в отдельном методе
        Point farthest = findFarthestPoint(line, points);
        double maxDistance = line.distanceTo(farthest);

        System.out.println("==================================================================");
        System.out.printf("НАИБОЛЕЕ УДАЛЕННАЯ ТОЧКА: %s с расстоянием d = %.2f px\n", farthest, maxDistance);
        System.out.println("Она будет выделена ярко-красным цветом на графической панели.");
        System.out.println("==================================================================");

        // Запуск графического интерфейса Swing
        SwingUtilities.invokeLater(() -> {
            PointsAndLineApp app = new PointsAndLineApp(line, points, farthest);
            app.setVisible(true);
        });
    }
}
