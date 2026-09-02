// AI OS desktop application.
// Основные разделы: Обзор / Проекты / Проверки.
// Паспорт и Справка вынесены во вторичную навигацию, быстрый захват живёт в Обзоре.
// Всё server-rendered поверх dash:// (обработчик асинхронный),
// правда живёт в markdown: приложение читает и только дописывает.
// В каждом разделе - объяснение по-человечески «как это работает и зачем».

#![cfg_attr(all(not(debug_assertions), windows), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader, Read as _, Write as _};
use std::net::{Shutdown, SocketAddr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Mutex, OnceLock};
use std::time::Duration;

#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
#[cfg(windows)]
use std::os::windows::process::CommandExt;

use chrono::{DateTime, Datelike, Local, NaiveDate, NaiveDateTime, TimeZone};
use tauri::image::Image;
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::TrayIconBuilder;
use tauri::{AppHandle, Manager, WebviewUrl, WebviewWindowBuilder, WindowEvent};

const AUTO_REBUILD_MINUTES: u64 = 30;
const WATCH_MINUTES: u64 = 10;
const STALE_HOURS: i64 = 26;
const ASK_TIMEOUT_SECS: u64 = 180;
#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;
const APP_VERSION: &str = env!("CARGO_PKG_VERSION");
const SETUP_VERSION: &str = "0.4.5";
const INSTANCE_SHOW: &str = "AIOS_CONTROL_CENTER_SHOW_V1";
const INSTANCE_PING: &str = "AIOS_CONTROL_CENTER_PING_V1";
const INSTANCE_ACK: &str = "AIOS_CONTROL_CENTER_OK_V1";
const MANAGER_SHOW: &str = "AIOS_WORKSPACE_MANAGER_SHOW_V1";
const MANAGER_ACK: &str = "AIOS_WORKSPACE_MANAGER_OK_V1";
const CONTENT_DIRS: [&str; 8] = [
    "01_Index",
    "10_Project",
    "20_Domain",
    "30_Tech",
    "40_Decisions",
    "50_Meetings",
    "60_Tasks",
    "70_Resources",
];
const RU_MONTHS: [&str; 12] = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
];

static APP_HANDLE: OnceLock<AppHandle> = OnceLock::new();
static OBSIDIAN_AVAILABLE: OnceLock<bool> = OnceLock::new();
const RU_WEEKDAYS: [&str; 7] = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
];

static REBUILDING: AtomicBool = AtomicBool::new(false);
static ASKING: AtomicBool = AtomicBool::new(false);
static INSTALLING_CLI: AtomicBool = AtomicBool::new(false);
static INSTALL_MSG: Mutex<Option<(bool, String)>> = Mutex::new(None);

/// Консоли, которые пульт умеет ставить и запускать: id, имя, npm-пакет, условие подписки.
const KNOWN_CLIS: [(&str, &str, &str, &str); 2] = [
    (
        "claude",
        "Claude Code",
        "@anthropic-ai/claude-code",
        "входит в подписку Claude Pro/Max",
    ),
    (
        "codex",
        "Codex CLI",
        "@openai/codex",
        "нужна подписка ChatGPT Plus/Pro",
    ),
];

// ---------- базовые мелочи ----------

fn esc(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}

fn looks_like_root(dir: &Path) -> bool {
    dir.join("AGENTS.md").is_file() && dir.join("tools").join("make_dashboard.ps1").is_file()
}

fn find_root() -> Option<PathBuf> {
    if let Ok(v) = std::env::var("AI_OS_ROOT") {
        let p = PathBuf::from(v);
        if looks_like_root(&p) {
            return Some(p);
        }
    }
    if let Ok(exe) = std::env::current_exe() {
        for dir in exe.ancestors() {
            if looks_like_root(dir) {
                return Some(dir.to_path_buf());
            }
        }
    }
    None
}

struct InstanceGuard {
    lock_path: PathBuf,
    state_path: PathBuf,
}

impl Drop for InstanceGuard {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.state_path);
        let _ = std::fs::remove_file(&self.lock_path);
    }
}

struct PrimaryInstance {
    listener: TcpListener,
    guard: InstanceGuard,
}

fn instance_paths(root: &Path) -> (PathBuf, PathBuf) {
    let local = root.join(".local");
    (
        local.join("control-center-instance.lock"),
        local.join("control-center-instance.json"),
    )
}

fn notify_existing_instance(state_path: &Path, show: bool) -> bool {
    let deadline = std::time::Instant::now() + Duration::from_secs(3);
    while std::time::Instant::now() < deadline {
        let state = std::fs::read_to_string(state_path).ok().and_then(|text| {
            serde_json::from_str::<serde_json::Value>(text.trim_start_matches('\u{feff}')).ok()
        });
        if let Some(port) = state
            .as_ref()
            .and_then(|value| value.get("port"))
            .and_then(|value| value.as_u64())
            .filter(|port| *port <= u16::MAX as u64)
        {
            let address = SocketAddr::from(([127, 0, 0, 1], port as u16));
            if let Ok(mut stream) = TcpStream::connect_timeout(&address, Duration::from_millis(300))
            {
                let _ = stream.set_read_timeout(Some(Duration::from_secs(2)));
                let command = if show { INSTANCE_SHOW } else { INSTANCE_PING };
                if stream.write_all(command.as_bytes()).is_ok()
                    && stream.write_all(b"\n").is_ok()
                    && stream.flush().is_ok()
                {
                    let _ = stream.shutdown(Shutdown::Write);
                    let mut response = vec![0u8; INSTANCE_ACK.len()];
                    if stream.read_exact(&mut response).is_ok()
                        && response.as_slice() == INSTANCE_ACK.as_bytes()
                    {
                        return true;
                    }
                }
            }
        }
        std::thread::sleep(Duration::from_millis(50));
    }
    false
}

fn acquire_workspace_instance(
    root: &Path,
    show_existing: bool,
) -> Result<Option<PrimaryInstance>, String> {
    let (lock_path, state_path) = instance_paths(root);
    let local = lock_path
        .parent()
        .ok_or("У lock-файла нет родительской папки")?;
    std::fs::create_dir_all(local).map_err(|error| error.to_string())?;

    for attempt in 0..2 {
        match std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&lock_path)
        {
            Ok(mut lock_file) => {
                writeln!(lock_file, "{}", std::process::id()).map_err(|error| error.to_string())?;
                let listener =
                    TcpListener::bind(("127.0.0.1", 0)).map_err(|error| error.to_string())?;
                let port = listener
                    .local_addr()
                    .map_err(|error| error.to_string())?
                    .port();
                let guard = InstanceGuard {
                    lock_path: lock_path.clone(),
                    state_path: state_path.clone(),
                };
                let state = serde_json::json!({
                    "schemaVersion": 1,
                    "pid": std::process::id(),
                    "port": port,
                    "workspace": root.to_string_lossy(),
                });
                let temporary =
                    state_path.with_extension(format!("json.{}.tmp", std::process::id()));
                std::fs::write(
                    &temporary,
                    serde_json::to_vec_pretty(&state).map_err(|error| error.to_string())?,
                )
                .map_err(|error| error.to_string())?;
                std::fs::rename(&temporary, &state_path).map_err(|error| error.to_string())?;
                return Ok(Some(PrimaryInstance { listener, guard }));
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                if notify_existing_instance(&state_path, show_existing) {
                    return Ok(None);
                }
                if attempt == 0 {
                    let _ = std::fs::remove_file(&state_path);
                    let _ = std::fs::remove_file(&lock_path);
                    continue;
                }
                return Err("Не удалось связаться с уже запущенным Центром проекта".into());
            }
            Err(error) => return Err(error.to_string()),
        }
    }
    Err("Не удалось определить активный экземпляр Центра проекта".into())
}

fn read_instance_command(stream: &mut TcpStream) -> Option<bool> {
    let _ = stream.set_read_timeout(Some(Duration::from_secs(2)));
    let mut command = String::new();
    {
        let mut reader = BufReader::new(&mut *stream);
        reader.read_line(&mut command).ok()?;
    }
    let command = command.trim();
    if command == INSTANCE_SHOW {
        Some(true)
    } else if command == INSTANCE_PING {
        Some(false)
    } else {
        None
    }
}

fn show_main_window(app: &AppHandle) {
    let handle = app.clone();
    if app
        .run_on_main_thread(move || {
            if let Some(window) = handle.get_webview_window("main") {
                let _ = window.show();
                let _ = window.unminimize();
                let _ = window.set_always_on_top(true);
                let _ = window.set_focus();
                let _ = window.set_always_on_top(false);
            }
        })
        .is_err()
    {
        eprintln!("AI OS could not schedule the window display");
    }
}

fn start_instance_listener(listener: TcpListener, app: AppHandle) {
    std::thread::spawn(move || {
        for connection in listener.incoming() {
            let Ok(mut stream) = connection else { continue };
            if let Some(show) = read_instance_command(&mut stream) {
                if show {
                    show_main_window(&app);
                }
                let _ = stream.write_all(INSTANCE_ACK.as_bytes());
                let _ = stream.flush();
            }
        }
    });
}

fn run_powershell(script: &Path, wait: bool) -> bool {
    let root = script
        .parent()
        .and_then(Path::parent)
        .map(Path::to_path_buf);
    let configured = root.as_ref().and_then(|root| {
        let config = serde_json::from_str::<serde_json::Value>(&read_text(
            &root.join("tools").join("ai_os.config.json"),
        ))
        .ok()?;
        let path = PathBuf::from(config.get("powershellPath")?.as_str()?);
        path.is_file().then_some(path)
    });
    #[cfg(windows)]
    let executable = configured.unwrap_or_else(|| PathBuf::from("powershell.exe"));
    #[cfg(not(windows))]
    let executable = configured
        .or_else(|| which_command("pwsh"))
        .unwrap_or_else(|| PathBuf::from("pwsh"));
    let mut cmd = Command::new(executable);
    cmd.args(["-NoProfile", "-File"]).arg(script);
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    if wait {
        cmd.status().map(|s| s.success()).unwrap_or(false)
    } else {
        cmd.spawn().is_ok()
    }
}

fn rebuild_passport(root: &Path) -> bool {
    run_powershell(&root.join("tools").join("make_dashboard.ps1"), true)
}

/// Пересборка под замком: одновременно живёт только одна. None = уже идёт.
fn rebuild_guarded(root: &Path) -> Option<bool> {
    if REBUILDING
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .is_err()
    {
        return None;
    }
    let r = rebuild_passport(root);
    REBUILDING.store(false, Ordering::SeqCst);
    Some(r)
}

fn spawn_readiness(root: &Path) -> bool {
    run_powershell(
        &root.join("tools").join("run_scheduled_readiness.ps1"),
        false,
    )
}

fn shell_open(target: &str) {
    #[cfg(windows)]
    {
        let _ = Command::new("explorer.exe")
            .arg(target)
            .creation_flags(CREATE_NO_WINDOW)
            .spawn();
    }
    #[cfg(not(windows))]
    {
        let _ = Command::new("xdg-open").arg(target).spawn();
    }
}

fn which_command(name: &str) -> Option<PathBuf> {
    if name.contains('/') || name.contains('\\') {
        let path = PathBuf::from(name);
        return path.is_file().then_some(path);
    }
    std::env::var_os("PATH").and_then(|paths| {
        std::env::split_paths(&paths).find_map(|dir| {
            #[cfg(windows)]
            let candidates = [
                dir.join(format!("{name}.exe")),
                dir.join(format!("{name}.cmd")),
                dir.join(format!("{name}.bat")),
                dir.join(name),
            ];
            #[cfg(not(windows))]
            let candidates = [dir.join(name)];
            candidates.into_iter().find(|path| {
                path.metadata()
                    .map(|meta| {
                        if !meta.is_file() {
                            return false;
                        }
                        #[cfg(windows)]
                        return true;
                        #[cfg(not(windows))]
                        return meta.permissions().mode() & 0o111 != 0;
                    })
                    .unwrap_or(false)
            })
        })
    })
}

fn read_text(p: &Path) -> String {
    let s = std::fs::read_to_string(p).unwrap_or_default();
    s.trim_start_matches('\u{feff}').to_string()
}

fn tail_lines(p: &Path, n: usize) -> Vec<String> {
    let t = read_text(p);
    let lines: Vec<&str> = t.lines().filter(|l| !l.trim().is_empty()).collect();
    lines
        .iter()
        .rev()
        .take(n)
        .rev()
        .map(|s| s.to_string())
        .collect()
}

fn query_param(query: &str, key: &str) -> Option<String> {
    for pair in query.split('&') {
        let mut it = pair.splitn(2, '=');
        let k = it.next().unwrap_or("");
        if k == key {
            let v = it.next().unwrap_or("").replace('+', " ");
            return Some(urlencoding::decode(&v).map(|c| c.into_owned()).unwrap_or(v));
        }
    }
    None
}

fn safe_back(v: Option<String>, default: &str) -> String {
    match v {
        Some(s) if s.starts_with('/') && !s.starts_with("//") => s,
        _ => default.to_string(),
    }
}

fn strip_md(line: &str) -> String {
    let mut s = line.replace('`', "").replace("**", "");
    while let (Some(a), Some(b)) = (s.find("[["), s.find("]]")) {
        if b < a {
            break;
        }
        let inner = s[a + 2..b].to_string();
        let name = inner
            .rsplit('/')
            .next()
            .unwrap_or(&inner)
            .split('|')
            .next_back()
            .unwrap_or(&inner)
            .to_string();
        s = format!("{}{}{}", &s[..a], name, &s[b + 2..]);
    }
    s
}

fn has_obsolete_release_version(text: &str) -> bool {
    text.split(|c: char| !(c.is_ascii_digit() || c == '.'))
        .filter(|part| part.starts_with("0.") && part.matches('.').count() >= 1)
        .any(|version| version != SETUP_VERSION && version != APP_VERSION && version != "0.9.0")
}

fn truncate_chars(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        return s.to_string();
    }
    let cut: String = s.chars().take(max).collect();
    let min_bytes = cut.len() / 2;
    match cut.rfind(' ') {
        Some(i) if i > min_bytes => format!("{}…", &cut[..i]),
        _ => format!("{}…", cut),
    }
}

fn ru_day(d: NaiveDate) -> String {
    let today = Local::now().date_naive();
    if d == today {
        return "Сегодня".into();
    }
    if today.pred_opt() == Some(d) {
        return "Вчера".into();
    }
    let y = if d.year() == today.year() {
        String::new()
    } else {
        format!(" {}", d.year())
    };
    format!("{} {}{}", d.day(), RU_MONTHS[(d.month0()) as usize], y)
}

// ---------- здоровье (по журналу, без запуска проверок) ----------

struct HealthNow {
    label: String,
    class: &'static str,
    age: String,
    stale: bool,
}

