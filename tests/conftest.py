import os
import hashlib
import tempfile
import pytest
from playwright.sync_api import sync_playwright, Page, CDPSession

# Default test URLs
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SIGNALING_URL = os.getenv("SIGNALING_URL", "ws://localhost:5000")


class NetworkSimulator:
    """Helper class to interact with Chrome DevTools Protocol (CDP) for simulating network conditions."""

    def __init__(self, page: Page):
        self.page = page
        self.cdp: CDPSession = page.context.new_cdp_session(page)
        self.cdp.send("Network.enable")

    def emulate_wifi_degradation(self, latency_ms: int = 200, throughput_kbps: int = 500):
        """Simulate high latency and bandwidth constraints (e.g., weak Wi-Fi)."""
        throughput_bytes = throughput_kbps * 1024
        self.cdp.send(
            "Network.emulateNetworkConditions",
            {
                "offline": False,
                "latency": latency_ms,
                "downloadThroughput": throughput_bytes,
                "uploadThroughput": throughput_bytes,
                "connectionType": "cellular3g",
            },
        )

    def set_offline(self, offline: bool = True):
        """Simulate complete socket/network drop or restoration."""
        self.cdp.send(
            "Network.emulateNetworkConditions",
            {
                "offline": offline,
                "latency": 0 if not offline else 500,
                "downloadThroughput": -1 if not offline else 0,
                "uploadThroughput": -1 if not offline else 0,
            },
        )

    def reset_network(self):
        """Reset network conditions to default unthrottled state."""
        self.cdp.send(
            "Network.emulateNetworkConditions",
            {
                "offline": False,
                "latency": 0,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
            },
        )


@pytest.fixture(scope="module")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def dual_peer_browsers(playwright_instance):
    """Fixture launching dual browser contexts for WebRTC Sender and Receiver."""
    browser = playwright_instance.chromium.launch(headless=True)
    
    sender_context = browser.new_context(accept_downloads=True)
    receiver_context = browser.new_context(accept_downloads=True)

    sender_page = sender_context.new_page()
    receiver_page = receiver_context.new_page()

    yield {
        "sender": sender_page,
        "receiver": receiver_page,
        "sender_sim": NetworkSimulator(sender_page),
        "receiver_sim": NetworkSimulator(receiver_page),
        "browser": browser,
    }

    sender_context.close()
    receiver_context.close()
    browser.close()


@pytest.fixture(scope="function")
def synthetic_test_file():
    """Generates a synthetic binary file for transfer & checksum assertion."""
    file_size = 2 * 1024 * 1024  # 2MB
    data = os.urandom(file_size)
    md5_hash = hashlib.md5(data).hexdigest()

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "test_payload.bin")
    
    with open(file_path, "wb") as f:
        f.write(data)

    yield {
        "path": file_path,
        "filename": "test_payload.bin",
        "size": file_size,
        "md5": md5_hash,
    }

    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)
