#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_ROOT="${1:-$ROOT/distribution/workspace-template}"
OUTPUT_DIR="${2:-$ROOT/dist/linux}"
PRODUCT_VERSION="${PRODUCT_VERSION:-0.4.5}"
CONTROL_CENTER_VERSION="${CONTROL_CENTER_VERSION:-0.6.2}"
MEMORY_VERSION="${MEMORY_VERSION:-2.4.0}"
CODE_INTEL_VERSION="${CODE_INTEL_VERSION:-0.9.0}"
POWERSHELL_VERSION="${POWERSHELL_VERSION:-7.6.3}"
TAURI_CLI_VERSION="${TAURI_CLI_VERSION:-2.11.4}"
LINUXDEPLOY_SHA256="e762bea85c8eb0d4b3508d46e5c1f037f717d0f9303ae3b4aafc8b04991fa1ef"
LINUXDEPLOY_GTK_SHA256="cb379f9b0733e9ad9f8bd78f8c2fa038aef2478523bb7d4c8e64ff6a1ea3501a"
APPIMAGE_PLUGIN_SHA256="1da16a46fa5e058ae740e7c35ed0d36d86cb869ac9cc8a5fd9a1847d7978d99a"
BUILD_ROOT="${CARGO_TARGET_DIR:-$ROOT/.local/linux-build}"
APP_ROOT="$ROOT/tools/ai-os-installer-app"
RESOURCES="$APP_ROOT/resources"
DOWNLOADS="$BUILD_ROOT/downloads"
CC_TARGET="$BUILD_ROOT/control-center"
SETUP_TARGET="$BUILD_ROOT/setup"

if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
  echo "AI OS Linux release currently supports Linux x86_64 only." >&2
  exit 2
fi
for command in cargo curl sha256sum tar python3 file iconv dpkg-deb; do
  command -v "$command" >/dev/null || { echo "Missing build dependency: $command" >&2; exit 2; }
done
[[ -f "$TEMPLATE_ROOT/AGENTS.md" ]] || { echo "Sanitized template not found: $TEMPLATE_ROOT" >&2; exit 2; }

template_version="$(grep -m1 -E '^##[[:space:]]+[0-9]+\.[0-9]+\.[0-9]+' "$TEMPLATE_ROOT/CHANGELOG.md" | awk '{print $2}')"
setup_version="$(grep -m1 -E '^version[[:space:]]*=' "$APP_ROOT/Cargo.toml" | cut -d'"' -f2)"
control_version="$(grep -m1 -E '^version[[:space:]]*=' "$ROOT/tools/control-center-app/Cargo.toml" | cut -d'"' -f2)"
control_setup_version="$(grep -m1 -E '^const SETUP_VERSION:' "$ROOT/tools/control-center-app/src/main.rs" | cut -d'"' -f2)"
[[ "$template_version" == "$PRODUCT_VERSION" ]] || { echo "Template $template_version != product $PRODUCT_VERSION" >&2; exit 2; }
[[ "$setup_version" == "$PRODUCT_VERSION" ]] || { echo "Setup Cargo $setup_version != product $PRODUCT_VERSION" >&2; exit 2; }
[[ "$control_version" == "$CONTROL_CENTER_VERSION" ]] || { echo "Control Center Cargo $control_version != expected $CONTROL_CENTER_VERSION" >&2; exit 2; }
[[ "$control_setup_version" == "$PRODUCT_VERSION" ]] || { echo "Control Center Setup contract $control_setup_version != product $PRODUCT_VERSION" >&2; exit 2; }

mkdir -p "$OUTPUT_DIR" "$DOWNLOADS" "$CC_TARGET" "$SETUP_TARGET"
if [[ -e "$RESOURCES" ]]; then
  resolved="$(realpath "$RESOURCES")"
  [[ "$resolved" == "$(realpath "$APP_ROOT")/resources" ]] || { echo "Unsafe resources path: $resolved" >&2; exit 2; }
  rm -rf -- "$resolved"
