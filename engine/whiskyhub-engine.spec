from pathlib import Path
from PyInstaller.utils.hooks import collect_dynamic_libs


engine_root = Path(SPECPATH)
vosk_binaries = collect_dynamic_libs("vosk")

analysis = Analysis(
    [str(engine_root / "main.py")],
    pathex=[str(engine_root)],
    binaries=vosk_binaries,
    datas=[
        (
            str(engine_root / "models" / "vosk-model-small-ru-0.22"),
            "models/vosk-model-small-ru-0.22",
        ),
        (
            str(engine_root / "models" / "piper-tts"),
            "models/piper-tts",
        ),
        (
            str(engine_root / "Dispatcher" / "Data" / "commands.yaml"),
            "Dispatcher/Data",
        ),
        (
            str(engine_root / "Core" / "Storage" / "Data" / "config.json"),
            "Core/Storage/Data",
        ),
    ],
    hiddenimports=["pycaw.pycaw", "comtypes", "sounddevice", "vosk", "piper"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="whiskyhub-engine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
