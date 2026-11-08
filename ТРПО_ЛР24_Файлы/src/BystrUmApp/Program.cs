using System;
using System.Collections.Generic;
using System.Drawing;
using System.Media;
using System.Windows.Forms;

namespace BystrUmApp
{
    // =========================================================================
    // ОСНОВНЫЕ МОДУЛИ СИСТЕМЫ (БИЗНЕС-ЛОГИКА)
    // =========================================================================

    public class ChildProfile
    {
        public string Nickname { get; set; } = "Артём";
        public int Age { get; set; } = 6;
        public int Level { get; set; } = 3;
        public int StarsCount { get; set; } = 14;
        public int ExperiencePoints { get; set; } = 360;

        public void AddRewards(int stars, int xp)
        {
            StarsCount += stars;
            ExperiencePoints += xp;
            if (ExperiencePoints >= Level * 150)
            {
                Level++;
            }
        }

        public void DisplayProfileInfo()
        {
            Console.WriteLine($"[Профиль игрока]: {Nickname}, {Age} лет | Уровень: {Level} | Звёзды: ★ {StarsCount} | Опыт: {ExperiencePoints} XP");
        }
    }

    public class AccessibilitySettings
    {
        public bool GameSoundsEnabled { get; set; } = true;
        public bool BackgroundMusicEnabled { get; set; } = false;
        public bool ReduceMotion { get; set; } = true;
        public bool PlayWithoutTimer { get; set; } = true;
        public int SessionDurationMinutes { get; set; } = 15;
        public bool BreakReminderEnabled { get; set; } = true;

        public void DisplaySettings()
        {
            Console.WriteLine("--- Родительские настройки доступности ---");
            Console.WriteLine($"Звуки игры: {(GameSoundsEnabled ? "Включены (мягкие звуки)" : "Выключены")}");
            Console.WriteLine($"Фоновая музыка: {(BackgroundMusicEnabled ? "Включена" : "Выключена (игра в тишине)")}");
            Console.WriteLine($"Спокойный режим (уменьшить анимацию): {(ReduceMotion ? "Включено" : "Выключено")}");
            Console.WriteLine($"Игра без таймера: {(PlayWithoutTimer ? "Включено (без ограничений)" : "Выключено (с таймером)")}");
            Console.WriteLine($"Длительность занятия: {SessionDurationMinutes} мин | Напоминать о перерыве: {(BreakReminderEnabled ? "Да" : "Нет")}");
        }
    }

    public class Achievement
    {
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public bool IsUnlocked { get; set; }

        public Achievement(string title, string description, string category, bool isUnlocked)
        {
            Title = title;
            Description = description;
            Category = category;
            IsUnlocked = isUnlocked;
        }
    }

    public class AchievementService
    {
        private readonly List<Achievement> _achievements = new();

        public AchievementService()
        {
            _achievements.Add(new Achievement("Друг чисел", "За 1 игру с числами", "Математический спринт", true));
            _achievements.Add(new Achievement("Кубок счёта", "За 5 игр с числами", "Математический спринт", false));
            _achievements.Add(new Achievement("Зоркий глаз", "За 1 игру на поиск", "Поиск лишнего", true));
            _achievements.Add(new Achievement("Кубок внимания", "За 5 игр на поиск", "Поиск лишнего", false));
            _achievements.Add(new Achievement("Первые пары", "За 1 игру с парами", "Логические пары", true));
            _achievements.Add(new Achievement("Кубок логики", "За 5 игр с парами", "Логические пары", false));
        }

        public void Unlock(string title)
        {
            var ach = _achievements.Find(a => a.Title == title);
            if (ach != null && !ach.IsUnlocked)
            {
                ach.IsUnlocked = true;
                Console.WriteLine($"[НОВАЯ НАГРАДА РАЗБЛОКИРОВАНА]: {ach.Title} ({ach.Category})");
            }
        }

        public void DisplayCollection()
        {
            Console.WriteLine("--- Мои достижения и кубки ---");
            Console.WriteLine("«Ты учишься и растёшь! Играй в своём темпе. Новые кубки подождут.»");
            foreach (var item in _achievements)
            {
                string status = item.IsUnlocked ? "[✓ Получено]" : "[Впереди]";
                Console.WriteLine($"  {status} {item.Title} ({item.Category}): {item.Description}");
            }
        }

        public IReadOnlyList<Achievement> Achievements => _achievements;
    }