fi
mkdir -p "$RESOURCES/workspace-template" "$RESOURCES/memory-tool" "$RESOURCES/code-intel-tool" "$RESOURCES/powershell"

copy_template() {
  (cd "$TEMPLATE_ROOT" && tar \
    --exclude='./.git' --exclude='./.local' --exclude='./target' --exclude='./gen' \
    --exclude='./resources' --exclude='./tools/ai-os-installer-app/resources' \
    --exclude='./tools/control-center-app/bin' \
    --exclude='./tools/ai_os.config.json' --exclude='./.mcp.json' \
    -cf - .) | (cd "$RESOURCES/workspace-template" && tar -xf -)
}

download() {
  local url="$1" destination="$2"
  [[ -f "$destination" ]] || curl --fail --location --retry 3 --output "$destination" "$url"
}

verify_from_sums() {
  local file="$1" sums="$2" asset="$3"
  local expected actual sums_input="$sums"
  if [[ "$(file -b --mime-encoding "$sums")" == "utf-16le" ]]; then
    sums_input="${sums}.utf8"
    iconv -f UTF-16LE -t UTF-8 "$sums" | tr -d '\r' > "$sums_input"
  fi
  expected="$(awk -v asset="$asset" '$NF == asset || $NF == "*" asset { print $1; exit }' "$sums_input")"
  [[ -n "$expected" ]] || { echo "Checksum for $asset not found in $sums" >&2; exit 2; }
  actual="$(sha256sum "$file" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || { echo "Checksum mismatch for $asset" >&2; exit 2; }
}

verify_sha256() {
  local file="$1" expected="$2"
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || { echo "Checksum mismatch for $file" >&2; exit 2; }
}

echo "[1/8] Staging sanitized template"
copy_template
cp "$ROOT/tools/install_ai_os_workspace.ps1" "$RESOURCES/install_ai_os_workspace.ps1"
cp "$ROOT/tools/ai_os_package_cache.psm1" "$RESOURCES/ai_os_package_cache.psm1"
cp "$ROOT/tools/ai_os_supervisor.ps1" "$RESOURCES/ai_os_supervisor.ps1"
cp "$ROOT/tools/install_ai_os_supervisor_linux.ps1" "$RESOURCES/install_ai_os_supervisor_linux.ps1"

echo "[2/8] Building Linux Control Center $CONTROL_CENTER_VERSION"
if [[ "${AI_OS_REUSE_CONTROL_CENTER:-0}" == "1" ]]; then
  [[ -x "$CC_TARGET/release/ai-os-control-center" ]] || {
    echo "Requested Control Center reuse, but no verified binary exists" >&2
    exit 2
  }
  echo "Reusing the locally verified Control Center binary"
else
  CARGO_TARGET_DIR="$CC_TARGET" cargo test --manifest-path "$ROOT/tools/control-center-app/Cargo.toml"
  CARGO_TARGET_DIR="$CC_TARGET" cargo build --release --manifest-path "$ROOT/tools/control-center-app/Cargo.toml"
fi
mkdir -p "$RESOURCES/workspace-template/tools/control-center-app/bin"
cp "$CC_TARGET/release/ai-os-control-center" "$RESOURCES/workspace-template/tools/control-center-app/bin/ai-os-control-center"
chmod 755 "$RESOURCES/workspace-template/tools/control-center-app/bin/ai-os-control-center"

