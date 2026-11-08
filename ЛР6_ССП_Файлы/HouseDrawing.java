import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Polygon;
import java.awt.RenderingHints;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

/**
 * Лабораторная работа №6 по дисциплине "Современные системы программирования"
 * Задание №1: Изучение графических возможностей Java AWT/Swing (Рисование дома)
 * Студент: Лабынцев Денис Янушевич, группа РС02-23
 */
public class HouseDrawing extends JFrame {

    public HouseDrawing() {
        setTitle("Лабораторная работа №6 — Задание №1 (Рисование дома)");
        setSize(800, 650);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Добавление графической панели с отрисовкой дома
        add(new HousePanel());
    }

    /**
     * Пользовательская панель Swing для отрисовки графических примитивов.
     */
    static class HousePanel extends JPanel {

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2d = (Graphics2D) g;

            // Включение сглаживания для качественной отрисовки линий и дуг
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            int width = getWidth();
            int height = getHeight();

            // 1. Небо (фон верхней части)
            g2d.setColor(new Color(135, 206, 235)); // Sky Blue
            g2d.fillRect(0, 0, width, height - 150);

            // 2. Земля / зеленая поляна (нижняя часть)
            g2d.setColor(new Color(34, 139, 34)); // Forest Green
            g2d.fillRect(0, height - 150, width, 150);

            // 3. Солнце и лучи (fillOval + drawLine)
            int sunX = 650, sunY = 70, sunRadius = 45;
            g2d.setColor(Color.YELLOW);
            g2d.fillOval(sunX - sunRadius, sunY - sunRadius, sunRadius * 2, sunRadius * 2);
            g2d.setColor(new Color(255, 165, 0)); // Оранжевый контур солнца
            g2d.drawOval(sunX - sunRadius, sunY - sunRadius, sunRadius * 2, sunRadius * 2);

            // Лучи солнца
            g2d.setColor(new Color(255, 215, 0));
            g2d.setStroke(new BasicStroke(2.5f));
            for (int angle = 0; angle < 360; angle += 30) {
                double rad = Math.toRadians(angle);
                int x1 = (int) (sunX + (sunRadius + 8) * Math.cos(rad));
                int y1 = (int) (sunY + (sunRadius + 8) * Math.sin(rad));
                int x2 = (int) (sunX + (sunRadius + 26) * Math.cos(rad));
                int y2 = (int) (sunY + (sunRadius + 26) * Math.sin(rad));
                g2d.drawLine(x1, y1, x2, y2);
            }

            // 4. Облака (несколько соединенных овалов fillOval)
            g2d.setColor(Color.WHITE);
            // Первое облако
            g2d.fillOval(100, 70, 70, 45);
            g2d.fillOval(130, 50, 90, 60);
            g2d.fillOval(180, 70, 75, 45);
            // Второе облако
            g2d.fillOval(360, 90, 65, 40);
            g2d.fillOval(390, 75, 80, 50);
            g2d.fillOval(430, 90, 60, 40);

            // 5. Дым из трубы (дуги drawArc и эллипсы fillOval)
            g2d.setColor(new Color(180, 180, 180, 180));
            g2d.fillOval(490, 140, 24, 18);
            g2d.fillOval(505, 115, 32, 22);
            g2d.fillOval(525, 85, 42, 28);
            g2d.setColor(new Color(150, 150, 150));
            g2d.drawArc(500, 135, 30, 30, 0, 180);
            g2d.drawArc(515, 110, 40, 35, 45, 180);

            // 6. Кирпичная труба на крыше (fillRect + drawRect)
            g2d.setColor(new Color(139, 69, 19)); // SaddleBrown
            g2d.fillRect(490, 160, 40, 80);
            g2d.setColor(Color.BLACK);
            g2d.setStroke(new BasicStroke(2.0f));
            g2d.drawRect(490, 160, 40, 80);
            // Козырек трубы
            g2d.setColor(new Color(105, 105, 105));
            g2d.fillRect(485, 152, 50, 8);
            g2d.setColor(Color.BLACK);
            g2d.drawRect(485, 152, 50, 8);

