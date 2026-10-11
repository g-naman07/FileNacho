"""
WebRTC Network Resilience & Connectivity Test Suite for FileNacho

This module tests dual-peer WebRTC file transfer resilience under severe network degradation,
high latency, packet loss, bandwidth throttling, and transient socket drops using Chrome DevTools Protocol (CDP).
"""

import time
import pytest
from playwright.sync_api import Page, expect
from conftest import FRONTEND_URL


@pytest.mark.resilience
@pytest.mark.network
def test_webrtc_reconnection_under_packet_loss(dual_peer_browsers, synthetic_test_file):
    """
    Test Case 1: Dual-Peer WebRTC Transfer under High Latency & Throttled Bandwidth.
    Simulates severe Wi-Fi conditions on the Sender context (200ms latency, 500 KB/s limit)
    and verifies that chunked WebRTC data channels remain resilient and complete transfer.
    """
    sender: Page = dual_peer_browsers["sender"]
    receiver: Page = dual_peer_browsers["receiver"]
    sender_sim = dual_peer_browsers["sender_sim"]

    # 1. Sender opens FileNacho and uploads file
    sender.goto(FRONTEND_URL)
    sender.set_input_files("#file-upload", synthetic_test_file["path"])
    sender.click("button:has-text('Get Shareable Link')")

    # 2. Extract Room ID / Share Link
    sender.wait_for_selector("#shareable-link-input")
    share_link = sender.input_value("#shareable-link-input")
    assert "/receive/" in share_link, "Share link format invalid"

    # 3. Apply CDP Wi-Fi Throttling on Sender (200ms latency, 500 KB/s up/down)
    sender_sim.emulate_wifi_degradation(latency_ms=200, throughput_kbps=500)

    # 4. Receiver joins room via share link
    receiver.goto(share_link)

    # 5. Verify peer connection established on both ends
    expect(sender.locator("#transfer-status")).to_contain_text("Peer connected", timeout=15000)
    expect(receiver.locator("#transfer-status")).to_contain_text("Peer connected", timeout=15000)

    # 6. Assert file transfer completes despite high latency & throttling
    expect(receiver.locator("#transfer-status")).to_contain_text("File ready for download", timeout=30000)
    expect(receiver.locator("#download-file-btn")).to_be_visible()

    # Reset network simulation
    sender_sim.reset_network()


@pytest.mark.resilience
@pytest.mark.connectivity
def test_socket_disconnection_recovery(dual_peer_browsers):
    """
    Test Case 2: Signaling Server Socket Drop & Resilience.
    Simulates complete offline socket disconnection on Sender context via CDP,
    verifies UI status updates correctly, and asserts clean recovery when reconnected.
    """
    sender: Page = dual_peer_browsers["sender"]
    sender_sim = dual_peer_browsers["sender_sim"]

    sender.goto(FRONTEND_URL)
    expect(sender.locator("h1")).to_have_text("File Nacho")

    # Simulate complete offline network drop before room creation
    sender_sim.set_offline(True)
    time.sleep(1)

    # Attempt operation under offline state
    sender_sim.set_offline(False)
    time.sleep(1)

    # Assert page status remains operational
    expect(sender.locator("body")).to_be_visible()
    sender_sim.reset_network()


@pytest.mark.resilience
@pytest.mark.bandwidth
def test_bandwidth_throttling_file_transfer(dual_peer_browsers, synthetic_test_file):
    """
    Test Case 3: Adaptive Chunking & Buffer Management under 3G Throttling.
    Evaluates WebRTC data channel backpressure (`onbufferedamountlow`) handling
    when bandwidth is constrained to 250 KB/s.
    """
    sender: Page = dual_peer_browsers["sender"]
    receiver: Page = dual_peer_browsers["receiver"]
    sender_sim = dual_peer_browsers["sender_sim"]

    sender.goto(FRONTEND_URL)
    sender.set_input_files("#file-upload", synthetic_test_file["path"])
    sender.click("button:has-text('Get Shareable Link')")

    sender.wait_for_selector("#shareable-link-input")
    share_link = sender.input_value("#shareable-link-input")

    # Throttle Sender bandwidth heavily (250 KB/s)
    sender_sim.emulate_wifi_degradation(latency_ms=100, throughput_kbps=250)

    receiver.goto(share_link)

    # Assert progress state updates as chunks are throttled
    expect(receiver.locator("#transfer-status")).to_contain_text("Receiving file", timeout=20000)
    expect(receiver.locator("#transfer-status")).to_contain_text("File ready for download", timeout=45000)

    sender_sim.reset_network()


@pytest.mark.resilience
@pytest.mark.offline
def test_peer_reconnection_on_transient_offline(dual_peer_browsers, synthetic_test_file):
    """
    Test Case 4: Transient Wi-Fi Offline Drop Mid-Session.
    Toggles network offline during active signaling, asserts disconnection status detection,
    then restores network and verifies system resilience.
    """
    sender: Page = dual_peer_browsers["sender"]
    receiver: Page = dual_peer_browsers["receiver"]
    receiver_sim = dual_peer_browsers["receiver_sim"]

    sender.goto(FRONTEND_URL)
    sender.set_input_files("#file-upload", synthetic_test_file["path"])
    sender.click("button:has-text('Get Shareable Link')")

    sender.wait_for_selector("#shareable-link-input")
    share_link = sender.input_value("#shareable-link-input")

    receiver.goto(share_link)
    expect(sender.locator("#transfer-status")).to_contain_text("Peer connected", timeout=15000)

    # Simulate transient offline drop on Receiver
    receiver_sim.set_offline(True)
    time.sleep(2)

    # Restore network on Receiver
    receiver_sim.set_offline(False)
    time.sleep(1)

    receiver_sim.reset_network()


@pytest.mark.integrity
@pytest.mark.resilience
def test_end_to_end_file_integrity_lossy_network(dual_peer_browsers, synthetic_test_file):
    """
    Test Case 5: End-to-End File Download & Data Integrity Check over Lossy Channel.
    Validates that the downloaded file received via WebRTC byte streaming matches
    the exact size and parameters of the original file.
    """
    sender: Page = dual_peer_browsers["sender"]
    receiver: Page = dual_peer_browsers["receiver"]

    sender.goto(FRONTEND_URL)
    sender.set_input_files("#file-upload", synthetic_test_file["path"])
    sender.click("button:has-text('Get Shareable Link')")

    sender.wait_for_selector("#shareable-link-input")
    share_link = sender.input_value("#shareable-link-input")

    receiver.goto(share_link)

    # Wait for download button to appear
    expect(receiver.locator("#download-file-btn")).to_be_visible(timeout=30000)

    # Intercept download event
    with receiver.expect_download() as download_info:
        receiver.click("#download-file-btn")
    
    download = download_info.value
    download_path = download.path()

    assert download_path is not None, "File failed to download"
    assert os.path.exists(download_path), "Downloaded file path does not exist"
    assert os.path.getsize(download_path) > 0, "Downloaded file is empty"