echo "[3/8] Downloading verified runtime tools"
mgi_asset="mgimind-x86_64-unknown-linux-gnu.tar.gz"
mgi_dir="$DOWNLOADS/mgimind-$MEMORY_VERSION"
mkdir -p "$mgi_dir/extracted"
download "https://github.com/madgodinc/mgi-mind/releases/download/v$MEMORY_VERSION/$mgi_asset" "$mgi_dir/$mgi_asset"
download "https://github.com/madgodinc/mgi-mind/releases/download/v$MEMORY_VERSION/$mgi_asset.sha256" "$mgi_dir/$mgi_asset.sha256"
verify_from_sums "$mgi_dir/$mgi_asset" "$mgi_dir/$mgi_asset.sha256" "$mgi_asset"
tar -xzf "$mgi_dir/$mgi_asset" -C "$mgi_dir/extracted"
mgi_binary="$(find "$mgi_dir/extracted" -type f -name mgimind -print -quit)"
[[ -n "$mgi_binary" ]] || { echo "MGI-Mind archive has no mgimind binary" >&2; exit 2; }
cp "$mgi_binary" "$RESOURCES/memory-tool/mgimind"
chmod 755 "$RESOURCES/memory-tool/mgimind"
download "https://raw.githubusercontent.com/madgodinc/mgi-mind/v$MEMORY_VERSION/LICENSE" "$RESOURCES/memory-tool/LICENSE.txt"

code_asset="codebase-memory-mcp-linux-amd64-portable.tar.gz"
code_dir="$DOWNLOADS/codebase-memory-$CODE_INTEL_VERSION"
mkdir -p "$code_dir/extracted"
download "https://github.com/DeusData/codebase-memory-mcp/releases/download/v$CODE_INTEL_VERSION/$code_asset" "$code_dir/$code_asset"
download "https://github.com/DeusData/codebase-memory-mcp/releases/download/v$CODE_INTEL_VERSION/checksums.txt" "$code_dir/checksums.txt"
verify_from_sums "$code_dir/$code_asset" "$code_dir/checksums.txt" "$code_asset"
tar -xzf "$code_dir/$code_asset" -C "$code_dir/extracted"
code_binary="$(find "$code_dir/extracted" -type f -name codebase-memory-mcp -print -quit)"
[[ -n "$code_binary" ]] || { echo "codebase-memory archive has no binary" >&2; exit 2; }
cp "$code_binary" "$RESOURCES/code-intel-tool/codebase-memory-mcp"
chmod 755 "$RESOURCES/code-intel-tool/codebase-memory-mcp"
download "https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/v$CODE_INTEL_VERSION/LICENSE" "$RESOURCES/code-intel-tool/LICENSE.txt"

pwsh_asset="powershell-$POWERSHELL_VERSION-linux-x64.tar.gz"
pwsh_dir="$DOWNLOADS/powershell-$POWERSHELL_VERSION"
mkdir -p "$pwsh_dir/extracted"
download "https://github.com/PowerShell/PowerShell/releases/download/v$POWERSHELL_VERSION/$pwsh_asset" "$pwsh_dir/$pwsh_asset"
download "https://github.com/PowerShell/PowerShell/releases/download/v$POWERSHELL_VERSION/hashes.sha256" "$pwsh_dir/hashes.sha256"
verify_from_sums "$pwsh_dir/$pwsh_asset" "$pwsh_dir/hashes.sha256" "$pwsh_asset"
tar -xzf "$pwsh_dir/$pwsh_asset" -C "$pwsh_dir/extracted"
cp -a "$pwsh_dir/extracted/." "$RESOURCES/powershell/"
chmod 755 "$RESOURCES/powershell/pwsh"

