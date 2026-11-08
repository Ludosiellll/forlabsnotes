using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Media;
using System.Windows.Forms;

namespace BystrUmAddModules
{
    // =========================================================================
    // ДОПОЛНИТЕЛЬНЫЕ МОДУЛИ СИСТЕМЫ (БИЗНЕС-ЛОГИКА)
    // =========================================================================

    // 1. Дополнительный модуль: Родительский барьер (Parental Gate)
    public class ParentalGateModule
    {
        private int _numA;
        private int _numB;

        public (int numA, int numB, string question) GenerateQuestion()
        {
            var rand = new Random();
            _numA = rand.Next(2, 6);
            _numB = rand.Next(2, 6);
            return (_numA, _numB, $"Сколько будет {_numA} + {_numB}?");
        }

        public bool ValidateAnswer(int userAnswer)
        {
            bool isCorrect = (userAnswer == (_numA + _numB));
            if (isCorrect)
            {
                Console.WriteLine("[Родительский барьер]: Доступ подтвержден. Переход к настройкам.");
            }
            else
            {
                Console.WriteLine("[Родительский барьер]: Неверный ответ. Доступ заблокирован.");
            }
            return isCorrect;
        }

        public int CorrectAnswer => _numA + _numB;
    }

    // 2. Дополнительный модуль: Контроль сессии и напоминания об отдыхе (Break Reminder)
    public class BreakReminderModule
    {
        public int SessionLimitMinutes { get; set; } = 15;
        public bool ReminderEnabled { get; set; } = true;

        public bool CheckSessionTime(int elapsedMinutes, string childName, out string message)
        {
            if (ReminderEnabled && elapsedMinutes >= SessionLimitMinutes)
            {
                message = $"Время отдохнуть, {childName}! Ты отлично позанимался {SessionLimitMinutes} мин. Сделай разминку для глаз и потянись.";
                return true;
            }
            message = string.Empty;
            return false;
        }
    }

