param(
    [switch]$EngineOnly,
    [switch]$DesktopOnly,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$engineRoot = Join-Path $projectRoot "engine"
$desktopRoot = Join-Path $projectRoot "desktop"
$python = Join-Path $engineRoot ".venv\Scripts\python.exe"
$engineDist = Join-Path $engineRoot "dist\whiskyhub-engine.exe"
$sidecarDirectory = Join-Path $desktopRoot "src-tauri\binaries"
$releaseDirectory = Join-Path $projectRoot "release"

function Remove-BuildArtifacts {
    $paths = @(
        (Join-Path $engineRoot "build"),
        (Join-Path $engineRoot "dist"),
        $sidecarDirectory,
        $releaseDirectory
    )

    foreach ($path in $paths) {
        $fullPath = [IO.Path]::GetFullPath($path)
        if (-not $fullPath.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar)) {
            throw "Refusing to delete a path outside the project: $fullPath"
        }
        if (Test-Path -LiteralPath $fullPath) {
            Remove-Item -LiteralPath $fullPath -Recurse -Force
        }
    }
}

if ($Clean) {
    Remove-BuildArtifacts
    Write-Host "[BUILD] Build artifacts removed"
    exit 0
}

if ($EngineOnly -and $DesktopOnly) {
    throw "EngineOnly and DesktopOnly cannot be used together"
}

if (-not $DesktopOnly) {
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "Python virtual environment not found: $python"
    }

    Write-Host "[BUILD] Checking Python dependencies..."
    & $python -m pip install -r (Join-Path $engineRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Failed to install Python dependencies" }

    Write-Host "[BUILD] Building Python Engine..."
    & $python -m PyInstaller `
        --noconfirm `
        --clean `
        --distpath (Join-Path $engineRoot "dist") `
        --workpath (Join-Path $engineRoot "build") `
        (Join-Path $engineRoot "whiskyhub-engine.spec")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
    if (-not (Test-Path -LiteralPath $engineDist -PathType Leaf)) {
        throw "PyInstaller did not create: $engineDist"
    }

    $targetTriple = (& rustc --print host-tuple).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $targetTriple) {
        throw "Failed to determine the Rust target triple"
    }

    New-Item -ItemType Directory -Path $sidecarDirectory -Force | Out-Null
    $sidecar = Join-Path $sidecarDirectory "whiskyhub-engine-$targetTriple.exe"
    Copy-Item -LiteralPath $engineDist -Destination $sidecar -Force
    Write-Host "[BUILD] Sidecar prepared: $sidecar"
}

if ($EngineOnly) {
    exit 0
}

$sidecars = @(Get-ChildItem -LiteralPath $sidecarDirectory -Filter "whiskyhub-engine-*.exe" -ErrorAction SilentlyContinue)
if ($sidecars.Count -eq 0) {
    throw "Sidecar not found. Run make engine or make release first"
}

Write-Host "[BUILD] Installing frontend dependencies..."
Push-Location $desktopRoot
try {
    & pnpm install --frozen-lockfile
    if ($LASTEXITCODE -ne 0) { throw "pnpm install failed" }

    Write-Host "[BUILD] Building the Tauri installer..."
    & pnpm tauri build --bundles nsis
    if ($LASTEXITCODE -ne 0) { throw "Tauri build failed" }
}
finally {
    Pop-Location
}

$bundleDirectory = Join-Path $desktopRoot "src-tauri\target\release\bundle\nsis"
$installer = Get-ChildItem -LiteralPath $bundleDirectory -Filter "*.exe" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $installer) {
    throw "NSIS installer not found: $bundleDirectory"
}

New-Item -ItemType Directory -Path $releaseDirectory -Force | Out-Null
$releaseInstaller = Join-Path $releaseDirectory "WhiskyHub-Setup.exe"
Copy-Item -LiteralPath $installer.FullName -Destination $releaseInstaller -Force
Write-Host "[BUILD] Done: $releaseInstaller"
