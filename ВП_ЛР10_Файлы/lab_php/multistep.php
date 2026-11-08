<?php
session_start();
$step = (int)($_POST['step'] ?? $_GET['step'] ?? 1);

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if ($step === 2) {
        $_SESSION['ms_name'] = trim($_POST['name'] ?? '');
        $_SESSION['ms_email'] = trim($_POST['email'] ?? '');
    } elseif ($step === 3) {
        $_SESSION['ms_phone'] = trim($_POST['phone'] ?? '');
        $_SESSION['ms_message'] = trim($_POST['message'] ?? '');
    }
}
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Многошаговая форма</title>
<style>
  body { font-family: Arial, sans-serif; padding: 24px 28px; line-height: 1.55; color: #222; background: #fff; margin: 0; }
  h2 { margin-top: 0; margin-bottom: 14px; font-size: 20px; }
  input[type="text"], input[type="email"], input[type="tel"], textarea {
      padding: 6px 8px; border: 1px solid #ccc; border-radius: 4px; width: 310px; font-family: Arial, sans-serif; font-size: 14px;
  }
  textarea { width: 380px; }
  input[type="submit"], button, .btn {
      padding: 7px 16px; background: #3498db; color: #fff; border: none; border-radius: 4px;
      cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block;
  }
  table { border-collapse: collapse; margin-top: 12px; font-size: 14px; }
  th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
  th { background: #f2f2f2; }
  .ok { color: #1e7e34; font-weight: bold; }
  .err { color: #c0392b; }
  .box { background: #f8f9fa; border: 1px solid #ced4da; padding: 12px 16px; border-radius: 4px; width: fit-content; margin-top: 10px; }
</style>
</head>
<body>
    <h2>Многостраничная форма (Шаг <?= $step ?> из 3)</h2>
    <?php if ($step === 1): ?>
        <form method="POST">
            <input type="hidden" name="step" value="2">
            <label>Имя:<br><input type="text" name="name" required></label><br><br>
            <label>Email:<br><input type="email" name="email" required></label><br><br>
            <input type="submit" value="Далее →">
        </form>
    <?php elseif ($step === 2): ?>
        <form method="POST">
            <input type="hidden" name="step" value="3">
            <label>Телефон:<br><input type="tel" name="phone" required></label><br><br>
            <label>Сообщение:<br><textarea name="message" rows="3" required></textarea></label><br><br>
            <input type="submit" value="Завершить отправку">
        </form>
    <?php else: ?>
        <div class="box">
            <b class="ok">Все шаги заполнены успешно!</b><br><br>
            Имя: <?= htmlspecialchars($_SESSION['ms_name'] ?? '') ?><br>
            Email: <?= htmlspecialchars($_SESSION['ms_email'] ?? '') ?><br>
            Телефон: <?= htmlspecialchars($_SESSION['ms_phone'] ?? '') ?><br>
            Сообщение: <?= htmlspecialchars($_SESSION['ms_message'] ?? '') ?>
        </div>
    <?php endif; ?>
</body>
</html>
