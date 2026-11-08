<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Валидация данных</title>
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
<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = trim($_POST['name'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $message = trim($_POST['message'] ?? '');

    $errors = [];

    if (empty($name)) {
        $errors[] = "Имя не может быть пустым.";
    }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Некорректный email.";
    }
    if (mb_strlen($message, 'UTF-8') < 10) {
        $errors[] = "Сообщение должно быть не менее 10 символов.";
    }

    if (empty($errors)) {
        $safeName = htmlspecialchars($name);
        $safeEmail = htmlspecialchars($email);
        $safeMsg = htmlspecialchars($message);
        echo "<h2 class='ok'>Спасибо за сообщение!</h2>";
        echo "<div class='box'>Имя: $safeName<br>Email: $safeEmail<br>Сообщение: $safeMsg</div>";
        $log = date('Y-m-d H:i:s') . " | $safeName | $safeEmail | $safeMsg\n";
        file_put_contents('log.txt', $log, FILE_APPEND);
    } else {
        echo "<h2 class='err'>Ошибки:</h2><ul class='err'>";
        foreach ($errors as $error) {
            echo "<li>" . htmlspecialchars($error) . "</li>";
        }
        echo "</ul>";
        echo "<p><a class='btn' href='form.html'>Назад к форме</a></p>";
    }
} else {
    echo "Данные не отправлены.";
}
?>
</body>
</html>