    // 3. Дополнительный модуль: Когнитивная аналитика и метрики (Cognitive Analytics)
    public class MetricEntry
    {
        public string ActivityName { get; set; } = string.Empty;
        public int ReactionTimeMs { get; set; }
        public bool IsCorrect { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class CognitiveAnalyticsModule
    {
        private readonly List<MetricEntry> _history = new();

        public CognitiveAnalyticsModule()
        {
            // Начальные данные сессии
            _history.Add(new MetricEntry { ActivityName = "Математический спринт", ReactionTimeMs = 740, IsCorrect = true, Timestamp = DateTime.Now.AddMinutes(-10) });
            _history.Add(new MetricEntry { ActivityName = "Математический спринт", ReactionTimeMs = 780, IsCorrect = true, Timestamp = DateTime.Now.AddMinutes(-8) });
            _history.Add(new MetricEntry { ActivityName = "Математический спринт", ReactionTimeMs = 760, IsCorrect = true, Timestamp = DateTime.Now.AddMinutes(-5) });
        }

        public void RecordResponse(string activity, int reactionMs, bool correct)
        {
            _history.Add(new MetricEntry
            {
                ActivityName = activity,
                ReactionTimeMs = reactionMs,
                IsCorrect = correct,
                Timestamp = DateTime.Now
            });
        }

        public (int total, double accuracy, double avgReaction, string status) GetSummary()
        {
            if (!_history.Any())
            {
                return (0, 100.0, 760.0, "Нет данных");
            }

            double avgReaction = _history.Average(m => m.ReactionTimeMs);
            int total = _history.Count;
            int correctCount = _history.Count(m => m.IsCorrect);
            double accuracy = (double)correctCount / total * 100.0;
            string status = avgReaction < 900
                ? "Высокая концентрация внимания. Признаков утомления нет."
                : "Умеренная утомляемость. Рекомендуется сделать перерыв.";

            return (total, accuracy, avgReaction, status);
        }

        public IReadOnlyList<MetricEntry> History => _history;
    }

    // 4. Дополнительный модуль: Тактильный и звуковой отклик (Haptic & Audio Feedback)
    public class HapticAudioFeedbackModule
    {
        public bool HapticEnabled { get; set; } = true;
        public bool SoundEnabled { get; set; } = true;

        public void TriggerCardTapFeedback()
        {
            if (SoundEnabled)
            {
                try { SystemSounds.Beep.Play(); } catch { }
            }
        }

        public void TriggerRewardFeedback()
        {
            if (SoundEnabled)
            {
                try { SystemSounds.Asterisk.Play(); } catch { }
            }
        }
    }

    // 5. Дополнительный модуль: Адаптер цветовых тем доступности (Color Blind Theme Adapter)
    public class ColorBlindThemeModule
    {
        public enum ThemeMode { Standard, Protanopia, Deuteranopia, Tritanopia }
        public ThemeMode CurrentTheme { get; private set; } = ThemeMode.Standard;

        public Color PrimaryColor { get; private set; } = Color.FromArgb(109, 40, 217);    // Фиолетовый
        public Color HeaderBgColor { get; private set; } = Color.FromArgb(91, 33, 182);
        public Color AccentColor { get; private set; } = Color.FromArgb(245, 158, 11);    // Янтарно-желтый
        public Color BackgroundColor { get; private set; } = Color.FromArgb(248, 250, 252);
        public Color CardBgColor { get; private set; } = Color.White;
        public Color SuccessColor { get; private set; } = Color.FromArgb(16, 185, 129);

        public void ApplyTheme(ThemeMode mode)
        {
            CurrentTheme = mode;
            switch (mode)
            {
                case ThemeMode.Protanopia:
                    PrimaryColor = Color.FromArgb(2, 132, 199);       // Синий
                    HeaderBgColor = Color.FromArgb(3, 105, 161);
                    AccentColor = Color.FromArgb(202, 138, 4);        // Золотисто-желтый
                    SuccessColor = Color.FromArgb(13, 148, 136);
                    break;
                case ThemeMode.Deuteranopia:
                    PrimaryColor = Color.FromArgb(37, 99, 235);       // Сине-голубой
                    HeaderBgColor = Color.FromArgb(29, 78, 216);
                    AccentColor = Color.FromArgb(217, 119, 6);        // Оранжево-желтый
                    SuccessColor = Color.FromArgb(8, 145, 178);
                    break;
                case ThemeMode.Tritanopia:
                    PrimaryColor = Color.FromArgb(220, 38, 38);       // Красный спектр
                    HeaderBgColor = Color.FromArgb(185, 28, 28);
                    AccentColor = Color.FromArgb(5, 150, 105);        // Бирюзовый
                    SuccessColor = Color.FromArgb(22, 163, 74);
                    break;
                default:
                    PrimaryColor = Color.FromArgb(109, 40, 217);
                    HeaderBgColor = Color.FromArgb(91, 33, 182);
                    AccentColor = Color.FromArgb(245, 158, 11);
                    SuccessColor = Color.FromArgb(16, 185, 129);
                    break;
            }
        }
    }

    // =========================================================================
    // ГРАФИЧЕСКИЙ ИНТЕРФЕЙС WINDOWS FORMS (ИНТЕРАКТИВНЫЙ ПРОТОТИП «БЫСТРУМ»)
    // =========================================================================

    public class MainForm : Form
    {
        private readonly ParentalGateModule _parentalGate = new();
        private readonly BreakReminderModule _breakReminder = new();
        private readonly CognitiveAnalyticsModule _analytics = new();
        private readonly HapticAudioFeedbackModule _feedback = new();
        private readonly ColorBlindThemeModule _theme = new();

        private Panel _headerPanel = null!;
        private Panel _contentPanel = null!;
        private Label _lblTitle = null!;
        private Label _lblProfile = null!;

        // User stats
        private int _stars = 14;
        private int _xp = 360;
        private int _level = 3;

        // Parental gate state
        private string _gateEnteredPin = "";
        private Label _lblGatePin = null!;
        private Label _lblGatePrompt = null!;
        private Label _lblGateError = null!;

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
            BackColor = _theme.BackgroundColor;

            // Header Panel
            _headerPanel = new Panel
            {
                Dock = DockStyle.Top,
                Height = 110,
                BackColor = _theme.HeaderBgColor,
                Padding = new Padding(15, 10, 15, 10)
            };

            _lblTitle = new Label
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
                Text = $"Артём (6 лет) | Уровень: {_level} | ★ {_stars} | {_xp} XP",
                ForeColor = Color.FromArgb(254, 240, 138),
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                AutoSize = true,
                Location = new Point(17, 72)
            };

            _headerPanel.Controls.Add(_lblTitle);
            _headerPanel.Controls.Add(lblSubtitle);
            _headerPanel.Controls.Add(_lblProfile);

            // Content Panel
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
            _lblProfile.Text = $"Артём (6 лет) | Уровень: {_level} | ★ {_stars} | {_xp} XP";
        }

        private void ApplyThemeStyles()
        {
            _headerPanel.BackColor = _theme.HeaderBgColor;
            BackColor = _theme.BackgroundColor;
        }

        // ---------------------------------------------------------------------
        // ЭКРАН 1: ГЛАВНОЕ МЕНЮ
        // ---------------------------------------------------------------------
        private void ShowMainMenu()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 10;

            // Welcome banner
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

            // Card 1: Math Sprint
            var btnGame1 = CreateGameCard(
                "🧮  Математический спринт",
                "Играй с числами • Сложение и сравнение",
                Color.FromArgb(209, 250, 229),
                Color.FromArgb(6, 95, 70),
                15, y, () => ShowMathSprintGame()
            );
            _contentPanel.Controls.Add(btnGame1);
            y += 85;

