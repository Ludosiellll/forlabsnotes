#![cfg_attr(all(not(debug_assertions), windows), windows_subsystem = "windows")]

mod registry;
mod supervisor;

use registry::{
    load_registry, memory_library_name, save_registry, state_dir, workspace_id, WorkspaceRecord,
    WorkspaceRegistry,
};
use supervisor::reconcile_supervisor;

use std::fs::{self, File};
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{Shutdown, SocketAddr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::{Mutex, OnceLock};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[cfg(unix)]
use std::os::unix::ffi::OsStrExt;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
#[cfg(windows)]
use std::os::windows::ffi::OsStrExt;
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use tauri::{AppHandle, Manager, WebviewUrl, WebviewWindowBuilder};

const APP_VERSION: &str = env!("CARGO_PKG_VERSION");
const MANAGER_SHOW: &str = "AIOS_WORKSPACE_MANAGER_SHOW_V1";
const MANAGER_PING: &str = "AIOS_WORKSPACE_MANAGER_PING_V1";
const MANAGER_ACK: &str = "AIOS_WORKSPACE_MANAGER_OK_V1";
#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;
const MIN_FREE_SPACE_BYTES: u64 = 2 * 1024 * 1024 * 1024;
#[cfg(windows)]
const MEMORY_BINARY_NAME: &str = "mgimind.exe";
#[cfg(not(windows))]
const MEMORY_BINARY_NAME: &str = "mgimind";
#[cfg(windows)]
const CODE_INTEL_BINARY_NAME: &str = "codebase-memory-mcp.exe";
#[cfg(not(windows))]
const CODE_INTEL_BINARY_NAME: &str = "codebase-memory-mcp";
#[cfg(windows)]
const QDRANT_BINARY_NAME: &str = "qdrant.exe";
#[cfg(windows)]
const ONNX_RUNTIME_BINARY_NAME: &str = "onnxruntime.dll";
#[cfg(windows)]
const CONTROL_CENTER_BINARY_NAME: &str = "ai-os-control-center.exe";
#[cfg(not(windows))]
const CONTROL_CENTER_BINARY_NAME: &str = "ai-os-control-center";

static RESOURCE_DIR: OnceLock<PathBuf> = OnceLock::new();
static APP_HANDLE: OnceLock<AppHandle> = OnceLock::new();
static JOB: Mutex<Option<SetupJob>> = Mutex::new(None);

struct ManagerInstanceGuard {
    lock_path: PathBuf,
    state_path: PathBuf,
}

impl Drop for ManagerInstanceGuard {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.state_path);
        let _ = fs::remove_file(&self.lock_path);
    }
}

struct PrimaryManagerInstance {
    listener: TcpListener,
    guard: ManagerInstanceGuard,
}

struct SetupJob {
    child: Child,
    destination: PathBuf,
    workspace_id: String,
    project_name: String,
    automation_enabled: bool,
    log_path: PathBuf,
    mode: String,
}

#[derive(Default)]
struct InstallForm {
    project_name: String,
    user_name: String,
    client_name: String,
    company_name: String,
    code_repo_path: String,
    destination: String,
    summary: String,
    memory: bool,
    code_intel: bool,
    automation: bool,
    git: bool,
}

const INSTALLER_CSS: &str = include_str!("installer.css");
const INSTALLER_JS: &str = include_str!("installer.js");
const THREE_JS: &str = include_str!("vendor/three.module.min.js");
const THREE_CORE_JS: &str = include_str!("vendor/three.core.min.js");
const BRAIN_GLB: &[u8] = include_bytes!("vendor/brain.glb");
const DALA_REPLICA_LICENSE: &str = include_str!("vendor/DALA-REPLICA-LICENSE.txt");
const ONEST_CYRILLIC: &[u8] = include_bytes!("vendor/onest-cyrillic-wght-normal.woff2");
const ONEST_LATIN: &[u8] = include_bytes!("vendor/onest-latin-wght-normal.woff2");
const SETUP_ICON_PNG: &[u8] = include_bytes!("../icons/128x128.png");
const ONEST_LICENSE: &str = include_str!("vendor/ONEST-LICENSE.txt");

const HTML_HEAD: &str = r#"<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,">
<title>Установка AI OS</title>
<script>try{if(sessionStorage.getItem("ai-os-setup-entered")==="1")document.documentElement.classList.add("setup-active","boot-complete","scene-retired");else document.documentElement.classList.add("first-entry")}catch(_){document.documentElement.classList.add("first-entry")}</script>
<style>"#;

const HTML_SHELL: &str = r#"</style>
<script type="module" src="/assets/installer.js"></script>
</head>
<body><header class="titlebar" data-window-drag><div class="titlebar-brand"><span class="brand-mark" aria-hidden="true"></span><b>AI OS</b><span>/</span><span>Установка</span></div><div class="titlebar-meta">На этом компьютере</div><div class="window-actions"><button type="button" data-window-action="minimize" title="Свернуть" aria-label="Свернуть"><svg viewBox="0 0 16 16"><path d="M3 8.5h10"/></svg></button><button type="button" data-window-action="maximize" title="Развернуть" aria-label="Развернуть"><svg viewBox="0 0 16 16"><rect x="3.5" y="3.5" width="9" height="9" rx="1"/></svg></button><button type="button" class="window-close" data-window-action="close" title="Закрыть" aria-label="Закрыть"><svg viewBox="0 0 16 16"><path d="m4 4 8 8m0-8-8 8"/></svg></button></div></header><div class="boot-screen" role="status" aria-live="polite"><div class="boot-core"><span class="boot-mark brand-mark" aria-hidden="true"></span><p class="boot-name">AI OS</p><div class="boot-signal" aria-hidden="true"><span></span><i></i><i></i><i></i></div><p class="boot-status">Запускаем установщик</p></div><button class="boot-skip" type="button">Пропустить</button></div><div class="shell"><aside class="rail"><div class="brand"><span class="brand-mark" aria-hidden="true"></span><span>AI OS <small>настройка проекта</small></span></div><div class="constellation" aria-hidden="true">
<canvas id="knowledge-field"></canvas>
<i class="particle" style="--x:8%;--y:42%;--s:8px;--c:#15846e;--d:-1s"></i><i class="particle" style="--x:15%;--y:25%;--s:10px;--c:#8052ff;--d:-2.1s"></i><i class="particle" style="--x:19%;--y:63%;--s:6px;--c:#ffb829;--d:-.4s"></i><i class="particle" style="--x:26%;--y:13%;--s:7px;--c:#3dd6f5;--d:-3s"></i><i class="particle" style="--x:27%;--y:37%;--s:12px;--c:#8052ff;--d:-1.6s"></i><i class="particle" style="--x:29%;--y:76%;--s:9px;--c:#ff6da8;--d:-2.7s"></i><i class="particle" style="--x:34%;--y:54%;--s:6px;--c:#ffb829;--d:-.8s"></i><i class="particle" style="--x:38%;--y:22%;--s:9px;--c:#15846e;--d:-2.2s"></i><i class="particle" style="--x:40%;--y:68%;--s:11px;--c:#8052ff;--d:-1.2s"></i><i class="particle" style="--x:45%;--y:7%;--s:5px;--c:#ffb829;--d:-3.4s"></i><i class="particle" style="--x:46%;--y:42%;--s:13px;--c:#3dd6f5;--d:-1.9s"></i><i class="particle" style="--x:50%;--y:84%;--s:7px;--c:#15846e;--d:-.6s"></i><i class="particle" style="--x:54%;--y:27%;--s:7px;--c:#ff6da8;--d:-2.4s"></i><i class="particle" style="--x:57%;--y:58%;--s:10px;--c:#ffb829;--d:-1.1s"></i><i class="particle" style="--x:61%;--y:15%;--s:11px;--c:#8052ff;--d:-3.1s"></i><i class="particle" style="--x:64%;--y:74%;--s:6px;--c:#3dd6f5;--d:-.3s"></i><i class="particle" style="--x:68%;--y:38%;--s:8px;--c:#15846e;--d:-2.6s"></i><i class="particle" style="--x:72%;--y:56%;--s:12px;--c:#8052ff;--d:-1.4s"></i><i class="particle" style="--x:77%;--y:22%;--s:6px;--c:#ffb829;--d:-3.5s"></i><i class="particle" style="--x:80%;--y:70%;--s:9px;--c:#ff6da8;--d:-.9s"></i><i class="particle" style="--x:86%;--y:43%;--s:7px;--c:#3dd6f5;--d:-2s"></i><i class="particle" style="--x:91%;--y:57%;--s:5px;--c:#8052ff;--d:-1.7s"></i>
</div><div class="intro-copy"><p class="eyebrow">Для работы с ИИ</p><h1>Контекст проекта в одном месте.</h1><p>Заметки, решения и память хранятся отдельно для каждого проекта.</p><button id="begin-setup" class="begin-setup" type="button"><span>Настроить проект</span><i aria-hidden="true">→</i></button><small>Данные остаются на этом компьютере</small></div><div class="rail-copy"><span class="phase-index">Установка</span><p class="eyebrow" data-phase-kicker>Проект · 01</p><h2 data-phase-title>Параметры проекта</h2><p data-phase-copy>У каждого проекта будет своя папка с заметками, правилами и памятью.</p></div><ol class="steps" aria-label="Этапы установки"><li class="active" aria-current="step"><b>01</b><span>Проект</span></li><li><b>02</b><span>Установка</span></li><li><b>03</b><span>Готово</span></li></ol><div class="credit">Разработал и поддерживает<br><b>Денис Лабынцев / @Ludosiel</b></div></aside><main class="content">"#;

const HTML_FOOT: &str = "</main></div></body></html>";

fn esc(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}

fn page(body: String) -> Vec<u8> {
    format!("{HTML_HEAD}{INSTALLER_CSS}{HTML_SHELL}{body}{HTML_FOOT}").into_bytes()
}

fn manager_instance_paths() -> (PathBuf, PathBuf) {
    let root = state_dir();
    (
        root.join("workspace-manager-instance.lock"),
        root.join("workspace-manager-instance.json"),
    )
}

