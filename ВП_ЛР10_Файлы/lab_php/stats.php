<?php
$file = 'log.txt';
$lines = file_exists($file) ? file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) : [];
?>
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Статистика сообщений</title>
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
    <h2>Статистика отправленных сообщений</h2>
    <p><b>Всего отправлено сообщений:</b> <?= count($lines) ?></p>
    <table>
        <tr><th>№</th><th>Дата и время</th><th>Имя</th><th>Email</th><th>Сообщение</th></tr>
        <?php foreach ($lines as $i => $line):
            $parts = explode(" | ", $line);
            if (count($parts) >= 4): ?>
            <tr>
                <td><?= $i + 1 ?></td>
                <td><?= htmlspecialchars($parts[0]) ?></td>
                <td><?= htmlspecialchars($parts[1]) ?></td>
                <td><?= htmlspecialchars($parts[2]) ?></td>
                <td><?= htmlspecialchars($parts[3]) ?></td>
            </tr>
        <?php endif; endforeach; ?>
    </table>
</body>
</html>