    public class GameSessionResult
    {
        public string GameTitle { get; set; } = string.Empty;
        public int TotalTasks { get; set; }
        public int CorrectAnswers { get; set; }
        public double AverageReactionTimeMs { get; set; }
        public int EarnedStars { get; set; }
        public int EarnedXP { get; set; }
    }

    public class GameEngine
    {
        public GameSessionResult PlayMathSprint(AccessibilitySettings settings)
        {
            Console.WriteLine("\n[Запуск мини-игры]: Математический спринт (Играй с числами)");
            if (settings.PlayWithoutTimer)
            {
                Console.WriteLine("Режим: Без таймера (комфортный темп для ребенка)");
            }

            int tasksCount = 3;
            int correct = 3;
            double reactionMs = 760.0;

            Console.WriteLine($"Выполнено заданий: {tasksCount}/{tasksCount}");
            Console.WriteLine($"Точность: 100% | Зафиксированная скорость реакции: {reactionMs:F0} мс");

            return new GameSessionResult
            {
                GameTitle = "Математический спринт",
                TotalTasks = tasksCount,
                CorrectAnswers = correct,
                AverageReactionTimeMs = reactionMs,
                EarnedStars = 3,
                EarnedXP = 50
            };
        }
    }

    // =========================================================================
    // ГРАФИЧЕСКИЙ ИНТЕРФЕЙС WINDOWS FORMS (ПРОТОТИП ЛР24)
    // =========================================================================

    public class MainForm : Form
    {
        private readonly ChildProfile _profile = new();
        private readonly AccessibilitySettings _settings = new();
        private readonly AchievementService _achievements = new();
        private readonly GameEngine _engine = new();

        private Panel _headerPanel = null!;
        private Panel _contentPanel = null!;
        private Label _lblProfile = null!;

        public MainForm()
        {
            InitializeComponent();
            ShowMainMenu();
        }

        private void InitializeComponent()
        {
            Text = "БыстрУм";
            Size = new Size(460, 780);
            MinimumSize = new Size(460, 780);
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            Font = new Font("Segoe UI", 10F, FontStyle.Regular);
            BackColor = Color.FromArgb(248, 250, 252);

            _headerPanel = new Panel
            {
                Dock = DockStyle.Top,
                Height = 110,
                BackColor = Color.FromArgb(91, 33, 182),
                Padding = new Padding(15, 10, 15, 10)
            };

            var lblTitle = new Label
            {
                Text = "БыстрУм 🐻",
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 16F, FontStyle.Bold),
                AutoSize = true,
                Location = new Point(15, 12)
            };

            var lblSubtitle = new Label
            {
                Text = "Детское инклюзивное развивающее приложение",
                ForeColor = Color.FromArgb(233, 213, 255),
                Font = new Font("Segoe UI", 8.5F),
                AutoSize = true,
                Location = new Point(17, 44)
            };

            _lblProfile = new Label
            {
                Text = $"{_profile.Nickname} ({_profile.Age} лет) | Уровень: {_profile.Level} | ★ {_profile.StarsCount} | {_profile.ExperiencePoints} XP",
                ForeColor = Color.FromArgb(254, 240, 138),
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                AutoSize = true,
                Location = new Point(17, 72)
            };

            _headerPanel.Controls.Add(lblTitle);
            _headerPanel.Controls.Add(lblSubtitle);
            _headerPanel.Controls.Add(_lblProfile);

            _contentPanel = new Panel
            {
                Dock = DockStyle.Fill,
                AutoScroll = true,
                Padding = new Padding(15)
            };

            Controls.Add(_contentPanel);
            Controls.Add(_headerPanel);
        }

        private void UpdateProfileLabel()
        {
            _lblProfile.Text = $"{_profile.Nickname} ({_profile.Age} лет) | Уровень: {_profile.Level} | ★ {_profile.StarsCount} | {_profile.ExperiencePoints} XP";
        }

        private void ShowMainMenu()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 10;

            var lblWelcome = new Label
            {
                Text = "«Играй, Артём! Выбери игру и играй в своём темпе»",
                Font = new Font("Segoe UI", 10F, FontStyle.Italic),
                ForeColor = Color.FromArgb(71, 85, 105),
                Location = new Point(15, y),
                Size = new Size(400, 35)
            };
            _contentPanel.Controls.Add(lblWelcome);
            y += 45;

