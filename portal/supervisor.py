"""
Homelab System & Service Supervisor for OmniForge Mission Control.
Provides cross-platform telemetry (CPU, RAM, Disk), systemd service management,
live journalctl log streaming, and Antigravity CLI prompt dispatching.
"""

import asyncio
import os
import platform
import shutil
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import psutil

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


class HomelabSupervisor:
    """Manages system metrics, background services, log streams, and agent tasks."""

    def __init__(self, monitored_services: Optional[List[str]] = None):
        self.monitored_services = monitored_services or ["omniforge.service"]
        self.is_linux = platform.system() == "Linux"
        self.systemctl_bin = shutil.which("systemctl")
        self.journalctl_bin = shutil.which("journalctl")
        self.agy_bin = (
            shutil.which("agy")
            or str(Path.home() / ".local" / "bin" / "agy")
            or str(Path.home() / ".gemini" / "bin" / "agy")
        )

    def get_system_metrics(self) -> Dict[str, Any]:
        """Returns comprehensive host CPU, RAM, disk, and load average telemetry."""
        cpu_pct = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        boot_ts = psutil.boot_time()
        uptime_sec = int(time.time() - boot_ts)

        load_avg = []
        if hasattr(os, "getloadavg"):
            try:
                load_avg = list(os.getloadavg())
            except Exception:
                load_avg = []

        return {
            "status": "healthy",
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "uptime_seconds": uptime_sec,
            "cpu": {
                "percent": cpu_pct,
                "cores_logical": psutil.cpu_count(logical=True),
                "cores_physical": psutil.cpu_count(logical=False),
                "load_avg": load_avg,
            },
            "memory": {
                "total_mb": round(vm.total / (1024 * 1024), 1),
                "used_mb": round(vm.used / (1024 * 1024), 1),
                "available_mb": round(vm.available / (1024 * 1024), 1),
                "percent": vm.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 1),
                "used_gb": round(disk.used / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1),
                "percent": disk.percent,
            },
            "timestamp": time.time(),
        }

    async def get_service_status(self, service_name: str = "omniforge.service") -> Dict[str, Any]:
        """Inspects status of a managed system service."""
        # Linux systemd check
        if self.is_linux and self.systemctl_bin:
            try:
                proc = await asyncio.create_subprocess_exec(
                    self.systemctl_bin, "is-active", service_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                active_state = stdout.decode().strip()
                is_active = (active_state == "active")

                # Get PID and memory if active
                pid = None
                memory_mb = 0.0
                if is_active:
                    p_show = await asyncio.create_subprocess_exec(
                        self.systemctl_bin, "show", service_name, "--property=MainPID",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    out_show, _ = await p_show.communicate()
                    show_str = out_show.decode().strip()
                    if "MainPID=" in show_str:
                        pid_str = show_str.split("MainPID=")[1].strip()
                        if pid_str.isdigit() and int(pid_str) > 0:
                            pid = int(pid_str)
                            try:
                                p = psutil.Process(pid)
                                memory_mb = round(p.memory_info().rss / (1024 * 1024), 1)
                            except Exception:
                                pass

                return {
                    "service": service_name,
                    "state": active_state,
                    "active": is_active,
                    "pid": pid,
                    "memory_mb": memory_mb,
                    "backend": "systemd",
                }
            except Exception as e:
                return {
                    "service": service_name,
                    "state": "error",
                    "active": False,
                    "error": str(e),
                    "backend": "systemd",
                }

        # Fallback for macOS / non-systemd environments (detect via process table)
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info.get("cmdline") or [])
                if "main.py" in cmdline and "--run" in cmdline:
                    mem = round(proc.memory_info().rss / (1024 * 1024), 1)
                    return {
                        "service": service_name,
                        "state": "active",
                        "active": True,
                        "pid": proc.info["pid"],
                        "memory_mb": mem,
                        "backend": "process_scan",
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "service": service_name,
            "state": "inactive",
            "active": False,
            "pid": None,
            "memory_mb": 0.0,
            "backend": "process_scan",
        }

    async def control_service(self, service_name: str, action: str) -> Dict[str, Any]:
        """Executes start, stop, or restart on a service."""
        action = action.lower().strip()
        if action not in ("start", "stop", "restart"):
            return {"status": "error", "message": f"Unsupported action: {action}"}

        if self.is_linux and self.systemctl_bin:
            try:
                cmd = ["sudo", self.systemctl_bin, action, service_name]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await proc.communicate()
                if proc.returncode == 0:
                    status = await self.get_service_status(service_name)
                    return {"status": "success", "action": action, "service": status}
                return {"status": "error", "message": stderr.decode().strip()}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {
            "status": "error",
            "message": "Direct service lifecycle control is only supported in Linux systemd environments.",
        }

    async def stream_service_logs(
        self, service_name: str = "omniforge.service", lines: int = 50
    ) -> AsyncGenerator[str, None]:
        """Asynchronously streams journalctl logs line-by-line."""
        if self.is_linux and self.journalctl_bin:
            proc = await asyncio.create_subprocess_exec(
                self.journalctl_bin,
                "-u", service_name,
                "-n", str(lines),
                "-f",
                "-o", "cat",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            try:
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    yield line.decode(errors="replace").rstrip()
            finally:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
        else:
            # Fallback mock/dev log stream for macOS/local testing
            yield f"[Dev Supervisor] Connected to log stream for {service_name}."
            yield f"[Dev Supervisor] Host system: {platform.system()} {platform.release()}"
            counter = 0
            while True:
                await asyncio.sleep(2.0)
                counter += 1
                yield f"[{time.strftime('%X')}] Heartbeat tick #{counter} - Service {service_name} idle."

    async def list_recent_assets(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lists generated audio stories and video clips in output/."""
        if not OUTPUT_DIR.exists():
            return []

        files = []
        for f in sorted(OUTPUT_DIR.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True):
            if f.name.startswith("."):
                continue
            suffix = f.suffix.lower()
            if suffix not in (".mp3", ".mp4", ".wav", ".json"):
                continue

            stat = f.stat()
            files.append({
                "filename": f.name,
                "path": str(f),
                "url": f"/api/assets/{f.name}",
                "size_kb": round(stat.st_size / 1024, 1),
                "modified_ts": stat.st_mtime,
                "modified_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                "type": "audio" if suffix in (".mp3", ".wav") else "video" if suffix == ".mp4" else "data",
            })
            if len(files) >= limit:
                break
        return files

    async def run_agent_prompt(
        self, prompt: str, cwd: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Dispatches a prompt task to Antigravity CLI and streams the stdout."""
        target_dir = cwd or str(BASE_DIR)
        cmd = [self.agy_bin, "--dangerously-skip-permissions", "-p", prompt]

        if not Path(self.agy_bin).exists() and not shutil.which(self.agy_bin):
            yield f"❌ Antigravity CLI binary not found at '{self.agy_bin}'."
            return

        yield f"🚀 Launching agent task inside {target_dir}..."
        yield f"💬 Prompt: \"{prompt}\"\n"

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=target_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                yield line.decode(errors="replace").rstrip()
            await proc.wait()
            yield f"\n🏁 Task completed with exit code {proc.returncode}."
        finally:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
