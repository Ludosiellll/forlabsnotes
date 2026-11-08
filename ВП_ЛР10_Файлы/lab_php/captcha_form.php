<?php
session_start();
$status = "";
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $userCode = trim($_POST['captcha'] ?? '');
    if (isset($_SESSION['captcha_sum']) && (int)$userCode === $_SESSION['captcha_sum']) {
        $status = "<div class='box ok'>Проверка CAPTCHA пройдена! Сообщение от " . htmlspecialchars($_POST['name']) . " отправлено.</div>";
    } else {
        $status = "<p class='err'><b>Ошибка:</b> неверный ответ CAPTCHA!</p>";
    }
}
$a = 7; $b = 5;
$_SESSION['captcha_sum'] = $a + $b;
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Защита CAPTCHA</title>
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
    <h2>Форма обратной связи с защитой CAPTCHA</h2>
    <form method="POST">
        <label>Имя:<br><input type="text" name="name" value="<?= htmlspecialchars($_POST['name'] ?? 'Соколова Дарья') ?>" required></label><br><br>
        <label>Защита от спама — сколько будет <b><?= "$a + $b" ?></b>?<br>
            <input type="text" name="captcha" value="<?= htmlspecialchars($_POST['captcha'] ?? '12') ?>" required>
        </label><br><br>
        <input type="submit" value="Отправить">
    </form>
    <?= $status ?>
</body>
</html>
