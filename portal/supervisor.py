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
        self.cartridge_config_file = self.data_dir / "cartridge_config.json"
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

    def _format_time_left(self, seconds: int) -> str:
        """Formats remaining duration into natural language string like Antigravity Desktop."""
        if seconds <= 0:
            return "0 minutes"
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        mins, _ = divmod(rem, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if mins > 0 and days == 0:
            parts.append(f"{mins} minute{'s' if mins > 1 else ''}")
        if not parts:
            return "less than 1 minute"
        return ", ".join(parts[:2])

    def get_agent_limits(self) -> Dict[str, Any]:
        """
        Returns quota telemetry split into Gemini Models and Claude/GPT models,
        matching Antigravity Desktop Settings UX.
        """
        now = time.time()
        limits_file = self.data_dir / "antigravity_limits.json"

        # Baseline calibrated from Antigravity Desktop Settings telemetry
        base_state = {
            "gemini_baseline_ts": 1791337344.0,
            "gemini_5h_reset_ts": 1791337344.0 + (79 * 60),       # 1 hour, 19 minutes
            "gemini_weekly_reset_ts": 1791337344.0 + (49 * 3600), # 2 days, 1 hour
            "gemini_5h_base_pct": 63,
            "gemini_weekly_base_pct": 65,
            "claude_5h_base_pct": 100,
            "claude_weekly_base_pct": 100,
        }

        if limits_file.exists():
            try:
                loaded = json.loads(limits_file.read_text(encoding="utf-8"))
                base_state.update(loaded)
            except Exception:
                pass
        else:
            try:
                limits_file.write_text(json.dumps(base_state, indent=2), encoding="utf-8")
            except Exception:
                pass

        # Count session prompts since baseline calibration
        gemini_prompts = sum(
            1 for t in self.session_history
            if t.get("timestamp", 0) >= base_state["gemini_baseline_ts"]
            and "gemini" in t.get("model", "gemini").lower()
        )
        claude_prompts = sum(
            1 for t in self.session_history
            if t.get("timestamp", 0) >= base_state["gemini_baseline_ts"]
            and ("claude" in t.get("model", "").lower() or "gpt" in t.get("model", "").lower())
        )

        # Gemini calculations
        g_5h_sec = max(0, int(base_state["gemini_5h_reset_ts"] - now))
        g_5h_pct = max(0, min(100, base_state["gemini_5h_base_pct"] - (gemini_prompts * 2)))
        if g_5h_sec > 0:
            g_5h_desc = f"You have used some of your 5-hour limit, it will fully refresh in {self._format_time_left(g_5h_sec)}."
        else:
            g_5h_pct = 100
            g_5h_desc = "Window fully available"

        g_wk_sec = max(0, int(base_state["gemini_weekly_reset_ts"] - now))
        g_wk_pct = max(0, min(100, base_state["gemini_weekly_base_pct"] - gemini_prompts))
        if g_wk_sec > 0:
            g_wk_desc = f"You have used some of your weekly limit, it will fully refresh in {self._format_time_left(g_wk_sec)}."
        else:
            g_wk_pct = 100
            g_wk_desc = "Window fully available"

        # Claude & GPT calculations
        c_5h_pct = max(0, min(100, base_state["claude_5h_base_pct"] - (claude_prompts * 4)))
        c_wk_pct = max(0, min(100, base_state["claude_weekly_base_pct"] - (claude_prompts * 2)))
        c_5h_desc = "Window fully available" if c_5h_pct == 100 else "You have used some of your 5-hour limit, it will fully refresh in 5 hours."
        c_wk_desc = "Window fully available" if c_wk_pct == 100 else "You have used some of your weekly limit, it will fully refresh on Sunday."

        return {
            "status": "healthy",
            "tier": "Standard Tier",
            "gemini": {
                "name": "Gemini Models",
                "weekly": {
                    "percent_remaining": g_wk_pct,
                    "description": g_wk_desc,
                },
                "five_hour": {
                    "percent_remaining": g_5h_pct,
                    "description": g_5h_desc,
                },
            },
            "claude_gpt": {
                "name": "Claude and GPT models",
                "weekly": {
                    "percent_remaining": c_wk_pct,
                    "description": c_wk_desc,
                },
                "five_hour": {
                    "percent_remaining": c_5h_pct,
                    "description": c_5h_desc,
                },
            },
            # Backwards-compatibility aliases
            "five_hour": {
                "percent_remaining": g_5h_pct,
                "used": gemini_prompts,
                "budget": 50,
                "resets_in": g_5h_desc,
            },
            "weekly": {
                "percent_remaining": g_wk_pct,
                "used": gemini_prompts,
                "budget": 250,
                "resets_on": g_wk_desc,
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

    def get_cartridge_config(self) -> Dict[str, bool]:
        """Loads cartridge enabled states from data/cartridge_config.json."""
        if self.cartridge_config_file.exists():
            try:
                return json.loads(self.cartridge_config_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Failed to read cartridge config: {e}")
        return {}

    def set_cartridge_config(self, config: Dict[str, bool]) -> None:
        """Saves cartridge enabled states to data/cartridge_config.json."""
        try:
            self.cartridge_config_file.parent.mkdir(parents=True, exist_ok=True)
            self.cartridge_config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save cartridge config: {e}")

    def get_cartridges(self) -> List[Dict[str, Any]]:
        """
        Discovers all available cartridges and annotates them with enabled state,
        metadata, command, description, and display icon.
        """
        cartridges_dir = BASE_DIR / "cartridges"
        cfg = self.get_cartridge_config()
        results = []

        icon_map = {
            "bedtime_story": "🌙",
            "podcast_clipper": "🎙️",
            "morning_affirmation": "☀️",
        }

        display_name_map = {
            "bedtime_story": "Bedtime Story",
            "podcast_clipper": "Podcast Clipper",
            "morning_affirmation": "Morning Affirmation",
        }

        cmd_map = {
            "bedtime_story": "story",
            "podcast_clipper": "clip",
            "morning_affirmation": "morning",
        }

        desc_map = {
            "bedtime_story": "Screen-free personalized bedtime audio journeys with ambient soundscapes and neural voice narration.",
            "podcast_clipper": "Automated vertical 9:16 short extractor from podcasts and YouTube video URLs.",
            "morning_affirmation": "Empowering daily morning affirmations and energy routines in English and Indonesian.",
        }

        if cartridges_dir.exists():
            for f in sorted(cartridges_dir.glob("*.py")):
                if f.name.startswith("__") or f.name == "base.py" or f.stem == "story_library":
                    continue
                cid = f.stem
                is_enabled = cfg.get(cid, True)
                results.append({
                    "id": cid,
                    "name": display_name_map.get(cid, cid.replace("_", " ").title()),
                    "command": cmd_map.get(cid, cid),
                    "description": desc_map.get(cid, "OmniForge modular cartridge capability."),
                    "icon": icon_map.get(cid, "⚡"),
                    "enabled": is_enabled,
                })
        return results

    def toggle_cartridge(self, cartridge_id: str, enabled: Optional[bool] = None) -> Dict[str, Any]:
        """Toggles or sets the enabled state for a specific cartridge."""
        cfg = self.get_cartridge_config()
        current_state = cfg.get(cartridge_id, True)
        new_state = (not current_state) if enabled is None else bool(enabled)
        cfg[cartridge_id] = new_state
        self.set_cartridge_config(cfg)

        cartridges = self.get_cartridges()
        updated = next((c for c in cartridges if c["id"] == cartridge_id), None)
        return {
            "status": "success",
            "cartridge_id": cartridge_id,
            "enabled": new_state,
            "cartridge": updated,
            "all_cartridges": cartridges,
        }

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
