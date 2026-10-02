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


if __name__ == "__main__":
    unittest.main()