fn age_ru(from: DateTime<Local>) -> String {
    let mins = (Local::now() - from).num_minutes().max(0);
    if mins < 2 {
        "только что".into()
    } else if mins < 60 {
        format!("{} мин назад", mins)
    } else if mins < 48 * 60 {
        format!("{} ч назад", mins / 60)
    } else {
        format!("{} дн назад", mins / (24 * 60))
    }
}

fn health_now(root: &Path) -> HealthNow {
    let lines = tail_lines(&root.join(".local").join("health-check.log"), 1);
    let Some(last) = lines.last() else {
        return HealthNow {
            label: "поверок ещё не было".into(),
            class: "muted",
            age: "—".into(),
            stale: true,
        };
    };
    let ts_str = last
        .split(']')
        .next()
        .unwrap_or("")
        .trim_start_matches('[')
        .to_string();
    let ts = parse_local(&ts_str, "%Y-%m-%d %H:%M:%S");
    let age = ts.map(age_ru).unwrap_or_else(|| ts_str.clone());
    let stale = ts
        .map(|t| (Local::now() - t).num_hours() >= STALE_HOURS)
        .unwrap_or(true);
    if stale {
        return HealthNow {
            label: "поверка устарела".into(),
            class: "muted",
            age,
            stale,
        };
    }
    let grab = |key: &str| -> i64 {
        last.split(key)
            .nth(1)
            .and_then(|r| r.split_whitespace().next())
            .and_then(|v| v.parse().ok())
            .unwrap_or(0)
    };
    let (warn, fail) = (grab("WARN="), grab("FAIL="));
    if fail > 0 {
        HealthNow {
            label: "есть проблемы".into(),
            class: "bad",
            age,
            stale: false,
        }
    } else if warn > 0 {
        HealthNow {
            label: "есть предупреждения".into(),
            class: "warn",
            age,
            stale: false,
        }
    } else {
        HealthNow {
            label: "система здорова".into(),
            class: "good",
            age,
            stale: false,
        }
    }
}

// ---------- лента дня ----------

struct FeedItem {
    t: DateTime<Local>,
    kind: &'static str,
    text: String,
    link: Option<String>,
}

fn parse_local(s: &str, fmt: &str) -> Option<DateTime<Local>> {
    NaiveDateTime::parse_from_str(s, fmt)
        .ok()
        .and_then(|n| Local.from_local_datetime(&n).earliest())
}

fn obsidian_link(root: &Path, rel: &str) -> String {
    let available = *OBSIDIAN_AVAILABLE.get_or_init(|| {
        #[cfg(windows)]
        {
            let local = std::env::var_os("LOCALAPPDATA").map(PathBuf::from);
            local.as_ref().is_some_and(|path| {
                path.join("Programs/Obsidian/Obsidian.exe").is_file()
                    || path.join("Obsidian/Obsidian.exe").is_file()
            }) || which_command("Obsidian").is_some()
        }
        #[cfg(not(windows))]
        {
            which_command("obsidian").is_some()
                || Path::new("/var/lib/flatpak/exports/bin/md.obsidian.Obsidian").is_file()
                || std::env::var_os("HOME")
                    .map(PathBuf::from)
                    .is_some_and(|home| {
                        home.join(".local/share/flatpak/exports/bin/md.obsidian.Obsidian")
                            .is_file()
                    })
        }
    });
    if !available {
        return format!("/open?f={}", urlencoding::encode(rel));
    }
    let vault = root
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_default();
    let file = rel.trim_end_matches(".md").replace('\\', "/");
    format!(
        "obsidian://open?vault={}&file={}",
        urlencoding::encode(&vault),
        urlencoding::encode(&file)
    )
}

fn walk_notes(root: &Path) -> Vec<(String, DateTime<Local>)> {
    let mut out = Vec::new();
    fn rec(base: &Path, dir: &Path, out: &mut Vec<(String, DateTime<Local>)>) {
        let Ok(rd) = std::fs::read_dir(dir) else {
            return;
        };
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                rec(base, &p, out);
            } else if p.extension().map(|x| x == "md").unwrap_or(false) {
                if let Ok(meta) = e.metadata() {
                    if let Ok(m) = meta.modified() {
                        let rel = p
                            .strip_prefix(base)
                            .unwrap_or(&p)
                            .to_string_lossy()
                            .to_string();
                        out.push((rel, DateTime::<Local>::from(m)));
                    }
                }
            }
        }
    }
    for d in CONTENT_DIRS {
        rec(root, &root.join(d), &mut out);
    }
    out
}

fn build_feed(root: &Path) -> Vec<FeedItem> {
    let mut items: Vec<FeedItem> = Vec::new();

    for line in tail_lines(&root.join(".local").join("agent-events.ndjson"), 40) {
        let Ok(v) = serde_json::from_str::<serde_json::Value>(&line) else {
            continue;
        };
        let Some(t) = v["time"]
            .as_str()
            .and_then(|s| parse_local(s, "%Y-%m-%dT%H:%M:%S"))
        else {
            continue;
        };
        let agent = v["agent"].as_str().unwrap_or("агент");
        let task = v["task"].as_str().unwrap_or("");
        let value = v["value"].as_str().unwrap_or("");
        let mut text = format!("{} — {}", agent, task);
        if !value.is_empty() {
            text = format!("{} · {}", text, value);
        }
        if has_obsolete_release_version(&text) {
            continue;
        }
        items.push(FeedItem {
            t,
            kind: "агент",
            text: truncate_chars(&text, 220),
            link: None,
        });
    }

    {
        let mut command = Command::new("git");
        command.args(["-C"]).arg(root).args([
            "log",
            "--date=format:%Y-%m-%d %H:%M",
            "--pretty=%ad|%s",
            "-n",
            "20",
        ]);
        #[cfg(windows)]
        command.creation_flags(CREATE_NO_WINDOW);
        if let Ok(out) = command.output() {
            for line in String::from_utf8_lossy(&out.stdout).lines() {
                let mut it = line.splitn(2, '|');
                let (Some(d), Some(msg)) = (it.next(), it.next()) else {
                    continue;
                };
                let Some(t) = parse_local(d, "%Y-%m-%d %H:%M") else {
                    continue;
                };
                if has_obsolete_release_version(msg) {
                    continue;
                }
                items.push(FeedItem {
                    t,
                    kind: "коммит",
                    text: truncate_chars(msg, 200),
                    link: None,
                });
            }
        }
    }

    let mut notes = walk_notes(root);
    notes.sort_by_key(|item| std::cmp::Reverse(item.1));
    for (rel, t) in notes.into_iter().take(15) {
        let link = obsidian_link(root, &rel);
        items.push(FeedItem {
            t,
            kind: "заметка",
            text: rel.replace('\\', "/"),
            link: Some(link),
        });
    }

    items.sort_by_key(|item| std::cmp::Reverse(item.t));
    items.truncate(40);
    items
}

fn open_tasks(root: &Path, n: usize) -> (Vec<String>, usize) {
    let all: Vec<String> = read_text(&root.join("60_Tasks").join("Task_Log.md"))
        .lines()
        .filter(|l| l.trim_start().starts_with("- [ ]"))
        .map(|l| {
            truncate_chars(
                strip_md(l.trim_start().trim_start_matches("- [ ]").trim()).trim(),
                180,
            )
        })
        .collect();
    let total = all.len();
    (
        all.into_iter()
            .filter(|task| !has_obsolete_release_version(task))
            .take(n)
            .collect(),
        total,
    )
}

// ---------- поиск (mgimind CLI) ----------

fn memory_tool(root: &Path) -> Result<(PathBuf, String), String> {
    let cfg_path = root.join("tools").join("ai_os.config.json");
    if !cfg_path.is_file() {
        return Err(
            "memory is not configured for this workspace — create tools/ai_os.config.json first"
                .to_string(),
        );
    }
    let config = serde_json::from_str::<serde_json::Value>(&read_text(&cfg_path))
        .map_err(|e| format!("tools/ai_os.config.json is invalid: {e}"))?;
    let lib = config["memoryLibrary"]
        .as_str()
        .filter(|value| !value.trim().is_empty() && !value.contains("{{"))
        .ok_or_else(|| {
            "memoryLibrary is missing or still a placeholder in tools/ai_os.config.json".to_string()
        })?;
    let tool_value = config["memoryToolPath"]
        .as_str()
        .filter(|value| !value.trim().is_empty() && !value.contains("{{"))
        .ok_or_else(|| {
            "memoryToolPath is missing or still a placeholder in tools/ai_os.config.json"
                .to_string()
        })?;
    let tool = PathBuf::from(tool_value);
    if !tool.is_file() {
        return Err(format!(
            "configured memory tool does not exist: {}",
            tool.display()
        ));
    }
    Ok((tool, lib.to_string()))
}

struct Hit {
    score: String,
    snippet: String,
    source: String,
}

fn memory_search(root: &Path, q: &str) -> Result<Vec<Hit>, String> {
    let (tool, lib) = memory_tool(root)?;
    let mut command = Command::new(&tool);
    command
        .arg("search")
        .arg(q)
        .args(["--library", &lib, "--limit", "8"]);
    #[cfg(windows)]
    command.creation_flags(CREATE_NO_WINDOW);
    let out = command
        .output()
        .map_err(|_| "инструмент памяти (mgimind) не найден — поиск по смыслу недоступен, пока слой памяти не подключён".to_string())?;
    if !out.status.success() {
        return Err(format!(
            "поиск вернул ошибку: {}",
            String::from_utf8_lossy(&out.stderr).trim()
        ));
    }
    let text = String::from_utf8_lossy(&out.stdout).to_string();
    let mut hits = Vec::new();
    let mut cur: Option<Hit> = None;
    for line in text.lines() {
        let trimmed = line.trim_start();
        let is_head = line
            .chars()
            .next()
            .map(|c| c.is_ascii_digit())
            .unwrap_or(false)
            && line.contains(". [")
            && line.contains("(score:");
        if is_head {
            if let Some(h) = cur.take() {
                hits.push(h);
            }
            let score = line
                .split("(score:")
                .nth(1)
                .and_then(|r| r.split(')').next())
                .unwrap_or("")
                .trim()
                .to_string();
            cur = Some(Hit {
                score,
                snippet: String::new(),
                source: String::new(),
            });
        } else if let Some(h) = cur.as_mut() {
            if let Some(src) = trimmed.strip_prefix("source: ") {
                h.source = src.trim().to_string();
            } else if !trimmed.is_empty() && !trimmed.starts_with("id:") {
                if !h.snippet.is_empty() {
                    h.snippet.push(' ');
                }
                h.snippet.push_str(trimmed);
            }
        }
    }
    if let Some(h) = cur.take() {
        hits.push(h);
    }
    if hits.is_empty() && !text.trim().is_empty() && !text.contains("(score:") {
        return Err(format!(
            "не смог разобрать ответ mgimind — возможно, формат вывода изменился. Сырой ответ:\n{}",
            text.trim()
        ));
    }
    Ok(hits)
}

fn find_note_by_name(root: &Path, name: &str) -> Option<String> {
    walk_notes(root)
        .into_iter()
        .map(|(rel, _)| rel)
        .find(|rel| {
            rel.rsplit(['\\', '/'])
                .next()
                .map(|f| f == name)
                .unwrap_or(false)
        })
}

// ---------- «Спросить»: живой агент через CLI-адаптеры ----------

struct AgentCli {
    id: &'static str,
    label: &'static str,
    path: String,
    args_prefix: Vec<String>,
}

/// Возвращает исполняемый файл из PATH в формате, пригодном для Command.
fn which_exe(name: &str) -> Option<String> {
    which_command(name).map(|path| path.to_string_lossy().into_owned())
}

/// npm-пакеты (claude, codex) надёжнее запускать движком node напрямую -
/// без cmd-обёрток и их правил экранирования.
fn npm_js_entry(pkg_rel: &str) -> Option<(String, String)> {
    let node = which_exe("node")?;
    #[cfg(windows)]
    let js = PathBuf::from(std::env::var("APPDATA").ok()?)
        .join("npm")
        .join("node_modules")
        .join(pkg_rel);
    #[cfg(not(windows))]
    let js = {
        let npm = which_exe("npm")?;
        let output = Command::new(npm).args(["root", "-g"]).output().ok()?;
        if !output.status.success() {
            return None;
        }
        PathBuf::from(String::from_utf8_lossy(&output.stdout).trim()).join(pkg_rel)
    };
    if js.is_file() {
        Some((node, js.to_string_lossy().to_string()))
    } else {
        None
    }
}

/// Установка консоли по клику: обычный npm install -g, вывод сохраняется честно.
fn install_cli(pkg: &str) -> (bool, String) {
    let Some(npm) = which_exe("npm") else {
        return (
            false,
            "npm не найден — сначала поставь Node.js с nodejs.org".into(),
        );
    };
    let mut cmd = Command::new(npm);
    cmd.args(["install", "-g", pkg]);
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    match run_with_timeout(cmd, 600) {
        Ok((_, _, true)) => (
            true,
            "установлена — осталось войти один раз (кнопка рядом откроет консоль)".into(),
        ),
        Ok((so, se, false)) => {
            let detail = if se.trim().is_empty() { so } else { se };
            (
                false,
                format!(
                    "установка не удалась: {}",
                    truncate_chars(detail.trim(), 500)
                ),
            )
        }
        Err(e) => (false, e),
    }
}

/// Открыть консоль в отдельном окне, чтобы человек мог войти в аккаунт.
fn open_cli_terminal(cli_path: &str) -> bool {
    #[cfg(windows)]
    {
        Command::new("cmd")
            .args(["/c", "start", "", cli_path])
            .spawn()
            .is_ok()
    }
    #[cfg(not(windows))]
    {
        let Some(terminal) = [
            "x-terminal-emulator",
            "gnome-terminal",
            "konsole",
            "kitty",
            "alacritty",
        ]
        .iter()
        .find_map(|name| which_exe(name)) else {
            return false;
        };
        let name = Path::new(&terminal)
            .file_name()
            .and_then(|value| value.to_str())
            .unwrap_or_default();
        let mut command = Command::new(&terminal);
        if name == "gnome-terminal" {
            command.args(["--", cli_path]);
        } else if name == "konsole" {
            command.args(["-e", cli_path]);
        } else {
            command.args(["-e", cli_path]);
        }
        command.spawn().is_ok()
    }
}

