use std::sync::Mutex;

#[cfg(debug_assertions)]
use std::process::{Child, Command};
#[cfg(all(debug_assertions, target_os = "windows"))]
use std::os::windows::process::CommandExt;
use tauri::{Manager, RunEvent};
#[cfg(not(debug_assertions))]
use tauri_plugin_shell::{process::CommandChild, ShellExt};

enum EngineProcess {
    #[cfg(debug_assertions)]
    Development(Child),
    #[cfg(not(debug_assertions))]
    Sidecar(CommandChild),
}

impl EngineProcess {
    fn stop(self) -> Result<(), String> {
        match self {
            #[cfg(debug_assertions)]
            Self::Development(mut child) => {
                child.kill().map_err(|error| error.to_string())?;
                let _ = child.wait();
                Ok(())
            }
            #[cfg(not(debug_assertions))]
            Self::Sidecar(child) => child.kill().map_err(|error| error.to_string()),
        }
    }
}

#[derive(Default)]
struct EngineState {
    process: Mutex<Option<EngineProcess>>,
}

#[tauri::command]
fn start_engine(
    #[allow(unused_variables)]
    app: tauri::AppHandle,
    state: tauri::State<'_, EngineState>,
) -> Result<bool, String> {
    let mut process = state
        .process
        .lock()
        .map_err(|_| "Не удалось получить состояние WhiskyHub Engine".to_string())?;

    if let Some(_engine_process) = process.as_mut() {
        #[cfg(debug_assertions)]
        if let EngineProcess::Development(child) = _engine_process {
            if child.try_wait().map_err(|error| error.to_string())?.is_some() {
                *process = None;
            } else {
                return Ok(false);
            }
        }

        #[cfg(not(debug_assertions))]
        return Ok(false);
    }

    #[cfg(debug_assertions)]
    {
    let project_root = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .map_err(|error| format!("Не найден каталог проекта: {error}"))?;
    let python = project_root.join("engine/.venv/Scripts/python.exe");
    let engine = project_root.join("engine/main.py");

    if !python.is_file() {
        return Err(format!("Python не найден: {}", python.display()));
    }
    if !engine.is_file() {
        return Err(format!("WhiskyHub Engine не найден: {}", engine.display()));
    }

    let mut command = Command::new(python);
    command.arg(engine).current_dir(project_root);

    #[cfg(target_os = "windows")]
    command.creation_flags(0x08000000);

    let child = command
        .spawn()
        .map_err(|error| format!("Не удалось запустить WhiskyHub Engine: {error}"))?;
    *process = Some(EngineProcess::Development(child));
    }

    #[cfg(not(debug_assertions))]
    {
        let sidecar = app
            .shell()
            .sidecar("whiskyhub-engine")
            .map_err(|error| format!("Не удалось найти Python sidecar: {error}"))?;
        let (_events, child) = sidecar
            .spawn()
            .map_err(|error| format!("Не удалось запустить Python sidecar: {error}"))?;
        *process = Some(EngineProcess::Sidecar(child));
    }

    Ok(true)
}

#[tauri::command]
fn stop_engine(state: tauri::State<'_, EngineState>) -> Result<bool, String> {
    let mut process = state
        .process
        .lock()
        .map_err(|_| "Не удалось получить состояние WhiskyHub Engine".to_string())?;

    let Some(engine_process) = process.take() else {
        return Ok(false);
    };

    engine_process
        .stop()
        .map_err(|error| format!("Не удалось остановить WhiskyHub Engine: {error}"))?;
    Ok(true)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .manage(EngineState::default())
        .invoke_handler(tauri::generate_handler![start_engine, stop_engine])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|app_handle, event| {
        if let RunEvent::Exit = event {
            let state = app_handle.state::<EngineState>();
            if let Ok(mut process) = state.process.lock() {
                if let Some(engine_process) = process.take() {
                    let _ = engine_process.stop();
                }
            };
        }
    });
}
