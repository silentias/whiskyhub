.PHONY: release engine desktop clean

release:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-release.ps1

engine:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-release.ps1 -EngineOnly

desktop:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-release.ps1 -DesktopOnly

clean:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-release.ps1 -Clean
