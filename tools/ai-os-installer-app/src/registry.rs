use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

const SCHEMA_VERSION: u32 = 2;

fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

fn default_true() -> bool {
    true
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct WorkspaceRecord {
    pub id: String,
    pub root: String,
    pub project_name: String,
    #[serde(default = "default_true")]
    pub automation_enabled: bool,
    #[serde(default)]
    pub registered_unix: u64,
    #[serde(default)]
    pub updated_unix: u64,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct WorkspaceRegistry {
    pub schema_version: u32,
    #[serde(default)]
    pub active_workspace_id: Option<String>,
    #[serde(default)]
    pub workspaces: Vec<WorkspaceRecord>,
}

impl Default for WorkspaceRegistry {
    fn default() -> Self {
        Self {
            schema_version: SCHEMA_VERSION,
            active_workspace_id: None,
            workspaces: Vec::new(),
        }
    }
}

impl WorkspaceRegistry {
    pub fn upsert(&mut self, root: &Path, project_name: &str, automation_enabled: bool) -> String {
        let id = workspace_id(root);
        let display_root = display_root(root);
        let stamp = now_unix();
        if let Some(existing) = self.workspaces.iter_mut().find(|item| item.id == id) {
            existing.root = display_root;
            existing.project_name = project_name.trim().to_string();
            existing.automation_enabled = automation_enabled;
            existing.updated_unix = stamp;
            if existing.registered_unix == 0 {
                existing.registered_unix = stamp;
            }
        } else {
            self.workspaces.push(WorkspaceRecord {
                id: id.clone(),
                root: display_root,
                project_name: project_name.trim().to_string(),
                automation_enabled,
                registered_unix: stamp,
                updated_unix: stamp,
            });
        }
        self.schema_version = SCHEMA_VERSION;
        self.active_workspace_id = Some(id.clone());
        id
    }

    pub fn get(&self, id: &str) -> Option<&WorkspaceRecord> {
        self.workspaces.iter().find(|workspace| workspace.id == id)
    }

    pub fn set_active(&mut self, id: &str) -> bool {
        if self.get(id).is_none() {
            return false;
        }
        self.active_workspace_id = Some(id.to_string());
        true
    }

    pub fn set_automation(&mut self, id: &str, enabled: bool) -> bool {
        let Some(workspace) = self
            .workspaces
            .iter_mut()
            .find(|workspace| workspace.id == id)
        else {
            return false;
        };
        workspace.automation_enabled = enabled;
        workspace.updated_unix = now_unix();
        true
    }

    pub fn remove(&mut self, id: &str) -> bool {
        let before = self.workspaces.len();
        self.workspaces.retain(|workspace| workspace.id != id);
        if self.workspaces.len() == before {
            return false;
        }
        if self.active_workspace_id.as_deref() == Some(id) {
            self.active_workspace_id = self
                .workspaces
                .first()
                .map(|workspace| workspace.id.clone());
        }
        true
    }

    pub fn sanitize(&mut self) {
        self.schema_version = SCHEMA_VERSION;
        let mut seen = HashSet::new();
        self.workspaces.retain_mut(|workspace| {
            let path = PathBuf::from(&workspace.root);
            workspace.id = workspace_id(&path);
            workspace.root = display_root(&path);
            if workspace.project_name.trim().is_empty() {
                workspace.project_name = read_project_name(&path);
            }
            if workspace.registered_unix == 0 {
                workspace.registered_unix = now_unix();
            }
            if workspace.updated_unix == 0 {
                workspace.updated_unix = workspace.registered_unix;
            }
            seen.insert(workspace.id.clone())
        });
        if self
            .active_workspace_id
            .as_deref()
            .and_then(|id| self.get(id))
            .is_none()
        {
            self.active_workspace_id = self
                .workspaces
                .first()
                .map(|workspace| workspace.id.clone());
        }
    }
}

fn read_project_name(root: &Path) -> String {
    let state = root.join(".local").join("install-state.json");
    fs::read_to_string(state)
        .ok()
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok())
        .and_then(|value| value.get("projectName")?.as_str().map(str::to_owned))
        .filter(|name| !name.trim().is_empty())
        .or_else(|| {
            root.file_name()
                .map(|name| name.to_string_lossy().into_owned())
        })
        .unwrap_or_else(|| "Рабочая среда AI OS".into())
}

fn display_root(path: &Path) -> String {
    let resolved = fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf());
    resolved
        .to_string_lossy()
        .trim_start_matches(r"\\?\")
        .trim_end_matches(['\\', '/'])
        .to_string()
}

fn normalized_root(path: &Path) -> String {
    #[cfg(windows)]
    {
        display_root(path).replace('/', "\\").to_lowercase()
    }
    #[cfg(not(windows))]
    {
        display_root(path).replace('\\', "/")
    }
}

pub fn workspace_id(path: &Path) -> String {
    let digest = Sha256::digest(normalized_root(path).as_bytes());
    let suffix = digest[..8]
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<String>();
    format!("ws-{suffix}")
}

pub fn memory_library_name(path: &Path) -> String {
    format!("aios-{}", workspace_id(path).trim_start_matches("ws-"))
}

pub fn state_dir() -> PathBuf {
    if let Some(path) = std::env::var_os("AI_OS_SETUP_STATE_DIR") {
        return PathBuf::from(path);
    }
    #[cfg(windows)]
    {
        let base = std::env::var_os("LOCALAPPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        base.join("AI OS Setup")
    }
    #[cfg(not(windows))]
    {
        let base = std::env::var_os("XDG_STATE_HOME")
            .map(PathBuf::from)
            .or_else(|| {
                std::env::var_os("HOME").map(|home| PathBuf::from(home).join(".local/state"))
            })
            .unwrap_or_else(std::env::temp_dir);
        base.join("ai-os")
    }
}

pub fn data_dir() -> PathBuf {
    if let Some(path) = std::env::var_os("AI_OS_SETUP_DATA_DIR") {
        return PathBuf::from(path);
    }
    #[cfg(windows)]
    {
        let base = std::env::var_os("LOCALAPPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        base.join("AI OS")
    }
    #[cfg(not(windows))]
    {
        let base = std::env::var_os("XDG_DATA_HOME")
            .map(PathBuf::from)
            .or_else(|| {
                std::env::var_os("HOME").map(|home| PathBuf::from(home).join(".local/share"))
            })
            .unwrap_or_else(std::env::temp_dir);
        base.join("ai-os")
    }
}

pub fn state_path() -> PathBuf {
    state_dir().join("state.json")
}

pub fn load_registry_from(path: &Path) -> Result<WorkspaceRegistry, String> {
    if !path.is_file() {
        return Ok(WorkspaceRegistry::default());
    }
    let text = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let value: serde_json::Value = serde_json::from_str(text.trim_start_matches('\u{feff}'))
        .map_err(|error| error.to_string())?;

    let mut registry = if value.get("workspaces").is_some() {
        serde_json::from_value::<WorkspaceRegistry>(value).map_err(|error| error.to_string())?
    } else if let Some(root) = value.get("workspaceRoot").and_then(|item| item.as_str()) {
        let path = PathBuf::from(root);
        let mut migrated = WorkspaceRegistry::default();
        migrated.upsert(&path, &read_project_name(&path), true);
        migrated
    } else {
        WorkspaceRegistry::default()
    };
    registry.sanitize();
    Ok(registry)
}

pub fn load_registry() -> Result<WorkspaceRegistry, String> {
    load_registry_from(&state_path())
}

pub fn save_registry_to(path: &Path, registry: &WorkspaceRegistry) -> Result<(), String> {
    let parent = path
        .parent()
        .ok_or("У файла registry нет родительской папки")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    let bytes = serde_json::to_vec_pretty(registry).map_err(|error| error.to_string())?;
    // The supervisor retries transient parse errors. Keeping the path present is
    // safer on Windows than remove-then-rename, which briefly looks like an
    // empty registry to a running supervisor.
    fs::write(path, bytes).map_err(|error| error.to_string())
}

pub fn save_registry(registry: &WorkspaceRegistry) -> Result<(), String> {
    save_registry_to(&state_path(), registry)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;
    use std::fs;

    #[test]
    fn ten_same_named_workspaces_remain_distinct() {
        let mut registry = WorkspaceRegistry::default();
        for index in 0..10 {
            let root = PathBuf::from(format!(r"C:\Projects\Shared name\{index}"));
            registry.upsert(&root, "Одинаковое имя", true);
        }

        let ids: HashSet<_> = registry
            .workspaces
            .iter()
            .map(|workspace| workspace.id.as_str())
            .collect();
        assert_eq!(registry.schema_version, 2);
        assert_eq!(registry.workspaces.len(), 10);
        assert_eq!(ids.len(), 10);
        assert_eq!(
            registry.active_workspace_id.as_deref(),
            registry
                .workspaces
                .last()
                .map(|workspace| workspace.id.as_str())
        );
    }

    #[test]
    fn legacy_single_workspace_state_migrates_without_loss() {
        let root = std::env::temp_dir().join("ai-os-registry-v1-workspace");
        let state = std::env::temp_dir().join("ai-os-registry-v1-state.json");
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_file(&state);
        fs::create_dir_all(root.join(".local")).unwrap();
        fs::write(root.join("AGENTS.md"), "# fixture").unwrap();
        fs::write(
            root.join(".local/install-state.json"),
            r#"{"projectName":"Старый проект"}"#,
        )
        .unwrap();
        let legacy = format!(
            r#"{{"schemaVersion":1,"workspaceRoot":"{}","updatedUnix":1}}"#,
            root.to_string_lossy().replace('\\', "\\\\")
        );
        fs::write(&state, format!("\u{feff}{legacy}")).unwrap();

        let migrated = load_registry_from(&state).unwrap();
        assert_eq!(migrated.schema_version, 2);
        assert_eq!(migrated.workspaces.len(), 1);
        assert_eq!(migrated.workspaces[0].project_name, "Старый проект");
        assert_eq!(migrated.workspaces[0].id, workspace_id(&root));
        assert_eq!(
            migrated.active_workspace_id.as_deref(),
            Some(migrated.workspaces[0].id.as_str())
        );

        let _ = fs::remove_dir_all(root);
        let _ = fs::remove_file(state);
    }
}