fn launch_workspace_manager(root: &Path) -> Result<(), String> {
    if notify_workspace_manager(&workspace_manager_state_path()) {
        return Ok(());
    }
    let configured = serde_json::from_str::<serde_json::Value>(&read_text(
        &root.join("tools").join("ai_os.config.json"),
    ))
    .ok()
    .and_then(|config| {
        config
            .get("setupExecutablePath")?
            .as_str()
            .map(PathBuf::from)
    })
    .filter(|path| path.is_file());
    #[cfg(windows)]
    let executable = configured
        .or_else(|| {
            let local = std::env::var_os("LOCALAPPDATA").map(PathBuf::from)?;
            let install_dir = local.join("AI OS");
            let preferred = [
                "ai-os-workspace-manager.exe",
                "AI OS.exe",
                "ai-os-installer-app.exe",
            ];
            preferred
                .iter()
                .map(|name| install_dir.join(name))
                .find(|path| path.is_file())
                .or_else(|| {
                    std::fs::read_dir(&install_dir)
                        .ok()?
                        .flatten()
                        .find_map(|entry| {
                            let path = entry.path();
                            let name = path.file_name()?.to_string_lossy().to_lowercase();
                            (path.extension().is_some_and(|ext| ext == "exe")
                                && name != "uninstall.exe")
                                .then_some(path)
                        })
                })
        })
        .ok_or("Менеджер проектов не найден. Запустите AI OS Setup ещё раз.")?;
    #[cfg(not(windows))]
    let executable = configured
        .or_else(|| which_command("ai-os-workspace-manager"))
        .or_else(|| which_command("ai-os"))
        .ok_or("Менеджер проектов не найден. Установите пакет AI OS Setup ещё раз.")?;
    Command::new(executable)
        .spawn()
        .map_err(|error| format!("Не удалось открыть менеджер проектов: {error}"))?;
    Ok(())
}

fn workspace_manager_state_path() -> PathBuf {
    if let Some(path) = std::env::var_os("AI_OS_SETUP_STATE_DIR") {
        return PathBuf::from(path).join("workspace-manager-instance.json");
    }
    #[cfg(windows)]
    {
        let base = std::env::var_os("LOCALAPPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        base.join("AI OS Setup")
            .join("workspace-manager-instance.json")
    }
    #[cfg(not(windows))]
    {
        let base = std::env::var_os("XDG_STATE_HOME")
            .map(PathBuf::from)
            .or_else(|| {
                std::env::var_os("HOME").map(|home| PathBuf::from(home).join(".local/state"))
            })
            .unwrap_or_else(std::env::temp_dir);
        base.join("ai-os").join("workspace-manager-instance.json")
    }
}

fn notify_workspace_manager(state_path: &Path) -> bool {
    let deadline = std::time::Instant::now() + Duration::from_secs(1);
    while std::time::Instant::now() < deadline {
        let state = std::fs::read_to_string(state_path).ok().and_then(|text| {
            serde_json::from_str::<serde_json::Value>(text.trim_start_matches('\u{feff}')).ok()
        });
        if let Some(port) = state
            .as_ref()
            .and_then(|value| value.get("port"))
            .and_then(serde_json::Value::as_u64)
            .filter(|port| *port <= u16::MAX as u64)
        {
            let address = SocketAddr::from(([127, 0, 0, 1], port as u16));
            if let Ok(mut stream) = TcpStream::connect_timeout(&address, Duration::from_millis(250))
            {
                let _ = stream.set_read_timeout(Some(Duration::from_secs(1)));
                if stream.write_all(MANAGER_SHOW.as_bytes()).is_ok()
                    && stream.write_all(b"\n").is_ok()
                    && stream.flush().is_ok()
                {
                    let _ = stream.shutdown(Shutdown::Write);
                    let mut response = [0u8; 64];
                    if let Ok(count) = stream.read(&mut response) {
                        if String::from_utf8_lossy(&response[..count]).trim() == MANAGER_ACK {
                            return true;
                        }
                    }
                }
            }
        }
        std::thread::sleep(Duration::from_millis(50));
    }
    false
}

fn detect_clis() -> Vec<AgentCli> {
    let mut v = Vec::new();
    if let Some((node, js)) = npm_js_entry("@anthropic-ai/claude-code/cli.js") {
        v.push(AgentCli {
            id: "claude",
            label: "Claude Code",
            path: node,
            args_prefix: vec![js],
        });
    } else if let Some(p) = which_exe("claude") {
        v.push(AgentCli {
            id: "claude",
            label: "Claude Code",
            path: p,
            args_prefix: vec![],
        });
    }
    if let Some((node, js)) = npm_js_entry("@openai/codex/bin/codex.js") {
        v.push(AgentCli {
            id: "codex",
            label: "Codex CLI",
            path: node,
            args_prefix: vec![js],
        });
    } else if let Some(p) = which_exe("codex") {
        v.push(AgentCli {
            id: "codex",
            label: "Codex CLI",
            path: p,
            args_prefix: vec![],
        });
    }
    v
}

/// Запуск с таймаутом и параллельным чтением stdout/stderr (иначе пайп забьётся).
fn run_with_timeout(mut cmd: Command, secs: u64) -> Result<(String, String, bool), String> {
    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        cmd.process_group(0);
    }
    cmd.stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = cmd
        .spawn()
        .map_err(|e| format!("консоль не запустилась: {}", e))?;
    let mut out_pipe = child.stdout.take();
    let mut err_pipe = child.stderr.take();
    let out_h = std::thread::spawn(move || {
        let mut buf = String::new();
        if let Some(p) = out_pipe.as_mut() {
            let _ = p.read_to_string(&mut buf);
        }
        buf
    });
    let err_h = std::thread::spawn(move || {
        let mut buf = String::new();
        if let Some(p) = err_pipe.as_mut() {
            let _ = p.read_to_string(&mut buf);
        }
        buf
    });
    let start = std::time::Instant::now();
    let status = loop {
        match child.try_wait() {
            Ok(Some(s)) => break s,
            Ok(None) => {
                if start.elapsed().as_secs() > secs {
                    // Убить всё дерево процессов: за cmd-обёрткой прячется настоящий
                    // node/агент, обычный kill() оставил бы его работать в фоне.
                    #[cfg(windows)]
                    {
                        let _ = Command::new("taskkill")
                            .args(["/PID", &child.id().to_string(), "/T", "/F"])
                            .creation_flags(CREATE_NO_WINDOW)
                            .output();
                    }
                    #[cfg(unix)]
                    unsafe {
                        libc::kill(-(child.id() as i32), libc::SIGKILL);
                    }
                    let _ = child.wait();
                    return Err(format!("агент думал дольше {} секунд — остановил. Попробуй вопрос попроще или ещё раз.", secs));
                }
                std::thread::sleep(Duration::from_millis(400));
            }
            Err(e) => return Err(e.to_string()),
        }
    };
    let stdout = out_h.join().unwrap_or_default();
    let stderr = err_h.join().unwrap_or_default();
    Ok((stdout, stderr, status.success()))
}

fn memory_mcp_server_name(root: &Path) -> Option<String> {
    let config =
        serde_json::from_str::<serde_json::Value>(&read_text(&root.join(".mcp.json"))).ok()?;
    let servers = config.get("mcpServers")?.as_object()?;

    for preferred in ["mgimind", "memory"] {
        if servers.contains_key(preferred) {
            return Some(preferred.to_string());
        }
    }

    servers.iter().find_map(|(name, server)| {
        let command = server.get("command")?.as_str()?.to_lowercase();
        command.contains("mgimind").then(|| name.clone())
    })
}

fn build_agent_args(
    cli_id: &str,
    prompt: &str,
    memory_server: Option<&str>,
) -> Result<Vec<String>, String> {
    match cli_id {
        "codex" => Ok(vec![
            "exec".into(),
            "--sandbox".into(), "read-only".into(),
            "--ephemeral".into(),
            "--color".into(), "never".into(),
            prompt.into(),
        ]),
        "claude" => {
            let mut args = vec![
                "-p".into(), prompt.into(),
                "--output-format".into(), "text".into(),
                "--no-session-persistence".into(),
                "--permission-mode".into(), "plan".into(),
                "--tools".into(), "Read,Grep,Glob".into(),
                "--disallowedTools".into(), "Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch".into(),
            ];
            if let Some(server) = memory_server {
                args.push("--allowedTools".into());
                args.push(format!(
                    "mcp__{server}__mind_search,mcp__{server}__mind_recall_all,mcp__{server}__mind_browse,mcp__{server}__mind_stats"
                ));
            }
            Ok(args)
        }
        _ => Err(format!(
            "Для {} пока нет доказанного read-only режима. В «Спросить» безопасно поддерживаются Claude Code и Codex CLI.",
            cli_id
        )),
    }
}

fn ask_agent(root: &Path, cli: &AgentCli, question: &str) -> Result<String, String> {
    // Вопрос - одной строкой: переносы ломают экранирование cmd-обёрток.
    let question: String = question.split_whitespace().collect::<Vec<_>>().join(" ");
    let prompt = format!(
        "Ты отвечаешь владельцу этой рабочей папки на вопрос по её заметкам. \
         Сначала найди ответ в заметках (семантическая память/поиск/чтение файлов), \
         назови заметки-источники по именам, отвечай по-русски, коротко и по делу. \
         Только чтение — ничего не изменяй и не создавай. Вопрос: {}",
        question
    );
    let mut cmd = Command::new(&cli.path);
    cmd.current_dir(root);
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    for a in &cli.args_prefix {
        cmd.arg(a);
    }
    let memory_server = memory_mcp_server_name(root);
    cmd.args(build_agent_args(cli.id, &prompt, memory_server.as_deref())?);
    if cli.id == "claude" {
        let mcp_config = root.join(".mcp.json");
        if mcp_config.is_file() {
            cmd.arg("--mcp-config")
                .arg(mcp_config)
                .arg("--strict-mcp-config");
        }
    }
    let (stdout, stderr, ok) = run_with_timeout(cmd, ASK_TIMEOUT_SECS)?;
    let low = format!("{}\n{}", stdout, stderr).to_lowercase();
    // «Не залогинен» — только когда процесс реально упал: в удачном ответе
    // эти же слова могут просто встречаться в тексте.
    let login_words = low.contains("not logged in")
        || low.contains("please run /login")
        || low.contains("please log in")
        || low.contains("api key");
    if !ok && login_words {
        return Err(format!(
            "{} установлен, но вход не выполнен. Откройте терминал, введите «{}» и войдите один раз. После этого AI OS сможет запускать консоль.",
            cli.label, cli.id
        ));
    }
    if !ok && stdout.trim().is_empty() {
        return Err(format!(
            "{} вернул ошибку: {}",
            cli.label,
            truncate_chars(stderr.trim(), 600)
        ));
    }
    if stdout.trim().is_empty() {
        return Err(format!(
            "{} ничего не ответил. Стандартный вывод пуст; ошибки: {}",
            cli.label,
            truncate_chars(stderr.trim(), 400)
        ));
    }
    Ok(stdout.trim().to_string())
}

/// Лёгкий markdown → HTML: абзацы, **жирный**, маркеры списков. Всё экранируется.
fn md_lite(s: &str) -> String {
    let e = esc(s);
    let mut out = String::new();
    for para in e.split("\n\n") {
        if para.trim().is_empty() {
            continue;
        }
        let mut p = String::new();
        let mut first = true;
        for line in para.lines() {
            if !first {
                p.push_str("<br>");
            }
            first = false;
            let t = line.trim_start();
            if t.starts_with("- ") || t.starts_with("* ") {
                p.push_str("• ");
                p.push_str(&t[2..]);
            } else if let Some(h) = t.strip_prefix("## ") {
                p.push_str(&format!("<b>{}</b>", h));
            } else if let Some(h) = t.strip_prefix("# ") {
                p.push_str(&format!("<b>{}</b>", h));
            } else {
                p.push_str(line);
            }
        }
        // Пары ** → <b>/</b> внутри одного абзаца, чтобы жирный не «протекал» дальше.
        if p.matches("**").count().is_multiple_of(2) {
            let mut open = false;
            while p.contains("**") {
                let tag = if open { "</b>" } else { "<b>" };
                p = p.replacen("**", tag, 1);
                open = !open;
            }
        }
        out.push_str("<p>");
        out.push_str(&p);
        out.push_str("</p>");
    }
    out
}

// ---------- захват ----------

fn inbox_path(root: &Path) -> PathBuf {
    root.join("60_Tasks").join("Inbox.md")
}

fn append_capture(root: &Path, text: &str) -> Result<(), String> {
    let clean: String = text.split_whitespace().collect::<Vec<_>>().join(" ");
    if clean.is_empty() {
        return Err("пустую строку не записываю".into());
    }
    let p = inbox_path(root);
    if !p.is_file() {
        let header = "---\ntype: task\nstatus: active\ntags:\n  - tasks/inbox\n---\n\n# Входящие\n\nКороткие заметки, которые нужно разобрать.\n\n## Записи\n";
        std::fs::write(&p, header).map_err(|e| e.to_string())?;
    }
    let mut f = std::fs::OpenOptions::new()
        .append(true)
        .open(&p)
        .map_err(|e| e.to_string())?;
    let line = format!(
        "- [ ] {} — {}\n",
        Local::now().format("%Y-%m-%d %H:%M"),
        clean
    );
    f.write_all(line.as_bytes()).map_err(|e| e.to_string())
}

fn verify_capture_behavior(root: &Path) -> Result<(), String> {
    append_capture(root, "[selftest] isolated capture check")?;
    let content = std::fs::read_to_string(inbox_path(root)).map_err(|e| e.to_string())?;
    if !content.contains("[selftest] isolated capture check") {
        return Err("capture text was not written to the temporary Inbox".into());
    }
    if append_capture(root, "   ").is_ok() {
        return Err("empty capture was accepted".into());
    }
    Ok(())
}

fn inbox_recent(root: &Path, n: usize) -> Vec<String> {
    read_text(&inbox_path(root))
        .lines()
        .filter(|l| l.trim_start().starts_with("- [ ]"))
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .take(n)
        .map(|l| {
            l.trim_start()
                .trim_start_matches("- [ ]")
                .trim()
                .to_string()
        })
        .collect()
}

// ---------- оформление ----------