            // 7. Стены дома (главный фасад fillRect + drawRect)
            int houseX = 230, houseY = 270, houseW = 340, houseH = 240;
            g2d.setColor(new Color(222, 184, 135)); // Burlywood (теплый цвет бруса)
            g2d.fillRect(houseX, houseY, houseW, houseH);
            g2d.setColor(new Color(101, 67, 33)); // Темно-коричневый контур
            g2d.setStroke(new BasicStroke(3.0f));
            g2d.drawRect(houseX, houseY, houseW, houseH);

            // Горизонтальные линии имитации деревянного бруса
            g2d.setStroke(new BasicStroke(1.0f));
            g2d.setColor(new Color(188, 143, 85));
            for (int y = houseY + 30; y < houseY + houseH; y += 30) {
                g2d.drawLine(houseX + 1, y, houseX + houseW - 1, y);
            }

            // 8. Крыша дома (треугольный полигон fillPolygon + drawPolygon)
            Polygon roof = new Polygon();
            roof.addPoint(houseX - 35, houseY);                  // Левый свес крыши
            roof.addPoint(houseX + houseW / 2, houseY - 140);    // Конек крыши
            roof.addPoint(houseX + houseW + 35, houseY);         // Правый свес крыши

            g2d.setColor(new Color(178, 34, 34)); // Firebrick (черепичный красный)
            g2d.fillPolygon(roof);
            g2d.setColor(new Color(90, 15, 15));
            g2d.setStroke(new BasicStroke(3.0f));
            g2d.drawPolygon(roof);

            // Чердачное круглое окно (fillOval + drawOval + drawLine)
            int atticX = houseX + houseW / 2 - 25, atticY = houseY - 80, atticR = 50;
            g2d.setColor(new Color(224, 255, 255)); // Светло-голубое стекло
            g2d.fillOval(atticX, atticY, atticR, atticR);
            g2d.setColor(new Color(101, 67, 33));
            g2d.setStroke(new BasicStroke(2.5f));
            g2d.drawOval(atticX, atticY, atticR, atticR);
            g2d.drawLine(atticX + atticR / 2, atticY, atticX + atticR / 2, atticY + atticR);
            g2d.drawLine(atticX, atticY + atticR / 2, atticX + atticR, atticY + atticR / 2);

            // 9. Входная дверь (fillRect + drawRect + ручка fillOval)
            int doorW = 75, doorH = 135;
            int doorX = houseX + 45, doorY = houseY + houseH - doorH;
            g2d.setColor(new Color(139, 69, 19)); // Коричневая дверь
            g2d.fillRect(doorX, doorY, doorW, doorH);
            g2d.setColor(new Color(60, 25, 5));
            g2d.setStroke(new BasicStroke(2.5f));
            g2d.drawRect(doorX, doorY, doorW, doorH);

            // Декоративные панели на двери
            g2d.drawRect(doorX + 10, doorY + 15, doorW - 20, 45);
            g2d.drawRect(doorX + 10, doorY + 70, doorW - 20, 50);

            // Круглая золотистая ручка двери
            g2d.setColor(new Color(255, 215, 0));
            g2d.fillOval(doorX + doorW - 16, doorY + doorH / 2, 9, 9);
            g2d.setColor(Color.BLACK);
            g2d.drawOval(doorX + doorW - 16, doorY + doorH / 2, 9, 9);

            // Ступеньки перед дверью
            g2d.setColor(new Color(128, 128, 128));
            g2d.fillRect(doorX - 10, doorY + doorH, doorW + 20, 10);
            g2d.fillRect(doorX - 18, doorY + doorH + 10, doorW + 36, 10);
            g2d.setColor(Color.BLACK);
            g2d.drawRect(doorX - 10, doorY + doorH, doorW + 20, 10);
            g2d.drawRect(doorX - 18, doorY + doorH + 10, doorW + 36, 10);

            // Козырек над дверью (дуга fillArc + кронштейн drawLine)
            g2d.setColor(new Color(178, 34, 34));
            g2d.fillArc(doorX - 15, doorY - 30, doorW + 30, 40, 0, 180);
            g2d.setColor(Color.BLACK);
            g2d.drawArc(doorX - 15, doorY - 30, doorW + 30, 40, 0, 180);
            g2d.drawLine(doorX - 15, doorY - 10, doorX - 5, doorY);
            g2d.drawLine(doorX + doorW + 15, doorY - 10, doorX + doorW + 5, doorY);