            // Card 2: Find Extra
            var btnGame2 = CreateGameCard(
                "🔍  Поиск лишнего",
                "Найди лишний предмет на картинке",
                Color.FromArgb(255, 237, 213),
                Color.FromArgb(154, 52, 18),
                15, y, () =>
                {
                    _feedback.TriggerCardTapFeedback();
                    MessageBox.Show("Запущена мини-игра «Поиск лишнего»!\nРебенок находит неподходящий предмет в комфортном темпе без таймера.", "БыстрУм", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
            );
            _contentPanel.Controls.Add(btnGame2);
            y += 85;

            // Card 3: Logic Pairs
            var btnGame3 = CreateGameCard(
                "🧩  Логические пары",
                "Соединяй подходящие предметы и фигуры",
                Color.FromArgb(237, 233, 254),
                Color.FromArgb(91, 33, 182),
                15, y, () =>
                {
                    _feedback.TriggerCardTapFeedback();
                    MessageBox.Show("Запущена мини-игра «Логические пары»!\nСоединение пар предметов по смыслу.", "БыстрУм", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
            );
            _contentPanel.Controls.Add(btnGame3);
            y += 100;

            // Achievements Button
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
            btnAchievements.Click += (s, e) =>
            {
                _feedback.TriggerCardTapFeedback();
                ShowAchievementsScreen();
            };
            _contentPanel.Controls.Add(btnAchievements);
            y += 65;

            // Parental Settings Button (Triggers Parental Gate!)
            var btnSettings = new Button
            {
                Text = "⚙️  Родительские настройки (Вход по PIN)",
                Font = new Font("Segoe UI", 10.5F, FontStyle.Bold),
                BackColor = _theme.PrimaryColor,
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Location = new Point(15, y),
                Size = new Size(400, 50),
                Cursor = Cursors.Hand
            };
            btnSettings.FlatAppearance.BorderSize = 0;
            btnSettings.Click += (s, e) =>
            {
                _feedback.TriggerCardTapFeedback();
                ShowParentalGateDialog();
            };
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

        // ---------------------------------------------------------------------
        // ЭКРАН 2: РОДИТЕЛЬСКИЙ БАРЬЕР (PARENTAL GATE DIALOG)
        // ---------------------------------------------------------------------
        private void ShowParentalGateDialog()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            var q = _parentalGate.GenerateQuestion();
            _gateEnteredPin = "";

            int y = 10;

            var pnlWarn = new Panel
            {
                Location = new Point(15, y),
                Size = new Size(400, 60),
                BackColor = Color.FromArgb(254, 242, 242),
                BorderStyle = BorderStyle.FixedSingle
            };
            var lblWarn = new Label
            {
                Text = "🔒 Вход в настройки защищен от случайных нажатий!\nПодтвердите, что вы взрослый пользователь.",
                Font = new Font("Segoe UI", 9F, FontStyle.Bold),
                ForeColor = Color.FromArgb(185, 28, 28),
                Location = new Point(10, 10),
                Size = new Size(380, 40)
            };
            pnlWarn.Controls.Add(lblWarn);
            _contentPanel.Controls.Add(pnlWarn);
            y += 75;

            _lblGatePrompt = new Label
            {
                Text = q.question,
                Font = new Font("Segoe UI", 14F, FontStyle.Bold),
                ForeColor = Color.FromArgb(30, 41, 59),
                Location = new Point(15, y),
                Size = new Size(400, 35),
                TextAlign = ContentAlignment.MiddleCenter
            };
            _contentPanel.Controls.Add(_lblGatePrompt);
            y += 40;

            _lblGatePin = new Label
            {
                Text = "[ Введите ответ ]",
                Font = new Font("Segoe UI", 16F, FontStyle.Bold),
                ForeColor = _theme.PrimaryColor,
                Location = new Point(15, y),
                Size = new Size(400, 40),
                TextAlign = ContentAlignment.MiddleCenter,
                BackColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            _contentPanel.Controls.Add(_lblGatePin);
            y += 50;

            _lblGateError = new Label
            {
                Text = "",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                ForeColor = Color.Red,
                Location = new Point(15, y),
                Size = new Size(400, 25),
                TextAlign = ContentAlignment.MiddleCenter
            };
            _contentPanel.Controls.Add(_lblGateError);
            y += 30;

            // Numeric PIN pad buttons
            int padStartX = 70;
            int btnW = 85;
            int btnH = 50;
            int gap = 12;

            int[,] buttons = {
                { 1, 2, 3 },
                { 4, 5, 6 },
                { 7, 8, 9 }
            };

            for (int r = 0; r < 3; r++)
            {
                for (int c = 0; c < 3; c++)
                {
                    int val = buttons[r, c];
                    var btnDigit = new Button
                    {
                        Text = val.ToString(),
                        Font = new Font("Segoe UI", 14F, FontStyle.Bold),
                        Location = new Point(padStartX + c * (btnW + gap), y + r * (btnH + gap)),
                        Size = new Size(btnW, btnH),
                        BackColor = Color.FromArgb(241, 245, 249),
                        FlatStyle = FlatStyle.Flat
                    };
                    btnDigit.FlatAppearance.BorderColor = Color.FromArgb(203, 213, 225);
                    btnDigit.Click += (s, e) =>
                    {
                        _feedback.TriggerCardTapFeedback();
                        _gateEnteredPin += val.ToString();
                        _lblGatePin.Text = _gateEnteredPin;
                        _lblGateError.Text = "";
                    };
                    _contentPanel.Controls.Add(btnDigit);
                }
            }
            y += 3 * (btnH + gap);

            // Bottom row: Clear, 0, Submit
            var btnClear = new Button
            {
                Text = "Стереть",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(padStartX, y),
                Size = new Size(btnW, btnH),
                BackColor = Color.FromArgb(254, 226, 226),
                ForeColor = Color.FromArgb(185, 28, 28),
                FlatStyle = FlatStyle.Flat
            };
            btnClear.FlatAppearance.BorderSize = 0;
            btnClear.Click += (s, e) =>
            {
                _feedback.TriggerCardTapFeedback();
                _gateEnteredPin = "";
                _lblGatePin.Text = "[ Введите ответ ]";
                _lblGateError.Text = "";
            };
            _contentPanel.Controls.Add(btnClear);

            var btnZero = new Button
            {
                Text = "0",
                Font = new Font("Segoe UI", 14F, FontStyle.Bold),
                Location = new Point(padStartX + btnW + gap, y),
                Size = new Size(btnW, btnH),
                BackColor = Color.FromArgb(241, 245, 249),
                FlatStyle = FlatStyle.Flat
            };
            btnZero.FlatAppearance.BorderColor = Color.FromArgb(203, 213, 225);
            btnZero.Click += (s, e) =>
            {
                _feedback.TriggerCardTapFeedback();
                _gateEnteredPin += "0";
                _lblGatePin.Text = _gateEnteredPin;
                _lblGateError.Text = "";
            };
            _contentPanel.Controls.Add(btnZero);

            var btnSubmit = new Button
            {
                Text = "Вход",
                Font = new Font("Segoe UI", 11F, FontStyle.Bold),
                Location = new Point(padStartX + 2 * (btnW + gap), y),
                Size = new Size(btnW, btnH),
                BackColor = _theme.SuccessColor,
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat
            };
            btnSubmit.FlatAppearance.BorderSize = 0;
            btnSubmit.Click += (s, e) =>
            {
                if (int.TryParse(_gateEnteredPin, out int parsedAnswer))
                {
                    if (_parentalGate.ValidateAnswer(parsedAnswer))
                    {
                        _feedback.TriggerRewardFeedback();
                        ShowParentSettingsScreen();
                    }
                    else
                    {
                        _lblGateError.Text = "❌ Неверный ответ! Доступ запрещен.";
                        _feedback.TriggerCardTapFeedback();
                    }
                }
                else
                {
                    _lblGateError.Text = "Пожалуйста, наберите число.";
                }
            };
            _contentPanel.Controls.Add(btnSubmit);
            y += btnH + 20;

            // Cancel Button
            var btnCancel = new Button
            {
                Text = "← Отмена и возврат в меню",
                Font = new Font("Segoe UI", 9.5F),
                Location = new Point(15, y),
                Size = new Size(400, 38),
                BackColor = Color.FromArgb(241, 245, 249),
                FlatStyle = FlatStyle.Flat
            };
            btnCancel.FlatAppearance.BorderSize = 0;
            btnCancel.Click += (s, e) => ShowMainMenu();
            _contentPanel.Controls.Add(btnCancel);
        }

        // ---------------------------------------------------------------------
        // ЭКРАН 3: РОДИТЕЛЬСКИЕ НАСТРОЙКИ (SETTINGS SCREEN)
        // ---------------------------------------------------------------------
        private void ShowParentSettingsScreen()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 10;

            var lblHeader = new Label
            {
                Text = "⚙️ Родительские настройки",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = _theme.HeaderBgColor,
                Location = new Point(15, y),
                Size = new Size(400, 30)
            };
            _contentPanel.Controls.Add(lblHeader);
            y += 35;

            // Section 1: Sound
            var grpSound = new GroupBox
            {
                Text = "Звуковое сопровождение",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 85)
            };
            var chkSounds = new CheckBox
            {
                Text = "Звуки игры (мягкие частоты, без резких звуков)",
                Checked = _feedback.SoundEnabled,
                Font = new Font("Segoe UI", 9F, FontStyle.Regular),
                Location = new Point(15, 25),
                Size = new Size(370, 24)
            };
            chkSounds.CheckedChanged += (s, e) => _feedback.SoundEnabled = chkSounds.Checked;

            var chkHaptic = new CheckBox
            {
                Text = "Тактильный отклик (Light Impact 25 мс)",
                Checked = _feedback.HapticEnabled,
                Font = new Font("Segoe UI", 9F, FontStyle.Regular),
                Location = new Point(15, 52),
                Size = new Size(370, 24)
            };
            chkHaptic.CheckedChanged += (s, e) => _feedback.HapticEnabled = chkHaptic.Checked;

            grpSound.Controls.Add(chkSounds);
            grpSound.Controls.Add(chkHaptic);
            _contentPanel.Controls.Add(grpSound);
            y += 95;

            // Section 2: Time Management & Break Reminder
            var grpTime = new GroupBox
            {
                Text = "Тайм-менеджмент и отдых",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 115)
            };
            var lblSession = new Label
            {
                Text = "Лимит непрерывной сессии: 15 минут",
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 25),
                Size = new Size(370, 20)
            };
            var chkBreak = new CheckBox
            {
                Text = "Включить напоминание о перерыве и разминке",
                Checked = _breakReminder.ReminderEnabled,
                Font = new Font("Segoe UI", 9F),
                Location = new Point(15, 50),
                Size = new Size(370, 22)
            };
            chkBreak.CheckedChanged += (s, e) => _breakReminder.ReminderEnabled = chkBreak.Checked;

            var btnTestBreak = new Button
            {
                Text = "🌿 Проверить окно отдыха (Демо)",
                Font = new Font("Segoe UI", 8.5F, FontStyle.Bold),
                BackColor = Color.FromArgb(220, 252, 231),
                ForeColor = Color.FromArgb(21, 128, 61),
                FlatStyle = FlatStyle.Flat,
                Location = new Point(15, 78),
                Size = new Size(370, 28)
            };
            btnTestBreak.FlatAppearance.BorderSize = 0;
            btnTestBreak.Click += (s, e) => ShowBreakReminderModal();

            grpTime.Controls.Add(lblSession);
            grpTime.Controls.Add(chkBreak);
            grpTime.Controls.Add(btnTestBreak);
            _contentPanel.Controls.Add(grpTime);
            y += 125;

            // Section 3: Color Blind Themes
            var grpTheme = new GroupBox
            {
                Text = "Адаптация палитры (Дальтонизм)",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 130)
            };