            var btnGame1 = CreateGameCard(
                "🧮  Математический спринт",
                "Играй с числами • Сложение и сравнение",
                Color.FromArgb(209, 250, 229),
                Color.FromArgb(6, 95, 70),
                15, y, () => ShowMathSprintGame()
            );
            _contentPanel.Controls.Add(btnGame1);
            y += 85;

            var btnGame2 = CreateGameCard(
                "🔍  Поиск лишнего",
                "Найди лишний предмет на картинке",
                Color.FromArgb(255, 237, 213),
                Color.FromArgb(154, 52, 18),
                15, y, () =>
                {
                    try { SystemSounds.Beep.Play(); } catch { }
                    MessageBox.Show("Запущена мини-игра «Поиск лишнего»!\nРебенок находит неподходящий предмет в комфортном темпе без таймера.", "БыстрУм", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
            );
            _contentPanel.Controls.Add(btnGame2);
            y += 85;

            var btnGame3 = CreateGameCard(
                "🧩  Логические пары",
                "Соединяй подходящие предметы и фигуры",
                Color.FromArgb(237, 233, 254),
                Color.FromArgb(91, 33, 182),
                15, y, () =>
                {
                    try { SystemSounds.Beep.Play(); } catch { }
                    MessageBox.Show("Запущена мини-игра «Логические пары»!\nСоединение предметов по смыслу.", "БыстрУм", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
            );
            _contentPanel.Controls.Add(btnGame3);
            y += 100;

            var btnAchievements = new Button
            {
                Text = "🏆  Мои достижения и кубки",
                Font = new Font("Segoe UI", 10.5F, FontStyle.Bold),
                BackColor = Color.FromArgb(254, 243, 199),
                ForeColor = Color.FromArgb(146, 64, 14),
                FlatStyle = FlatStyle.Flat,
                Location = new Point(15, y),
                Size = new Size(400, 50),
                Cursor = Cursors.Hand
            };
            btnAchievements.FlatAppearance.BorderColor = Color.FromArgb(252, 211, 77);
            btnAchievements.FlatAppearance.BorderSize = 2;
            btnAchievements.Click += (s, e) => ShowAchievementsScreen();
            _contentPanel.Controls.Add(btnAchievements);
            y += 65;

            var btnSettings = new Button
            {
                Text = "⚙️  Родительские настройки",
                Font = new Font("Segoe UI", 10.5F, FontStyle.Bold),
                BackColor = Color.FromArgb(109, 40, 217),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Location = new Point(15, y),
                Size = new Size(400, 50),
                Cursor = Cursors.Hand
            };
            btnSettings.FlatAppearance.BorderSize = 0;
            btnSettings.Click += (s, e) => ShowParentSettingsScreen();
            _contentPanel.Controls.Add(btnSettings);
        }

        private Panel CreateGameCard(string title, string subtitle, Color bg, Color textCol, int x, int y, Action onClick)
        {
            var pnl = new Panel
            {
                Location = new Point(x, y),
                Size = new Size(400, 75),
                BackColor = bg,
                Cursor = Cursors.Hand
            };

            var lblT = new Label
            {
                Text = title,
                Font = new Font("Segoe UI", 11.5F, FontStyle.Bold),
                ForeColor = textCol,
                Location = new Point(15, 12),
                AutoSize = true
            };

            var lblS = new Label
            {
                Text = subtitle,
                Font = new Font("Segoe UI", 9F),
                ForeColor = Color.FromArgb(51, 65, 85),
                Location = new Point(17, 40),
                AutoSize = true
            };

            pnl.Controls.Add(lblT);
            pnl.Controls.Add(lblS);

            pnl.Click += (s, e) => onClick();
            lblT.Click += (s, e) => onClick();
            lblS.Click += (s, e) => onClick();

            return pnl;
        }

        private void ShowParentSettingsScreen()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 10;

            var lblHeader = new Label
            {
                Text = "⚙️ Родительские настройки",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = Color.FromArgb(91, 33, 182),
                Location = new Point(15, y),
                Size = new Size(400, 30)
            };
            _contentPanel.Controls.Add(lblHeader);
            y += 35;

            var grpSound = new GroupBox
            {
                Text = "Звук",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 85)
            };
            var chkSounds = new CheckBox
            {
                Text = "Звуки игры (мягкие частоты)",
                Checked = _settings.GameSoundsEnabled,
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 25),
                Size = new Size(370, 24)
            };
            chkSounds.CheckedChanged += (s, e) => _settings.GameSoundsEnabled = chkSounds.Checked;

            var chkMusic = new CheckBox
            {
                Text = "Фоновая музыка",
                Checked = _settings.BackgroundMusicEnabled,
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 52),
                Size = new Size(370, 24)
            };
            chkMusic.CheckedChanged += (s, e) => _settings.BackgroundMusicEnabled = chkMusic.Checked;

