use crate::registry::{data_dir, state_path, WorkspaceRegistry};
#[cfg(windows)]
use crate::CREATE_NO_WINDOW;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[cfg(unix)]
fn copy_runtime_tree(source: &Path, destination: &Path) -> Result<(), String> {
    if destination.join("pwsh").is_file() {
        return Ok(());
    }
    if !source.join("pwsh").is_file() {
        return Err("В Linux-пакете не найден встроенный PowerShell runtime.".into());
    }
    fs::create_dir_all(destination).map_err(|error| error.to_string())?;
    for entry in fs::read_dir(source).map_err(|error| error.to_string())? {
        let entry = entry.map_err(|error| error.to_string())?;
        let from = entry.path();
        let to = destination.join(entry.file_name());
        if from.is_dir() {
            copy_runtime_tree(&from, &to)?;
        } else {
            fs::copy(&from, &to).map_err(|error| error.to_string())?;
        }
    }
    let executable = destination.join("pwsh");
    let mut permissions = fs::metadata(&executable)
        .map_err(|error| error.to_string())?
        .permissions();
    permissions.set_mode(0o755);
    fs::set_permissions(&executable, permissions).map_err(|error| error.to_string())?;
    Ok(())
}

#[cfg(unix)]
fn linux_runtime_powershell(payload: &Path) -> Result<PathBuf, String> {
    let destination = data_dir().join("runtime").join("powershell");
    copy_runtime_tree(&payload.join("powershell"), &destination)?;
    Ok(destination.join("pwsh"))
}

fn supervisor_command_args(
    task_installer: &Path,
    supervisor_target: &Path,
    registry_path: &Path,
    powershell: &Path,
    remove: bool,
) -> Vec<String> {
    #[cfg(windows)]
    let _ = powershell;
    let mut args = vec!["-NoProfile".into()];
    #[cfg(windows)]
    args.extend(["-ExecutionPolicy".into(), "RemoteSigned".into()]);
    args.extend([
        "-File".into(),
        crate::child_process_path(task_installer),
        "-SupervisorScript".into(),
        crate::child_process_path(supervisor_target),
        "-RegistryPath".into(),
        crate::child_process_path(registry_path),
    ]);
    #[cfg(unix)]
    args.extend([
        "-PowerShellPath".into(),
        crate::child_process_path(powershell),
    ]);
    if remove {
        args.push("-Remove".into());
    }
    args
}

fn decode_process_output(bytes: &[u8]) -> String {
    String::from_utf8(bytes.to_vec())
        .ok()
        .or_else(|| crate::decode_native_log(bytes))
        .unwrap_or_else(|| String::from_utf8_lossy(bytes).into_owned())
        .trim()
        .to_string()
}

pub fn reconcile_supervisor(payload: &Path, registry: &WorkspaceRegistry) -> Result<(), String> {
    if std::env::var_os("AI_OS_SETUP_DISABLE_SUPERVISOR").as_deref()
        == Some(std::ffi::OsStr::new("1"))
    {
        return Ok(());
    }

    #[cfg(windows)]
    let (supervisor_source, task_installer, powershell) = (
        payload.join("ai_os_supervisor.ps1"),
        payload.join("install_ai_os_supervisor_task.ps1"),
        PathBuf::from("powershell.exe"),
    );
    #[cfg(unix)]
    let (supervisor_source, task_installer, powershell) = (
        payload.join("ai_os_supervisor.ps1"),
        payload.join("install_ai_os_supervisor_linux.ps1"),
        linux_runtime_powershell(payload)?,
    );

    if !supervisor_source.is_file() || !task_installer.is_file() {
        return Err("В установщике не хватает файлов общего supervisor.".into());
    }

    let target_dir = data_dir().join("runtime");
    fs::create_dir_all(&target_dir).map_err(|error| error.to_string())?;
    let supervisor_target = target_dir.join("ai_os_supervisor.ps1");
    fs::copy(&supervisor_source, &supervisor_target).map_err(|error| error.to_string())?;

    let remove = !registry
        .workspaces
        .iter()
        .any(|workspace| workspace.automation_enabled);
    let args = supervisor_command_args(
        &task_installer,
        &supervisor_target,
        &state_path(),
        &powershell,
        remove,
    );
    let mut command = Command::new(&powershell);
    command.args(args);
    #[cfg(windows)]
    command.creation_flags(CREATE_NO_WINDOW);
    let output = command.output().map_err(|error| error.to_string())?;
    if !output.status.success() {
        let stderr = decode_process_output(&output.stderr);
        let stdout = decode_process_output(&output.stdout);
        let detail = if stderr.is_empty() { stdout } else { stderr };
        return Err(if detail.is_empty() {
            format!(
                "Не удалось настроить общий supervisor: код {}",
                output.status.code().unwrap_or(-1)
            )
        } else {
            format!("Не удалось настроить общий supervisor: {detail}")
        });
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[cfg(windows)]
    #[test]
    fn windows_supervisor_paths_drop_verbatim_prefix_without_bypass() {
        let root = std::env::temp_dir().join("ai-os-supervisor-path-test");
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let verbatim = fs::canonicalize(&root).unwrap();
        assert!(verbatim.to_string_lossy().starts_with(r"\\?\"));

        let args = supervisor_command_args(
            &verbatim.join("install.ps1"),
            &verbatim.join("supervisor.ps1"),
            &verbatim.join("state.json"),
            Path::new("powershell.exe"),
            true,
        );

        assert!(args
            .windows(2)
            .any(|pair| pair == ["-ExecutionPolicy", "RemoteSigned"]));
        assert!(!args.iter().any(|arg| arg.eq_ignore_ascii_case("bypass")));
        assert!(!args.iter().any(|arg| arg.starts_with(r"\\?\")));
        assert!(args.iter().any(|arg| arg == "-Remove"));
        let _ = fs::remove_dir_all(root);
    }
}