            // 10. Большое двухстворчатое окно (fillRect + drawRect + рама drawLine)
            int winW = 120, winH = 100;
            int winX = houseX + 175, winY = houseY + 45;

            // Наличники окна
            g2d.setColor(new Color(255, 250, 240)); // Бежевые наличники
            g2d.fillRect(winX - 6, winY - 6, winW + 12, winH + 12);
            g2d.setColor(Color.BLACK);
            g2d.setStroke(new BasicStroke(1.5f));
            g2d.drawRect(winX - 6, winY - 6, winW + 12, winH + 12);

            // Теплый свет в окне (желтый фон)
            g2d.setColor(new Color(255, 250, 205));
            g2d.fillRect(winX, winY, winW, winH);
            g2d.setColor(new Color(101, 67, 33));
            g2d.setStroke(new BasicStroke(2.0f));
            g2d.drawRect(winX, winY, winW, winH);

            // Оконный переплет (рамы drawLine)
            g2d.drawLine(winX + winW / 2, winY, winX + winW / 2, winY + winH);
            g2d.drawLine(winX, winY + winH / 3, winX + winW, winY + winH / 3);

            // Подоконник
            g2d.setColor(new Color(255, 250, 240));
            g2d.fillRect(winX - 12, winY + winH + 6, winW + 24, 8);
            g2d.setColor(Color.BLACK);
            g2d.drawRect(winX - 12, winY + winH + 6, winW + 24, 8);

            // 11. Забор вокруг дома (линии drawLine и штакетник fillRect)
            g2d.setColor(new Color(160, 82, 45)); // Sienna
            // Левый забор
            for (int x = 20; x < houseX - 20; x += 22) {
                g2d.fillRect(x, height - 190, 14, 70);
                Polygon tip = new Polygon();
                tip.addPoint(x, height - 190);
                tip.addPoint(x + 7, height - 205);
                tip.addPoint(x + 14, height - 190);
                g2d.fillPolygon(tip);
            }
            // Перекладины забора
            g2d.setColor(new Color(110, 50, 20));
            g2d.fillRect(15, height - 175, houseX - 35, 8);
            g2d.fillRect(15, height - 145, houseX - 35, 8);

            // Правый забор
            for (int x = houseX + houseW + 20; x < width - 20; x += 22) {
                g2d.fillRect(x, height - 190, 14, 70);
                Polygon tip = new Polygon();
                tip.addPoint(x, height - 190);
                tip.addPoint(x + 7, height - 205);
                tip.addPoint(x + 14, height - 190);
                g2d.fillPolygon(tip);
            }
            g2d.fillRect(houseX + houseW + 15, height - 175, width - (houseX + houseW + 30), 8);
            g2d.fillRect(houseX + houseW + 15, height - 145, width - (houseX + houseW + 30), 8);

            // 12. Куст и цветы у дома (fillOval + drawLine)
            g2d.setColor(new Color(0, 100, 0));
            g2d.fillOval(houseX + 160, height - 165, 45, 35);
            g2d.fillOval(houseX + 185, height - 175, 55, 45);
            g2d.fillOval(houseX + 225, height - 165, 40, 35);

            // Цветы
            Color[] flowerColors = {Color.RED, Color.MAGENTA, Color.YELLOW, Color.WHITE};
            int[] flowerXs = {houseX + 175, houseX + 205, houseX + 235, houseX + 195};
            int[] flowerYs = {height - 150, height - 160, height - 152, height - 142};
            for (int i = 0; i < flowerXs.length; i++) {
                g2d.setColor(flowerColors[i]);
                g2d.fillOval(flowerXs[i] - 5, flowerYs[i] - 5, 10, 10);
                g2d.setColor(Color.ORANGE);
                g2d.fillOval(flowerXs[i] - 2, flowerYs[i] - 2, 4, 4);
            }
        }
    }

    public static void main(String[] args) {
        // Запуск графического приложения в потоке диспетчеризации событий Swing
        SwingUtilities.invokeLater(() -> {
            HouseDrawing app = new HouseDrawing();
            app.setVisible(true);
        });
    }
}