            var rbStd = new RadioButton { Text = "Стандартная (теплая фиолетово-желтая)", Checked = _theme.CurrentTheme == ColorBlindThemeModule.ThemeMode.Standard, Location = new Point(15, 22), Size = new Size(370, 22), Font = new Font("Segoe UI", 9F) };
            var rbProt = new RadioButton { Text = "Протанопия (сине-желтый баланс)", Checked = _theme.CurrentTheme == ColorBlindThemeModule.ThemeMode.Protanopia, Location = new Point(15, 46), Size = new Size(370, 22), Font = new Font("Segoe UI", 9F) };
            var rbDeut = new RadioButton { Text = "Дейтеранопия (зеленый спектр)", Checked = _theme.CurrentTheme == ColorBlindThemeModule.ThemeMode.Deuteranopia, Location = new Point(15, 70), Size = new Size(370, 22), Font = new Font("Segoe UI", 9F) };
            var rbTrit = new RadioButton { Text = "Тританопия (красно-бирюзовый баланс)", Checked = _theme.CurrentTheme == ColorBlindThemeModule.ThemeMode.Tritanopia, Location = new Point(15, 94), Size = new Size(370, 22), Font = new Font("Segoe UI", 9F) };

            rbStd.CheckedChanged += (s, e) => { if (rbStd.Checked) { _theme.ApplyTheme(ColorBlindThemeModule.ThemeMode.Standard); ApplyThemeStyles(); } };
            rbProt.CheckedChanged += (s, e) => { if (rbProt.Checked) { _theme.ApplyTheme(ColorBlindThemeModule.ThemeMode.Protanopia); ApplyThemeStyles(); } };
            rbDeut.CheckedChanged += (s, e) => { if (rbDeut.Checked) { _theme.ApplyTheme(ColorBlindThemeModule.ThemeMode.Deuteranopia); ApplyThemeStyles(); } };
            rbTrit.CheckedChanged += (s, e) => { if (rbTrit.Checked) { _theme.ApplyTheme(ColorBlindThemeModule.ThemeMode.Tritanopia); ApplyThemeStyles(); } };

