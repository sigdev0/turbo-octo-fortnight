"""
Homelab System & Service Supervisor for OmniForge Mission Control.
Provides cross-platform telemetry (CPU, RAM, Disk), systemd service management,
live journalctl log streaming, and Antigravity CLI prompt dispatching.
"""

import asyncio
import json
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
        self.is_windows = platform.system() == "Windows"
        self.systemctl_bin = shutil.which("systemctl")
        self.journalctl_bin = shutil.which("journalctl")
        self.agy_bin = (
            shutil.which("agy.cmd")
            or shutil.which("agy.exe")
            or shutil.which("agy")
            or str(Path.home() / "AppData" / "Roaming" / "npm" / "agy.cmd")
            or str(Path.home() / ".local" / "bin" / "agy")
            or str(Path.home() / ".gemini" / "bin" / "agy.cmd")
            or str(Path.home() / ".gemini" / "bin" / "agy.exe")
            or str(Path.home() / ".gemini" / "bin" / "agy")
        )
        self.data_dir = BASE_DIR / "data"
        self.logs_dir = BASE_DIR / "logs"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.data_dir / "portal_agent_session.json"
        self.pid_file = self.data_dir / "omniforge.pid"
        self.log_file = self.logs_dir / "omniforge.log"
        self.active_conversation_id: Optional[str] = None
        self.session_history: List[Dict[str, Any]] = []
        self._load_agent_session()

    def _load_agent_session(self) -> None:
        """Loads persistent session state and history across device connections."""
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text(encoding="utf-8"))
                self.active_conversation_id = data.get("active_conversation_id")
                self.session_history = data.get("history", [])
            except Exception:
                self.active_conversation_id = None
                self.session_history = []

    def _save_agent_session(self) -> None:
        """Persists session state and last 50 turns."""
        try:
            payload = {
                "active_conversation_id": self.active_conversation_id,
                "history": self.session_history[-50:],
                "updated_at": time.time()
            }
            self.session_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_agent_session(self) -> Dict[str, Any]:
        """Returns the current active conversation metadata and transcript history."""
        return {
            "conversation_id": self.active_conversation_id,
            "history": self.session_history,
            "turns_count": len(self.session_history),
        }

    def clear_agent_session(self) -> Dict[str, Any]:
        """Resets active conversation to start fresh."""
        self.active_conversation_id = None
        self.session_history = []
        self._save_agent_session()
        return {"status": "success", "message": "Cleared session. Next prompt will start a new conversation."}

    def get_agent_limits(self) -> Dict[str, Any]:
        """
        Calculates 5-hour rolling limit and weekly limit quota estimates
        based on in-memory session telemetry, matching the Antigravity Desktop UX.
        """
        now = time.time()
        five_hours_ago = now - (5 * 3600)
        seven_days_ago = now - (7 * 86400)

        # Count prompts in 5-hour rolling window
        recent_5h = [t for t in self.session_history if t.get("timestamp", 0) >= five_hours_ago]
        used_5h = len(recent_5h)
        budget_5h = 50  # Standard prompt budget per 5-hour burst window
        rem_5h_pct = max(0, min(100, int(((budget_5h - used_5h) / budget_5h) * 100)))

        # Calculate time until reset of the oldest prompt in the window
        if recent_5h:
            oldest_ts = min(t.get("timestamp", now) for t in recent_5h)
            diff_sec = max(0, int((oldest_ts + (5 * 3600)) - now))
            hrs, mins = divmod(diff_sec // 60, 60)
            resets_5h_str = f"Resets in {hrs}h {mins}m"
        else:
            resets_5h_str = "Resets in 5h 0m (Window clear)"

        # Count prompts in 7-day window
        recent_7d = [t for t in self.session_history if t.get("timestamp", 0) >= seven_days_ago]
        used_7d = len(recent_7d)
        budget_7d = 250  # Standard weekly prompt budget
        rem_7d_pct = max(0, min(100, int(((budget_7d - used_7d) / budget_7d) * 100)))

        # Next weekly reset (Sunday midnight)
        days_until_sunday = (6 - time.localtime().tm_wday) % 7
        if days_until_sunday == 0:
            resets_7d_str = "Resets tonight at 00:00"
        else:
            resets_7d_str = f"Resets in {days_until_sunday} day{'s' if days_until_sunday > 1 else ''} (Sunday)"

        return {
            "status": "healthy",
            "tier": "Standard Tier",
            "five_hour": {
                "percent_remaining": rem_5h_pct,
                "used": used_5h,
                "budget": budget_5h,
                "resets_in": resets_5h_str,
            },
            "weekly": {
                "percent_remaining": rem_7d_pct,
                "used": used_7d,
                "budget": budget_7d,
                "resets_on": resets_7d_str,
            },
            "throttling": False,
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Returns comprehensive host CPU, RAM, disk, and load average telemetry."""
        cpu_pct = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        root_path = BASE_DIR.anchor if self.is_windows else "/"
        disk = psutil.disk_usage(root_path)
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

        # Cross-platform / Windows: check PID file
        if self.pid_file.exists():
            try:
                pid_cand = int(self.pid_file.read_text().strip())
                if psutil.pid_exists(pid_cand):
                    p = psutil.Process(pid_cand)
                    if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                        mem = round(p.memory_info().rss / (1024 * 1024), 1)
                        return {
                            "service": service_name,
                            "state": "active",
                            "active": True,
                            "pid": pid_cand,
                            "memory_mb": mem,
                            "backend": "pidfile",
                        }
            except Exception:
                pass

        # Fallback: scan process table for active bot runner
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info.get("cmdline") or [])
                if ("core.bot" in cmdline or "main.py" in cmdline) and proc.info["pid"] != os.getpid():
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
            "backend": "pidfile" if self.is_windows else "process_scan",
        }

    async def control_service(self, service_name: str, action: str) -> Dict[str, Any]:
        """Executes start, stop, or restart on a service."""
        import subprocess
        import sys

        action = action.lower().strip()
        if action not in ("start", "stop", "restart"):
            return {"status": "error", "message": f"Unsupported action: {action}"}

        # Linux systemd environment
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

        # Windows / Non-systemd background process supervisor
        if action == "start":
            current = await self.get_service_status(service_name)
            if current.get("active"):
                return {"status": "success", "action": "start", "message": "Service already running.", "service": current}

            with open(self.log_file, "a", encoding="utf-8") as lf:
                lf.write(f"\n--- [OmniForge Daemon Started at {time.strftime('%Y-%m-%d %H:%M:%S')}] ---\n")

            log_out = open(self.log_file, "a", encoding="utf-8")
            creationflags = 0
            if self.is_windows:
                creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)

            proc = subprocess.Popen(
                [sys.executable, "-m", "core.bot", "--run"],
                cwd=str(BASE_DIR),
                stdout=log_out,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
            self.pid_file.write_text(str(proc.pid))
            await asyncio.sleep(0.5)
            status = await self.get_service_status(service_name)
            return {"status": "success", "action": "start", "service": status}

        elif action == "stop":
            stopped = False
            if self.pid_file.exists():
                try:
                    pid = int(self.pid_file.read_text().strip())
                    if psutil.pid_exists(pid):
                        p = psutil.Process(pid)
                        p.terminate()
                        try:
                            p.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            p.kill()
                        stopped = True
                except Exception:
                    pass
                finally:
                    try:
                        self.pid_file.unlink(missing_ok=True)
                    except Exception:
                        pass

            for proc in psutil.process_iter(["pid", "cmdline"]):
                try:
                    cmdline = " ".join(proc.info.get("cmdline") or [])
                    if ("core.bot" in cmdline or "main.py --run" in cmdline) and proc.info["pid"] != os.getpid():
                        proc.terminate()
                        stopped = True
                except Exception:
                    pass

            status = await self.get_service_status(service_name)
            return {"status": "success", "action": "stop", "service": status}

        elif action == "restart":
            await self.control_service(service_name, "stop")
            await asyncio.sleep(1.0)
            return await self.control_service(service_name, "start")

    async def stream_service_logs(
        self, service_name: str = "omniforge.service", lines: int = 50
    ) -> AsyncGenerator[str, None]:
        """Asynchronously streams logs line-by-line (journalctl on Linux, log tailer on Windows/macOS)."""
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
            # Cross-platform log tailer for Windows and non-systemd environments
            if not self.log_file.exists():
                self.log_file.write_text(
                    f"[OmniForge Log Stream Initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}]\n",
                    encoding="utf-8"
                )

            try:
                with open(self.log_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.readlines()
                    for line in content[-lines:]:
                        yield line.rstrip()

                    f.seek(0, os.SEEK_END)
                    while True:
                        line = f.readline()
                        if line:
                            yield line.rstrip()
                        else:
                            await asyncio.sleep(0.5)
            except Exception as e:
                yield f"[Log Tailer Error] {e}"

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
        self,
        prompt: str,
        cwd: Optional[str] = None,
        model: str = "gemini-3.8-flash-medium",
        effort: str = "low",
        conversation_id: Optional[str] = None,
        resume: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Dispatches a prompt task to Antigravity CLI and streams the stdout."""
        target_dir = cwd or str(BASE_DIR)
        target_conv_id = conversation_id or (self.active_conversation_id if resume else None)

        # Determine appropriate effort parameter for the selected model
        effort_arg = effort
        if "claude" in model.lower():
            effort_arg = None
        elif "-low" in model.lower():
            effort_arg = "low"
        elif "-medium" in model.lower():
            effort_arg = "medium"
        elif "-high" in model.lower():
            effort_arg = "high"

        cmd = [
            self.agy_bin,
            "--dangerously-skip-permissions",
            "--model", model,
        ]
        if effort_arg:
            cmd.extend(["--effort", effort_arg])
        cmd.extend(["--output-format", "stream-json"])
        if target_conv_id:
            cmd.extend(["--conversation", target_conv_id])
        cmd.extend(["-p", prompt])

        if not Path(self.agy_bin).exists() and not shutil.which(self.agy_bin):
            yield f"❌ Antigravity CLI binary not found at '{self.agy_bin}'."
            return

        exec_cmd = cmd
        if self.is_windows:
            lower_bin = str(self.agy_bin).lower()
            if lower_bin.endswith((".cmd", ".bat")) or not lower_bin.endswith(".exe"):
                exec_cmd = ["cmd.exe", "/c"] + cmd

        session_label = f" [Session: {target_conv_id[:8]}...]" if target_conv_id else " [New Session]"
        yield f"🚀 Launching agent task ({model}){session_label}...\n💬 Prompt: \"{prompt}\"\n"

        proc_env = os.environ.copy()
        proc_env["PYTHONUNBUFFERED"] = "1"

        try:
            proc = await asyncio.create_subprocess_exec(
                *exec_cmd,
                cwd=target_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=proc_env,
            )
        except Exception as e:
            yield f"❌ Failed to launch Antigravity process: {type(e).__name__}: {e or repr(e)}"
            return

        accumulated_response: List[str] = []
        turn_saved = False

        try:
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode(errors="replace").strip()
                if not line:
                    continue

                # Parse stream-json event
                try:
                    event_data = json.loads(line)
                    event_type = event_data.get("event")

                    if event_type == "init":
                        init_conv_id = event_data.get("conversation_id")
                        if init_conv_id:
                            self.active_conversation_id = init_conv_id
                            self._save_agent_session()
                        tag = self.active_conversation_id[:8] if self.active_conversation_id else "active"
                        yield f"⚡ Agent initialized in {target_dir} (Session: {tag})."
                    elif event_type == "step_update":
                        step = event_data.get("step_update", {})
                        stype = step.get("step_type")
                        state = step.get("state")

                        if stype == "tool":
                            tool_name = step.get("tool_name", "tool")
                            tool_info = step.get("tool_info", {})
                            if state == "ACTIVE":
                                params = tool_info.get("parameters", {})
                                cmd_str = params.get("CommandLine", str(params))
                                yield f"⚙️ [Tool: {tool_name}] {cmd_str}"
                            elif state == "DONE":
                                out = tool_info.get("output", "").strip()
                                if out:
                                    snippet = out[:160] + ("..." if len(out) > 160 else "")
                                    yield f"📄 {snippet}"
                        elif stype == "agent_response":
                            delta = step.get("text_delta")
                            if delta:
                                accumulated_response.append(delta)
                                yield delta
                        elif stype == "thought":
                            tdelta = step.get("thought_delta")
                            if tdelta:
                                yield f"💭 {tdelta}"
                    elif event_type == "result":
                        res = event_data.get("result", {})
                        dur = res.get("duration_seconds", 0)
                        full_response = "".join(accumulated_response).strip()
                        turn_record = {
                            "conversation_id": self.active_conversation_id,
                            "prompt": prompt,
                            "response": full_response,
                            "model": model,
                            "timestamp": time.time(),
                            "duration_seconds": round(dur, 2),
                        }
                        self.session_history.append(turn_record)
                        self._save_agent_session()
                        turn_saved = True
                        yield f"\n🏁 Task completed successfully ({dur:.1f}s)."
                except json.JSONDecodeError:
                    # Non-JSON output (e.g. system warnings or info)
                    yield line
            await proc.wait()
            if not turn_saved and accumulated_response:
                full_response = "".join(accumulated_response).strip()
                turn_record = {
                    "conversation_id": self.active_conversation_id,
                    "prompt": prompt,
                    "response": full_response,
                    "model": model,
                    "timestamp": time.time(),
                    "duration_seconds": 0.0,
                }
                self.session_history.append(turn_record)
                self._save_agent_session()
        finally:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