            grpSound.Controls.Add(chkSounds);
            grpSound.Controls.Add(chkMusic);
            _contentPanel.Controls.Add(grpSound);
            y += 95;

            var grpCalm = new GroupBox
            {
                Text = "Спокойный режим (Инклюзивность)",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 85)
            };
            var chkMotion = new CheckBox
            {
                Text = "Уменьшить анимацию (для детей с РАС)",
                Checked = _settings.ReduceMotion,
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 25),
                Size = new Size(370, 24)
            };
            chkMotion.CheckedChanged += (s, e) => _settings.ReduceMotion = chkMotion.Checked;

            var chkTimer = new CheckBox
            {
                Text = "Игра без таймера (без стресса)",
                Checked = _settings.PlayWithoutTimer,
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 52),
                Size = new Size(370, 24)
            };
            chkTimer.CheckedChanged += (s, e) => _settings.PlayWithoutTimer = chkTimer.Checked;

            grpCalm.Controls.Add(chkMotion);
            grpCalm.Controls.Add(chkTimer);
            _contentPanel.Controls.Add(grpCalm);
            y += 95;

            var grpTime = new GroupBox
            {
                Text = "Время занятий",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 75)
            };
            var lblTime = new Label
            {
                Text = "Лимит сессии: 15 минут (с напоминанием о перерыве)",
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 30),
                Size = new Size(370, 25)
            };
            grpTime.Controls.Add(lblTime);
            _contentPanel.Controls.Add(grpTime);
            y += 95;

            var btnBack = new Button
            {
                Text = "← Назад в главное меню",
                Font = new Font("Segoe UI", 9.5F),
                Location = new Point(15, y),
                Size = new Size(400, 38),
                BackColor = Color.FromArgb(241, 245, 249),
                FlatStyle = FlatStyle.Flat
            };
            btnBack.FlatAppearance.BorderSize = 0;
            btnBack.Click += (s, e) => ShowMainMenu();
            _contentPanel.Controls.Add(btnBack);
        }

        private void ShowAchievementsScreen()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 10;

            var lblHeader = new Label
            {
                Text = "🏆 Мои достижения и кубки",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = Color.FromArgb(91, 33, 182),
                Location = new Point(15, y),
                Size = new Size(400, 30)
            };
            _contentPanel.Controls.Add(lblHeader);
            y += 35;

            var lblMotto = new Label
            {
                Text = "«Ты учишься и растёшь! Играй в своём темпе. Новые кубки подождут.»",
                Font = new Font("Segoe UI", 9F, FontStyle.Italic),
                ForeColor = Color.FromArgb(100, 116, 139),
                Location = new Point(15, y),
                Size = new Size(400, 35)
            };
            _contentPanel.Controls.Add(lblMotto);
            y += 45;

            foreach (var item in _achievements.Achievements)
            {
                var pnl = new Panel
                {
                    Location = new Point(15, y),
                    Size = new Size(400, 48),
                    BackColor = item.IsUnlocked ? Color.FromArgb(254, 243, 199) : Color.FromArgb(241, 245, 249),
                    BorderStyle = BorderStyle.FixedSingle
                };
                var lbl = new Label
                {
                    Text = $"{(item.IsUnlocked ? "🏆" : "🔒")} {item.Title} — {item.Description} {(item.IsUnlocked ? "[Получено]" : "[Впереди]")}",
                    Font = new Font("Segoe UI", 9F, item.IsUnlocked ? FontStyle.Bold : FontStyle.Regular),
                    ForeColor = item.IsUnlocked ? Color.FromArgb(146, 64, 14) : Color.FromArgb(100, 116, 139),
                    Location = new Point(10, 12),
                    AutoSize = true
                };
                pnl.Controls.Add(lbl);
                _contentPanel.Controls.Add(pnl);
                y += 56;
            }

            y += 10;
            var btnBack = new Button
            {
                Text = "← Назад в главное меню",
                Font = new Font("Segoe UI", 9.5F),
                Location = new Point(15, y),
                Size = new Size(400, 38),
                BackColor = Color.FromArgb(241, 245, 249),
                FlatStyle = FlatStyle.Flat
            };
            btnBack.FlatAppearance.BorderSize = 0;
            btnBack.Click += (s, e) => ShowMainMenu();
            _contentPanel.Controls.Add(btnBack);
        }

        private void ShowMathSprintGame()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 15;

            var lblGameTitle = new Label
            {
                Text = "🧮 Математический спринт",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = Color.FromArgb(91, 33, 182),
                Location = new Point(15, y),
                Size = new Size(400, 30)
            };
            _contentPanel.Controls.Add(lblGameTitle);
            y += 35;

            var pnlCard = new Panel
            {
                Location = new Point(15, y),
                Size = new Size(400, 100),
                BackColor = Color.FromArgb(254, 249, 195),
                BorderStyle = BorderStyle.FixedSingle
            };
            var lblMath = new Label
            {
                Text = "3 + 2 = ?",
                Font = new Font("Segoe UI", 26F, FontStyle.Bold),
                ForeColor = Color.FromArgb(113, 63, 18),
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter
            };
            pnlCard.Controls.Add(lblMath);
            _contentPanel.Controls.Add(pnlCard);
            y += 120;

            int[] opts = { 4, 5, 6 };
            for (int i = 0; i < opts.Length; i++)
            {
                int val = opts[i];
                var btnOpt = new Button
                {
                    Text = val.ToString(),
                    Font = new Font("Segoe UI", 16F, FontStyle.Bold),
                    Location = new Point(15, y + i * 65),
                    Size = new Size(400, 55),
                    BackColor = Color.FromArgb(241, 245, 249),
                    FlatStyle = FlatStyle.Flat,
                    Cursor = Cursors.Hand
                };
                btnOpt.FlatAppearance.BorderColor = Color.FromArgb(203, 213, 225);
                btnOpt.Click += (s, e) =>
                {
                    if (val == 5)
                    {
                        try { SystemSounds.Asterisk.Play(); } catch { }
                        _profile.AddRewards(1, 15);
                        _achievements.Unlock("Кубок счёта");
                        UpdateProfileLabel();
                        MessageBox.Show("🌟 Отлично, Артём! Ответ правильный!\n★ Начислена 1 звезда и 15 XP!", "Победа!", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                    else
                    {
                        MessageBox.Show("Попробуй ещё раз! Играем без спешки.", "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                    ShowMainMenu();
                };
                _contentPanel.Controls.Add(btnOpt);
            }
            y += 3 * 65 + 15;

            var btnBack = new Button
            {
                Text = "← Завершить игру",
                Font = new Font("Segoe UI", 9.5F),
                Location = new Point(15, y),
                Size = new Size(400, 38),
                BackColor = Color.FromArgb(241, 245, 249),
                FlatStyle = FlatStyle.Flat
            };
            btnBack.FlatAppearance.BorderSize = 0;
            btnBack.Click += (s, e) => ShowMainMenu();
            _contentPanel.Controls.Add(btnBack);
        }
    }

    // =========================================================================
    // ТОЧКА ВХОДА (MAIN)
    // =========================================================================
    internal static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            if (args.Length > 0 && args[0] == "--console")
            {
                Console.OutputEncoding = System.Text.Encoding.UTF8;
                Console.WriteLine("=== Прототип программной системы «БыстрУм» ===");

                var profile = new ChildProfile();
                var settings = new AccessibilitySettings();
                var achievements = new AchievementService();
                var engine = new GameEngine();

                profile.DisplayProfileInfo();
                Console.WriteLine();
                settings.DisplaySettings();
                Console.WriteLine();
                achievements.DisplayCollection();

                var session = engine.PlayMathSprint(settings);

                profile.AddRewards(session.EarnedStars, session.EarnedXP);
                achievements.Unlock("Кубок счёта");

                Console.WriteLine("\n--- Итоги раунда ---");
                Console.WriteLine($"Получено звёзд: +{session.EarnedStars} ★ | Опыт: +{session.EarnedXP} XP");
                profile.DisplayProfileInfo();

                Console.WriteLine("\nНажмите любую клавишу для завершения работы...");
                try { Console.ReadKey(); } catch { }
                return;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}