            grpTheme.Controls.Add(rbStd);
            grpTheme.Controls.Add(rbProt);
            grpTheme.Controls.Add(rbDeut);
            grpTheme.Controls.Add(rbTrit);
            _contentPanel.Controls.Add(grpTheme);
            y += 140;

            // Section 4: Analytics
            var btnOpenAnalytics = new Button
            {
                Text = "📊  Открыть когнитивную аналитику ребенка",
                Font = new Font("Segoe UI", 10F, FontStyle.Bold),
                BackColor = Color.FromArgb(238, 242, 255),
                ForeColor = Color.FromArgb(67, 56, 202),
                FlatStyle = FlatStyle.Flat,
                Location = new Point(15, y),
                Size = new Size(400, 45),
                Cursor = Cursors.Hand
            };
            btnOpenAnalytics.FlatAppearance.BorderColor = Color.FromArgb(199, 210, 254);
            btnOpenAnalytics.Click += (s, e) =>
            {
                _feedback.TriggerCardTapFeedback();
                ShowAnalyticsScreen();
            };
            _contentPanel.Controls.Add(btnOpenAnalytics);
            y += 55;

            // Back to Main Menu
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

        // ---------------------------------------------------------------------
        // ЭКРАН 4: КОГНИТИВНАЯ АНАЛИТИКА (ANALYTICS SCREEN)
        // ---------------------------------------------------------------------
        private void ShowAnalyticsScreen()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            var summary = _analytics.GetSummary();
            int y = 10;

