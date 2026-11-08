<?php
$conn = mysqli_connect('localhost', 'root', '', 'lab_db');
mysqli_set_charset($conn, 'utf8mb4');

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = mysqli_real_escape_string($conn, trim($_POST['name'] ?? ''));
    $email = mysqli_real_escape_string($conn, trim($_POST['email'] ?? ''));
    $msg = mysqli_real_escape_string($conn, trim($_POST['message'] ?? ''));
    if ($name && filter_var($email, FILTER_VALIDATE_EMAIL) && mb_strlen($msg, 'UTF-8') >= 10) {
        mysqli_query($conn, "INSERT INTO feedback_messages (name, email, message) VALUES ('$name', '$email', '$msg')");
    }
}
$res = mysqli_query($conn, "SELECT id, name, email, message, created_at FROM feedback_messages ORDER BY id");
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Сохранение в MySQL</title>
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
    <h2>Сохранение обращений в базу данных MySQL</h2>
    <p class="ok">Запись успешно сохранена в таблицу feedback_messages (БД lab_db).</p>
    <table>
        <tr><th>ID</th><th>Имя</th><th>Email</th><th>Сообщение</th><th>Дата</th></tr>
        <?php while ($row = mysqli_fetch_assoc($res)): ?>
        <tr>
            <td><?= $row['id'] ?></td>
            <td><?= htmlspecialchars($row['name']) ?></td>
            <td><?= htmlspecialchars($row['email']) ?></td>
            <td><?= htmlspecialchars($row['message']) ?></td>
            <td><?= $row['created_at'] ?></td>
        </tr>
        <?php endwhile; ?>
    </table>
</body>
</html>