echo "[4/8] Writing verifiable payload manifest"
PRODUCT_VERSION="$PRODUCT_VERSION" TEMPLATE_VERSION="$template_version" MEMORY_VERSION="$MEMORY_VERSION" \
CODE_INTEL_VERSION="$CODE_INTEL_VERSION" POWERSHELL_VERSION="$POWERSHELL_VERSION" RESOURCES="$RESOURCES" \
python3 - <<'PY'
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["RESOURCES"])
def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    "schemaVersion": 2,
    "productVersion": os.environ["PRODUCT_VERSION"],
    "templateVersion": os.environ["TEMPLATE_VERSION"],
    "distributionMode": "offline",
    "createdUtc": datetime.now(timezone.utc).isoformat(),
    "platform": "linux-x86_64",
    "author": "Denis Labyntsev (@Ludosiel)",
    "memoryTool": {
        "name": "MGI-Mind", "version": os.environ["MEMORY_VERSION"],
        "source": f"https://github.com/madgodinc/mgi-mind/releases/tag/v{os.environ['MEMORY_VERSION']}",
        "sha256": digest(root / "memory-tool" / "mgimind"),
        "binarySizeBytes": (root / "memory-tool" / "mgimind").stat().st_size,
    },
    "codeIntelligence": {
        "name": "codebase-memory-mcp", "version": os.environ["CODE_INTEL_VERSION"],
        "source": f"https://github.com/DeusData/codebase-memory-mcp/releases/tag/v{os.environ['CODE_INTEL_VERSION']}",
        "sha256": digest(root / "code-intel-tool" / "codebase-memory-mcp"),
        "binarySizeBytes": (root / "code-intel-tool" / "codebase-memory-mcp").stat().st_size,
    },
    "powershell": {
        "version": os.environ["POWERSHELL_VERSION"],
        "source": f"https://github.com/PowerShell/PowerShell/releases/tag/v{os.environ['POWERSHELL_VERSION']}",
        "sha256": digest(root / "powershell" / "pwsh"),
    },
}
(root / "PAYLOAD_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

privacy_args=(
  --include='*.md' --include='*.json' --include='*.ps1' --include='*.sh' --include='*.toml'
  --exclude='build_ai_os_installer.ps1' --exclude='build_ai_os_linux.sh'
)
privacy_hits="$(grep -RInE '([[:alpha:]]:\\Users\\[^\\[:space:]]+|/home/[^/[:space:]]+)' \
  "${privacy_args[@]}" "$RESOURCES/workspace-template" || true)"
private_pattern_file="$ROOT/.local/private-template-patterns.txt"
if [[ -f "$private_pattern_file" ]]; then
  private_hits="$(grep -RInF -f "$private_pattern_file" \
    "${privacy_args[@]}" "$RESOURCES/workspace-template" || true)"
  privacy_hits="${privacy_hits}${privacy_hits:+$'\n'}${private_hits}"
fi
unexpected_privacy_hits="$(printf '%s\n' "$privacy_hits" | grep -vE 'Denis Labyntsev|@Ludosiel' || true)"
if [[ -n "$unexpected_privacy_hits" ]]; then
  printf '%s\n' "$unexpected_privacy_hits" >&2
  echo "Sanitization check found live-project context in Linux payload" >&2
  exit 2
fi

echo "[5/8] Testing Linux workspace installation"
pwsh="$RESOURCES/powershell/pwsh"
"$pwsh" -NoProfile -File "$ROOT/tools/tests/test_app_icons.ps1" -Root "$ROOT"
"$pwsh" -NoProfile -File "$RESOURCES/workspace-template/tools/check_ai_os_readiness.ps1" \
  -Root "$RESOURCES/workspace-template" -SkipHealth
fixture="$BUILD_ROOT/workspace-contract"
rm -rf -- "$fixture"
"$pwsh" -NoProfile -File "$RESOURCES/install_ai_os_workspace.ps1" \
  -SourceRoot "$RESOURCES/workspace-template" -DestinationRoot "$fixture" \
  -ProjectName 'Linux contract' -UserName 'Test User' -ProjectSummary 'Linux installation contract workspace' \
  -MemoryLibraryName 'linux-contract' -PowerShellRuntimeSource "$RESOURCES/powershell" \
  -SetupExecutablePath '/usr/bin/ai-os-workspace-manager' \
  -SkipMemory -SkipCodeIntelligence -SkipScheduledTasks -SkipGit
test -f "$fixture/AGENTS.md"
test -f "$fixture/tools/ai_os.config.json"
grep -q 'linux-contract' "$fixture/tools/ai_os.config.json"
rm -rf -- "$fixture"

# Readiness writes runtime logs under .local. They are useful to the build
# contract, but must never become part of a clean workspace distribution.
generated_local="$RESOURCES/workspace-template/.local"
if [[ -e "$generated_local" ]]; then
  [[ "$(realpath -m "$generated_local")" == "$(realpath -m "$RESOURCES/workspace-template")/.local" ]] || {
    echo "Unsafe generated .local path: $generated_local" >&2
    exit 2
  }
  rm -rf -- "$generated_local"
fi

echo "[6/8] Building Setup tests and bundles"
CARGO_TARGET_DIR="$SETUP_TARGET" AI_OS_SETUP_RESOURCE_DIR="$RESOURCES" cargo test --manifest-path "$APP_ROOT/Cargo.toml"
if ! command -v cargo-tauri >/dev/null 2>&1; then
  cargo install tauri-cli --version "$TAURI_CLI_VERSION" --locked
fi
(cd "$APP_ROOT" && CARGO_TARGET_DIR="$SETUP_TARGET" cargo tauri build --config tauri.linux.conf.json --bundles deb)

# linuxdeploy treats every executable resource as part of the UI dependency
# graph. Build the AppDir from the verified deb, hide the payload while GTK
# dependencies are deployed, then restore it before the final squashfs pass.
appimage_bundle="$SETUP_TARGET/release/bundle/appimage"
bundle_parent="$(realpath -m "$SETUP_TARGET/release/bundle")"
expected_appimage_bundle="$bundle_parent/appimage"
[[ "$(realpath -m "$appimage_bundle")" == "$(realpath -m "$expected_appimage_bundle")" ]] || {
  echo "Unsafe AppImage bundle path: $appimage_bundle" >&2
  exit 2
}
rm -rf -- "$appimage_bundle"
mkdir -p "$appimage_bundle"
deb="$(find "$SETUP_TARGET/release/bundle/deb" -maxdepth 1 -type f -name '*.deb' -print -quit)"
[[ -n "$deb" ]] || { echo "Tauri did not create the deb package" >&2; exit 2; }

# Ubuntu 22.04 reliably supports xz-compressed deb archives. Repack explicitly
# instead of inheriting the build host's dpkg default (which can be zstd).
deb_repack="$(mktemp -d)"
cleanup_deb_repack() {
  rm -rf -- "$deb_repack"
}
trap cleanup_deb_repack EXIT
dpkg-deb -R "$deb" "$deb_repack/root"
dpkg-deb -Zxz -z6 -b --root-owner-group "$deb_repack/root" "$deb_repack/ai-os.deb"
cp "$deb_repack/ai-os.deb" "$deb"
cleanup_deb_repack
trap - EXIT

appdir="$appimage_bundle/AI OS.AppDir"
dpkg-deb -x "$deb" "$appdir"

appimage_tools="$DOWNLOADS/appimage-tools"
mkdir -p "$appimage_tools"
linuxdeploy="$appimage_tools/linuxdeploy-x86_64.AppImage"
gtk_plugin="$appimage_tools/linuxdeploy-plugin-gtk.sh"
appimage_plugin="$appimage_tools/linuxdeploy-plugin-appimage.AppImage"
download "https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-x86_64.AppImage" "$linuxdeploy"
download "https://raw.githubusercontent.com/tauri-apps/linuxdeploy-plugin-gtk/master/linuxdeploy-plugin-gtk.sh" "$gtk_plugin"
download "https://github.com/linuxdeploy/linuxdeploy-plugin-appimage/releases/download/continuous/linuxdeploy-plugin-appimage-x86_64.AppImage" "$appimage_plugin"
verify_sha256 "$linuxdeploy" "$LINUXDEPLOY_SHA256"
verify_sha256 "$gtk_plugin" "$LINUXDEPLOY_GTK_SHA256"
verify_sha256 "$appimage_plugin" "$APPIMAGE_PLUGIN_SHA256"
chmod 755 "$linuxdeploy" "$gtk_plugin" "$appimage_plugin"

payload_path="$appdir/usr/lib/AI OS/resources"
payload_stash="$appimage_bundle/payload-resources-stash"
[[ -d "$payload_path" && ! -e "$payload_stash" ]] || { echo "Invalid AppImage payload staging state" >&2; exit 2; }
restore_appdir_payload() {
  if [[ -d "$payload_stash" ]]; then
    mkdir -p "$(dirname "$payload_path")"
    rm -rf -- "$payload_path"
    mv -- "$payload_stash" "$payload_path"
  fi
}
mv -- "$payload_path" "$payload_stash"
trap restore_appdir_payload EXIT
PATH="$appimage_tools:$PATH" "$linuxdeploy" --appimage-extract-and-run --verbosity 2 \
  --appdir "$appdir" \
  --executable "$appdir/usr/bin/ai-os-workspace-manager" \
  --desktop-file "$appdir/usr/share/applications/AI OS.desktop" \
  --icon-file "$appdir/usr/share/icons/hicolor/128x128/apps/ai-os-workspace-manager.png" \
  --plugin gtk
restore_appdir_payload
trap - EXIT
(cd "$appimage_bundle" && ARCH=x86_64 "$appimage_plugin" --appimage-extract-and-run --appdir="$appdir")

raw_setup="$SETUP_TARGET/release/ai-os-workspace-manager"
AI_OS_SETUP_RESOURCE_DIR="$RESOURCES" "$raw_setup" --selftest
AI_OS_ROOT="$RESOURCES/workspace-template" "$RESOURCES/workspace-template/tools/control-center-app/bin/ai-os-control-center" --selftest
"$raw_setup" --render-setup-html "$BUILD_ROOT/setup-linux.html"
AI_OS_ROOT="$RESOURCES/workspace-template" "$RESOURCES/workspace-template/tools/control-center-app/bin/ai-os-control-center" --render-pages "$BUILD_ROOT/control-center-pages"
[[ ! -e "$RESOURCES/workspace-template/.local" ]] || {
  echo "Generated .local content leaked back into the Linux payload" >&2
  exit 2
}

echo "[7/8] Publishing Linux artifacts"
appimage="$(find "$appimage_bundle" -maxdepth 1 -type f -name '*.AppImage' -print -quit)"
[[ -n "$appimage" && -n "$deb" ]] || { echo "Tauri did not create both AppImage and deb" >&2; exit 2; }
final_appimage="$OUTPUT_DIR/AI_OS_Setup_v${PRODUCT_VERSION}_linux_x86_64.AppImage"
final_deb="$OUTPUT_DIR/AI_OS_Setup_v${PRODUCT_VERSION}_linux_x86_64.deb"
cp "$appimage" "$final_appimage"
cp "$deb" "$final_deb"
chmod 755 "$final_appimage"

"$final_appimage" --appimage-extract-and-run --selftest
deb_selftest="$BUILD_ROOT/deb-selftest"
[[ "$(realpath -m "$deb_selftest")" == "$(realpath -m "$BUILD_ROOT")/deb-selftest" ]] || {
  echo "Unsafe deb selftest path: $deb_selftest" >&2
  exit 2
}
rm -rf -- "$deb_selftest"
dpkg-deb -x "$final_deb" "$deb_selftest"
"$deb_selftest/usr/bin/ai-os-workspace-manager" --selftest
rm -rf -- "$deb_selftest"

fallback="$OUTPUT_DIR/AI_OS_TEMPLATE_KIT_v${PRODUCT_VERSION}_linux_x86_64.tar.gz"
tar -czf "$fallback" -C "$RESOURCES" workspace-template memory-tool code-intel-tool powershell install_ai_os_workspace.ps1 ai_os_package_cache.psm1 ai_os_supervisor.ps1 install_ai_os_supervisor_linux.ps1 PAYLOAD_MANIFEST.json
(cd "$OUTPUT_DIR" && sha256sum "$(basename "$final_appimage")" "$(basename "$final_deb")" "$(basename "$fallback")" > SHA256SUMS-linux.txt)

echo "[8/8] Linux release complete"
ls -lh "$final_appimage" "$final_deb" "$fallback" "$OUTPUT_DIR/SHA256SUMS-linux.txt"