fn notify_workspace_manager(state_path: &Path, show: bool) -> bool {
    let deadline = std::time::Instant::now() + Duration::from_secs(2);
    while std::time::Instant::now() < deadline {
        let state = fs::read_to_string(state_path).ok().and_then(|text| {
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
                let command = if show { MANAGER_SHOW } else { MANAGER_PING };
                if stream.write_all(command.as_bytes()).is_ok()
                    && stream.write_all(b"\n").is_ok()
                    && stream.flush().is_ok()
                {
                    let _ = stream.shutdown(Shutdown::Write);
                    let mut response = vec![0u8; MANAGER_ACK.len()];
                    if stream.read_exact(&mut response).is_ok()
                        && response.as_slice() == MANAGER_ACK.as_bytes()
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

fn acquire_manager_instance(show_existing: bool) -> Result<Option<PrimaryManagerInstance>, String> {
    let (lock_path, state_path) = manager_instance_paths();
    let parent = lock_path
        .parent()
        .ok_or("У файла блокировки нет родительской папки")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;

    for attempt in 0..2 {
        match fs::OpenOptions::new()
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
                let guard = ManagerInstanceGuard {
                    lock_path: lock_path.clone(),
                    state_path: state_path.clone(),
                };
                let state = serde_json::json!({
                    "schemaVersion": 1,
                    "pid": std::process::id(),
                    "port": port
                });
                let temporary =
                    state_path.with_extension(format!("json.{}.tmp", std::process::id()));
                fs::write(
                    &temporary,
                    serde_json::to_vec_pretty(&state).map_err(|error| error.to_string())?,
                )
                .map_err(|error| error.to_string())?;
                fs::rename(&temporary, &state_path).map_err(|error| error.to_string())?;
                return Ok(Some(PrimaryManagerInstance { listener, guard }));
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                if notify_workspace_manager(&state_path, show_existing) {
                    return Ok(None);
                }
                if attempt == 0 {
                    let _ = fs::remove_file(&state_path);
                    let _ = fs::remove_file(&lock_path);
                    continue;
                }
                return Err("Не удалось связаться с уже открытым окном AI OS".into());
            }
            Err(error) => return Err(error.to_string()),
        }
    }
    Err("Не удалось проверить, открыто ли окно AI OS".into())
}

fn read_manager_command(stream: &mut TcpStream) -> Option<bool> {
    let _ = stream.set_read_timeout(Some(Duration::from_secs(1)));
    let mut request = String::new();
    {
        let mut reader = BufReader::new(&mut *stream);
        reader.read_line(&mut request).ok()?;
    }
    match request.trim() {
        MANAGER_SHOW => Some(true),
        MANAGER_PING => Some(false),
        _ => None,
    }
}

fn show_manager_window(app: &AppHandle) {
    let handle = app.clone();
    let _ = app.run_on_main_thread(move || {
        if let Some(window) = handle.get_webview_window("main") {
            let _ = window.show();
            let _ = window.unminimize();
            let _ = window.set_always_on_top(true);
            let _ = window.set_focus();
            let _ = window.set_always_on_top(false);
        }
    });
}

fn start_manager_listener(listener: TcpListener, app: AppHandle) {
    std::thread::spawn(move || {
        for connection in listener.incoming() {
            let Ok(mut stream) = connection else { continue };
            if let Some(show) = read_manager_command(&mut stream) {
                if show {
                    show_manager_window(&app);
                }
                let _ = stream.write_all(MANAGER_ACK.as_bytes());
                let _ = stream.flush();
            }
        }
    });
}

fn payload_root() -> Option<PathBuf> {
    let mut candidates = Vec::new();
    if let Ok(path) = std::env::var("AI_OS_SETUP_RESOURCE_DIR") {
        candidates.push(PathBuf::from(path));
    }
    if let Some(path) = RESOURCE_DIR.get() {
        candidates.push(path.clone());
        candidates.push(path.join("resources"));
    }
    #[cfg(not(windows))]
    if let Some(appdir) = std::env::var_os("APPDIR").map(PathBuf::from) {
        candidates.push(appdir.join("usr/lib/AI OS/resources"));
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            candidates.push(parent.join("resources"));
            candidates.push(parent.to_path_buf());
            #[cfg(not(windows))]
            if let Some(prefix) = parent.parent() {
                candidates.push(prefix.join("lib/AI OS/resources"));
            }
        }
    }
    candidates
        .into_iter()
        .find(|path| path.join("PAYLOAD_MANIFEST.json").is_file())
}

fn payload_manifest(root: &Path) -> Result<serde_json::Value, String> {
    let text = fs::read_to_string(root.join("PAYLOAD_MANIFEST.json"))
        .map_err(|e| format!("Не удалось прочитать состав установщика: {e}"))?;
    serde_json::from_str(text.trim_start_matches('\u{feff}'))
        .map_err(|e| format!("Повреждён список файлов установщика: {e}"))
}

fn manifest_string(value: &serde_json::Value, path: &[&str]) -> String {
    let mut current = value;
    for part in path {
        let Some(next) = current.get(*part) else {
            return String::new();
        };
        current = next;
    }
    current.as_str().unwrap_or_default().to_string()
}

fn manifest_number(value: &serde_json::Value, path: &[&str]) -> String {
    let mut current = value;
    for part in path {
        let Some(next) = current.get(*part) else {
            return String::new();
        };
        current = next;
    }
    current
        .as_u64()
        .map(|number| number.to_string())
        .unwrap_or_default()
}

fn valid_sha256(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

fn safe_package_name(value: &str) -> bool {
    !value.is_empty()
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b'-'))
}

fn validate_package_metadata(
    manifest: &serde_json::Value,
    key: &str,
    require_download: bool,
) -> Result<(), String> {
    let version = manifest_string(manifest, &[key, "version"]);
    let binary_sha = manifest_string(manifest, &[key, "sha256"]);
    let binary_size = manifest
        .get(key)
        .and_then(|package| package.get("binarySizeBytes"))
        .and_then(serde_json::Value::as_u64)
        .unwrap_or_default();
    if !safe_package_name(&version) || !valid_sha256(&binary_sha) || binary_size == 0 {
        return Err(format!("Некорректные проверочные данные пакета: {key}"));
    }
    if !require_download {
        return Ok(());
    }

    let download_url = manifest_string(manifest, &[key, "downloadUrl"]);
    let archive_name = manifest_string(manifest, &[key, "archiveName"]);
    let archive_sha = manifest_string(manifest, &[key, "archiveSha256"]);
    let archive_size = manifest
        .get(key)
        .and_then(|package| package.get("archiveSizeBytes"))
        .and_then(serde_json::Value::as_u64)
        .unwrap_or_default();
    if !download_url.starts_with("https://")
        || !safe_package_name(&archive_name)
        || !archive_name.ends_with(".zip")
        || !valid_sha256(&archive_sha)
        || archive_size == 0
    {
        return Err(format!("Некорректные проверочные данные пакета: {key}"));
    }
    Ok(())
}

fn validate_payload(root: &Path) -> Result<serde_json::Value, String> {
    let mut required = vec![
        "PAYLOAD_MANIFEST.json",
        "install_ai_os_workspace.ps1",
        "ai_os_package_cache.psm1",
        "ai_os_supervisor.ps1",
        "workspace-template/AGENTS.md",
    ];
    #[cfg(windows)]
    required.push("install_ai_os_supervisor_task.ps1");
    #[cfg(not(windows))]
    required.extend(["install_ai_os_supervisor_linux.ps1", "powershell/pwsh"]);
    for required in required {
        if !root.join(required).is_file() {
            return Err(format!("В установщике не хватает файла: {required}"));
        }
    }

    let manifest = payload_manifest(root)?;
    let mode = manifest_string(&manifest, &["distributionMode"]);
    match mode.as_str() {
        "online" => {
            validate_package_metadata(&manifest, "memoryTool", true)?;
            validate_package_metadata(&manifest, "codeIntelligence", true)?;
            #[cfg(windows)]
            {
                validate_package_metadata(&manifest, "memoryQdrant", true)?;
                validate_package_metadata(&manifest, "memoryOnnxRuntime", true)?;
            }
        }
        "offline" => {
            validate_package_metadata(&manifest, "memoryTool", false)?;
            validate_package_metadata(&manifest, "codeIntelligence", false)?;
            let mut bundled = vec![
                PathBuf::from("memory-tool").join(MEMORY_BINARY_NAME),
                PathBuf::from("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
            ];
            #[cfg(windows)]
            {
                validate_package_metadata(&manifest, "memoryQdrant", false)?;
                validate_package_metadata(&manifest, "memoryOnnxRuntime", false)?;
                bundled.extend([
                    PathBuf::from("memory-runtime").join(QDRANT_BINARY_NAME),
                    PathBuf::from("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
                ]);
            }
            for path in bundled {
                if !root.join(&path).is_file() {
                    return Err(format!(
                        "В Offline Kit не хватает файла: {}",
                        path.display()
                    ));
                }
            }
        }
        _ => return Err("Неизвестный режим поставки AI OS".into()),
    }
    Ok(manifest)
}

fn cleanup_stale_online_binaries(root: &Path, manifest: &serde_json::Value) -> Vec<String> {
    if manifest_string(manifest, &["distributionMode"]) != "online" {
        return Vec::new();
    }

    let mut stale = vec![
        PathBuf::from("memory-tool").join(MEMORY_BINARY_NAME),
        PathBuf::from("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
    ];
    #[cfg(windows)]
    stale.extend([
        PathBuf::from("memory-runtime").join(QDRANT_BINARY_NAME),
        PathBuf::from("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
    ]);
    stale
        .into_iter()
        .filter_map(|relative| {
            let path = root.join(&relative);
            if !path.is_file() {
                return None;
            }
            fs::remove_file(&path)
                .err()
                .map(|error| format!("{}: {error}", relative.display()))
        })
        .collect()
}

fn decode_form(body: &[u8], key: &str) -> Option<String> {
    let text = std::str::from_utf8(body).ok()?;
    text.split('&').find_map(|pair| {
        let mut split = pair.splitn(2, '=');
        let raw_key = split.next()?.replace('+', " ");
        let raw_value = split.next().unwrap_or("").replace('+', " ");
        let decoded_key = urlencoding::decode(&raw_key).ok()?;
        if decoded_key == key {
            Some(
                urlencoding::decode(&raw_value)
                    .ok()
                    .map(|v| v.into_owned())
                    .unwrap_or_default(),
            )
        } else {
            None
        }
    })
}

fn normalize_path_input(value: &str) -> String {
    let trimmed = value.trim();
    if trimmed.len() >= 2 && trimmed.starts_with('"') && trimmed.ends_with('"') {
        trimmed[1..trimmed.len() - 1].trim().to_string()
    } else {
        trimmed.to_string()
    }
}

fn form_from_body(body: &[u8]) -> InstallForm {
    InstallForm {
        project_name: decode_form(body, "project_name").unwrap_or_default(),
        user_name: decode_form(body, "user_name").unwrap_or_default(),
        client_name: decode_form(body, "client_name").unwrap_or_else(|| "n/a".into()),
        company_name: decode_form(body, "company_name").unwrap_or_else(|| "n/a".into()),
        code_repo_path: decode_form(body, "code_repo_path")
            .map(|value| normalize_path_input(&value))
            .unwrap_or_else(|| "none yet".into()),
        destination: decode_form(body, "destination")
            .map(|value| normalize_path_input(&value))
            .unwrap_or_default(),
        summary: decode_form(body, "summary").unwrap_or_default(),
        memory: decode_form(body, "memory").is_some(),
        code_intel: decode_form(body, "code_intel").is_some(),
        automation: decode_form(body, "automation").is_some(),
        git: decode_form(body, "git").is_some(),
    }
}

fn default_projects_directory() -> PathBuf {
    #[cfg(windows)]
    let home = std::env::var_os("USERPROFILE")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("C:\\Users\\Public"));
    #[cfg(not(windows))]
    let home = std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(std::env::temp_dir);
    home.join("Documents").join("AI OS")
}

fn destination_is_available(path: &Path) -> bool {
    match fs::metadata(path) {
        Ok(metadata) if !metadata.is_dir() => false,
        Ok(_) => fs::read_dir(path)
            .map(|mut entries| entries.next().is_none())
            .unwrap_or(false),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => true,
        Err(_) => false,
    }
}

fn suggested_destination_in(base: &Path, registry: &WorkspaceRegistry) -> PathBuf {
    for number in 1_u32.. {
        let name = if number == 1 {
            "Мой проект".to_string()
        } else {
            format!("Мой проект {number}")
        };
        let candidate = base.join(name);
        let registered = registry.get(&workspace_id(&candidate)).is_some();
        if !registered && destination_is_available(&candidate) {
            return candidate;
        }
    }
    unreachable!("u32 project suffix space exhausted")
}

fn default_destination(registry: &WorkspaceRegistry) -> String {
    suggested_destination_in(&default_projects_directory(), registry)
        .to_string_lossy()
        .into_owned()
}

#[cfg(windows)]
fn available_space(path: &Path) -> Option<u64> {
    use windows_sys::Win32::Storage::FileSystem::GetDiskFreeSpaceExW;

    let existing = path.ancestors().find(|candidate| candidate.exists())?;
    let wide: Vec<u16> = existing
        .as_os_str()
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();
    let mut free = 0u64;
    let result = unsafe {
        GetDiskFreeSpaceExW(
            wide.as_ptr(),
            &mut free,
            std::ptr::null_mut(),
            std::ptr::null_mut(),
        )
    };
    (result != 0).then_some(free)
}

#[cfg(not(windows))]
fn available_space(path: &Path) -> Option<u64> {
    let existing = path.ancestors().find(|candidate| candidate.exists())?;
    let c_path = std::ffi::CString::new(existing.as_os_str().as_bytes()).ok()?;
    let mut stats = std::mem::MaybeUninit::<libc::statvfs>::uninit();
    let result = unsafe { libc::statvfs(c_path.as_ptr(), stats.as_mut_ptr()) };
    if result != 0 {
        return None;
    }
    let stats = unsafe { stats.assume_init() };
    Some((stats.f_bavail as u64).saturating_mul(stats.f_frsize as u64))
}

fn command_available(name: &str) -> bool {
    #[cfg(windows)]
    {
        let mut command = Command::new("where.exe");
        command
            .arg(name)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .creation_flags(CREATE_NO_WINDOW);
        command
            .status()
            .map(|status| status.success())
            .unwrap_or(false)
    }
    #[cfg(not(windows))]
    {
        if name.contains('/') {
            return Path::new(name)
                .metadata()
                .map(|meta| meta.is_file() && meta.permissions().mode() & 0o111 != 0)
                .unwrap_or(false);
        }
        std::env::var_os("PATH")
            .map(|paths| {
                std::env::split_paths(&paths).any(|dir| {
                    dir.join(name)
                        .metadata()
                        .map(|meta| meta.is_file() && meta.permissions().mode() & 0o111 != 0)
                        .unwrap_or(false)
                })
            })
            .unwrap_or(false)
    }
}

fn obsidian_available() -> bool {
    #[cfg(windows)]
    {
        let local = std::env::var_os("LOCALAPPDATA").map(PathBuf::from);
        local.as_ref().is_some_and(|root| {
            root.join("Programs/Obsidian/Obsidian.exe").is_file()
                || root.join("Obsidian/Obsidian.exe").is_file()
        }) || command_available("Obsidian.exe")
    }
    #[cfg(not(windows))]
    {
        command_available("obsidian")
            || Path::new("/var/lib/flatpak/exports/bin/md.obsidian.Obsidian").is_file()
            || std::env::var_os("HOME")
                .map(PathBuf::from)
                .is_some_and(|home| {
                    home.join(".local/share/flatpak/exports/bin/md.obsidian.Obsidian")
                        .is_file()
                })
    }
}

fn environment_row(label: &str, state: &str, detail: &str, class: &str) -> String {
    format!(
        r#"<div class="environment-row {}"><i aria-hidden="true"></i><div><b>{}</b><span>{}</span></div><strong>{}</strong></div>"#,
        class,
        esc(label),
        esc(detail),
        esc(state)
    )
}

fn environment_html() -> String {
    #[cfg(windows)]
    let foundation = command_available("powershell.exe");
    #[cfg(not(windows))]
    let foundation = true;
    #[cfg(windows)]
    let git = command_available("git.exe");
    #[cfg(not(windows))]
    let git = command_available("git");
    let obsidian = obsidian_available();
    #[cfg(windows)]
    let cli_names = ["claude.exe", "codex.exe"];
    #[cfg(not(windows))]
    let cli_names = ["claude", "codex"];
    let cli = cli_names.iter().any(|name| command_available(name));
    #[cfg(windows)]
    let node = command_available("node.exe") && command_available("npm.cmd");
    #[cfg(not(windows))]
    let node = command_available("node") && command_available("npm");
    let mut rows = String::new();
    rows.push_str(&environment_row(
        if cfg!(windows) {
            "Основа Windows"
        } else {
            "Основа Linux"
        },
        if foundation {
            "Готово"
        } else {
            "Нужна проверка"
        },
        if cfg!(windows) {
            "WebView2 и PowerShell runtime включены в Setup."
        } else {
            "Графическая оболочка и PowerShell runtime включены в Linux-пакет."
        },
        if foundation { "ready" } else { "blocked" },
    ));
    rows.push_str(&environment_row(
        "Obsidian",
        if obsidian {
            "Найден"
        } else {
            "Необязательно"
        },
        if obsidian {
            "Заметки будут открываться как Obsidian vault."
        } else {
            "Среда работает без него; заметки откроются обычным редактором."
        },
        if obsidian { "ready" } else { "optional" },
    ));
    rows.push_str(&environment_row(
        "История Git",
        if git {
            "Найден"
        } else {
            "Подключается позже"
        },
        if git {
            "Первый локальный снимок будет создан автоматически."
        } else {
            "Проект установится, но история изменений пока будет выключена."
        },
        if git { "ready" } else { "optional" },
    ));
    rows.push_str(&environment_row(
        "ИИ-консоль",
        if cli {
            "Найдена"
        } else if node {
            "Можно установить"
        } else {
            "Подключается позже"
        },
        if cli {
            "Консоль готова для работы с проектом после входа в аккаунт."
        } else if node {
            "Claude Code или Codex можно установить отдельно после настройки среды."
        } else {
            "Позже установите выбранное ИИ-приложение или его консоль."
        },
        if cli { "ready" } else { "optional" },
    ));
    format!(
        r#"<section class="band environment-section"><div class="section-heading"><div><p class="eyebrow">Этот компьютер</p><h2>Что уже готово</h2></div><span class="step-number">00</span></div><div class="environment-list">{}</div><p class="environment-note">Rust, Python и ручная установка MCP не нужны. Интернет понадобится только для первой загрузки модели памяти и входа в выбранный ИИ-сервис. Если сети нет, проект всё равно создастся, а незавершённые компоненты можно восстановить позже.</p></section>"#,
        rows
    )
}

fn validate_form(form: &InstallForm, registry: &WorkspaceRegistry) -> Result<PathBuf, String> {
    if form.project_name.trim().len() < 2 {
        return Err("Укажите название проекта — минимум два символа.".into());
    }
    if form.user_name.trim().len() < 2 {
        return Err("Укажите имя человека, который будет работать с системой.".into());
    }
    if form.summary.trim().len() < 10 {
        return Err("Кратко опишите проект — минимум десять символов.".into());
    }
    let destination = PathBuf::from(normalize_path_input(&form.destination));
    if !destination.is_absolute() {
        return Err(if cfg!(windows) {
            "Укажите полный путь к рабочей папке Windows.".into()
        } else {
            "Укажите абсолютный путь к рабочей папке Linux.".into()
        });
    }
    if registry.get(&workspace_id(&destination)).is_some() {
        return Err(
            "Эта папка уже добавлена как проект. Откройте её в списке проектов или нажмите «Восстановить»."
                .into(),
        );
    }
    if destination.exists() {
        if !destination.is_dir() {
            return Err("Путь к рабочей среде указывает на файл. Выберите новую папку.".into());
        }
        let has_files = fs::read_dir(&destination)
            .map_err(|error| format!("Не удалось проверить рабочую папку: {error}"))?
            .next()
            .is_some();
        if has_files {
            let suggestion = destination.join("AI OS");
            return Err(format!(
                "Папка «{}» уже содержит файлы. AI OS не смешивает свои заметки с существующим проектом. Укажите новую или пустую папку, например «{}», а путь к коду оставьте в поле «Репозиторий кода».",
                destination.display(),
                suggestion.display()
            ));
        }
    }
    if available_space(&destination).is_some_and(|bytes| bytes < MIN_FREE_SPACE_BYTES) {
        return Err(
            "На выбранном диске меньше 2 ГБ свободного места. Освободите место или выберите другую папку."
                .into(),
        );
    }
    Ok(destination)
}

fn read_install_project_name(root: &Path) -> String {
    let path = root.join(".local").join("install-state.json");
    fs::read_to_string(path)
        .ok()
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok())
        .and_then(|value| value.get("projectName")?.as_str().map(str::to_owned))
        .unwrap_or_else(|| "Рабочая среда AI OS".into())
}

#[cfg(windows)]
fn setup_powershell(_payload: &Path) -> PathBuf {
    PathBuf::from("powershell.exe")
}

#[cfg(not(windows))]
fn setup_powershell(payload: &Path) -> PathBuf {
    payload.join("powershell").join("pwsh")
}

#[cfg(windows)]
fn child_process_path(path: &Path) -> String {
    let value = path.to_string_lossy();
    if let Some(rest) = value.strip_prefix(r"\\?\UNC\") {
        format!(r"\\{rest}")
    } else if let Some(rest) = value.strip_prefix(r"\\?\") {
        rest.to_string()
    } else {
        value.into_owned()
    }
}

#[cfg(not(windows))]
fn child_process_path(path: &Path) -> String {
    path.to_string_lossy().into_owned()
}

fn setup_launcher_path() -> String {
    let path = std::env::var_os("APPIMAGE")
        .map(PathBuf::from)
        .or_else(|| std::env::current_exe().ok())
        .unwrap_or_default();
    child_process_path(&path)
}

fn build_setup_args(
    payload: &Path,
    destination: &Path,
    form: Option<&InstallForm>,
    repair: bool,
    remove_automation: bool,
    automation_enabled: bool,
) -> Result<Vec<String>, String> {
    let script = payload.join("install_ai_os_workspace.ps1");
    let source = payload.join("workspace-template");
    let manifest = payload_manifest(payload)?;
    let memory = payload.join("memory-tool").join(MEMORY_BINARY_NAME);
    let code_intel = payload.join("code-intel-tool").join(CODE_INTEL_BINARY_NAME);
    #[cfg(windows)]
    let qdrant = payload.join("memory-runtime").join(QDRANT_BINARY_NAME);
    #[cfg(windows)]
    let onnx_runtime = payload
        .join("memory-runtime")
        .join(ONNX_RUNTIME_BINARY_NAME);

    let mut args = vec!["-NoProfile".into()];
    #[cfg(windows)]
    args.extend(["-ExecutionPolicy".into(), "RemoteSigned".into()]);
    args.extend([
        "-File".into(),
        child_process_path(&script),
        "-DestinationRoot".into(),
        child_process_path(destination),
        "-SetupExecutablePath".into(),
        setup_launcher_path(),
    ]);
    #[cfg(not(windows))]
    args.extend([
        "-PowerShellRuntimeSource".into(),
        child_process_path(&payload.join("powershell")),
    ]);
    if remove_automation {
        args.push("-RemoveAutomation".into());
        return Ok(args);
    }

    args.extend([
        "-SourceRoot".into(),
        child_process_path(&source),
        "-MemoryToolSource".into(),
        child_process_path(&memory),
        "-MemoryToolSha256".into(),
        manifest_string(&manifest, &["memoryTool", "sha256"]),
        "-MemoryToolVersion".into(),
        manifest_string(&manifest, &["memoryTool", "version"]),
        "-MemoryToolDownloadUrl".into(),
        manifest_string(&manifest, &["memoryTool", "downloadUrl"]),
        "-MemoryToolArchiveName".into(),
        manifest_string(&manifest, &["memoryTool", "archiveName"]),
        "-MemoryToolArchiveSha256".into(),
        manifest_string(&manifest, &["memoryTool", "archiveSha256"]),
        "-MemoryToolArchiveSizeBytes".into(),
        manifest_number(&manifest, &["memoryTool", "archiveSizeBytes"]),
        "-MemoryToolBinarySizeBytes".into(),
        manifest_number(&manifest, &["memoryTool", "binarySizeBytes"]),
        "-CodeIntelToolSource".into(),
        child_process_path(&code_intel),
        "-CodeIntelToolSha256".into(),
        manifest_string(&manifest, &["codeIntelligence", "sha256"]),
        "-CodeIntelToolVersion".into(),
        manifest_string(&manifest, &["codeIntelligence", "version"]),
        "-CodeIntelToolDownloadUrl".into(),
        manifest_string(&manifest, &["codeIntelligence", "downloadUrl"]),
        "-CodeIntelToolArchiveName".into(),
        manifest_string(&manifest, &["codeIntelligence", "archiveName"]),
        "-CodeIntelToolArchiveSha256".into(),
        manifest_string(&manifest, &["codeIntelligence", "archiveSha256"]),
        "-CodeIntelToolArchiveSizeBytes".into(),
        manifest_number(&manifest, &["codeIntelligence", "archiveSizeBytes"]),
        "-CodeIntelToolBinarySizeBytes".into(),
        manifest_number(&manifest, &["codeIntelligence", "binarySizeBytes"]),
        "-MemoryLibraryName".into(),
        memory_library_name(destination),
    ]);
    #[cfg(windows)]
    args.extend([
        "-MemoryQdrantSource".into(),
        child_process_path(&qdrant),
        "-MemoryQdrantSha256".into(),
        manifest_string(&manifest, &["memoryQdrant", "sha256"]),
        "-MemoryQdrantVersion".into(),
        manifest_string(&manifest, &["memoryQdrant", "version"]),
        "-MemoryQdrantDownloadUrl".into(),
        manifest_string(&manifest, &["memoryQdrant", "downloadUrl"]),
        "-MemoryQdrantArchiveName".into(),
        manifest_string(&manifest, &["memoryQdrant", "archiveName"]),
        "-MemoryQdrantArchiveSha256".into(),
        manifest_string(&manifest, &["memoryQdrant", "archiveSha256"]),
        "-MemoryQdrantArchiveSizeBytes".into(),
        manifest_number(&manifest, &["memoryQdrant", "archiveSizeBytes"]),
        "-MemoryQdrantBinarySizeBytes".into(),
        manifest_number(&manifest, &["memoryQdrant", "binarySizeBytes"]),
        "-MemoryOnnxSource".into(),
        child_process_path(&onnx_runtime),
        "-MemoryOnnxSha256".into(),
        manifest_string(&manifest, &["memoryOnnxRuntime", "sha256"]),
        "-MemoryOnnxVersion".into(),
        manifest_string(&manifest, &["memoryOnnxRuntime", "version"]),
        "-MemoryOnnxDownloadUrl".into(),
        manifest_string(&manifest, &["memoryOnnxRuntime", "downloadUrl"]),
        "-MemoryOnnxArchiveName".into(),
        manifest_string(&manifest, &["memoryOnnxRuntime", "archiveName"]),
        "-MemoryOnnxArchiveSha256".into(),
        manifest_string(&manifest, &["memoryOnnxRuntime", "archiveSha256"]),
        "-MemoryOnnxArchiveSizeBytes".into(),
        manifest_number(&manifest, &["memoryOnnxRuntime", "archiveSizeBytes"]),
        "-MemoryOnnxBinarySizeBytes".into(),
        manifest_number(&manifest, &["memoryOnnxRuntime", "binarySizeBytes"]),
    ]);

    if repair {
        args.push("-Repair".into());
        if automation_enabled {
            args.push("-SharedSupervisor".into());
        } else {
            args.push("-SkipScheduledTasks".into());
        }
        return Ok(args);
    }

    let form = form.ok_or("Не найдены данные формы установки")?;
    args.extend([
        "-ProjectName".into(),
        form.project_name.trim().into(),
        "-UserName".into(),
        form.user_name.trim().into(),
        "-ClientName".into(),
        if form.client_name.trim().is_empty() {
            "n/a".into()
        } else {
            form.client_name.trim().into()
        },
        "-CompanyName".into(),
        if form.company_name.trim().is_empty() {
            "n/a".into()
        } else {
            form.company_name.trim().into()
        },
        "-CodeRepoPath".into(),
        if normalize_path_input(&form.code_repo_path).is_empty() {
            "none yet".into()
        } else {
            normalize_path_input(&form.code_repo_path)
        },
        "-ProjectSummary".into(),
        form.summary.trim().into(),
    ]);
    if !form.memory {
        args.push("-SkipMemory".into());
    }
    if !form.code_intel {
        args.push("-SkipCodeIntelligence".into());
    }
    if form.automation {
        args.push("-SharedSupervisor".into());
    } else {
        args.push("-SkipScheduledTasks".into());
    }
    if !form.git {
        args.push("-SkipGit".into());
    }
    Ok(args)
}

fn start_job(
    destination: PathBuf,
    form: Option<&InstallForm>,
    repair: bool,
    remove_automation: bool,
    selected: Option<&WorkspaceRecord>,
) -> Result<(), String> {
    let payload = payload_root().ok_or("Не найдены файлы установщика. Переустановите AI OS.")?;
    validate_payload(&payload)?;

    let mut slot = JOB
        .lock()
        .map_err(|_| "Не удалось получить состояние установки")?;
    if let Some(job) = slot.as_mut() {
        if job.child.try_wait().map_err(|e| e.to_string())?.is_none() {
            return Err("Другая установка или восстановление ещё выполняется.".into());
        }
    }

    fs::create_dir_all(state_dir()).map_err(|e| e.to_string())?;
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    let log_path = state_dir().join(format!("setup-{stamp}.log"));
    let stdout = File::create(&log_path).map_err(|e| e.to_string())?;
    let stderr = stdout.try_clone().map_err(|e| e.to_string())?;
    let id = selected
        .map(|workspace| workspace.id.clone())
        .unwrap_or_else(|| workspace_id(&destination));
    let project_name = form
        .map(|value| value.project_name.trim().to_string())
        .or_else(|| selected.map(|workspace| workspace.project_name.clone()))
        .unwrap_or_else(|| read_install_project_name(&destination));
    let automation_enabled = form
        .map(|value| value.automation)
        .or_else(|| selected.map(|workspace| workspace.automation_enabled))
        .unwrap_or(false);
    let args = build_setup_args(
        &payload,
        &destination,
        form,
        repair,
        remove_automation,
        automation_enabled,
    )?;

    let powershell = setup_powershell(&payload);
    if !powershell.is_file() && !cfg!(windows) {
        return Err(format!(
            "В Linux-пакете не найден PowerShell runtime: {}",
            powershell.display()
        ));
    }
    let mut command = Command::new(&powershell);
    command
        .args(&args)
        .current_dir(&payload)
        .stdin(Stdio::null())
        .stdout(Stdio::from(stdout))
        .stderr(Stdio::from(stderr));
    #[cfg(windows)]
    command.creation_flags(CREATE_NO_WINDOW);
    let child = command
        .spawn()
        .map_err(|e| format!("Не удалось запустить установку: {e}"))?;
    *slot = Some(SetupJob {
        child,
        destination,
        workspace_id: id,
        project_name,
        automation_enabled,
        log_path,
        mode: if remove_automation {
            "remove automation".into()
        } else if repair {
            "repair".into()
        } else {
            "install".into()
        },
    });
    Ok(())
}

#[cfg(windows)]
fn decode_native_log(bytes: &[u8]) -> Option<String> {
    use windows_sys::Win32::Globalization::MultiByteToWideChar;

    const CP_OEMCP: u32 = 1;
    if bytes.is_empty() {
        return Some(String::new());
    }
    let byte_count = bytes.len().try_into().ok()?;
    let length = unsafe {
        MultiByteToWideChar(
            CP_OEMCP,
            0,
            bytes.as_ptr(),
            byte_count,
            std::ptr::null_mut(),
            0,
        )
    };
    if length <= 0 {
        return None;
    }
    let mut wide = vec![0u16; length as usize];
    let written = unsafe {
        MultiByteToWideChar(
            CP_OEMCP,
            0,
            bytes.as_ptr(),
            byte_count,
            wide.as_mut_ptr(),
            length,
        )
    };
    (written > 0).then(|| String::from_utf16_lossy(&wide[..written as usize]))
}

#[cfg(not(windows))]
fn decode_native_log(_bytes: &[u8]) -> Option<String> {
    None
}

fn tail_log(path: &Path, max_lines: usize) -> String {
    let mut bytes = Vec::new();
    if File::open(path)
        .and_then(|mut file| file.read_to_end(&mut bytes))
        .is_err()
    {
        return "Ожидание первого сообщения установщика...".into();
    }
    let text = String::from_utf8(bytes.clone())
        .ok()
        .or_else(|| decode_native_log(&bytes))
        .unwrap_or_else(|| String::from_utf8_lossy(&bytes).into_owned());
    let lines: Vec<&str> = text
        .lines()
        .filter(|line| {
            !line
                .trim_start()
                .starts_with("warning: in the working copy of ")
        })
        .collect();
    lines[lines.len().saturating_sub(max_lines)..].join("\n")
}

fn install_failure_detail(log: &str, exit_code: i32) -> String {
    let lower = log.to_lowercase();
    if lower.contains("not digitally signed")
        || lower.contains("не имеет цифровой подписи")
        || lower.contains("execution_policies")
    {
        return "Windows заблокировала встроенный установочный скрипт. Переустановите AI OS свежим установщиком: он передаёт локальный путь в совместимом с RemoteSigned виде.".into();
    }
    if lower.contains("destination is not empty") {
        return "Выбранная рабочая папка уже содержит файлы. Вернитесь и укажите новую или пустую папку; существующий проект подключается отдельным полем «Репозиторий кода».".into();
    }
    format!(
        "Установка остановилась с кодом {exit_code}. Журнал с точной причиной открыт ниже; ваши существующие файлы не удалялись."
    )
}

fn component_view(key: &str, state: &str) -> (&'static str, &'static str, &'static str) {
    match (key, state) {
        ("workspace", "installed") => (
            "Готово",
            "Файлы проекта созданы в отдельной папке.",
            "ready",
        ),
        ("workspace", "preserved") => (
            "Сохранено",
            "Пользовательские заметки не перезаписаны.",
            "ready",
        ),
        ("skills", "installed") => (
            "Готово",
            "Скиллы подключены для поддерживаемых агентов.",
            "ready",
        ),
        ("memory", "installed") => ("Готово", "Локальный смысловой поиск подключён.", "ready"),
        ("memory", "pending") => (
            "Нужно закончить",
            "Подключите интернет и запустите восстановление.",
            "warn",
        ),
        ("codeIntelligence", "installed-not-indexed") => (
            "Готово",
            "Карта кода ждёт явного выбора репозитория.",
            "ready",
        ),
        ("git", "initialized-and-committed") => {
            ("Готово", "Создан первый локальный снимок проекта.", "ready")
        }
        ("git", "initialized") => (
            "Почти готово",
            "Git включён; первый коммит можно сделать после настройки имени и email.",
            "warn",
        ),
        ("git", "pending") => (
            "Не найден",
            "Проект работает, но локальной истории пока нет.",
            "warn",
        ),
        ("automation", "shared-supervisor") => (
            "Готово",
            "Одна фоновая служба обслуживает все проекты.",
            "ready",
        ),
        ("automation", "installed") => ("Готово", "Фоновые проверки включены.", "ready"),
        ("automation", "pending") => (
            "Нужно закончить",
            "Операционная система не разрешила включить фоновые проверки.",
            "warn",
        ),
        ("readiness", "passed") => (
            "Пройдено",
            "Финальная проверка не нашла блокирующих ошибок.",
            "ready",
        ),
        (_, "skipped-by-user") => (
            "Пропущено",
            "Компонент можно подключить позже через восстановление.",
            "optional",
        ),
        (_, "missing") => (
            "Не найдено",
            "Нужна ручная проверка комплекта установки.",
            "bad",
        ),
        (_, "failed") => ("Ошибка", "Компонент не прошёл финальную проверку.", "bad"),
        (_, "pending") => (
            "Нужно закончить",
            "Компонент можно завершить через восстановление.",
            "warn",
        ),
        _ => ("Готово", "Компонент настроен.", "ready"),
    }
}

fn install_report_html(root: &Path) -> String {
    let state_path = root.join(".local").join("install-state.json");
    let Ok(text) = fs::read_to_string(state_path) else {
        return String::new();
    };
    let Ok(state) = serde_json::from_str::<serde_json::Value>(&text) else {
        return String::new();
    };
    let components = state
        .get("components")
        .and_then(serde_json::Value::as_object);
    let definitions = [
        ("workspace", "Рабочая папка"),
        ("skills", "Скиллы агентов"),
        ("memory", "Память и поиск"),
        ("codeIntelligence", "Карта кода"),
        ("git", "История Git"),
        ("automation", "Фоновые проверки"),
        ("readiness", "Финальная поверка"),
    ];
    let mut rows = String::new();
    for (key, label) in definitions {
        let raw = components
            .and_then(|items| items.get(key))
            .and_then(serde_json::Value::as_str)
            .unwrap_or("missing");
        let (status, detail, class) = component_view(key, raw);
        rows.push_str(&format!(
            r#"<div class="report-row {}"><i aria-hidden="true"></i><div><b>{}</b><span>{}</span></div><strong>{}</strong></div>"#,
            class,
            esc(label),
            esc(detail),
            esc(status)
        ));
    }
    let warnings = state
        .get("warnings")
        .and_then(serde_json::Value::as_array)
        .map(|items| {
            items
                .iter()
                .filter_map(serde_json::Value::as_str)
                .map(|item| format!("<li>{}</li>", esc(item)))
                .collect::<String>()
        })
        .unwrap_or_default();
    let warning_block = if warnings.is_empty() {
        String::new()
    } else {
        format!(
            r#"<details class="report-warnings"><summary>Что можно закончить позже</summary><ul>{}</ul></details>"#,
            warnings
        )
    };
    format!(
        r#"<section class="band install-report"><div class="section-heading"><div><p class="eyebrow">Итог</p><h2>Состав рабочей среды</h2></div></div><div class="report-list">{}</div>{}</section>"#,
        rows, warning_block
    )
}

fn action_form(action: &str, label: &str, class_name: &str, workspace_id: &str) -> String {
    format!(
        r#"<form method="post" action="{}"><input type="hidden" name="workspace_id" value="{}"><button class="{}" type="submit">{}</button></form>"#,
        esc(action),
        esc(workspace_id),
        esc(class_name),
        esc(label)
    )
}

fn workspace_list_html(registry: &WorkspaceRegistry) -> String {
    if registry.workspaces.is_empty() {
        return String::new();
    }
    let mut workspaces: Vec<_> = registry.workspaces.iter().collect();
    workspaces.sort_by_key(|workspace| {
        (
            registry.active_workspace_id.as_deref() != Some(workspace.id.as_str()),
            workspace.project_name.to_lowercase(),
        )
    });

    let rows = workspaces
        .into_iter()
        .map(|workspace| {
            let root = PathBuf::from(&workspace.root);
            let available = root.join("AGENTS.md").is_file();
            let active = registry.active_workspace_id.as_deref() == Some(workspace.id.as_str());
            let mut actions = String::new();
            if available {
                actions.push_str(&action_form(
                    "/launch",
                    "Открыть AI OS",
                    "btn small",
                    &workspace.id,
                ));
                actions.push_str(&action_form(
                    "/open-folder",
                    "Открыть папку",
                    "btn secondary small",
                    &workspace.id,
                ));
                if active {
                    actions.push_str(
                        r#"<button class="btn secondary small" type="button" disabled>Уже активный</button>"#,
                    );
                } else {
                    actions.push_str(&action_form(
                        "/activate",
                        "Сделать активным",
                        "btn secondary small",
                        &workspace.id,
                    ));
                }
                actions.push_str(&action_form(
                    "/repair",
                    "Восстановить",
                    "btn secondary small",
                    &workspace.id,
                ));
                actions.push_str(&action_form(
                    if workspace.automation_enabled {
                        "/disable-automation"
                    } else {
                        "/enable-automation"
                    },
                    if workspace.automation_enabled {
                        "Отключить проверки"
                    } else {
                        "Включить проверки"
                    },
                    "btn secondary small",
                    &workspace.id,
                ));
            }
            actions.push_str(&action_form(
                "/forget",
                "Убрать из списка",
                "btn danger small",
                &workspace.id,
            ));
            let state = if active {
                "<span class=\"workspace-state\">Активная</span>"
            } else {
                ""
            };
            let automation = if workspace.automation_enabled {
                "Фоновые проверки включены"
            } else {
                "Фоновые проверки выключены"
            };
            let availability = if available {
                automation.to_string()
            } else {
                "Папка не найдена. Запись можно убрать из списка; данные не удаляются.".into()
            };
            format!(
                r#"<details class="workspace {} {}" {}><summary><span class="workspace-glyph" aria-hidden="true"></span><span class="workspace-head"><span><h3>{}</h3><span class="workspace-note">{}</span></span>{}</span><span class="workspace-chevron" aria-hidden="true"></span></summary><div class="workspace-body"><code class="path">{}</code><p class="workspace-tool-note">AI OS показывает состояние заметок, памяти и проверок. Если окно уже открыто, кнопка просто вернёт его на экран.</p><div class="actions">{}</div></div></details>"#,
                if active { "active" } else { "" },
                if available { "" } else { "missing" },
                if active { "open" } else { "" },
                esc(&workspace.project_name),
                esc(&availability),
                state,
                esc(&workspace.root),
                actions
            )
        })
        .collect::<String>();
    format!(
        r#"<section class="band workspace-section"><div class="section-heading"><div><p class="eyebrow">Проекты</p><h2>Ваши проекты</h2></div><span class="workspace-count">{}</span></div><p class="section-copy">У каждого проекта своя папка с заметками и памятью. Нажмите на проект, чтобы увидеть действия.</p><div class="workspace-list">{rows}</div></section>"#,
        registry.workspaces.len()
    )
}

fn setup_page_with_registry_and_form(
    error: Option<&str>,
    registry: &WorkspaceRegistry,
    submitted: Option<&InstallForm>,
) -> Vec<u8> {
    let existing = workspace_list_html(registry);
    let error = error
        .map(|message| {
            format!(
                r#"<div class="status bad"><b>Установка не запущена</b><p>{}</p></div>"#,
                esc(message)
            )
        })
        .unwrap_or_default();
    let first_workspace = registry.workspaces.is_empty();
    let (heading, intro, form_heading) = if first_workspace {
        (
            "Новый проект",
            "Укажите папку и выберите, что подключить.",
            "Параметры проекта",
        )
    } else {
        (
            "Проекты",
            "Откройте нужный проект или создайте новый.",
            "Новый проект",
        )
    };
    let form_start = if first_workspace {
        r#"<section class="create-project first"><div class="create-body">"#
    } else if submitted.is_some() {
        r#"<details class="create-project" open><summary><span class="summary-icon" aria-hidden="true"></span><span><b>Новый проект</b><small>Создать отдельную среду, память и проверки</small></span><span class="summary-arrow" aria-hidden="true"></span></summary><div class="create-body">"#
    } else {
        r#"<details class="create-project"><summary><span class="summary-icon" aria-hidden="true"></span><span><b>Новый проект</b><small>Создать отдельную среду, память и проверки</small></span><span class="summary-arrow" aria-hidden="true"></span></summary><div class="create-body">"#
    };
    let form_end = if first_workspace {
        "</div></section>"
    } else {
        "</div></details>"
    };
    let environment = environment_html();
    let project_name = esc(submitted
        .map(|form| form.project_name.as_str())
        .unwrap_or_default());
    let user_name = esc(submitted
        .map(|form| form.user_name.as_str())
        .unwrap_or_default());
    let summary = esc(submitted
        .map(|form| form.summary.as_str())
        .unwrap_or_default());
    let destination_value = submitted
        .map(|form| form.destination.trim())
        .filter(|value| !value.is_empty())
        .map(str::to_owned)
        .unwrap_or_else(|| default_destination(registry));
    let destination = esc(&destination_value);
    let client_name = esc(submitted
        .map(|form| form.client_name.as_str())
        .unwrap_or_default());
    let company_name = esc(submitted
        .map(|form| form.company_name.as_str())
        .unwrap_or_default());
    let code_repo_path = esc(submitted
        .map(|form| form.code_repo_path.as_str())
        .unwrap_or_default());
    let advanced_open = submitted
        .is_some_and(|form| {
            !form.client_name.trim().is_empty()
                || !form.company_name.trim().is_empty()
                || !form.code_repo_path.trim().is_empty()
        })
        .then_some(" open")
        .unwrap_or_default();
    let memory_checked = submitted
        .map(|form| form.memory)
        .unwrap_or(true)
        .then_some(" checked")
        .unwrap_or_default();
    let code_intel_checked = submitted
        .map(|form| form.code_intel)
        .unwrap_or(true)
        .then_some(" checked")
        .unwrap_or_default();
    let automation_checked = submitted
        .map(|form| form.automation)
        .unwrap_or(true)
        .then_some(" checked")
        .unwrap_or_default();
    let git_checked = submitted
        .map(|form| form.git)
        .unwrap_or(true)
        .then_some(" checked")
        .unwrap_or_default();
    let body = format!(
        r#"<span data-installer-entry hidden></span><div class="topline"><div><h1>{heading}</h1><p class="lead">{intro}</p></div></div>
        {existing}{error}
        {form_start}<form method="post" action="/install">
        {environment}
        <section class="band form-section"><div class="section-heading"><div><p class="eyebrow">Настройка</p><h2>{form_heading}</h2></div><span class="step-number">01</span></div><div class="grid2"><div><label for="project_name">Название проекта</label><input id="project_name" name="project_name" type="text" required maxlength="100" value="{project_name}" placeholder="Например, управленческий отчёт"></div><div><label for="user_name">Ваше имя</label><input id="user_name" name="user_name" type="text" required maxlength="100" value="{user_name}" placeholder="Как к вам обращаться"></div></div><div class="field-spacer"><label for="summary">Коротко о проекте</label><textarea id="summary" name="summary" required maxlength="1200" placeholder="Что вы создаёте и над чем работаете сейчас">{summary}</textarea></div></section>
        <section class="band form-section"><div class="section-heading"><div><p class="eyebrow">Папка</p><h2>Папка AI OS</h2></div><span class="step-number">02</span></div><div><label for="destination">Новая или пустая папка для заметок и памяти</label><input id="destination" name="destination" type="text" required value="{destination}"><p class="hint">Код сюда переносить не нужно. Для среды потребуется не менее 2 ГБ свободного места.</p></div><details class="advanced"{advanced_open}><summary>Существующий проект и другие данные</summary><div class="advanced-body grid2"><div><label for="client_name">Заказчик</label><input id="client_name" name="client_name" type="text" maxlength="120" value="{client_name}" placeholder="Необязательно"></div><div><label for="company_name">Компания</label><input id="company_name" name="company_name" type="text" maxlength="120" value="{company_name}" placeholder="Необязательно"></div><div class="wide-field"><label for="code_repo_path">Папка с кодом</label><input id="code_repo_path" name="code_repo_path" type="text" value="{code_repo_path}" placeholder="C:\Projects\my-app или пока не создан"><p class="hint">Можно указать уже существующий проект. Установщик не изменяет его файлы.</p></div></div></details></section>
        <section class="band form-section"><div class="section-heading"><div><p class="eyebrow">Компоненты</p><h2>Что подключить</h2></div><span class="step-number">03</span></div><div class="checks"><label class="check"><input type="checkbox" name="memory"{memory_checked}><span><b>Поиск по заметкам</b><span>Локальная память проекта.</span></span></label><label class="check"><input type="checkbox" name="code_intel"{code_intel_checked}><span><b>Карта кода</b><span>Включается только для выбранного репозитория.</span></span></label><label class="check"><input type="checkbox" name="automation"{automation_checked}><span><b>Фоновые проверки</b><span>Следят за памятью и состоянием системы.</span></span></label><label class="check"><input type="checkbox" name="git"{git_checked}><span><b>История изменений</b><span>Локальная защита от потери правок.</span></span></label></div></section>
        <div class="privacy-note"><span class="privacy-icon" aria-hidden="true"><svg class="privacy-icon-mark" viewBox="0 0 24 24" focusable="false"><path d="M20 13c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V5l8-3 8 3v8Z"></path><path d="m9 12 2 2 4-4"></path></svg></span><p><b>Данные остаются на компьютере.</b> Пароли и токены установщик не запрашивает. Вход в ИИ-сервисы подтверждаете только вы.</p></div>
        <div class="actions final-actions"><button class="btn primary" type="submit">Создать проект <span aria-hidden="true">→</span></button><span class="hint">Обычно 2–5 минут.</span></div></form>{form_end}"#
    );
    page(body)
}

fn setup_page_with_registry(error: Option<&str>, registry: &WorkspaceRegistry) -> Vec<u8> {
    setup_page_with_registry_and_form(error, registry, None)
}

fn setup_page_for_form(error: &str, form: &InstallForm) -> Vec<u8> {
    match load_registry() {
        Ok(registry) => setup_page_with_registry_and_form(Some(error), &registry, Some(form)),
        Err(registry_error) => setup_page_with_registry_and_form(
            Some(&format!(
                "{error} Дополнительно не удалось прочитать список проектов: {registry_error}"
            )),
            &WorkspaceRegistry::default(),
            Some(form),
        ),
    }
}

fn setup_page(error: Option<&str>) -> Vec<u8> {
    match load_registry() {
        Ok(registry) => {
            let _ = save_registry(&registry);
            setup_page_with_registry(error, &registry)
        }
        Err(registry_error) => setup_page_with_registry(
            Some(&format!(
                "Не удалось прочитать список проектов: {registry_error}"
            )),
            &WorkspaceRegistry::default(),
        ),
    }
}

fn running_progress_body(log: &str) -> String {
    format!(
        r#"<div class="topline"><div><h1>Создаём проект</h1><p class="lead">Недостающие компоненты загружаются один раз и сохраняются на компьютере.</p></div></div><div class="meter"><span></span></div><section class="installation-live"><div class="live-route"><div class="live-step active"><i></i><span><b>Файлы проекта</b><small>заметки, правила и скиллы</small></span></div><div class="live-step active"><i></i><span><b>Компоненты</b><small>проверка локального кэша и загрузка</small></span></div><div class="live-step active"><i></i><span><b>Проверка</b><small>первый запуск и фоновые задачи</small></span></div></div></section><details class="install-log"><summary>Журнал установки</summary><pre data-progress-log>{}</pre></details><p class="progress-error" data-progress-error hidden></p><script>(()=>{{const log=document.querySelector('[data-progress-log]');const error=document.querySelector('[data-progress-error]');let stopped=false;const poll=async()=>{{if(stopped)return;try{{const response=await fetch('/progress-status',{{cache:'no-store'}});const state=await response.json();if(log&&typeof state.log==='string')log.textContent=state.log;if(state.error&&error){{error.hidden=false;error.textContent=state.error;}}if(!state.running){{stopped=true;location.replace('/progress');return;}}}}catch(_){{if(error){{error.hidden=false;error.textContent='Не удалось обновить состояние. Повторяем попытку.';}}}}window.setTimeout(poll,1500);}};window.setTimeout(poll,500);}})();</script>"#,
        esc(log)
    )
}

fn progress_page() -> Vec<u8> {
    let mut slot = match JOB.lock() {
        Ok(value) => value,
        Err(_) => return setup_page(Some("Состояние установки недоступно.")),
    };
    let Some(job) = slot.as_mut() else {
        return setup_page(Some("Сейчас установка не выполняется."));
    };
    let log = tail_log(&job.log_path, 45);
    match job.child.try_wait() {
        Ok(None) => page(running_progress_body(&log)),
        Ok(Some(status)) => {
            let mut registry_error = None;
            let mut supervisor_warning = None;
            if status.success() {
                match load_registry() {
                    Ok(mut registry) => {
                        if job.mode == "remove automation" {
                            registry.set_automation(&job.workspace_id, false);
                        } else {
                            registry.upsert(
                                &job.destination,
                                &job.project_name,
                                job.automation_enabled,
                            );
                        }
                        match persist_registry_with_supervisor_warning(&registry) {
                            Ok(warning) => supervisor_warning = warning,
                            Err(error) => registry_error = Some(error),
                        }
                    }
                    Err(error) => registry_error = Some(error),
                }
            }
            let success = status.success() && registry_error.is_none();
            let title = if success {
                if job.mode == "remove automation" {
                    if supervisor_warning.is_some() {
                        "Автозапуск отключён с замечанием"
                    } else {
                        "Автозапуск отключён"
                    }
                } else if supervisor_warning.is_some() {
                    "Проект готов с замечанием"
                } else {
                    "Проект готов"
                }
            } else {
                "Нужна проверка"
            };
            let class = if !success {
                "status bad"
            } else if supervisor_warning.is_some() {
                "status warn"
            } else {
                "status"
            };
            let actions = if success && job.mode != "remove automation" {
                format!(
                    r#"<div class="actions">{}{}<a class="btn secondary" href="/">Вернуться</a></div>"#,
                    action_form("/launch", "Открыть AI OS", "btn", &job.workspace_id),
                    action_form(
                        "/open-folder",
                        "Открыть рабочую папку",
                        "btn secondary",
                        &job.workspace_id
                    )
                )
            } else {
                r#"<div class="actions"><a class="btn secondary" href="/">Вернуться</a></div>"#
                    .to_string()
            };
            let exit_code = status.code().unwrap_or(-1);
            let detail = registry_error
                .map(|error| format!("Проект создан, но не добавлен в список: {error}"))
                .unwrap_or_else(|| {
                    if let Some(error) = supervisor_warning.as_ref() {
                        format!("Проект создан и добавлен в список, но фоновую проверку не удалось настроить: {error}. Работать можно сейчас; восстановление можно запустить позже.")
                    } else if success {
                        "Проверка завершена. Вход в ИИ-сервисы и подключение репозитория остаются под вашим контролем.".into()
                    } else {
                        install_failure_detail(&log, exit_code)
                    }
                });
            let report = if success {
                install_report_html(&job.destination)
            } else {
                String::new()
            };
            let log_open = if success { "" } else { " open" };
            page(format!(
                r#"<div class="topline"><div><h1>{}</h1><p class="lead">Проверили рабочую папку и доступные компоненты.</p></div></div><div class="{}"><b>{}</b><p>{}</p></div>{}<details class="install-log"{}><summary>{} · код {}</summary><pre>{}</pre></details>{}"#,
                title,
                class,
                title,
                esc(&detail),
                report,
                log_open,
                if success {
                    "Технический журнал"
                } else {
                    "Что помешало установке"
                },
                exit_code,
                esc(&log),
                actions
            ))
        }
        Err(error) => setup_page(Some(&format!(
            "Не удалось получить статус установки: {error}"
        ))),
    }
}

fn progress_status() -> Vec<u8> {
    let mut slot = match JOB.lock() {
        Ok(value) => value,
        Err(_) => {
            return serde_json::json!({
                "running": false,
                "log": "",
                "error": "Состояние установки недоступно."
            })
            .to_string()
            .into_bytes()
        }
    };
    let Some(job) = slot.as_mut() else {
        return serde_json::json!({
            "running": false,
            "log": "",
            "error": "Установка уже завершена."
        })
        .to_string()
        .into_bytes();
    };
    let log = tail_log(&job.log_path, 45);
    match job.child.try_wait() {
        Ok(status) => serde_json::json!({
            "running": status.is_none(),
            "log": log,
            "exitCode": status.and_then(|value| value.code())
        })
        .to_string()
        .into_bytes(),
        Err(error) => serde_json::json!({
            "running": false,
            "log": log,
            "error": format!("Не удалось получить состояние установки: {error}")
        })
        .to_string()
        .into_bytes(),
    }
}

fn launch_control_center(root: &Path) -> Result<(), String> {
    let exe = root
        .join("tools")
        .join("control-center-app")
        .join("bin")
        .join(CONTROL_CENTER_BINARY_NAME);
    if !exe.is_file() {
        return Err(format!("Не найдено приложение AI OS: {}", exe.display()));
    }
    Command::new(exe)
        .current_dir(root)
        .env("AI_OS_ROOT", root)
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(())
}

fn open_folder(root: &Path) -> Result<(), String> {
    #[cfg(windows)]
    let opener = "explorer.exe";
    #[cfg(not(windows))]
    let opener = "xdg-open";
    Command::new(opener)
        .arg(root)
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(())
}

fn simple_message(title: &str, detail: &str, bad: bool) -> Vec<u8> {
    page(format!(
        r#"<div class="topline"><div><h1>{}</h1><p class="lead">{}</p></div></div><div class="{}"><b>{}</b><p>{}</p></div><div class="actions"><a class="btn secondary" href="/">Вернуться</a></div>"#,
        esc(title),
        esc(detail),
        if bad { "status bad" } else { "status" },
        esc(title),
        esc(detail)
    ))
}

fn selected_workspace(body: &[u8]) -> Result<(WorkspaceRegistry, WorkspaceRecord), String> {
    let id = decode_form(body, "workspace_id")
        .filter(|value| !value.trim().is_empty())
        .ok_or("Не указан проект.")?;
    let registry = load_registry()?;
    let workspace = registry
        .get(&id)
        .cloned()
        .ok_or("Проект не найден в списке.")?;
    Ok((registry, workspace))
}

fn persist_registry_and_supervisor(registry: &WorkspaceRegistry) -> Result<(), String> {
    save_registry(registry)?;
    let payload = payload_root().ok_or("Не найдены файлы установщика.")?;
    reconcile_supervisor(&payload, registry)
}

fn persist_registry_with_supervisor_warning(
    registry: &WorkspaceRegistry,
) -> Result<Option<String>, String> {
    save_registry(registry)?;
    let Some(payload) = payload_root() else {
        return Ok(Some("Не найдены файлы фоновой проверки".into()));
    };
    Ok(reconcile_supervisor(&payload, registry).err())
}

fn remove_legacy_automation(root: &Path) -> Result<(), String> {
    let payload = payload_root().ok_or("Не найдены файлы установщика.")?;
    let args = build_setup_args(&payload, root, None, false, true, false)?;
    let mut command = Command::new(setup_powershell(&payload));
    command.args(&args).current_dir(&payload);
    #[cfg(windows)]
    command.creation_flags(CREATE_NO_WINDOW);
    let output = command.output().map_err(|error| error.to_string())?;
    if output.status.success() {
        Ok(())
    } else {
        let detail = String::from_utf8_lossy(&output.stderr).trim().to_string();
        Err(if detail.is_empty() {
            "Не удалось убрать старые фоновые задачи проекта.".into()
        } else {
            detail
        })
    }
}

fn route(method: &str, path: &str, body: &[u8]) -> Vec<u8> {
    match (method, path) {
        ("GET", "/window/minimize") => {
            if let Some(window) = APP_HANDLE
                .get()
                .and_then(|app| app.get_webview_window("main"))
            {
                let _ = window.minimize();
            }
            Vec::new()
        }
        ("GET", "/window/maximize") => {
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
            Vec::new()
        }
        ("GET", "/window/drag") => {
            if let Some(window) = APP_HANDLE
                .get()
                .and_then(|app| app.get_webview_window("main"))
            {
                let _ = window.start_dragging();
            }
            Vec::new()
        }
        ("GET", "/window/close") => {
            if let Some(app) = APP_HANDLE.get() {
                app.exit(0);
            }
            Vec::new()
        }
        ("GET", "/") => setup_page(None),
        ("POST", "/install") => {
            if body.len() > 64 * 1024 {
                return setup_page(Some("Форма содержит слишком много данных."));
            }
            let form = form_from_body(body);
            let registry = match load_registry() {
                Ok(registry) => registry,
                Err(error) => {
                    let message = format!("Не удалось прочитать список проектов: {error}");
                    return setup_page_with_registry_and_form(
                        Some(&message),
                        &WorkspaceRegistry::default(),
                        Some(&form),
                    );
                }
            };
            let destination = match validate_form(&form, &registry) {
                Ok(path) => path,
                Err(error) => return setup_page_for_form(&error, &form),
            };
            match start_job(destination, Some(&form), false, false, None) {
                Ok(()) => progress_page(),
                Err(error) => setup_page_for_form(&error, &form),
            }
        }
        ("GET", "/progress") => progress_page(),
        ("GET", "/progress-status") => progress_status(),
        ("POST", "/repair") => {
            let (_, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            let root = PathBuf::from(&workspace.root);
            match start_job(root, None, true, false, Some(&workspace)) {
                Ok(()) => progress_page(),
                Err(error) => setup_page(Some(&error)),
            }
        }
        ("POST", "/disable-automation") => {
            let (_, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            let root = PathBuf::from(&workspace.root);
            match start_job(root, None, false, true, Some(&workspace)) {
                Ok(()) => progress_page(),
                Err(error) => setup_page(Some(&error)),
            }
        }
        ("POST", "/enable-automation") => {
            let (mut registry, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            registry.set_automation(&workspace.id, true);
            registry.set_active(&workspace.id);
            match persist_registry_and_supervisor(&registry) {
                Ok(()) => setup_page(None),
                Err(error) => setup_page(Some(&error)),
            }
        }
        ("POST", "/activate") => {
            let (mut registry, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            if !PathBuf::from(&workspace.root).join("AGENTS.md").is_file() {
                return setup_page(Some("Папка проекта недоступна."));
            }
            registry.set_active(&workspace.id);
            match persist_registry_and_supervisor(&registry) {
                Ok(()) => setup_page(None),
                Err(error) => setup_page(Some(&error)),
            }
        }
        ("POST", "/forget") => {
            let (mut registry, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            if let Err(error) = remove_legacy_automation(Path::new(&workspace.root)) {
                return setup_page(Some(&error));
            }
            registry.remove(&workspace.id);
            match persist_registry_and_supervisor(&registry) {
                Ok(()) => setup_page(None),
                Err(error) => setup_page(Some(&error)),
            }
        }
        ("POST", "/launch") => {
            let (mut registry, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            let root = PathBuf::from(&workspace.root);
            registry.set_active(&workspace.id);
            if let Err(error) = persist_registry_and_supervisor(&registry) {
                return setup_page(Some(&error));
            }
            match launch_control_center(&root) {
                Ok(()) => simple_message(
                    "AI OS открыт",
                    if cfg!(windows) {
                        "Окно AI OS открыто. После закрытия оно остаётся в области уведомлений Windows; повторное нажатие вернёт то же окно."
                    } else {
                        "Окно AI OS открыто. После закрытия оно остаётся в системной области Linux; повторное нажатие вернёт то же окно."
                    },
                    false,
                ),
                Err(error) => simple_message("Не удалось открыть AI OS", &error, true),
            }
        }
        ("POST", "/open-folder") => {
            let (_, workspace) = match selected_workspace(body) {
                Ok(value) => value,
                Err(error) => return setup_page(Some(&error)),
            };
            let root = PathBuf::from(&workspace.root);
            match open_folder(&root) {
                Ok(()) => setup_page(None),
                Err(error) => simple_message("Не удалось открыть папку", &error, true),
            }
        }
        _ => simple_message(
            "Страница не найдена",
            "Вернитесь к установке и повторите действие.",
            true,
        ),
    }
}

fn selftest() -> i32 {
    let Some(root) = payload_root() else {
        println!("SELFTEST FAIL: payload root not found");
        return 1;
    };
    if let Err(error) = validate_payload(&root) {
        println!("SELFTEST FAIL: {error}");
        return 1;
    }
    if !root
        .join("workspace-template/tools/check_ai_os_readiness.ps1")
        .is_file()
    {
        println!("SELFTEST FAIL: readiness check is missing");
        return 1;
    }
    let html = String::from_utf8(setup_page(None)).unwrap_or_default();
    if !html.contains("Создать проект")
        || html.contains("BUILD ")
        || html.contains("SETUP v")
        || html.len() < 1000
    {
        println!("SELFTEST FAIL: setup page did not render");
        return 1;
    }
    println!("AI OS Setup v{APP_VERSION}");
    println!("payload: {}", root.display());
    println!("SELFTEST PASS");
    0
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|arg| arg == "--selftest") {
        std::process::exit(selftest());
    }
    if let Some(index) = args.iter().position(|arg| arg == "--render-setup-html") {
        let Some(output) = args.get(index + 1) else {
            eprintln!("--render-setup-html requires an output path");
            std::process::exit(2);
        };
        match fs::write(output, setup_page(None)) {
            Ok(()) => std::process::exit(0),
            Err(error) => {
                eprintln!("could not render setup HTML: {error}");
                std::process::exit(1);
            }
        }
    }

    let primary_instance = match acquire_manager_instance(true) {
        Ok(Some(instance)) => instance,
        Ok(None) => return,
        Err(error) => {
            eprintln!("AI OS workspace manager instance error: {error}");
            return;
        }
    };
    let instance_guard = primary_instance.guard;
    let instance_listener = Mutex::new(Some(primary_instance.listener));

    let run_result = tauri::Builder::default()
        .register_asynchronous_uri_scheme_protocol("dash", |_context, request, responder| {
            let method = request.method().as_str().to_string();
            let path = request.uri().path().to_string();
            let body = request.body().clone();
            std::thread::spawn(move || {
                let (bytes, content_type) = match path.as_str() {
                    "/assets/installer.js" => (
                        INSTALLER_JS.as_bytes().to_vec(),
                        "text/javascript; charset=utf-8",
                    ),
                    "/assets/three.module.min.js" => (
                        THREE_JS.as_bytes().to_vec(),
                        "text/javascript; charset=utf-8",
                    ),
                    "/assets/three.core.min.js" => (
                        THREE_CORE_JS.as_bytes().to_vec(),
                        "text/javascript; charset=utf-8",
                    ),
                    "/assets/brain.glb" => (BRAIN_GLB.to_vec(), "model/gltf-binary"),
                    "/assets/onest-cyrillic.woff2" => (ONEST_CYRILLIC.to_vec(), "font/woff2"),
                    "/assets/onest-latin.woff2" => (ONEST_LATIN.to_vec(), "font/woff2"),
                    "/assets/DALA-REPLICA-LICENSE.txt" => (
                        DALA_REPLICA_LICENSE.as_bytes().to_vec(),
                        "text/plain; charset=utf-8",
                    ),
                    "/assets/ONEST-LICENSE.txt" => (
                        ONEST_LICENSE.as_bytes().to_vec(),
                        "text/plain; charset=utf-8",
                    ),
                    _ => (route(&method, &path, &body), "text/html; charset=utf-8"),
                };
                let response = tauri::http::Response::builder()
                    .status(200)
                    .header("Content-Type", content_type)
                    .header("Cache-Control", "no-store")
                    .header("X-Content-Type-Options", "nosniff")
                    .body(bytes)
                    .unwrap();
                responder.respond(response);
            });
        })
        .setup(move |app| {
            let _ = APP_HANDLE.set(app.handle().clone());
            if let Some(listener) = instance_listener
                .lock()
                .ok()
                .and_then(|mut value| value.take())
            {
                start_manager_listener(listener, app.handle().clone());
            }
            let resources = if let Ok(path) = std::env::var("AI_OS_SETUP_RESOURCE_DIR") {
                PathBuf::from(path)
            } else {
                app.path().resource_dir()?
            };
            let _ = RESOURCE_DIR.set(resources);
            if let Some(payload) = payload_root() {
                if let Ok(manifest) = payload_manifest(&payload) {
                    for error in cleanup_stale_online_binaries(&payload, &manifest) {
                        eprintln!("Could not remove a stale offline package: {error}");
                    }
                }
            }
            if let Ok(registry) = load_registry() {
                let _ = save_registry(&registry);
                if let Some(payload) = payload_root() {
                    let _ = reconcile_supervisor(&payload, &registry);
                }
            }
            let icon = tauri::image::Image::from_bytes(SETUP_ICON_PNG)?;
            let window = WebviewWindowBuilder::new(
                app,
                "main",
                WebviewUrl::External("http://dash.localhost/".parse().unwrap()),
            )
            .title("Установка AI OS")
            .inner_size(1180.0, 820.0)
            .min_inner_size(720.0, 560.0)
            .decorations(false)
            .icon(icon.clone())?
            .build()?;
            window.set_icon(icon)?;
            Ok(())
        })
        .run(tauri::generate_context!());
    drop(instance_guard);
    run_result.expect("error while running AI OS Setup");
}

#[cfg(test)]
mod tests {
    use super::*;

    fn write_fixture_manifest(root: &Path, mode: &str, download_scheme: &str) {
        let manifest = serde_json::json!({
            "distributionMode": mode,
            "memoryTool": {
                "version": "2.4.0",
                "downloadUrl": format!("{download_scheme}://github.com/example/memory.zip"),
                "archiveName": "memory.zip",
                "archiveSha256": "a".repeat(64),
                "archiveSizeBytes": 128,
                "sha256": "b".repeat(64),
                "binarySizeBytes": 64
            },
            "memoryQdrant": {
                "version": "1.18.1",
                "downloadUrl": format!("{download_scheme}://github.com/example/qdrant.zip"),
                "archiveName": "qdrant.zip",
                "archiveSha256": "e".repeat(64),
                "archiveSizeBytes": 512,
                "sha256": "f".repeat(64),
                "binarySizeBytes": 256
            },
            "memoryOnnxRuntime": {
                "version": "1.24.2",
                "downloadUrl": format!("{download_scheme}://github.com/example/onnx.zip"),
                "archiveName": "onnx.zip",
                "archiveSha256": "1".repeat(64),
                "archiveSizeBytes": 1024,
                "sha256": "2".repeat(64),
                "binarySizeBytes": 512
            },
            "codeIntelligence": {
                "version": "0.9.0",
                "downloadUrl": format!("{download_scheme}://github.com/example/code.zip"),
                "archiveName": "code.zip",
                "archiveSha256": "c".repeat(64),
                "archiveSizeBytes": 256,
                "sha256": "d".repeat(64),
                "binarySizeBytes": 128
            }
        });
        fs::write(
            root.join("PAYLOAD_MANIFEST.json"),
            serde_json::to_vec(&manifest).unwrap(),
        )
        .unwrap();
    }

    fn create_payload_shell(root: &Path) {
        fs::create_dir_all(root.join("workspace-template")).unwrap();
        fs::write(root.join("workspace-template/AGENTS.md"), "# fixture").unwrap();
        fs::write(root.join("install_ai_os_workspace.ps1"), "exit 0").unwrap();
        fs::write(root.join("ai_os_package_cache.psm1"), "# fixture").unwrap();
        fs::write(root.join("ai_os_supervisor.ps1"), "# fixture").unwrap();
        #[cfg(windows)]
        fs::write(root.join("install_ai_os_supervisor_task.ps1"), "# fixture").unwrap();
        #[cfg(not(windows))]
        {
            fs::create_dir_all(root.join("powershell")).unwrap();
            fs::write(root.join("powershell/pwsh"), "fixture").unwrap();
            fs::write(root.join("install_ai_os_supervisor_linux.ps1"), "# fixture").unwrap();
        }
    }

    #[test]
    fn form_decoder_handles_spaces_and_unicode() {
        let body = b"project_name=My+Project&user_name=Denis&summary=%D0%A2%D0%B5%D1%81%D1%82+workspace&memory=on";
        let form = form_from_body(body);
        assert_eq!(form.project_name, "My Project");
        assert_eq!(form.summary, "Тест workspace");
        assert!(form.memory);
        assert!(!form.code_intel);
    }

    #[test]
    fn html_escapes_user_values() {
        assert_eq!(
            esc("<script>'x'</script>"),
            "&lt;script&gt;&#39;x&#39;&lt;/script&gt;"
        );
    }

    #[test]
    fn setup_ui_is_russian_without_release_badges() {
        let html = String::from_utf8(setup_page_with_registry(
            None,
            &WorkspaceRegistry::default(),
        ))
        .unwrap();
        assert!(html.contains(r#"<html lang="ru">"#));
        assert!(html.contains("Контекст проекта в одном месте."));
        assert!(html.contains("Создать проект"));
        assert!(!html.contains("Среда, которая помнит"));
        assert!(!html.contains("Центр проекта"));
        assert!(!html.contains("BUILD "));
        assert!(!html.contains("SETUP v"));
    }

    #[test]
    fn new_project_form_skips_a_registered_default_destination() {
        let mut registry = WorkspaceRegistry::default();
        let occupied = PathBuf::from(default_destination(&registry));
        registry.upsert(&occupied, "Existing project", false);

        let html = String::from_utf8(setup_page_with_registry(None, &registry)).unwrap();
        let next_name = format!("{} 2", occupied.file_name().unwrap().to_string_lossy());
        let expected = occupied.with_file_name(next_name);
        let expected_input = format!(
            r#"name="destination" type="text" required value="{}""#,
            esc(&expected.to_string_lossy())
        );

        assert!(
            html.contains(&expected_input),
            "new project form reused a registered destination"
        );
    }

    #[test]
    fn destination_suggestion_skips_registered_and_nonempty_folders() {
        let base = std::env::temp_dir().join(format!(
            "ai-os-destination-suggestion-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&base);
        fs::create_dir_all(base.join("Мой проект 2")).unwrap();
        fs::write(base.join("Мой проект 2").join("existing.txt"), "occupied").unwrap();

        let mut registry = WorkspaceRegistry::default();
        registry.upsert(&base.join("Мой проект"), "Existing project", false);

        assert_eq!(
            suggested_destination_in(&base, &registry),
            base.join("Мой проект 3")
        );

        fs::remove_dir_all(base).unwrap();
    }

    #[test]
    fn manager_protocol_accepts_a_fragmented_command() {
        let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let address = listener.local_addr().unwrap();
        let sender = std::thread::spawn(move || {
            let mut stream = TcpStream::connect(address).unwrap();
            let split = MANAGER_SHOW.len() / 2;
            stream.write_all(&MANAGER_SHOW.as_bytes()[..split]).unwrap();
            stream.flush().unwrap();
            std::thread::sleep(Duration::from_millis(20));
            stream.write_all(&MANAGER_SHOW.as_bytes()[split..]).unwrap();
            stream.write_all(b"\n").unwrap();
            stream.flush().unwrap();
        });
        let (mut stream, _) = listener.accept().unwrap();
        assert_eq!(read_manager_command(&mut stream), Some(true));
        sender.join().unwrap();
    }

    #[test]
    fn setup_layout_removes_the_intro_column_after_entry() {
        let full_width_rule = ".setup-active .shell { grid-template-columns: 0 minmax(0, 1fr);";
        assert!(INSTALLER_CSS.matches(full_width_rule).count() >= 2);
        assert!(INSTALLER_CSS.contains(".setup-active .rail {"));
        for obsolete in [
            "grid-template-columns: 44% 56%",
            "grid-template-columns: 41% 59%",
            "grid-template-rows: 250px",
        ] {
            assert!(!INSTALLER_CSS.contains(obsolete), "{obsolete}");
        }
    }

    #[test]
    fn running_progress_updates_in_place_without_page_refresh() {
        let html = running_progress_body("<unsafe log>");
        assert!(html.contains("fetch('/progress-status'"));
        assert!(html.contains("&lt;unsafe log&gt;"));
        assert!(!html.to_lowercase().contains("http-equiv"));
        assert_eq!(html.matches("<h1>").count(), 1);
    }

    #[test]
    fn workspace_list_renders_every_project_and_targets_its_id() {
        let base = std::env::temp_dir().join("ai-os-workspace-list-test");
        let _ = fs::remove_dir_all(&base);
        let first = base.join("One");
        let second = base.join("Two");
        fs::create_dir_all(&first).unwrap();
        fs::create_dir_all(&second).unwrap();
        fs::write(first.join("AGENTS.md"), "# fixture").unwrap();
        fs::write(second.join("AGENTS.md"), "# fixture").unwrap();
        let mut registry = WorkspaceRegistry::default();
        registry.upsert(&first, "Одинаковое имя", true);
        registry.upsert(&second, "Одинаковое имя", false);

        let html = workspace_list_html(&registry);
        assert_eq!(html.matches("Одинаковое имя").count(), 2);
        for workspace in &registry.workspaces {
            assert!(html.contains(&format!(r#"value="{}""#, workspace.id)));
        }
        assert!(html.contains("Активная"));
        assert!(html.contains("Сделать активным"));
        assert!(html.contains("Фоновые проверки выключены"));
        let _ = fs::remove_dir_all(base);
    }

    #[test]
    fn destination_must_be_absolute() {
        let form = InstallForm {
            project_name: "Project".into(),
            user_name: "User".into(),
            summary: "A sufficiently detailed project summary".into(),
            destination: "relative-folder".into(),
            ..InstallForm::default()
        };
        assert!(validate_form(&form, &WorkspaceRegistry::default()).is_err());
    }

    #[test]
    fn pasted_quoted_paths_are_normalized_before_validation_and_install() {
        let destination = std::env::temp_dir().join("ai-os-quoted-path-test");
        let code_repo = std::env::temp_dir().join("existing-code-repository");
        let body = format!(
            "project_name=Project&user_name=User&summary=A+sufficiently+detailed+project+summary&destination={}&code_repo_path={}",
            urlencoding::encode(&format!("\"{}\"", destination.display())),
            urlencoding::encode(&format!("\"{}\"", code_repo.display()))
        );

        let form = form_from_body(body.as_bytes());

        assert_eq!(form.destination, destination.to_string_lossy());
        assert_eq!(form.code_repo_path, code_repo.to_string_lossy());
        assert_eq!(
            validate_form(&form, &WorkspaceRegistry::default()).unwrap(),
            destination
        );
    }

    #[test]
    fn registered_destination_is_rejected_even_if_the_folder_is_empty() {
        let destination = std::env::temp_dir().join(format!(
            "ai-os-registered-destination-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&destination);
        fs::create_dir_all(&destination).unwrap();

        let form = InstallForm {
            project_name: "Existing project".into(),
            user_name: "User".into(),
            summary: "A sufficiently detailed project summary".into(),
            destination: destination.to_string_lossy().into_owned(),
            ..InstallForm::default()
        };
        let mut registry = WorkspaceRegistry::default();
        registry.upsert(&destination, "Existing project", false);

        let error = validate_form(&form, &registry).unwrap_err();
        assert!(error.contains("уже добавлена как проект"));

        fs::remove_dir_all(destination).unwrap();
    }

    #[test]
    fn non_empty_destination_is_rejected_before_install_starts() {
        let root = std::env::temp_dir().join("ai-os-non-empty-destination-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        fs::write(root.join("existing-project.txt"), "keep").unwrap();
        let form = InstallForm {
            project_name: "Existing project".into(),
            user_name: "User".into(),
            summary: "A sufficiently detailed project summary".into(),
            destination: root.to_string_lossy().into_owned(),
            ..InstallForm::default()
        };

        let error = validate_form(&form, &WorkspaceRegistry::default()).unwrap_err();
        assert!(error.contains("уже содержит файлы"));
        assert!(error.contains("Репозиторий кода"));
        assert_eq!(
            fs::read_to_string(root.join("existing-project.txt")).unwrap(),
            "keep"
        );
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn rejected_form_keeps_user_input() {
        let form = InstallForm {
            project_name: "Study <Forge>".into(),
            user_name: "Денис".into(),
            summary: "Описание проекта для повторной проверки".into(),
            destination: r"D:\ForStudyForge".into(),
            code_repo_path: r"D:\ForStudyForge\Для пробной".into(),
            memory: false,
            code_intel: true,
            automation: true,
            git: true,
            ..InstallForm::default()
        };
        let html = String::from_utf8(setup_page_with_registry_and_form(
            Some("Папка занята"),
            &WorkspaceRegistry::default(),
            Some(&form),
        ))
        .unwrap();

        assert!(html.contains(r#"value="Study &lt;Forge&gt;""#));
        assert!(html.contains(r#"value="Денис""#));
        assert!(html.contains(r#"value="D:\ForStudyForge\Для пробной""#));
        assert!(html.contains("Описание проекта для повторной проверки</textarea>"));
        assert!(html.contains(r#"name="code_intel" checked"#));
        assert!(!html.contains(r#"name="memory" checked"#));
    }

    #[test]
    fn online_payload_uses_verified_downloads_without_bundled_binaries() {
        let root = std::env::temp_dir().join("ai-os-online-payload-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        create_payload_shell(&root);
        write_fixture_manifest(&root, "online", "https");

        assert!(validate_payload(&root).is_ok());
        assert!(!root.join("memory-tool").exists());
        assert!(!root.join("code-intel-tool").exists());
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn online_startup_removes_only_stale_offline_binaries() {
        let root = std::env::temp_dir().join("ai-os-online-stale-binaries-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("memory-tool")).unwrap();
        fs::create_dir_all(root.join("code-intel-tool")).unwrap();
        #[cfg(windows)]
        fs::create_dir_all(root.join("memory-runtime")).unwrap();
        fs::write(root.join("memory-tool").join(MEMORY_BINARY_NAME), "stale").unwrap();
        fs::write(
            root.join("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
            "stale",
        )
        .unwrap();
        #[cfg(windows)]
        {
            fs::write(
                root.join("memory-runtime").join(QDRANT_BINARY_NAME),
                "stale",
            )
            .unwrap();
            fs::write(
                root.join("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
                "stale",
            )
            .unwrap();
        }
        fs::write(root.join("memory-tool/LICENSE.txt"), "keep").unwrap();
        write_fixture_manifest(&root, "online", "https");
        let manifest = payload_manifest(&root).unwrap();

        assert!(cleanup_stale_online_binaries(&root, &manifest).is_empty());
        assert!(!root.join("memory-tool").join(MEMORY_BINARY_NAME).exists());
        assert!(!root
            .join("code-intel-tool")
            .join(CODE_INTEL_BINARY_NAME)
            .exists());
        #[cfg(windows)]
        assert!(!root
            .join("memory-runtime")
            .join(QDRANT_BINARY_NAME)
            .exists());
        assert_eq!(
            fs::read_to_string(root.join("memory-tool/LICENSE.txt")).unwrap(),
            "keep"
        );
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn offline_startup_keeps_bundled_binaries() {
        let root = std::env::temp_dir().join("ai-os-offline-keeps-binaries-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("memory-tool")).unwrap();
        fs::create_dir_all(root.join("code-intel-tool")).unwrap();
        #[cfg(windows)]
        fs::create_dir_all(root.join("memory-runtime")).unwrap();
        fs::write(root.join("memory-tool").join(MEMORY_BINARY_NAME), "bundled").unwrap();
        fs::write(
            root.join("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
            "bundled",
        )
        .unwrap();
        #[cfg(windows)]
        {
            fs::write(
                root.join("memory-runtime").join(QDRANT_BINARY_NAME),
                "bundled",
            )
            .unwrap();
            fs::write(
                root.join("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
                "bundled",
            )
            .unwrap();
        }
        write_fixture_manifest(&root, "offline", "https");
        let manifest = payload_manifest(&root).unwrap();

        assert!(cleanup_stale_online_binaries(&root, &manifest).is_empty());
        assert!(root.join("memory-tool").join(MEMORY_BINARY_NAME).is_file());
        assert!(root
            .join("code-intel-tool")
            .join(CODE_INTEL_BINARY_NAME)
            .is_file());
        #[cfg(windows)]
        assert!(root
            .join("memory-runtime")
            .join(QDRANT_BINARY_NAME)
            .is_file());
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn payload_rejects_insecure_download_metadata() {
        let root = std::env::temp_dir().join("ai-os-insecure-payload-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        create_payload_shell(&root);
        write_fixture_manifest(&root, "online", "http");

        assert!(validate_payload(&root).unwrap_err().contains("memoryTool"));
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn offline_payload_requires_bundled_packages() {
        let root = std::env::temp_dir().join("ai-os-offline-payload-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        create_payload_shell(&root);
        write_fixture_manifest(&root, "offline", "https");

        assert!(validate_payload(&root).unwrap_err().contains("Offline Kit"));
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn offline_payload_does_not_depend_on_download_metadata() {
        let root = std::env::temp_dir().join("ai-os-offline-no-download-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("memory-tool")).unwrap();
        fs::create_dir_all(root.join("code-intel-tool")).unwrap();
        #[cfg(windows)]
        fs::create_dir_all(root.join("memory-runtime")).unwrap();
        create_payload_shell(&root);
        let manifest = serde_json::json!({
            "distributionMode": "offline",
            "memoryTool": {
                "version": "2.4.0",
                "sha256": "a".repeat(64),
                "binarySizeBytes": 64
            },
            "memoryQdrant": {
                "version": "1.18.1",
                "sha256": "e".repeat(64),
                "binarySizeBytes": 256
            },
            "memoryOnnxRuntime": {
                "version": "1.24.2",
                "sha256": "f".repeat(64),
                "binarySizeBytes": 512
            },
            "codeIntelligence": {
                "version": "0.9.0",
                "sha256": "b".repeat(64),
                "binarySizeBytes": 128
            }
        });
        fs::write(
            root.join("PAYLOAD_MANIFEST.json"),
            serde_json::to_vec(&manifest).unwrap(),
        )
        .unwrap();
        fs::write(root.join("memory-tool").join(MEMORY_BINARY_NAME), "fixture").unwrap();
        fs::write(
            root.join("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
            "fixture",
        )
        .unwrap();
        #[cfg(windows)]
        {
            fs::write(
                root.join("memory-runtime").join(QDRANT_BINARY_NAME),
                "fixture",
            )
            .unwrap();
            fs::write(
                root.join("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
                "fixture",
            )
            .unwrap();
        }

        assert!(validate_payload(&root).is_ok());
        let _ = fs::remove_dir_all(root);
    }

    #[cfg(windows)]
    #[test]
    fn powershell_receives_local_paths_without_bypassing_policy() {
        let root = std::env::temp_dir().join("ai-os-setup-args-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("workspace-template")).unwrap();
        fs::create_dir_all(root.join("memory-tool")).unwrap();
        fs::create_dir_all(root.join("code-intel-tool")).unwrap();
        fs::create_dir_all(root.join("memory-runtime")).unwrap();
        fs::write(root.join("install_ai_os_workspace.ps1"), "exit 0").unwrap();
        fs::write(root.join("workspace-template/AGENTS.md"), "# fixture").unwrap();
        fs::write(root.join("memory-tool").join(MEMORY_BINARY_NAME), "fixture").unwrap();
        fs::write(
            root.join("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
            "fixture",
        )
        .unwrap();
        fs::write(
            root.join("memory-runtime").join(QDRANT_BINARY_NAME),
            "fixture",
        )
        .unwrap();
        fs::write(
            root.join("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
            "fixture",
        )
        .unwrap();
        write_fixture_manifest(&root, "offline", "https");
        let verbatim_root = fs::canonicalize(&root).unwrap();
        assert!(verbatim_root.to_string_lossy().starts_with(r"\\?\"));
        let args =
            build_setup_args(&verbatim_root, &root.join("dest"), None, true, false, true).unwrap();
        assert!(args
            .windows(2)
            .any(|window| window == ["-ExecutionPolicy", "RemoteSigned"]));
        assert!(!args.iter().any(|arg| arg.eq_ignore_ascii_case("bypass")));
        assert!(!args.iter().any(|arg| arg.starts_with(r"\\?\")));
        let _ = fs::remove_dir_all(root);
    }

    #[cfg(windows)]
    #[test]
    fn powershell_oem_log_is_readable_and_actionable() {
        let path = std::env::temp_dir().join("ai-os-oem-log-test.log");
        let _ = fs::remove_file(&path);
        fs::write(
            &path,
            [0x8d, 0xa5, 0x20, 0xe3, 0xa4, 0xa0, 0xa5, 0xe2, 0xe1, 0xef],
        )
        .unwrap();
        assert_eq!(tail_log(&path, 10), "Не удается");

        let detail = install_failure_detail(
            "Файл не имеет цифровой подписи. about_Execution_Policies",
            1,
        );
        assert!(detail.contains("Windows заблокировала"));
        let _ = fs::remove_file(path);
    }

    #[test]
    fn git_line_ending_warnings_are_hidden_from_the_install_log() {
        let path =
            std::env::temp_dir().join(format!("ai-os-git-warning-log-{}.log", std::process::id()));
        let _ = fs::remove_file(&path);
        fs::write(
            &path,
            "copying files\n  warning: in the working copy of 'file.txt', LF will be replaced by CRLF\nproject ready\n",
        )
        .unwrap();
        let visible = tail_log(&path, 20);
        assert!(visible.contains("copying files"));
        assert!(visible.contains("project ready"));
        assert!(!visible.contains("LF will be replaced by CRLF"));
        let _ = fs::remove_file(path);
    }

    #[test]
    fn installer_runtime_icon_is_explicit_and_current() {
        assert!(SETUP_ICON_PNG.starts_with(&[137, 80, 78, 71, 13, 10, 26, 10]));
        assert!(SETUP_ICON_PNG.len() > 1_000);
        let source = include_str!("main.rs");
        assert!(source.contains(".icon(icon.clone())?"));
        assert!(source.contains("window.set_icon(icon)?"));
    }

    #[test]
    fn setup_transition_avoids_webgl_resize_thrashing() {
        assert!(INSTALLER_JS.contains("preserveDrawingBuffer: false"));
        assert!(INSTALLER_JS.contains("aios:setup-transition-start"));
        assert!(INSTALLER_JS.contains("aios:setup-transition-complete"));
        assert!(INSTALLER_JS.contains("new ResizeObserver(scheduleResize)"));
        assert!(!INSTALLER_JS.contains("new ResizeObserver(resize)"));
        assert!(!INSTALLER_JS.starts_with("import * as THREE"));
        assert!(INSTALLER_JS.contains("await import(\"./three.module.min.js\")"));
        assert!(INSTALLER_JS.contains("experience.firstEntry\n  ? startScene()"));
        assert!(INSTALLER_JS.contains("renderer.dispose()"));
        assert!(!INSTALLER_JS.contains("content.addEventListener(\"scroll\""));
    }

    #[test]
    fn subsequent_pages_skip_splash_and_keep_actions_aligned() {
        let source = include_str!("main.rs");
        assert!(source.contains("ai-os-setup-entered"));
        assert!(
            source.contains("classList.add(\"setup-active\",\"boot-complete\",\"scene-retired\")")
        );
        assert!(source.contains("data-phase-title"));
        assert!(INSTALLER_CSS.contains(".first-entry:not(.boot-complete) .boot-screen"));
        assert!(INSTALLER_CSS.contains(".actions { display: flex"));
        assert!(INSTALLER_CSS.contains(".setup-active .constellation { opacity: 0"));
    }

    #[test]
    fn fresh_install_uses_path_scoped_memory_and_shared_supervisor() {
        let root = std::env::temp_dir().join("ai-os-setup-shared-supervisor-args");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("workspace-template")).unwrap();
        fs::create_dir_all(root.join("memory-tool")).unwrap();
        fs::create_dir_all(root.join("code-intel-tool")).unwrap();
        #[cfg(windows)]
        fs::create_dir_all(root.join("memory-runtime")).unwrap();
        fs::write(root.join("install_ai_os_workspace.ps1"), "exit 0").unwrap();
        fs::write(root.join("workspace-template/AGENTS.md"), "# fixture").unwrap();
        fs::write(root.join("memory-tool").join(MEMORY_BINARY_NAME), "fixture").unwrap();
        fs::write(
            root.join("code-intel-tool").join(CODE_INTEL_BINARY_NAME),
            "fixture",
        )
        .unwrap();
        #[cfg(windows)]
        {
            fs::write(
                root.join("memory-runtime").join(QDRANT_BINARY_NAME),
                "fixture",
            )
            .unwrap();
            fs::write(
                root.join("memory-runtime").join(ONNX_RUNTIME_BINARY_NAME),
                "fixture",
            )
            .unwrap();
        }
        write_fixture_manifest(&root, "offline", "https");
        let destination = root.join("same-name-project");
        let form = InstallForm {
            project_name: "Одинаковое имя".into(),
            user_name: "Пользователь".into(),
            summary: "Достаточно подробное описание проекта".into(),
            automation: true,
            ..InstallForm::default()
        };

        let args = build_setup_args(&root, &destination, Some(&form), false, false, true).unwrap();
        assert!(args.iter().any(|arg| arg == "-SharedSupervisor"));
        assert!(!args.iter().any(|arg| arg == "-SkipScheduledTasks"));
        let library_index = args
            .iter()
            .position(|arg| arg == "-MemoryLibraryName")
            .unwrap();
        assert_eq!(args[library_index + 1], memory_library_name(&destination));
        let download_index = args
            .iter()
            .position(|arg| arg == "-MemoryToolDownloadUrl")
            .unwrap();
        assert_eq!(
            args[download_index + 1],
            "https://github.com/example/memory.zip"
        );
        let _ = fs::remove_dir_all(root);
    }
}