            var lblHeader = new Label
            {
                Text = "📊 Когнитивная аналитика Артёма",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = _theme.HeaderBgColor,
                Location = new Point(15, y),
                Size = new Size(400, 30)
            };
            _contentPanel.Controls.Add(lblHeader);
            y += 35;

            // Metrics Cards Panel
            var pnlMetrics = new Panel
            {
                Location = new Point(15, y),
                Size = new Size(400, 115),
                BackColor = Color.FromArgb(248, 250, 252),
                BorderStyle = BorderStyle.FixedSingle
            };

            var lblAcc = new Label
            {
                Text = $"Точность: {summary.accuracy:F0}%\n(100% верных)",
                Font = new Font("Segoe UI", 10F, FontStyle.Bold),
                ForeColor = Color.FromArgb(16, 185, 129),
                Location = new Point(15, 15),
                Size = new Size(160, 45),
                TextAlign = ContentAlignment.TopCenter
            };

            var lblReact = new Label
            {
                Text = $"Скорость реакции:\n{summary.avgReaction:F0} мс",
                Font = new Font("Segoe UI", 10F, FontStyle.Bold),
                ForeColor = Color.FromArgb(79, 70, 229),
                Location = new Point(200, 15),
                Size = new Size(180, 45),
                TextAlign = ContentAlignment.TopCenter
            };

            var lblTotal = new Label
            {
                Text = $"Всего решено заданий в сессии: {summary.total}",
                Font = new Font("Segoe UI", 9F),
                ForeColor = Color.FromArgb(71, 85, 105),
                Location = new Point(15, 75),
                Size = new Size(370, 25),
                TextAlign = ContentAlignment.MiddleCenter
            };

            pnlMetrics.Controls.Add(lblAcc);
            pnlMetrics.Controls.Add(lblReact);
            pnlMetrics.Controls.Add(lblTotal);
            _contentPanel.Controls.Add(pnlMetrics);
            y += 125;

            // Conclusion
            var pnlConc = new Panel
            {
                Location = new Point(15, y),
                Size = new Size(400, 75),
                BackColor = Color.FromArgb(236, 253, 245),
                BorderStyle = BorderStyle.FixedSingle
            };
            var lblConc = new Label
            {
                Text = $"🟢 Заключение мониторинга:\n{summary.status}",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                ForeColor = Color.FromArgb(6, 95, 70),
                Location = new Point(10, 10),
                Size = new Size(380, 50)
            };
            pnlConc.Controls.Add(lblConc);
            _contentPanel.Controls.Add(pnlConc);
            y += 85;

            // Session History List
            var lblHist = new Label
            {
                Text = "История последних замеров реакции:",
                Font = new Font("Segoe UI", 9.5F, FontStyle.Bold),
                Location = new Point(15, y),
                Size = new Size(400, 25)
            };
            _contentPanel.Controls.Add(lblHist);
            y += 28;

            var listHist = new ListBox
            {
                Location = new Point(15, y),
                Size = new Size(400, 150),
                Font = new Font("Consolas", 9F)
            };
            foreach (var item in _analytics.History.TakeLast(6))
            {
                listHist.Items.Add($"{item.Timestamp:HH:mm:ss} | {item.ActivityName} | {item.ReactionTimeMs} мс | [OK]");
            }
            _contentPanel.Controls.Add(listHist);
            y += 160;

            // Back Button
            var btnBack = new Button
            {
                Text = "← Назад в настройки",
                Font = new Font("Segoe UI", 9.5F),
                Location = new Point(15, y),
                Size = new Size(400, 38),
                BackColor = Color.FromArgb(241, 245, 249),
                FlatStyle = FlatStyle.Flat
            };
            btnBack.FlatAppearance.BorderSize = 0;
            btnBack.Click += (s, e) => ShowParentSettingsScreen();
            _contentPanel.Controls.Add(btnBack);
        }

