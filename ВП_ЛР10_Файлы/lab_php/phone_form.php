<?php
$result = "";
$error = "";
$name = trim($_POST['name'] ?? '');
$phone = trim($_POST['phone'] ?? '');

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!preg_match('/^\+?[0-9\s\-\(\)]{10,18}$/', $phone)) {
        $error = "Некорректный формат номера телефона!";
    } else {
        $result = "Контакт сохранён: " . htmlspecialchars($name) . ", тел.: " . htmlspecialchars($phone);
    }
}
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Валидация телефона</title>
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
    <h2>Форма с проверкой номера телефона</h2>
    <form method="POST">
        <label>Имя:<br><input type="text" name="name" value="<?= htmlspecialchars($name) ?>" required></label><br><br>
        <label>Телефон:<br><input type="tel" name="phone" value="<?= htmlspecialchars($phone) ?>" placeholder="+375 (29) 123-45-67" required></label><br><br>
        <input type="submit" value="Проверить и отправить">
    </form>
    <?php if ($error): ?><p class="err"><b>Ошибка:</b> <?= $error ?></p><?php endif; ?>
    <?php if ($result): ?><div class="box ok"><?= $result ?></div><?php endif; ?>
</body>
</html>