const CSS: &str = r#"
:root { color-scheme: light; }
* { box-sizing: border-box; margin: 0; }
body { background: #efe9dc; color: #211e17; font: 15px/1.6 "Segoe UI", system-ui, sans-serif; }
body::before { content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: linear-gradient(rgba(33,30,23,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(33,30,23,.025) 1px, transparent 1px);
  background-size: 28px 28px; }
a { color: #0d6b52; }
.shell { display: grid; grid-template-columns: 224px minmax(0,1fr); min-height: 100vh; position: relative; z-index: 1; }
aside { border-right: 1.5px solid #211e17; padding: 20px 0 16px; background: #e7e1d1; display: flex; flex-direction: column; }
.plate { margin: 0 16px 14px; border: 1.5px solid #211e17; outline: 1px solid #211e17; outline-offset: 2.5px; background: #f4f0e4; padding: 12px 14px 10px; }
.plate b { display: block; font-family: Constantia, Georgia, serif; font-size: 18px; font-weight: 400; letter-spacing: .3px; }
.plate small { display: block; font-size: 9.5px; letter-spacing: 2px; text-transform: uppercase; color: #6b6353; margin-top: 3px; }
.plate .serial { font: 10px Consolas, monospace; color: #6b6353; margin-top: 6px; border-top: 1px solid #d8d1bd; padding-top: 5px; }
.stamp-mini { margin: 4px 16px 16px; border: 2px double; padding: 7px 11px 6px; font-size: 11.5px; letter-spacing: 1.2px; text-transform: uppercase; transform: rotate(-1.4deg); background: rgba(250,248,240,.6); }
.stamp-mini small { display: block; font-size: 9.5px; letter-spacing: .5px; text-transform: none; opacity: .85; margin-top: 1px; }
.good { border-color: #0d6b52; color: #0d6b52; } .warn { border-color: #9a6b15; color: #9a6b15; }
.bad { border-color: #a63a2b; color: #a63a2b; } .muted { border-color: #a49b85; color: #6b6353; }
nav { display: flex; flex-direction: column; gap: 1px; }
nav a { display: flex; align-items: center; gap: 10px; padding: 9px 18px; color: #3d382e; text-decoration: none; border-left: 3px solid transparent; font-size: 14px; transition: background .12s; }
nav a svg { width: 15px; height: 15px; flex: none; opacity: .75; }
nav a:hover { background: #ded7c3; }
nav a.on { border-left-color: #0d6b52; color: #0d6b52; font-weight: 600; background: #ded7c3; }
nav a.on svg { opacity: 1; }
.side-foot { margin-top: auto; padding: 12px 18px 0; font-size: 10.5px; color: #6b6353; border-top: 1px solid #c9c1ab; letter-spacing: .3px; }
main { padding: 28px 38px 64px; max-width: 1000px; }
.crumb { font-size: 10.5px; font-weight: 600; letter-spacing: 2.2px; text-transform: uppercase; color: #0d6b52; margin-bottom: 4px; }
h1 { font-family: Constantia, Georgia, serif; font-size: 27px; font-weight: 400; margin-bottom: 4px; }
.sub { color: #6b6353; font-size: 13.5px; margin-bottom: 14px; max-width: 640px; }
details.how { margin: 0 0 20px; border: 1px solid #d0c8b2; border-left: 3px solid #0d6b52; background: #f4f0e4; max-width: 720px; }
details.how summary { cursor: pointer; padding: 9px 14px; font-size: 12px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; color: #0d6b52; user-select: none; }
details.how summary:hover { background: #ede7d6; }
details.how .how-body { padding: 4px 16px 14px; font: 14.5px/1.65 Cambria, Georgia, serif; color: #3d382e; }
details.how .how-body p { margin-bottom: 8px; } details.how .how-body p:last-child { margin-bottom: 0; }
.btn { display: inline-flex; align-items: center; gap: 8px; background: #0d6b52; color: #f7f4e9; padding: 9px 16px 8px; text-decoration: none; border: 1px solid #0a5240; box-shadow: 0 2px 0 #083f31; font: 600 11.5px "Segoe UI"; letter-spacing: 1.1px; text-transform: uppercase; cursor: pointer; transition: transform .06s, box-shadow .06s; }
.btn:hover { filter: brightness(1.06); }
.btn:active { transform: translateY(2px); box-shadow: 0 0 0 #083f31; }
.btn.ghost { background: #f4f0e4; color: #0d6b52; border: 1px solid #0d6b52; box-shadow: 0 2px 0 #9fb5ac; }
.btn.ghost:active { box-shadow: 0 0 0 #9fb5ac; }
.btn.ink { background: #211e17; border-color: #000; box-shadow: 0 2px 0 #000; }
.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.panel { background: #faf8f0; border: 1px solid #c9c1ab; box-shadow: 3px 3px 0 rgba(33,30,23,.07); padding: 18px 22px; margin-bottom: 20px; }
.panel h2 { font-family: Constantia, Georgia, serif; font-size: 18px; font-weight: 400; margin-bottom: 4px; }
.panel .ph-rule { border: none; border-top: 1px solid #211e17; margin: 8px 0 12px; }
.feed-day { font-family: Constantia, Georgia, serif; font-size: 16px; margin: 16px 0 6px; }
.fi { display: flex; gap: 10px; padding: 6px 0; border-bottom: 1px solid #e2dcc9; font-size: 13.5px; align-items: baseline; }
.fi:last-child { border-bottom: none; }
.fi time { color: #6b6353; font: 12px Consolas, monospace; flex: none; width: 42px; }
.tag { flex: none; font: 600 10px "Segoe UI"; letter-spacing: 1px; text-transform: uppercase; padding: 2px 7px; border: 1px solid; }
.tag.агент { color: #0d6b52; border-color: #0d6b52; } .tag.коммит { color: #6b4f8a; border-color: #6b4f8a; } .tag.заметка { color: #9a6b15; border-color: #9a6b15; }
input[type=text], textarea, select { width: 100%; background: #fffdf6; border: 1px solid #b6ad93; border-bottom-width: 2px; padding: 10px 13px; font: 14px "Segoe UI"; color: #211e17; }
input[type=text]:focus, textarea:focus { outline: 2px solid #0d6b52; outline-offset: -1px; }
textarea { min-height: 78px; resize: vertical; font-family: Cambria, Georgia, serif; font-size: 15px; }
select { width: auto; padding: 8px 10px; }
.hit { border-bottom: 1px solid #e2dcc9; padding: 12px 0; }
.hit:last-child { border-bottom: none; }
.hit-head { display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
.hit-title { font-weight: 600; font-size: 14.5px; }
.hit-score { font: 11px Consolas, monospace; color: #6b6353; }
.hit-snip { font: 13.5px/1.55 Cambria, Georgia, serif; color: #4d473a; margin-top: 4px; }
.ok-note { background: #e7f0eb; border: 1px solid #0d6b52; color: #0a5240; padding: 9px 14px; margin-bottom: 14px; font-size: 13.5px; box-shadow: 2px 2px 0 rgba(13,107,82,.12); }
.err-note { background: #f6e7e2; border: 1px solid #a63a2b; color: #7c2b1f; padding: 9px 14px; margin-bottom: 14px; font-size: 13.5px; white-space: pre-wrap; box-shadow: 2px 2px 0 rgba(166,58,43,.12); }
pre { background: #211e17; color: #e8e2d1; padding: 12px 14px; font: 12px Consolas, monospace; overflow-x: auto; }
ul.plain { padding-left: 18px; } ul.plain li { margin: 5px 0; font-size: 14px; }
.bars-wrap { border: 1px solid #c8c0a8; background-color: #f7f4e9; padding: 14px 12px 10px;
  background-image: linear-gradient(#e3dcc6 1px, transparent 1px), linear-gradient(90deg, #e3dcc6 1px, transparent 1px), linear-gradient(#efe9d8 1px, transparent 1px), linear-gradient(90deg, #efe9d8 1px, transparent 1px);
  background-size: 40px 40px, 40px 40px, 8px 8px, 8px 8px; }
.bars { display: flex; align-items: flex-end; gap: 3px; height: 60px; }
.bars span { width: 12px; display: block; }
.answer { font: 15px/1.7 Cambria, Georgia, serif; color: #2d2a22; }
.answer p { margin-bottom: 10px; } .answer p:last-child { margin-bottom: 0; }
.ask-meta { font-size: 12px; color: #6b6353; border-top: 1px solid #e2dcc9; margin-top: 12px; padding-top: 8px; }
.cli-chip { display: inline-block; font: 600 11px Consolas, monospace; border: 1px solid #0d6b52; color: #0d6b52; padding: 3px 9px; margin: 0 6px 6px 0; background: #eef2ee; }
.cli-chip.off { border-color: #a49b85; color: #6b6353; background: transparent; }
.help-item { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid #e2dcc9; align-items: baseline; }
.help-item:last-child { border-bottom: none; }
.help-item b { flex: none; width: 110px; font-family: Constantia, Georgia, serif; font-weight: 400; font-size: 15.5px; }
.help-item span { font: 14px/1.6 Cambria, Georgia, serif; color: #3d382e; }
.muted-t { color: #6b6353; }
@media (prefers-reduced-motion: reduce) { .btn { transition: none; } nav a { transition: none; } }
@media (max-width: 780px) { .shell { grid-template-columns: 1fr; } aside { flex-direction: row; flex-wrap: wrap; align-items: center; border-right: none; border-bottom: 1.5px solid #211e17; } nav { flex-direction: row; flex-wrap: wrap; } .side-foot { display: none; } main { padding: 20px 16px 50px; } }
"#;

const CONTROL_CENTER_THEME: &str = include_str!("control-center.css");
const WINDOW_SCRIPT: &str = r#"<script>
(() => {
  const call = action => fetch('/window/' + action, { cache: 'no-store' }).catch(() => {});
  document.querySelectorAll('[data-window-action]').forEach(button => {
    button.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      call(button.dataset.windowAction);
    });
  });
  const bar = document.querySelector('[data-window-drag]');
  if (bar) {
    bar.addEventListener('pointerdown', event => {
      if (event.button === 0 && !event.target.closest('[data-window-action]')) call('drag');
    });
    bar.addEventListener('dblclick', event => {
      if (!event.target.closest('[data-window-action]')) call('maximize');
    });
  }
  document.addEventListener('keydown', event => {
    if (!(event.ctrlKey || event.metaKey)) return;
    if (event.key.toLowerCase() === 'n') {
      event.preventDefault();
      const note = document.querySelector('#quick-note');
      if (note) note.focus();
      else location.href = '/#quick-capture';
    }
  });
})();
</script>"#;

const G_TODAY: &str = "<svg viewBox=\"0 0 15 15\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M1 8h2.6L6 3.5 9 11.5 11.2 8H14\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\"/></svg>";
const G_PROJECTS: &str = "<svg viewBox=\"0 0 15 15\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M1.8 4.2h4l1.2 1.4h6.2v6.5H1.8z\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.35\"/><path d=\"M1.8 5.6V2.8h4.4l1.1 1.4h5.1v1.4\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.15\"/></svg>";
const G_CHECKS: &str = "<svg viewBox=\"0 0 15 15\" xmlns=\"http://www.w3.org/2000/svg\"><circle cx=\"7.5\" cy=\"7.5\" r=\"5.8\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.4\"/><path d=\"M4.8 7.7l1.9 1.9 3.7-4.1\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\"/></svg>";
const G_PASSPORT: &str = "<svg viewBox=\"0 0 15 15\" xmlns=\"http://www.w3.org/2000/svg\"><rect x=\"3\" y=\"1.6\" width=\"9\" height=\"11.8\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.4\"/><path d=\"M5.2 4.6h4.6M5.2 7h4.6M5.2 9.4h2.8\" stroke=\"currentColor\" stroke-width=\"1.2\"/></svg>";
const G_HELP: &str = "<svg viewBox=\"0 0 15 15\" xmlns=\"http://www.w3.org/2000/svg\"><circle cx=\"7.5\" cy=\"7.5\" r=\"5.8\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.4\"/><path d=\"M5.7 5.6c.3-1.1 1.2-1.7 2.2-1.6 1 .1 1.8.9 1.8 1.8 0 1.3-1.7 1.4-1.7 2.7\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.3\"/><circle cx=\"7.9\" cy=\"10.6\" r=\".8\" fill=\"currentColor\"/></svg>";

fn layout(root: &Path, active: &str, health: &HealthNow, body: &str) -> Vec<u8> {
    let ws = root
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_default();
    let nav_primary: [(&str, &str, &str); 3] = [
        ("/", "Обзор", G_TODAY),
        ("/projects", "Проекты", G_PROJECTS),
        ("/checks", "Проверки", G_CHECKS),
    ];
    let nav_secondary: [(&str, &str, &str); 2] = [
        ("/passport", "Паспорт", G_PASSPORT),
        ("/help", "Справка", G_HELP),
    ];
    let mut nav_html = String::new();
    nav_html.push_str("<nav class=\"primary-nav\">");
    for (href, label, glyph) in nav_primary {
        let on = if href == active { " class=\"on\"" } else { "" };
        nav_html.push_str(&format!(
            "<a href=\"{}\"{} title=\"{}\">{}<span>{}</span></a>",
            href, on, label, glyph, label
        ));
    }
    nav_html.push_str("</nav><nav class=\"secondary-nav\">");
    for (href, label, glyph) in nav_secondary {
        let on = if href == active { " class=\"on\"" } else { "" };
        nav_html.push_str(&format!(
            "<a href=\"{}\"{} title=\"{}\">{}<span>{}</span></a>",
            href, on, label, glyph, label
        ));
    }
    nav_html.push_str("</nav>");
    let chrome = format!(
        "<header class=\"titlebar\" data-window-drag>\
         <div class=\"titlebar-brand\"><span class=\"brand-mark\" aria-hidden=\"true\"></span><b>AI OS</b><span>/</span><span>Проект</span></div>\
         <div class=\"titlebar-workspace\"><i class=\"{}\"></i><span>{}</span><small>{}</small></div>\
         <div class=\"window-actions\">\
         <button type=\"button\" data-window-action=\"minimize\" title=\"Свернуть\" aria-label=\"Свернуть\"><svg viewBox=\"0 0 16 16\"><path d=\"M3 8.5h10\"/></svg></button>\
         <button type=\"button\" data-window-action=\"maximize\" title=\"Развернуть\" aria-label=\"Развернуть\"><svg viewBox=\"0 0 16 16\"><rect x=\"3.5\" y=\"3.5\" width=\"9\" height=\"9\" rx=\"1\"/></svg></button>\
         <button type=\"button\" class=\"window-close\" data-window-action=\"close\" title=\"Закрыть\" aria-label=\"Закрыть\"><svg viewBox=\"0 0 16 16\"><path d=\"m4 4 8 8m0-8-8 8\"/></svg></button>\
         </div></header>",
        health.class,
        esc(&ws),
        esc(&health.label)
    );
    format!(
        "<!DOCTYPE html><html lang=\"ru\"><head><meta charset=\"utf-8\">\
         <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\
         <title>AI OS</title><style>{}{}</style></head><body>{}\
         <div class=\"shell\"><aside>\
         <div class=\"plate\"><b>AI OS</b><small>ПРОЕКТ</small><div class=\"serial\">Приложение {}<br>Установщик {}</div></div>\
         <div class=\"stamp-mini {}\">{}<small>проверено: {}</small></div>\
         {}\
         <div class=\"side-foot\">Лабынцев Денис / @Ludosiel</div>\
         </aside><main>{}</main></div>{}</body></html>",
        CSS,
        CONTROL_CENTER_THEME,
        chrome,
        APP_VERSION,
        SETUP_VERSION,
        health.class,
        esc(&health.label),
        esc(&health.age),
        nav_html,
        body,
        WINDOW_SCRIPT
    )
    .into_bytes()
}

fn header(crumb: &str, title: &str, sub: &str, how_body: &str) -> String {
    format!(
        "<div class=\"crumb\">{}</div><h1>{}</h1><div class=\"sub\">{}</div>\
         <details class=\"how\"><summary>Что здесь</summary><div class=\"how-body\">{}</div></details>",
        esc(crumb), esc(title), esc(sub), how_body
    )
}

fn capture_form(back: &str, draft: &str) -> String {
    format!(
        "<form method=\"post\" action=\"/capture\">\
         <textarea id=\"quick-note\" name=\"text\" placeholder=\"Например: проверить мобильную версию\">{}</textarea>\
         <div class=\"row\" style=\"margin-top:10px\"><button class=\"btn\" type=\"submit\">Сохранить</button>\
         <span class=\"muted-t\" style=\"font-size:12.5px\">Файл: 60_Tasks/Inbox.md</span></div>\
         <input type=\"hidden\" name=\"back\" value=\"{}\"></form>",
        esc(draft), esc(back)
    )
}

fn stale_banner(health: &HealthNow) -> String {
    if health.stale {
        "<div class=\"err-note\">Данные проверки устарели. Нажмите «Проверить сейчас».</div>"
            .to_string()
    } else {
        String::new()
    }
}

// ---------- страницы ----------

fn page_today(root: &Path, ok_msg: Option<&str>, err: Option<(&str, &str)>) -> Vec<u8> {
    let health = health_now(root);
    let now = Local::now();
    let (tasks, task_total) = open_tasks(root, 5);
    let feed = build_feed(root);
    let feed_total = feed.len();
    let memory_ready = root.join(".mcp.json").is_file();
    let history_ready = root.join(".git").is_dir();
    let date_line = format!(
        "{}, {} {}",
        RU_WEEKDAYS[now.weekday().num_days_from_monday() as usize],
        now.day(),
        RU_MONTHS[now.month0() as usize]
    );
    let mut b = String::new();
    b.push_str(&header(
        &date_line,
        "Обзор",
        "Состояние проекта, задачи и последние изменения.",
        "<p>Здесь видны изменения заметок, коммиты и записи агентов.</p>\
         <p>Поле «Записать на потом» добавляет новую строку в заметки проекта. Проверки показывают, работают ли память, Git и фоновые задачи.</p>",
    ));
    b.push_str(&stale_banner(&health));
    if let Some(m) = ok_msg {
        b.push_str(&format!("<div class=\"ok-note\">{}</div>", esc(m)));
    }
    if let Some((e, _)) = err {
        b.push_str(&format!(
            "<div class=\"err-note\">Не записалось: {}</div>",
            esc(e)
        ));
    }
    let draft = err.map(|(_, d)| d).unwrap_or("");
    b.push_str(&format!(
        "<div class=\"overview-grid\">\
         <section class=\"system-stage {}\">\
         <div class=\"stage-top\"><span><i></i> Система</span><small>ПРОВЕРЕНО: {}</small></div>\
         <div class=\"status-ledger\">\
         <div class=\"status-row is-ready\"><i></i><div><b>Заметки</b><small>Файлы проекта</small></div><strong>ГОТОВО</strong></div>\
         <div class=\"status-row {}\"><i></i><div><b>Память</b><small>Поиск по заметкам</small></div><strong>{}</strong></div>\
         <div class=\"status-row {}\"><i></i><div><b>Git</b><small>История изменений</small></div><strong>{}</strong></div>\
         <div class=\"status-row {}\"><i></i><div><b>Проверки</b><small>Последний результат</small></div><strong>{}</strong></div>\
         </div>\
         <div class=\"telemetry\"><div><span>Открытые задачи</span><b>{:02}</b></div><div><span>Изменения</span><b>{:02}</b></div><div><span>Проверено</span><b>{}</b></div></div>\
         </section>\
         <section class=\"quick-capture\" id=\"quick-capture\"><div class=\"section-kicker\">Заметка</div>\
         <h2>Записать на потом</h2><p>Добавьте мысль или задачу. Она сохранится в заметках проекта.</p>{}</section>\
         </div>",
        health.class,
        esc(&health.age),
        if memory_ready { "is-ready" } else { "is-off" },
        if memory_ready { "подключена" } else { "не настроена" },
        if history_ready { "is-ready" } else { "is-off" },
        if history_ready { "включён" } else { "не настроен" },
        health.class,
        esc(&health.label),
        task_total,
        feed_total,
        esc(&health.age),
        capture_form("/", draft)
    ));
    b.push_str("<div class=\"dashboard-grid\"><section class=\"panel tasks-panel\"><div class=\"panel-head\"><div><span class=\"section-kicker\">Задачи</span><h2>Открытые</h2></div>");
    b.push_str(&format!(
        "<strong class=\"panel-count\">{:02}</strong></div>",
        task_total
    ));
    if tasks.is_empty() {
        b.push_str("<div class=\"empty-state\">Открытых задач нет.</div>");
    } else {
        b.push_str("<ul class=\"task-list\">");
        for task in &tasks {
            b.push_str(&format!("<li><i></i><span>{}</span></li>", esc(task)));
        }
        b.push_str("</ul>");
    }
    b.push_str(&format!(
        "<a class=\"text-link\" href=\"{}\">Открыть журнал <span>↗</span></a></section>",
        esc(&obsidian_link(root, "60_Tasks/Task_Log.md"))
    ));
    b.push_str("<section class=\"panel feed-panel\"><div class=\"panel-head\"><div><span class=\"section-kicker\">Изменения</span><h2>Последние</h2></div>");
    b.push_str(&format!(
        "<strong class=\"panel-count\">{:02}</strong></div><div class=\"feed-stream\">",
        feed_total
    ));
    if feed.is_empty() {
        b.push_str("<div class=\"empty-state\">Здесь появятся изменения заметок, коммиты и записи агентов.</div>");
    } else {
        let mut day: Option<NaiveDate> = None;
        for it in feed {
            let d = it.t.date_naive();
            if day != Some(d) {
                day = Some(d);
                b.push_str(&format!("<div class=\"feed-day\">{}</div>", ru_day(d)));
            }
            let text = match &it.link {
                Some(l) => format!("<a href=\"{}\">{}</a>", esc(l), esc(&it.text)),
                None => esc(&it.text),
            };
            b.push_str(&format!(
                "<div class=\"fi\"><time>{}</time><span class=\"tag {}\">{}</span><span>{}</span></div>",
                it.t.format("%H:%M"), it.kind, it.kind, text
            ));
        }
    }
    b.push_str("</div></section></div>");
    b.push_str(
        "<div class=\"row system-actions\"><span class=\"section-kicker\">Проверки</span><a class=\"btn ghost\" href=\"/rebuild?back=/\" title=\"Проверить систему и обновить паспорт\">Проверить сейчас</a>\
         <a class=\"btn ghost\" href=\"/readiness?back=/\" title=\"Проверить все файлы и настройки\">Проверить всё</a></div>",
    );
    layout(root, "/", &health, &b)
}

fn page_search(root: &Path, q: Option<String>) -> Vec<u8> {
    let health = health_now(root);
    let mut b = String::new();
    b.push_str(&header(
        "AI OS · помощник",
        "Помощник",
        "Найди первоисточник за секунды или попроси ИИ прочитать заметки и ответить.",
        "<p>Обычный поиск ищет совпадение букв. Этот — <b>смысл</b>: спроси «что мы решили про деньги», и он найдёт заметку, где написано «бюджет утверждён», хотя слова «деньги» там нет. Так работает та же память, которой пользуются твои ИИ-агенты, — у вас с ними один указатель.</p>\
         <p>Найденное — это <b>подсказка, где лежит правда</b>, а не сама правда. Клик по названию открывает заметку-первоисточник в Obsidian, а без него — в системном редакторе.</p>",
    ));
    let qv = q.clone().unwrap_or_default();
    b.push_str(&format!(
        "<div class=\"panel\"><form method=\"get\" action=\"/search\">\
         <input type=\"text\" name=\"q\" value=\"{}\" placeholder=\"например: что мы решили про источник правды?\" autofocus>\
         <div style=\"margin-top:10px\"><button class=\"btn\" type=\"submit\">Искать</button></div></form></div>",
        esc(&qv)
    ));
    if let Some(q) = q.filter(|s| !s.trim().is_empty()) {
        match memory_search(root, &q) {
            Err(e) => b.push_str(&format!("<div class=\"err-note\">{}</div>", esc(&e))),
            Ok(hits) if hits.is_empty() => {
                b.push_str("<div class=\"panel\">Ничего не нашлось. Попробуй сказать иначе — поиск идёт по смыслу.</div>")
            }
            Ok(hits) => {
                b.push_str("<div class=\"panel\">");
                for h in hits {
                    let title = h.source.trim_end_matches(".md");
                    let link = find_note_by_name(root, &h.source)
                        .map(|rel| obsidian_link(root, &rel));
                    let title_html = match &link {
                        Some(l) => format!("<a href=\"{}\">{}</a>", esc(l), esc(title)),
                        None => esc(title),
                    };
                    b.push_str(&format!(
                        "<div class=\"hit\"><div class=\"hit-head\"><span class=\"hit-title\">{}</span>\
                         <span class=\"hit-score\">score {}</span></div>\
                         <div class=\"hit-snip\">{}</div></div>",
                        title_html, esc(&h.score), esc(&truncate_chars(&h.snippet, 420))
                    ));
                }
                b.push_str("</div>");
            }
        }
    }
    layout(root, "/search", &health, &b)
}

fn page_ask(
    root: &Path,
    result: Option<Result<(String, String), String>>,
    q_draft: &str,
    chosen: &str,
) -> Vec<u8> {
    let health = health_now(root);
    let clis = detect_clis();
    let mut b = String::new();
    b.push_str(&header(
        "AI OS · помощник",
        "Помощник",
        "Найди первоисточник за секунды или попроси ИИ прочитать заметки и ответить.",
        "<p>Чем это отличается от «Поиска»: поиск показывает, <b>где</b> лежит ответ, а здесь агент сам читает найденное и <b>формулирует ответ</b> — как коллега, который сходил в архив и вернулся с выжимкой.</p>\
         <p>Всё происходит на вашем компьютере через установленную консоль ИИ. Агент работает только на чтение и не меняет файлы.</p>\
         <p>Ответ — это пересказ твоих же заметок: агент называет источники, а важные решения стоит проверять по первоисточнику.</p>",
    ));
    // Панель консолей: все известные, с честным статусом и кнопками.
    b.push_str("<div class=\"panel\"><h2>Консоли ИИ</h2><hr class=\"ph-rule\">");
    let installing = INSTALLING_CLI.load(Ordering::SeqCst);
    if installing {
        b.push_str("<div class=\"ok-note\">Идёт установка консоли — обычно меньше минуты. Страница обновится сама.</div>");
    }
    if let Ok(mut guard) = INSTALL_MSG.lock() {
        if let Some((ok, msg)) = guard.take() {
            let cls = if ok { "ok-note" } else { "err-note" };
            b.push_str(&format!("<div class=\"{}\">{}</div>", cls, esc(&msg)));
        }
    }
    for (id, label, _pkg, note) in KNOWN_CLIS {
        let found = clis.iter().find(|c| c.id == id);
        match found {
            Some(c) => {
                b.push_str(&format!(
                    "<div class=\"help-item\"><b style=\"width:130px\"><span class=\"cli-chip\" title=\"{}\">{}</span></b>\
                     <span>подключена. Если ещё не входил в аккаунт — <a href=\"/login-cli?id={}\">открыть консоль для входа</a> (один раз).</span></div>",
                    esc(&c.path), esc(label), id
                ));
            }
            None => {
                b.push_str(&format!(
                    "<div class=\"help-item\"><b style=\"width:130px\"><span class=\"cli-chip off\">{}</span></b>\
                     <span>не установлена ({}). <a class=\"btn ghost\" style=\"padding:4px 10px 3px;font-size:10.5px\" href=\"/install?id={}\">Установить</a></span></div>",
                    esc(label), note, id
                ));
            }
        }
    }
    b.push_str("<div class=\"muted-t\" style=\"font-size:12.5px;margin-top:8px\">Cursor, Antigravity и Windsurf работают с теми же заметками из своих редакторов. AI OS запускает только консоли из списка.</div>");
    if installing {
        b.push_str("<script>setTimeout(function(){location.replace('/ask')},7000)</script>");
    }
    b.push_str("</div>");
    // Форма.
    if !clis.is_empty() {
        let mut cli_select = String::new();
        if clis.len() > 1 {
            cli_select.push_str("<div class=\"row\" style=\"margin-bottom:8px\"><span class=\"muted-t\" style=\"font-size:12.5px\">кто отвечает:</span><select name=\"cli\">");
            for c in &clis {
                let sel = if c.id == chosen { " selected" } else { "" };
                cli_select.push_str(&format!(
                    "<option value=\"{}\"{}>{}</option>",
                    c.id,
                    sel,
                    esc(c.label)
                ));
            }
            cli_select.push_str("</select></div>");
        } else {
            cli_select.push_str(&format!(
                "<input type=\"hidden\" name=\"cli\" value=\"{}\">",
                clis[0].id
            ));
        }
        b.push_str(&format!(
            "<div class=\"panel\"><form method=\"post\" action=\"/ask\" onsubmit=\"var b=this.querySelector('button[type=submit]');if(b){{b.disabled=true;b.textContent='Агент думает — до 3 минут…';}}\">{}\
             <textarea name=\"q\" placeholder=\"например: что мы решили на встрече про роли, и что я обещал сделать?\">{}</textarea>\
             <div class=\"row\" style=\"margin-top:10px\"><button class=\"btn\" type=\"submit\">Спросить</button>\
             <span class=\"muted-t\" style=\"font-size:12.5px\">агент думает до трёх минут — он по-настоящему читает твои заметки, а не ищет по кэшу</span></div></form></div>",
            cli_select, esc(q_draft)
        ));
    }
    // Результат.
    match result {
        Some(Ok((answer, who))) => {
            b.push_str(&format!(
                "<div class=\"panel\"><h2>Ответ</h2><hr class=\"ph-rule\"><div class=\"answer\">{}</div>\
                 <div class=\"ask-meta\">Ответил {} прямо на этой машине, прочитав твои заметки. Это навигация, а не истина — первоисточник всегда сама заметка.</div></div>",
                md_lite(&answer), esc(&who)
            ));
        }
        Some(Err(e)) => {
            b.push_str(&format!("<div class=\"err-note\">{}</div>", esc(&e)));
        }
        None => {}
    }
    layout(root, "/ask", &health, &b)
}

fn page_capture(root: &Path, ok: bool, err: Option<(&str, &str)>) -> Vec<u8> {
    let health = health_now(root);
    let mut b = String::new();
    b.push_str(&header(
        "Заметки",
        "Новая заметка",
        "Быстро сохраните мысль или задачу.",
        "<p>Новая строка добавляется в файл <b>60_Tasks/Inbox.md</b>. Существующие записи приложение не меняет и не удаляет.</p>",
    ));
    if ok {
        b.push_str("<div class=\"ok-note\">Записано в 60_Tasks/Inbox.md.</div>");
    }
    if let Some((e, _)) = err {
        b.push_str(&format!(
            "<div class=\"err-note\">Не записалось: {}</div>",
            esc(e)
        ));
    }
    let draft = err.map(|(_, d)| d).unwrap_or("");
    b.push_str(&format!(
        "<div class=\"panel\">{}</div>",
        capture_form("/capture", draft)
    ));
    let recent = inbox_recent(root, 12);
    if !recent.is_empty() {
        b.push_str(
            "<div class=\"panel\"><h2>Последние записи</h2><hr class=\"ph-rule\"><ul class=\"plain\">",
        );
        for r in recent {
            b.push_str(&format!("<li>{}</li>", esc(&r)));
        }
        b.push_str(&format!(
            "</ul><div style=\"margin-top:8px\"><a href=\"{}\">Открыть файл</a></div></div>",
            esc(&obsidian_link(root, "60_Tasks/Inbox.md"))
        ));
    }
    layout(root, "/capture", &health, &b)
}

fn page_checks(root: &Path) -> Vec<u8> {
    let health = health_now(root);
    let mut b = String::new();
    b.push_str(&header(
        "Система",
        "Проверки",
        "Запустите проверку или посмотрите предыдущие результаты.",
        "<p>Обычная проверка обновляет состояние проекта и паспорт. Полная проверка дополнительно сверяет файлы, правила и фоновые задачи.</p>\
         <p>Зелёный результат означает, что ошибок не найдено. Жёлтый требует внимания. Красный означает, что часть системы не работает.</p>",
    ));
    b.push_str(&stale_banner(&health));
    b.push_str(
        "<div class=\"row\" style=\"margin-bottom:18px\">\
         <a class=\"btn\" href=\"/rebuild?back=/checks\">Проверить сейчас</a>\
         <a class=\"btn ghost\" href=\"/readiness?back=/checks\">Проверить всё</a></div>",
    );
    let runs = tail_lines(&root.join(".local").join("health-check.log"), 40);
    if !runs.is_empty() {
        b.push_str("<div class=\"panel\"><h2>Предыдущие проверки</h2><hr class=\"ph-rule\"><div class=\"bars-wrap\"><div class=\"bars\">");
        for r in &runs {
            let grab = |key: &str| -> i64 {
                r.split(key)
                    .nth(1)
                    .and_then(|x| x.split_whitespace().next())
                    .and_then(|v| v.parse().ok())
                    .unwrap_or(0)
            };
            let (w, f) = (grab("WARN="), grab("FAIL="));
            let (h, c) = if f > 0 {
                (56, "#a63a2b")
            } else if w > 0 {
                (42, "#9a6b15")
            } else {
                (28, "#0d6b52")
            };
            let ts = r.split(']').next().unwrap_or("").trim_start_matches('[');
            b.push_str(&format!(
                "<span title=\"{}\" style=\"height:{}px;background:{}\"></span>",
                esc(ts),
                h,
                c
            ));
        }
        b.push_str("</div></div><div class=\"sub\" style=\"margin-top:8px\">Наведите на столбец, чтобы увидеть время проверки.</div></div>");
    }
    let sched = tail_lines(&root.join(".local").join("readiness-scheduled.log"), 12);
    if !sched.is_empty() {
        b.push_str("<div class=\"panel\"><h2>Последняя проверка по расписанию</h2><hr class=\"ph-rule\"><pre>");
        for l in &sched {
            b.push_str(&esc(l));
            b.push('\n');
        }
        b.push_str("</pre></div>");
    }
    b.push_str("<div class=\"sub\">Подробный отчёт находится в разделе «Паспорт».</div>");
    layout(root, "/checks", &health, &b)
}

fn page_help(root: &Path) -> Vec<u8> {
    let health = health_now(root);
    let installer_file = if cfg!(windows) {
        format!("AI_OS_Setup_v{SETUP_VERSION}_x64.exe")
    } else {
        format!("AI_OS_Setup_v{SETUP_VERSION}_linux_x86_64.AppImage или .deb")
    };
    let delivery_detail = if cfg!(windows) {
        format!(
            "Обычный установщик загружает только недостающие пакеты. Для установки без интернета используйте AI_OS_Offline_Kit_v{SETUP_VERSION}_x64.exe."
        )
    } else {
        "Linux-пакеты содержат необходимые локальные компоненты и работают как офлайн-комплект."
            .into()
    };
    let os_requirement = if cfg!(windows) {
        "Windows 10/11 x64"
    } else {
        "Linux x86_64"
    };
    let os_detail = if cfg!(windows) {
        "Основной автоматический путь установки."
    } else {
        "Ubuntu 22.04+/Debian 12+ через .deb; AppImage для других современных дистрибутивов."
    };
    let free_space_detail = if cfg!(windows) {
        "Не менее 2 ГБ на выбранном диске; общие пакеты скачиваются один раз."
    } else {
        "Не менее 2 ГБ на выбранном диске для компонентов и локального поиска."
    };
    let signing_note = if cfg!(windows) {
        "Бета-версия пока не подписана цифровым сертификатом. Windows SmartScreen может показать предупреждение. Проверяйте имя файла и SHA-256 из папки раздачи."
    } else {
        "Бета-версия для Linux пока не подписана. Для AppImage разрешите запуск и сверьте SHA-256. Пакет .deb устанавливайте через системный менеджер пакетов."
    };
    let workspace = root
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_else(|| "проект".to_string());
    let mut b = String::new();
    b.push_str(&header(
        "AI OS",
        "Справка",
        "Установка, создание проектов и восстановление.",
        "<p>Установщик создаёт отдельную папку для каждого проекта. Общие компоненты загружаются один раз и используются повторно.</p>",
    ));
    b.push_str(&format!(
        "<section class=\"release-strip\" aria-label=\"Текущая сборка\">\
         <div><span>Установщик</span><b>Версия {}</b></div>\
         <div><span>Приложение</span><b>Версия {}</b></div>\
         <div><span>Текущий проект</span><b>{}</b></div></section>",
        SETUP_VERSION,
        APP_VERSION,
        esc(&workspace)
    ));
    b.push_str(&format!(
        "<div class=\"panel help-panel\"><div class=\"panel-title-row\"><span class=\"section-kicker\">Установка</span><span class=\"step-index\">01</span></div>\
         <h2>Первый проект</h2><hr class=\"ph-rule\"><div class=\"prose\">\
         <p>Запустите <code>{}</code>. Установщик проверит компьютер, загрузит недостающие компоненты и сверит их SHA-256. Rust, Python, Node.js и MCP-серверы отдельно устанавливать не нужно.</p>\
         <ol class=\"setup-steps\">\
         <li><span>1</span><div><b>Запустите установщик</b><p>Нажмите «Настроить проект».</p></div></li>\
         <li><span>2</span><div><b>Заполните форму</b><p>Укажите название проекта, своё имя и новую папку.</p></div></li>\
         <li><span>3</span><div><b>Создайте проект</b><p>Заметки, правила, память и карта кода будут настроены автоматически.</p></div></li>\
         <li><span>4</span><div><b>Откройте AI OS</b><p>Работайте с Claude Code, Codex или Cursor из созданной папки.</p></div></li>\
         </ol></div></div>",
        esc(&installer_file)
    ));
    b.push_str(&format!(
        "<div class=\"panel help-panel\"><div class=\"panel-title-row\"><span class=\"section-kicker\">Совместимость</span><span class=\"step-index\">02</span></div>\
         <h2>Что требуется на компьютере</h2><hr class=\"ph-rule\"><div class=\"requirement-grid\">\
         <div class=\"requirement ok\"><b>{}</b><span>{}</span></div>\
         <div class=\"requirement ok\"><b>Свободное место</b><span>{}</span></div>\
         <div class=\"requirement optional\"><b>Obsidian и Git</b><span>Рекомендуются, но проект создаётся и без них.</span></div>\
         <div class=\"requirement optional\"><b>ИИ-консоль и интернет</b><span>Войти в аккаунт можно позже. Обычному установщику интернет нужен для первой загрузки. Офлайн-комплект работает без сети.</span></div>\
         </div><div class=\"callout\">{} {}</div></div>",
        esc(os_requirement),
        esc(os_detail),
        esc(free_space_detail),
        esc(&delivery_detail),
        esc(signing_note)
    ));
    b.push_str(
        "<div class=\"panel help-panel\"><div class=\"panel-title-row\"><span class=\"section-kicker\">Проекты</span><span class=\"step-index\">03</span></div>\
         <h2>Создание следующего проекта</h2><hr class=\"ph-rule\"><div class=\"prose\">\
         <p>Переустанавливать программу не нужно. Откройте «Проекты» в левом меню и создайте ещё один проект.</p>\
         <p>У каждого проекта своя папка, заметки, память и карта кода. Общие компоненты повторно не загружаются.</p></div></div>",
    );
    b.push_str("<div class=\"panel help-panel\"><div class=\"panel-title-row\"><span class=\"section-kicker\">Навигация</span><span class=\"step-index\">04</span></div><h2>Что находится в каждом разделе</h2><hr class=\"ph-rule\">");
    let items: [(&str, &str); 6] = [
        (
            "Обзор",
            "состояние проекта, открытые задачи и последние изменения.",
        ),
        (
            "Проекты",
            "создание нового проекта, переключение, восстановление и фоновые проверки.",
        ),
        (
            "Новая заметка",
            "быстрое сохранение мысли или задачи в файл проекта.",
        ),
        ("Проверки", "ручной запуск проверки и история результатов."),
        ("Паспорт", "подробный технический отчёт о системе."),
        ("Справка", "установка, требования и восстановление."),
    ];
    for (name, desc) in items {
        b.push_str(&format!(
            "<div class=\"help-item\"><b>{}</b><span>{}</span></div>",
            name, desc
        ));
    }
    b.push_str("</div>");
    b.push_str(
        "<div class=\"help-grid\">\
         <div class=\"panel help-panel\"><div class=\"panel-title-row\"><span class=\"section-kicker\">Данные</span><span class=\"step-index\">05</span></div><h2>Как всё хранится</h2><hr class=\"ph-rule\"><div class=\"prose compact\">\
         <p>Основные данные находятся в обычных Markdown-файлах. Память помогает искать, но не заменяет файлы.</p>\
         <p>Каждый проект хранится отдельно. Его заметки и индекс кода не используются в других проектах.</p></div></div>\
         <div class=\"panel help-panel\"><div class=\"panel-title-row\"><span class=\"section-kicker\">ИИ</span><span class=\"step-index\">06</span></div><h2>Поддерживаемые приложения</h2><hr class=\"ph-rule\"><div class=\"prose compact\">\
         <p><b>Claude Code, Codex и Cursor</b> читают правила из папки проекта. Другие редакторы могут работать с теми же Markdown-файлами и MCP-сервисами.</p>\
         <p>Вопросы и работу с кодом выполняйте в выбранном ИИ-приложении. AI OS показывает состояние проекта и результаты проверок.</p></div></div></div>",
    );
    b.push_str(
        "<div class=\"panel help-panel recovery\"><div class=\"panel-title-row\"><span class=\"section-kicker\">Восстановление</span><span class=\"step-index\">07</span></div><h2>Если что-то выглядит сломанным</h2><hr class=\"ph-rule\">\
         <div class=\"recovery-flow\"><div><span>1</span><b>Откройте «Проверки»</b><p>Нажмите «Проверить сейчас» и дождитесь результата.</p></div><div><span>2</span><b>Откройте «Паспорт»</b><p>Красный статус означает ошибку. Жёлтый требует внимания.</p></div><div><span>3</span><b>Не удаляйте папку проекта</b><p>Журналы находятся в <code>.local</code>, а основные данные в Markdown-файлах.</p></div></div>\
         <div class=\"prose compact\"><p>AI OS не переписывает существующие заметки без явного действия. Приложение можно закрыть и открыть заново без потери данных.</p></div></div>",
    );
    b.push_str(&format!(
        "<div class=\"sub\">Разработал <b>Лабынцев Денис / @Ludosiel</b>. Подробный отчёт находится в <a href=\"/passport\">Паспорте</a>. Папка проекта: {}.</div>",
        esc(&root.file_name().map(|s| s.to_string_lossy().to_string()).unwrap_or_default())
    ));
    layout(root, "/help", &health, &b)
}

fn page_passport(root: &Path) -> Vec<u8> {
    let raw = std::fs::read_to_string(root.join(".local").join("dashboard.html"))
        .unwrap_or_else(|_| String::from("<!DOCTYPE html><html><body>Паспорт ещё не собран — нажми «Обновить».</body></html>"));
    let bar = "<div style=\"position:fixed;top:14px;right:18px;z-index:9999;display:flex;gap:8px;font:600 10px 'Segoe UI',sans-serif;letter-spacing:.8px;text-transform:uppercase\">\
               <a href=\"/\" title=\"Вернуться в AI OS\" style=\"background:rgba(14,14,16,.94);color:#d1d3d4;padding:9px 14px;text-decoration:none;border:1px solid rgba(255,255,255,.14);border-radius:999px;backdrop-filter:blur(12px)\">← AI OS</a>\
               <a href=\"/rebuild?back=/passport\" title=\"Пересобрать паспорт из свежих данных (в фоне)\" style=\"background:#405bff;color:#fff;padding:9px 14px;text-decoration:none;border:1px solid #7084ff;border-radius:999px;box-shadow:0 0 20px rgba(64,91,255,.24)\">Обновить</a></div>";
    raw.replacen("<body>", &format!("<body>{}", bar), 1)
        .into_bytes()
}

fn page_wait(message: &str, back: &str, secs: u32) -> Vec<u8> {
    format!(
        "<!DOCTYPE html><html lang=\"ru\"><head><meta charset=\"utf-8\">\
         <meta http-equiv=\"refresh\" content=\"{};url={}\"><title>AI OS</title></head>\
         <body style=\"background:#0e0e0e;color:#fff;font:15px/1.6 'Segoe UI Variable','Segoe UI',sans-serif;padding:34px\">\
         <div style=\"max-width:620px;border:1px solid rgba(255,255,255,.12);border-radius:12px;background:#191919;box-shadow:0 24px 80px rgba(0,0,0,.35);padding:25px 28px\">{}\
         <div style=\"margin-top:16px;font-size:12px;color:#a7a9ac\"><a style=\"color:#aeb8ff\" href=\"{}\">вернуться сейчас →</a></div></div></body></html>",
        secs, esc(back), esc(message), esc(back)
    )
    .into_bytes()
}

fn page_plain(message: &str) -> Vec<u8> {
    format!(
        "<!DOCTYPE html><html lang=\"ru\"><head><meta charset=\"utf-8\"><title>AI OS</title></head>\
         <body style=\"background:#0e0e0e;color:#fff;font:15px/1.6 'Segoe UI Variable','Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0\">\
         <div style=\"border:1px solid rgba(255,255,255,.12);border-radius:12px;background:#191919;box-shadow:0 24px 80px rgba(0,0,0,.35);padding:36px 44px;max-width:620px\">{}</div></body></html>",
        message
    )
    .into_bytes()
}

// ---------- маршрутизация (в рабочем потоке, не в UI) ----------

fn route(root: Option<&Path>, method: &str, path: &str, query: &str, body: &[u8]) -> Vec<u8> {
    match path {
        "/window/minimize" => {
            if let Some(window) = APP_HANDLE
                .get()
                .and_then(|app| app.get_webview_window("main"))
            {
                let _ = window.minimize();
            }
            return Vec::new();
        }
        "/window/maximize" => {
            if let Some(window) = APP_HANDLE
                .get()
                .and_then(|app| app.get_webview_window("main"))
            {
                if window.is_maximized().unwrap_or(false) {
                    let _ = window.unmaximize();
                } else {
                    let _ = window.maximize();
                }
            }
            return Vec::new();
        }
        "/window/drag" => {
            if let Some(window) = APP_HANDLE
                .get()
                .and_then(|app| app.get_webview_window("main"))
            {
                let _ = window.start_dragging();
            }
            return Vec::new();
        }
        "/window/close" => {
            if let Some(app) = APP_HANDLE.get() {
                app.exit(0);
            }
            return Vec::new();
        }
        _ => {}
    }
    let Some(root) = root else {
        return page_plain("Папка-правда не найдена. Запустите приложение из <code>tools/control-center-app</code> внутри workspace или задайте переменную окружения <code>AI_OS_ROOT</code>.");
    };
    if matches!(path, "/search" | "/ask" | "/install" | "/login-cli") {
        return page_wait(
            "Встроенный помощник удалён: задавай вопросы в Claude Code, Codex или Cursor прямо из папки проекта.",
            "/",
            1,
        );
    }
    match path {
        "/" | "/index.html" => {
            let ok = query_param(query, "ok").map(|_| "Записано в 60_Tasks/Inbox.md.");
            page_today(root, ok, None)
        }
        "/search" => page_search(root, query_param(query, "q")),
        "/projects" => match launch_workspace_manager(root) {
            Ok(()) => page_wait("Менеджер проектов открыт.", "/", 1),
            Err(error) => page_plain(&error),
        },
        "/ask" => {
            if method == "POST" {
                let form = String::from_utf8_lossy(body).to_string();
                let q = query_param(&form, "q").unwrap_or_default();
                let cli_id = query_param(&form, "cli").unwrap_or_default();
                if q.trim().is_empty() {
                    return page_ask(
                        root,
                        Some(Err("вопрос пустой — напиши, что хочешь узнать".into())),
                        "",
                        &cli_id,
                    );
                }
                let clis = detect_clis();
                let cli = if cli_id.is_empty() {
                    clis.first()
                } else {
                    clis.iter().find(|c| c.id == cli_id)
                };
                let Some(cli) = cli else {
                    return page_ask(
                        root,
                        Some(Err(
                            "выбранная консоль больше не найдена — обнови страницу".into()
                        )),
                        &q,
                        "",
                    );
                };
                if ASKING
                    .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
                    .is_err()
                {
                    return page_ask(
                        root,
                        Some(Err(
                            "агент уже думает над предыдущим вопросом — подожди его ответа".into(),
                        )),
                        &q,
                        cli.id,
                    );
                }
                let res = ask_agent(root, cli, q.trim()).map(|a| (a, cli.label.to_string()));
                ASKING.store(false, Ordering::SeqCst);
                page_ask(root, Some(res), &q, cli.id)
            } else {
                page_ask(root, None, "", "")
            }
        }
        "/capture" => {
            if method == "POST" {
                let form = String::from_utf8_lossy(body).to_string();
                let text = query_param(&form, "text").unwrap_or_default();
                let back = safe_back(query_param(&form, "back"), "/capture");
                match append_capture(root, &text) {
                    Ok(()) => {
                        let sep = if back.contains('?') { '&' } else { '?' };
                        page_wait("Записано.", &format!("{}{}ok=1", back, sep), 0)
                    }
                    Err(e) => {
                        if back == "/" {
                            page_today(root, None, Some((&e, &text)))
                        } else {
                            page_capture(root, false, Some((&e, &text)))
                        }
                    }
                }
            } else {
                page_capture(root, query_param(query, "ok").is_some(), None)
            }
        }
        "/checks" => page_checks(root),
        "/passport" => page_passport(root),
        "/help" => page_help(root),
        "/install" => {
            let id = query_param(query, "id").unwrap_or_default();
            let Some((_, label, pkg, _)) = KNOWN_CLIS.iter().find(|k| k.0 == id) else {
                return page_wait("Эта консоль не поддерживается.", "/ask", 4);
            };
            if detect_clis().iter().any(|c| c.id == id) {
                return page_wait("Эта консоль уже установлена.", "/ask", 2);
            }
            if INSTALLING_CLI
                .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
                .is_err()
            {
                return page_wait(
                    "Установка уже идёт — подожди, страница вернётся сама.",
                    "/ask",
                    6,
                );
            }
            let pkg = pkg.to_string();
            let label = label.to_string();
            std::thread::spawn(move || {
                let (ok, msg) = install_cli(&pkg);
                if let Ok(mut guard) = INSTALL_MSG.lock() {
                    *guard = Some((ok, format!("{}: {}", label, msg)));
                }
                INSTALLING_CLI.store(false, Ordering::SeqCst);
            });
            page_wait("Ставлю консоль — обычно меньше минуты. Страница вернётся сама и покажет результат.", "/ask", 8)
        }
        "/login-cli" => {
            let id = query_param(query, "id").unwrap_or_default();
            let cli = detect_clis().into_iter().find(|c| c.id == id);
            match cli {
                Some(c) => {
                    // Для npm-обёрток открываем родную команду, не node-путь.
                    let target = if c.args_prefix.is_empty() {
                        c.path.clone()
                    } else {
                        c.id.to_string()
                    };
                    open_cli_terminal(&target);
                    page_wait("Открыл консоль в отдельном окне — войди там в аккаунт один раз и окно можно закрыть.", "/ask", 4)
                }
                None => page_wait("Эта консоль не установлена.", "/ask", 4),
            }
        }
        "/rebuild" => {
            let back = safe_back(query_param(query, "back"), "/passport");
            if REBUILDING.load(Ordering::SeqCst) {
                return page_wait(
                    "Поверка уже идёт — подожди немного, страница вернётся сама.",
                    &back,
                    10,
                );
            }
            let root_owned = root.to_path_buf();
            std::thread::spawn(move || {
                let _ = rebuild_guarded(&root_owned);
            });
            page_wait(
                "Поверка запущена (~20 секунд). Страница вернётся сама и покажет свежие данные.",
                &back,
                24,
            )
        }
        "/readiness" => {
            let back = safe_back(query_param(query, "back"), "/");
            spawn_readiness(root);
            page_wait(
                "Самопроверка запущена в фоне — итог появится в истории проверок.",
                &back,
                4,
            )
        }
        "/open" => {
            if let Some(f) = query_param(query, "f") {
                let p = root.join(f);
                let inside = p
                    .canonicalize()
                    .ok()
                    .zip(root.canonicalize().ok())
                    .map(|(a, b)| a.starts_with(&b))
                    .unwrap_or(false);
                if inside && p.is_file() {
                    shell_open(&p.to_string_lossy());
                }
            }
            b"<script>history.back()</script>".to_vec()
        }
        _ => page_plain("Такой страницы в AI OS нет."),
    }
}

// ---------- selftest ----------

fn selftest() -> i32 {
    let Some(root) = find_root() else {
        println!("SELFTEST FAIL: root not found");
        return 1;
    };
    println!("AI OS v{}", APP_VERSION);
    println!("root: {}", root.display());
    let mut failures = 0;
    let h = health_now(&root);
    println!(
        "health: {} ({}) age: {} stale: {}",
        h.label, h.class, h.age, h.stale
    );
    let ev_lines = tail_lines(&root.join(".local").join("agent-events.ndjson"), 40);
    let parsed_events: Vec<serde_json::Value> = ev_lines
        .iter()
        .filter_map(|line| serde_json::from_str::<serde_json::Value>(line).ok())
        .collect();
    let visible_events = parsed_events
        .iter()
        .filter(|event| {
            let agent = event["agent"].as_str().unwrap_or("агент");
            let task = event["task"].as_str().unwrap_or("");
            let value = event["value"].as_str().unwrap_or("");
            let text = format!("{agent} — {task} · {value}");
            !has_obsolete_release_version(&text)
        })
        .count();
    let feed = build_feed(&root);
    let (mut a, mut c, mut n) = (0, 0, 0);
    for i in &feed {
        match i.kind {
            "агент" => a += 1,
            "коммит" => c += 1,
            _ => n += 1,
        }
    }
    println!(
        "feed: {} items (агент={} из {} актуальных / {} сырых строк журнала, коммит={}, заметка={})",
        feed.len(),
        a,
        visible_events,
        ev_lines.len(),
        c,
        n
    );
    if parsed_events.len() != ev_lines.len() {
        println!(
            "WARNING: не все сырые строки журнала являются JSON ({} из {})",
            parsed_events.len(),
            ev_lines.len()
        );
    }
    let (tasks, total) = open_tasks(&root, 6);
    println!("open tasks: {} of {}", tasks.len(), total);
    match memory_search(&root, "источник правды") {
        Ok(hits) => {
            println!(
                "search: {} hits, first source: {}",
                hits.len(),
                hits.first().map(|h| h.source.as_str()).unwrap_or("-")
            );
        }
        Err(e) => {
            if memory_tool(&root).is_ok() {
                println!("search ERROR: {}", e);
                failures += 1;
            } else {
                println!("search SKIP: memory layer is not configured ({})", e);
            }
        }
    }
    let clis = detect_clis();
    println!(
        "ask CLIs: {}",
        if clis.is_empty() {
            "нет".to_string()
        } else {
            clis.iter()
                .map(|c| format!("{} ({})", c.id, c.path))
                .collect::<Vec<_>>()
                .join("; ")
        }
    );
    println!(
        "md_lite: {}",
        md_lite("Привет **мир**\n\n- пункт один\n- пункт два")
    );
    let capture_root = std::env::temp_dir().join(format!(
        "ai-os-control-center-selftest-{}-{}",
        std::process::id(),
        Local::now().timestamp_millis()
    ));
    if let Err(e) = std::fs::create_dir_all(capture_root.join("60_Tasks")) {
        println!("capture ERROR: could not create temporary root: {}", e);
        failures += 1;
    } else {
        match verify_capture_behavior(&capture_root) {
            Ok(()) => println!("capture: OK (isolated temporary root)"),
            Err(e) => {
                println!("capture ERROR: {}", e);
                failures += 1;
            }
        }
        if let Err(e) = std::fs::remove_dir_all(&capture_root) {
            println!("capture cleanup ERROR: {}", e);
            failures += 1;
        }
    }
    println!(
        "safe_back: {:?} {:?} {:?}",
        safe_back(Some("/checks".into()), "/"),
        safe_back(Some("//evil.com".into()), "/"),
        safe_back(Some("https://evil.com".into()), "/")
    );
    if failures == 0 {
        println!("SELFTEST PASS");
        0
    } else {
        println!("SELFTEST FAIL: {} mandatory check(s) failed", failures);
        1
    }
}

fn render_pages_for(root: &Path, output: &Path) -> Result<Vec<PathBuf>, String> {
    std::fs::create_dir_all(output).map_err(|e| e.to_string())?;
    let pages = [
        ("overview.html", page_today(root, None, None)),
        ("capture.html", page_capture(root, false, None)),
        ("checks.html", page_checks(root)),
        ("help.html", page_help(root)),
        ("passport.html", page_passport(root)),
    ];
    let mut written = Vec::new();
    for (name, bytes) in pages {
        let path = output.join(name);
        std::fs::write(&path, bytes).map_err(|e| format!("{}: {e}", path.display()))?;
        written.push(path);
    }
    Ok(written)
}

fn render_pages(output: &Path) -> i32 {
    let Some(root) = find_root() else {
        println!("RENDER FAIL: root not found");
        return 1;
    };
    match render_pages_for(&root, output) {
        Ok(paths) => {
            println!("Rendered {} pages to {}", paths.len(), output.display());
            for path in paths {
                println!("- {}", path.display());
            }
            0
        }
        Err(error) => {
            println!("RENDER FAIL: {error}");
            1
        }
    }
}

// ---------- main ----------

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a == "--selftest") {
        std::process::exit(selftest());
    }
    if let Some(index) = args.iter().position(|a| a == "--render-pages") {
        let output = args
            .get(index + 1)
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from(".local/control-center-pages"));
        std::process::exit(render_pages(&output));
    }

    let start_hidden = args.iter().any(|a| a == "--start-hidden");
    let root_for_protocol = find_root();
    let primary_instance = match root_for_protocol.as_deref() {
        Some(root) => match acquire_workspace_instance(root, !start_hidden) {
            Ok(Some(instance)) => Some(instance),
            Ok(None) => return,
            Err(error) => {
                eprintln!("AI OS instance error: {error}");
                return;
            }
        },
        None => None,
    };
    let (instance_guard, instance_listener) = match primary_instance {
        Some(instance) => (Some(instance.guard), Some(instance.listener)),
        None => (None, None),
    };
    let instance_listener = Mutex::new(instance_listener);

    let run_result = tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .register_asynchronous_uri_scheme_protocol("dash", move |_ctx, request, responder| {
            let root = root_for_protocol.clone();
            let method = request.method().to_string();
            let uri = request.uri();
            let path = uri.path().to_string();
            let query = uri.query().unwrap_or("").to_string();
            let body = request.body().clone();
            std::thread::spawn(move || {
                let bytes = route(root.as_deref(), &method, &path, &query, &body);
                let resp = tauri::http::Response::builder()
                    .status(200)
                    .header("Content-Type", "text/html; charset=utf-8")
                    .header("Cache-Control", "no-store")
                    .body(bytes)
                    .unwrap();
                responder.respond(resp);
            });
        })
        .setup(move |app| {
            let _ = APP_HANDLE.set(app.handle().clone());
            if let Some(listener) = instance_listener.lock().ok().and_then(|mut value| value.take()) {
                start_instance_listener(listener, app.handle().clone());
            }
            let win = WebviewWindowBuilder::new(
                app,
                "main",
                WebviewUrl::External("http://dash.localhost/".parse().unwrap()),
            )
            .title("AI OS")
            .inner_size(1280.0, 900.0)
            .min_inner_size(760.0, 540.0)
            .decorations(false)
            .build()?;
            if start_hidden {
                let _ = win.hide();
            } else {
                let _ = win.show();
                let _ = win.unminimize();
                let _ = win.set_focus();
            }

            if let Some(root) = find_root() {
                std::thread::spawn(move || {
                    let _ = rebuild_guarded(&root);
                });
            }

            {
                let handle = app.handle().clone();
                std::thread::spawn(move || loop {
                    std::thread::sleep(Duration::from_secs(AUTO_REBUILD_MINUTES * 60));
                    if let Some(root) = find_root() {
                        if rebuild_guarded(&root) == Some(true) {
                            if let Some(w) = handle.get_webview_window("main") {
                                if w.url().map(|u| u.path() == "/passport").unwrap_or(false) {
                                    let _ = w.eval("location.reload()");
                                }
                            }
                        }
                    }
                });
            }

            {
                use tauri_plugin_notification::NotificationExt;
                let handle = app.handle().clone();
                std::thread::spawn(move || {
                    let mut was_state = 0u8;
                    let mut first = true;
                    loop {
                        std::thread::sleep(Duration::from_secs(if first {
                            45
                        } else {
                            WATCH_MINUTES * 60
                        }));
                        first = false;
                        let Some(root) = find_root() else { continue };
                        let h = health_now(&root);
                        let sync_fail =
                            tail_lines(&root.join(".local").join("mgimind-watch.log"), 3)
                                .iter()
                                .any(|l| l.contains("Sync FAILED"));
                        let state: u8 = if h.class == "bad" || sync_fail {
                            1
                        } else if h.stale {
                            2
                        } else {
                            0
                        };
                        if let Some(tray) = handle.tray_by_id("cc-tray") {
                            let tip = match state {
                                1 => "AI OS: есть проблемы",
                                2 => "AI OS: поверка устарела",
                                _ => "AI OS: система здорова",
                            };
                            let _ = tray.set_tooltip(Some(tip));
                        }
                        if state != 0 && state != was_state {
                            let body = match (state, sync_fail) {
                                (1, true) => {
                                    "Не обновляется память. Откройте AI OS и перейдите в «Проверки»."
                                }
                                (1, false) => {
                                    "Проверка нашла проблемы. Откройте AI OS и перейдите в «Проверки»."
                                }
                                _ => "Поверка давно не запускалась — статус может быть неактуален.",
                            };
                            let _ = handle
                                .notification()
                                .builder()
                                .title("AI OS")
                                .body(body)
                                .show();
                        }
                        was_state = state;
                    }
                });
            }

            let open_i = MenuItem::with_id(app, "open", "Открыть AI OS", true, None::<&str>)?;
            let capture_i =
                MenuItem::with_id(app, "capture", "Новая заметка", true, None::<&str>)?;
            let rebuild_i =
                MenuItem::with_id(app, "rebuild", "Проверить сейчас", true, None::<&str>)?;
            let readiness_i =
                MenuItem::with_id(app, "readiness", "Полная самопроверка", true, None::<&str>)?;
            let sep = PredefinedMenuItem::separator(app)?;
            let quit_i = MenuItem::with_id(app, "quit", "Выход", true, None::<&str>)?;
            let menu = Menu::with_items(
                app,
                &[&open_i, &capture_i, &rebuild_i, &readiness_i, &sep, &quit_i],
            )?;

            let icon = Image::from_bytes(include_bytes!("../icons/32x32.png"))?;
            TrayIconBuilder::with_id("cc-tray")
                .icon(icon)
                .tooltip("AI OS")
                .menu(&menu)
                .show_menu_on_left_click(true)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "open" => {
                        show_main_window(app);
                    }
                    "capture" => {
                        if let Some(w) = app.get_webview_window("main") {
                            let _ = w.show();
                            let _ = w.unminimize();
                            let _ = w.set_focus();
                            let _ = w.eval("location.href='/capture'");
                        }
                    }
                    "rebuild" => {
                        let app = app.clone();
                        std::thread::spawn(move || {
                            if let Some(root) = find_root() {
                                if rebuild_guarded(&root) == Some(true) {
                                    if let Some(w) = app.get_webview_window("main") {
                                        if w.url().map(|u| u.path() == "/passport").unwrap_or(false)
                                        {
                                            let _ = w.eval("location.reload()");
                                        }
                                    }
                                }
                            }
                        });
                    }
                    "readiness" => {
                        if let Some(root) = find_root() {
                            spawn_readiness(&root);
                        }
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .build(app)?;

            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                let _ = window.hide();
                api.prevent_close();
            }
        })
        .run(tauri::generate_context!());
    drop(instance_guard);
    run_result.expect("error while running AI OS");
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn unique_temp_root(label: &str) -> PathBuf {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!(
            "ai-os-control-center-{label}-{}-{nonce}",
            std::process::id()
        ))
    }

    #[test]
    fn instance_protocol_accepts_a_fragmented_command() {
        let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let address = listener.local_addr().unwrap();
        let sender = std::thread::spawn(move || {
            let mut stream = TcpStream::connect(address).unwrap();
            let split = INSTANCE_SHOW.len() / 2;
            stream
                .write_all(&INSTANCE_SHOW.as_bytes()[..split])
                .unwrap();
            stream.flush().unwrap();
            std::thread::sleep(Duration::from_millis(20));
            stream
                .write_all(&INSTANCE_SHOW.as_bytes()[split..])
                .unwrap();
            stream.write_all(b"\n").unwrap();
            stream.flush().unwrap();
        });
        let (mut stream, _) = listener.accept().unwrap();
        assert_eq!(read_instance_command(&mut stream), Some(true));
        sender.join().unwrap();
    }

    #[test]
    fn second_workspace_instance_notifies_primary_instead_of_staying_open() {
        let root = unique_temp_root("single-instance");
        std::fs::create_dir_all(root.join(".local")).unwrap();
        let primary = acquire_workspace_instance(&root, true).unwrap().unwrap();
        let listener = primary.listener.try_clone().unwrap();
        let (ready_tx, ready_rx) = std::sync::mpsc::channel();
        let received = std::thread::spawn(move || {
            ready_tx.send(()).unwrap();
            let (mut stream, _) = listener.accept().unwrap();
            let show = read_instance_command(&mut stream).unwrap();
            stream.write_all(INSTANCE_ACK.as_bytes()).unwrap();
            stream.flush().unwrap();
            show
        });

        ready_rx.recv_timeout(Duration::from_secs(1)).unwrap();
        assert!(acquire_workspace_instance(&root, true).unwrap().is_none());
        assert!(received.join().unwrap());
        let (lock, state) = instance_paths(&root);
        drop(primary);
        assert!(!lock.exists());
        assert!(!state.exists());
        let _ = std::fs::remove_dir_all(root);
    }

    #[test]
    fn background_probe_does_not_raise_the_existing_window() {
        let root = unique_temp_root("background-probe");
        std::fs::create_dir_all(root.join(".local")).unwrap();
        let primary = acquire_workspace_instance(&root, false).unwrap().unwrap();
        let listener = primary.listener.try_clone().unwrap();
        let (ready_tx, ready_rx) = std::sync::mpsc::channel();
        let received = std::thread::spawn(move || {
            ready_tx.send(()).unwrap();
            let (mut stream, _) = listener.accept().unwrap();
            let show = read_instance_command(&mut stream).unwrap();
            stream.write_all(INSTANCE_ACK.as_bytes()).unwrap();
            stream.flush().unwrap();
            show
        });

        ready_rx.recv_timeout(Duration::from_secs(1)).unwrap();
        assert!(acquire_workspace_instance(&root, false).unwrap().is_none());
        assert!(!received.join().unwrap());
        drop(primary);
        let _ = std::fs::remove_dir_all(root);
    }

    #[test]
    fn stale_workspace_instance_state_is_recovered() {
        let root = unique_temp_root("stale-instance");
        let (lock, state) = instance_paths(&root);
        std::fs::create_dir_all(lock.parent().unwrap()).unwrap();
        std::fs::write(&lock, "stale").unwrap();
        std::fs::write(&state, r#"{"schemaVersion":1,"pid":1,"port":9}"#).unwrap();

        let primary = acquire_workspace_instance(&root, false).unwrap().unwrap();
        assert!(lock.exists());
        assert!(state.exists());
        drop(primary);
        assert!(!lock.exists());
        assert!(!state.exists());
        let _ = std::fs::remove_dir_all(root);
    }

    #[test]
    fn codex_ask_is_hard_read_only_and_ephemeral() {
        let args = build_agent_args("codex", "question", None).unwrap();
        assert!(args.windows(2).any(|w| w == ["--sandbox", "read-only"]));
        assert!(args.iter().any(|a| a == "--ephemeral"));
        assert!(!args.iter().any(|a| a.contains("dangerously-bypass")));
        assert_eq!(args.last().map(String::as_str), Some("question"));
    }

    #[test]
    fn claude_ask_uses_plan_mode_and_only_read_tools() {
        let args = build_agent_args("claude", "question", Some("memory")).unwrap();
        assert!(args.windows(2).any(|w| w == ["--permission-mode", "plan"]));
        assert!(args.windows(2).any(|w| w == ["--tools", "Read,Grep,Glob"]));
        assert!(args
            .windows(2)
            .any(|w| w[0] == "--allowedTools" && w[1].contains("mcp__memory__mind_search")));
        assert!(args
            .windows(2)
            .any(|w| w[0] == "--disallowedTools" && w[1].contains("Edit")));
        assert!(args.iter().any(|a| a == "--no-session-persistence"));
    }

    #[test]
    fn unknown_agent_is_not_allowed_to_answer() {
        assert!(build_agent_args("gemini", "question", None).is_err());
    }

    #[test]
    fn every_cli_offered_by_the_ui_has_a_read_only_adapter() {
        for (id, _, _, _) in KNOWN_CLIS {
            assert!(build_agent_args(id, "question", None).is_ok(), "{id}");
        }
    }

    #[test]
    fn memory_server_name_comes_from_mcp_config() {
        let root = unique_temp_root("mcp");
        std::fs::create_dir_all(&root).unwrap();
        std::fs::write(
            root.join(".mcp.json"),
            r#"{"mcpServers":{"memory":{"command":"mgimind.exe","args":["mcp"]}}}"#,
        )
        .unwrap();
        assert_eq!(memory_mcp_server_name(&root).as_deref(), Some("memory"));
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn unconfigured_workspace_never_falls_back_to_global_memory() {
        let root = unique_temp_root("memory-isolation");
        std::fs::create_dir_all(&root).unwrap();
        assert!(memory_tool(&root).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn configured_memory_uses_only_this_workspace_config() {
        let root = unique_temp_root("memory-config");
        let tools = root.join("tools");
        std::fs::create_dir_all(&tools).unwrap();
        let exe = root.join("workspace-memory.exe");
        std::fs::write(&exe, b"test").unwrap();
        std::fs::write(
            tools.join("ai_os.config.json"),
            format!(
                r#"{{"memoryToolPath":"{}","memoryLibrary":"workspace-only"}}"#,
                exe.to_string_lossy().replace('\\', "\\\\")
            ),
        )
        .unwrap();
        let (configured_exe, library) = memory_tool(&root).unwrap();
        assert_eq!(configured_exe, exe);
        assert_eq!(library, "workspace-only");
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn capture_selftest_isolated_to_temporary_root() {
        let root = unique_temp_root("capture");
        std::fs::create_dir_all(root.join("60_Tasks")).unwrap();
        verify_capture_behavior(&root).unwrap();
        let content = std::fs::read_to_string(inbox_path(&root)).unwrap();
        assert!(content.contains("[selftest]"));
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn help_uses_current_release_and_real_setup_actions() {
        let root = unique_temp_root("help-release");
        std::fs::create_dir_all(root.join(".local")).unwrap();
        let html = String::from_utf8(page_help(&root)).unwrap();
        #[cfg(windows)]
        assert!(html.contains(&format!("AI_OS_Setup_v{}_x64.exe", SETUP_VERSION)));
        #[cfg(not(windows))]
        assert!(html.contains(&format!(
            "AI_OS_Setup_v{}_linux_x86_64.AppImage",
            SETUP_VERSION
        )));
        assert!(html.contains(&format!("Версия {}", APP_VERSION)));
        assert!(html.contains("Настроить проект"));
        assert!(html.contains("Создайте проект"));
        assert!(html.contains("Общие компоненты"));
        #[cfg(windows)]
        assert!(html.contains(&format!("AI_OS_Offline_Kit_v{}_x64.exe", SETUP_VERSION)));
        assert!(!html.contains("Control Center"));
        assert!(!html.contains("Центр проекта"));
        assert!(!html.contains("AI_OS_Setup_v0.1"));
        assert!(!html.contains("AI_OS_Setup_v0.2"));
        assert!(!html.contains("AI_OS_Setup_v0.3.1"));
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn removed_assistant_routes_do_not_render_the_old_interface() {
        let root = unique_temp_root("assistant-removed");
        std::fs::create_dir_all(root.join(".local")).unwrap();
        let html = String::from_utf8(route(Some(&root), "GET", "/ask", "", b"")).unwrap();
        assert!(html.contains("Встроенный помощник удалён"));
        assert!(!html.contains("Консоли ИИ"));
        assert!(!html.contains("<textarea name=\"q\""));
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn visual_qa_export_writes_every_user_facing_page() {
        let root = unique_temp_root("render-pages");
        let output = root.join("rendered");
        std::fs::create_dir_all(root.join(".local")).unwrap();
        std::fs::create_dir_all(root.join("60_Tasks")).unwrap();
        std::fs::write(
            root.join(".local").join("dashboard.html"),
            "<!DOCTYPE html><html><body>passport</body></html>",
        )
        .unwrap();
        let pages = render_pages_for(&root, &output).unwrap();
        assert_eq!(pages.len(), 5);
        for page in pages {
            let html = std::fs::read_to_string(page).unwrap();
            assert!(html.contains("<html"));
            for obsolete in [
                "БЫСТРЫЙ ЗАХВАТ",
                "Телеметрия",
                "Очередь",
                "Центр проекта",
                "Control Center",
            ] {
                assert!(!html.contains(obsolete), "{obsolete}");
            }
        }
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn overview_filters_obsolete_release_numbers_but_keeps_current_tools() {
        assert!(has_obsolete_release_version("AI OS Setup 0.3.1"));
        assert!(has_obsolete_release_version("Control Center v0.4"));
        assert!(!has_obsolete_release_version(&format!(
            "AI OS Setup {SETUP_VERSION} and Control Center {APP_VERSION}"
        )));
        assert!(!has_obsolete_release_version("codebase-memory-mcp 0.9.0"));
    }
}