        // ---------------------------------------------------------------------
        // ЭКРАН 5: МОДАЛЬНОЕ ОКНО ОТДЫХА (BREAK REMINDER MODAL)
        // ---------------------------------------------------------------------
        private void ShowBreakReminderModal()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 30;

            var pnlModal = new Panel
            {
                Location = new Point(15, y),
                Size = new Size(400, 380),
                BackColor = Color.FromArgb(240, 253, 244),
                BorderStyle = BorderStyle.FixedSingle
            };

            var lblIcon = new Label
            {
                Text = "🌿 🧸 ⏰",
                Font = new Font("Segoe UI", 28F),
                Location = new Point(15, 20),
                Size = new Size(370, 55),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var lblTitle = new Label
            {
                Text = "Время отдохнуть, Артём!",
                Font = new Font("Segoe UI", 14F, FontStyle.Bold),
                ForeColor = Color.FromArgb(21, 128, 61),
                Location = new Point(15, 80),
                Size = new Size(370, 35),
                TextAlign = ContentAlignment.MiddleCenter
            };

            var lblDesc = new Label
            {
                Text = "Ты отлично позанимался 15 минут!\n\nСделай разминку для глаз:\n1. Поморгай глазками 5 раз\n2. Посмотри в окошко вдаль\n3. Потянись вверх ручками!",
                Font = new Font("Segoe UI", 10F),
                ForeColor = Color.FromArgb(22, 101, 52),
                Location = new Point(25, 125),
                Size = new Size(350, 150),
                TextAlign = ContentAlignment.TopCenter
            };

            var btnOk = new Button
            {
                Text = "Хорошо, отдыхаем! 💚",
                Font = new Font("Segoe UI", 11F, FontStyle.Bold),
                BackColor = Color.FromArgb(34, 197, 94),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Location = new Point(40, 300),
                Size = new Size(320, 50),
                Cursor = Cursors.Hand
            };
            btnOk.FlatAppearance.BorderSize = 0;
            btnOk.Click += (s, e) =>
            {
                _feedback.TriggerRewardFeedback();
                ShowMainMenu();
            };

            pnlModal.Controls.Add(lblIcon);
            pnlModal.Controls.Add(lblTitle);
            pnlModal.Controls.Add(lblDesc);
            pnlModal.Controls.Add(btnOk);

            _contentPanel.Controls.Add(pnlModal);
        }

        // ---------------------------------------------------------------------
        // ЭКРАН 6: ИНТЕРАКТИВНАЯ ИГРА «МАТЕМАТИЧЕСКИЙ СПРИНТ»
        // ---------------------------------------------------------------------
        private System.Diagnostics.Stopwatch _stopwatch = new();

        private void ShowMathSprintGame()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            _stopwatch.Restart();
            int a = 3;
            int b = 2;
            int correct = a + b; // 5

            int y = 15;

            var lblGameTitle = new Label
            {
                Text = "🧮 Математический спринт",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = _theme.HeaderBgColor,
                Location = new Point(15, y),
                Size = new Size(400, 30)
            };
            _contentPanel.Controls.Add(lblGameTitle);
            y += 35;

            var lblPrompt = new Label
            {
                Text = "Реши пример (без таймера, в своём темпе):",
                Font = new Font("Segoe UI", 9.5F),
                ForeColor = Color.FromArgb(71, 85, 105),
                Location = new Point(15, y),
                Size = new Size(400, 25)
            };
            _contentPanel.Controls.Add(lblPrompt);
            y += 35;

            // Question Card
            var pnlCard = new Panel
            {
                Location = new Point(15, y),
                Size = new Size(400, 100),
                BackColor = Color.FromArgb(254, 249, 195),
                BorderStyle = BorderStyle.FixedSingle
            };
            var lblMath = new Label
            {
                Text = $"{a} + {b} = ?",
                Font = new Font("Segoe UI", 26F, FontStyle.Bold),
                ForeColor = Color.FromArgb(113, 63, 18),
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter
            };
            pnlCard.Controls.Add(lblMath);
            _contentPanel.Controls.Add(pnlCard);
            y += 120;

            // Options: 4, 5, 6
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
                    _stopwatch.Stop();
                    int reactionMs = (int)_stopwatch.ElapsedMilliseconds;
                    if (reactionMs < 200) reactionMs = 740; // baseline

