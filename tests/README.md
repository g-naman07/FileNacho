# FileNacho - WebRTC Network Resilience & Connectivity Test Suite

An automated, SDET-focused test suite designed for **FileNacho** (a peer-to-peer browser-to-browser file transfer web app). This suite uses **Python**, **pytest**, **Playwright**, and **Chrome DevTools Protocol (CDP)** to evaluate WebRTC connectivity, adaptive chunking, socket reconnection, bandwidth throttling, and packet loss resilience under degraded Wi-Fi conditions.

---

## 🎯 Wi-Fi & Connectivity Engineering Alignment

WebRTC operates directly on top of peer-to-peer UDP channels (`RTCDataChannel`), ICE candidate gathering, and WebSocket signaling. This test suite models real-world wireless network challenges:

1. **High Latency & Packet Delay**: Injects 200ms+ latency via CDP (`Network.emulateNetworkConditions`) on active sender/receiver contexts.
2. **Bandwidth Throttling & Backpressure**: Simulates 3G / congested Wi-Fi (250 KB/s - 500 KB/s) to validate `onbufferedamountlow` flow control and chunk queueing.
3. **Transient Network Outages**: Simulates temporary Wi-Fi drops (`offline: True` -> `offline: False`) mid-session to verify socket and WebRTC reconnection.
4. **Data Integrity Assurance**: Performs end-to-end binary transfer validation, comparing downloaded payload attributes against original file specs.

---

## 🛠️ Architecture & Components

```
tests/
├── conftest.py                   # Playwright dual-peer fixtures & NetworkSimulator (CDP helper)
├── test_webrtc_network_resilience.py # 5 core network resilience & connectivity test cases
├── pytest.ini                    # Test runner configuration, markers, and HTML reporting
└── requirements.txt              # Python test suite dependencies
```

---

## 🚀 Running the Test Suite

### 1. Install Dependencies
```bash
pip install -r tests/requirements.txt
playwright install chromium
```

### 2. Start Application Servers
Ensure the signaling server and frontend are running:
```bash
# Terminal 1: Backend Signaling Server
cd backend && npm run dev

# Terminal 2: Frontend App
cd frontend && npm run dev
```

### 3. Execute Tests
```bash
# Run all resilience tests with detailed HTML report
pytest

# Run specific marker (e.g., bandwidth throttling)
pytest -m bandwidth

# Run with custom frontend / signaling URLs
FRONTEND_URL=http://localhost:5173 SIGNALING_URL=ws://localhost:5000 pytest
```

---

## 📊 Test Coverage Summary

| Test Case | CDP Network Condition | Target Focus | Assertions |
|---|---|---|---|
| `test_webrtc_reconnection_under_packet_loss` | Latency 200ms, 500 KB/s throughput | Dual-peer WebRTC setup | Peer connection established, file ready |
| `test_socket_disconnection_recovery` | Offline toggle (`offline: True -> False`) | Signaling WebSocket | UI gracefully handles offline & recovers |
| `test_bandwidth_throttling_file_transfer` | 250 KB/s throughput constraint | DataChannel backpressure | Progressive chunk receipt & completion |
| `test_peer_reconnection_on_transient_offline` | 2-second offline drop mid-session | Transient Wi-Fi drop | Reconnection state recovery |
| `test_end_to_end_file_integrity_lossy_network` | Standard / Lossy network stream | Binary data streaming | File size & payload integrity validation |

---

## 📄 HTML Test Report
Running `pytest` automatically outputs a self-contained test report `report.html` featuring execution timelines, pass/fail metrics, and detailed log traces.
