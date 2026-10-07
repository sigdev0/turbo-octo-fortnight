"""
Unit tests for OmniForge Homelab Mission Control Portal.
Tests API endpoints, system telemetry, service supervisor, and static file serving.
"""

import unittest
from pathlib import Path
from starlette.testclient import TestClient

from portal.server import app
from portal.supervisor import HomelabSupervisor


class TestMissionControlPortal(unittest.TestCase):
    """Test suite for Mission Control Portal backend."""

    def setUp(self):
        self.client = TestClient(app)
        self.supervisor = HomelabSupervisor()

    def test_health_check_endpoint(self):
        """Verify /api/health returns 200 OK."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("OmniForge", data.get("app", ""))

    def test_system_telemetry_endpoint(self):
        """Verify /api/system returns CPU, RAM, Disk, and host details."""
        res = self.client.get("/api/system")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("cpu", data)
        self.assertIn("memory", data)
        self.assertIn("disk", data)
        self.assertIn("uptime_seconds", data)

        # Check values
        self.assertGreaterEqual(data["cpu"]["percent"], 0.0)
        self.assertGreater(data["memory"]["total_mb"], 0)
        self.assertGreater(data["disk"]["total_gb"], 0)

    def test_services_endpoint(self):
        """Verify /api/services lists monitored services."""
        res = self.client.get("/api/services")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("services", data)
        self.assertTrue(len(data["services"]) >= 1)
        svc_names = [s["service"] for s in data["services"]]
        self.assertIn("omniforge.service", svc_names)

    def test_cartridges_endpoint(self):
        """Verify /api/cartridges returns discovered cartridges."""
        res = self.client.get("/api/cartridges")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("cartridges", data)
        self.assertGreaterEqual(data.get("total", 0), 1)

    def test_assets_endpoint(self):
        """Verify /api/assets returns file list."""
        res = self.client.get("/api/assets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("assets", data)
        self.assertIsInstance(data["assets"], list)

    def test_portal_html_serving(self):
        """Verify / and /portal serve the HTML Single Page App."""
        res1 = self.client.get("/")
        self.assertEqual(res1.status_code, 200)
        self.assertIn("OmniForge Homelab Mission Control", res1.text)

        res2 = self.client.get("/portal")
        self.assertEqual(res2.status_code, 200)
        self.assertIn("OmniForge Homelab Mission Control", res2.text)

    def test_supervisor_telemetry_types(self):
        """Verify direct supervisor metrics return proper typed dict."""
        metrics = self.supervisor.get_system_metrics()
        self.assertIsInstance(metrics["cpu"]["percent"], (int, float))
        self.assertIsInstance(metrics["memory"]["percent"], (int, float))
        self.assertIsInstance(metrics["disk"]["percent"], (int, float))
        self.assertIsInstance(metrics["uptime_seconds"], int)

    def test_agent_session_endpoints(self):
        """Verify /api/agent/session and /api/agent/session/new work properly."""
        # Check current session
        res = self.client.get("/api/agent/session")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("conversation_id", data)
        self.assertIn("history", data)
        self.assertIn("turns_count", data)

        # Reset session
        res_new = self.client.post("/api/agent/session/new")
        self.assertEqual(res_new.status_code, 200)
        new_data = res_new.json()
        self.assertEqual(new_data.get("status"), "success")

        # Verify session is reset
        res_after = self.client.get("/api/agent/session")
        after_data = res_after.json()
        self.assertIsNone(after_data["conversation_id"])
        self.assertEqual(after_data["turns_count"], 0)
        self.assertEqual(len(after_data["history"]), 0)

    def test_supervisor_session_persistence(self):
        """Verify supervisor saves and reloads session state to disk."""
        test_id = "test-conv-1234-uuid"
        self.supervisor.active_conversation_id = test_id
        self.supervisor.session_history = [{"prompt": "hi", "response": "hello", "model": "gemini"}]
        self.supervisor._save_agent_session()

        # Create a fresh supervisor instance to verify disk loading
        new_sup = HomelabSupervisor()
        self.assertEqual(new_sup.active_conversation_id, test_id)
        self.assertEqual(len(new_sup.session_history), 1)
        self.assertEqual(new_sup.session_history[0]["prompt"], "hi")

        # Clean up
        new_sup.clear_agent_session()
        self.assertIsNone(new_sup.active_conversation_id)
        self.assertEqual(len(new_sup.session_history), 0)

    def test_agent_limits_endpoint(self):
        """Verify /api/agent/limits returns rolling 5-hour and weekly quota structure."""
        res = self.client.get("/api/agent/limits")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("tier", data)
        self.assertIn("five_hour", data)
        self.assertIn("weekly", data)

        five_hour = data["five_hour"]
        self.assertIn("percent_remaining", five_hour)
        self.assertIn("used", five_hour)
        self.assertIn("budget", five_hour)
        self.assertIn("resets_in", five_hour)

        weekly = data["weekly"]
        self.assertIn("percent_remaining", weekly)
        self.assertIn("used", weekly)
        self.assertIn("budget", weekly)
        self.assertIn("resets_on", weekly)


if __name__ == "__main__":
    unittest.main()