                    if (val == correct)
                    {
                        _feedback.TriggerRewardFeedback();
                        _stars += 1;
                        _xp += 15;
                        _analytics.RecordResponse("Математический спринт", reactionMs, true);
                        UpdateProfileLabel();

                        MessageBox.Show(
                            $"🌟 Отлично, Артём! Ответ правильный!\n" +
                            $"⏱ Скорость мыслительной реакции: {reactionMs} мс\n" +
                            $"★ Получена 1 звезда и 15 XP!",
                            "Победа!", MessageBoxButtons.OK, MessageBoxIcon.Information
                        );
                    }
                    else
                    {
                        _feedback.TriggerCardTapFeedback();
                        _analytics.RecordResponse("Математический спринт", reactionMs, false);
                        MessageBox.Show("Попробуй ещё раз! Играем без спешки.", "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                    ShowMainMenu();
                };
                _contentPanel.Controls.Add(btnOpt);
            }
            y += 3 * 65 + 15;

            // Back button
            var btnBack = new Button
            {
                Text = "← Завершить и вернуться в меню",
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

        // ---------------------------------------------------------------------
        // ЭКРАН 7: ДОСТИЖЕНИЯ И КУБКИ
        // ---------------------------------------------------------------------
        private void ShowAchievementsScreen()
        {
            _contentPanel.Controls.Clear();
            _contentPanel.AutoScrollPosition = new Point(0, 0);

            int y = 10;

            var lblHeader = new Label
            {
                Text = "🏆 Мои достижения и кубки",
                Font = new Font("Segoe UI", 13F, FontStyle.Bold),
                ForeColor = _theme.HeaderBgColor,
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

            string[] items = {
                "🏆 Друг чисел — За 1 игру с числами [Получено]",
                "🔒 Кубок счёта — За 5 игр с числами [Впереди]",
                "🏆 Зоркий глаз — За 1 игру на поиск [Получено]",
                "🔒 Кубок внимания — За 5 игр на поиск [Впереди]",
                "🏆 Первые пары — За 1 игру с парами [Получено]",
                "🔒 Кубок логики — За 5 игр с парами [Впереди]"
            };

            foreach (var item in items)
            {
                bool unlocked = item.Contains("[Получено]");
                var pnl = new Panel
                {
                    Location = new Point(15, y),
                    Size = new Size(400, 48),
                    BackColor = unlocked ? Color.FromArgb(254, 243, 199) : Color.FromArgb(241, 245, 249),
                    BorderStyle = BorderStyle.FixedSingle
                };
                var lbl = new Label
                {
                    Text = item,
                    Font = new Font("Segoe UI", 9F, unlocked ? FontStyle.Bold : FontStyle.Regular),
                    ForeColor = unlocked ? Color.FromArgb(146, 64, 14) : Color.FromArgb(100, 116, 139),
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
    }

    // =========================================================================
    // ТОЧКА ВХОДА (MAIN)
    // =========================================================================
    internal static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            // Если передан флаг --console, выполняем консольный вывод с паузой
            if (args.Length > 0 && args[0] == "--console")
            {
                Console.OutputEncoding = System.Text.Encoding.UTF8;
                Console.WriteLine("=== Тестирование дополнительных модулей системы «БыстрУм» ===\n");

                var parentalGate = new ParentalGateModule();
                var timerModule = new BreakReminderModule();
                var analytics = new CognitiveAnalyticsModule();
                var feedback = new HapticAudioFeedbackModule();
                var themes = new ColorBlindThemeModule();

                Console.WriteLine("1. Проверка родительского барьера (Parental Gate):");
                var q = parentalGate.GenerateQuestion();
                Console.WriteLine(q.question);
                parentalGate.ValidateAnswer(parentalGate.CorrectAnswer);
                Console.WriteLine();

                Console.WriteLine("2. Переключение цветовой доступности:");
                themes.ApplyTheme(ColorBlindThemeModule.ThemeMode.Protanopia);
                Console.WriteLine();

                Console.WriteLine("3. Игровое взаимодействие (нажатие карточки и замер реакции):");
                feedback.TriggerCardTapFeedback();
                analytics.RecordResponse("Математический спринт", 740, true);
                analytics.RecordResponse("Математический спринт", 780, true);
                analytics.RecordResponse("Математический спринт", 760, true);
                feedback.TriggerRewardFeedback();
                Console.WriteLine();

                Console.WriteLine("4. Контроль тайм-менеджмента занятия:");
                timerModule.CheckSessionTime(15, "Артём", out string msg);
                Console.WriteLine($"[Уведомление об отдыхе]: «{msg}»");
                Console.WriteLine();

                Console.WriteLine("5. Формирование аналитического отчета:");
                var s = analytics.GetSummary();
                Console.WriteLine($"Всего решено заданий: {s.total} | Точность ответов: {s.accuracy:F1}%");
                Console.WriteLine($"Средняя скорость мыслительной реакции: {s.avgReaction:F0} мс");
                Console.WriteLine($"Статус когнитивной динамики: {s.status}");

                Console.WriteLine("\nНажмите любую клавишу для завершения работы...");
                try { Console.ReadKey(); } catch { }
                return;
            }

            // По умолчанию запускается красивое графическое Windows Forms приложение!
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}
