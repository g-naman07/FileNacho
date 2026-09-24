# 🌮 FileNacho

> **Chunk it. Crunch it. Send it. The FileNacho way.**

FileNacho is a modern peer-to-peer file transfer web application built with **React**, **Vite**, **Node.js WebSocket Signaling**, and **WebRTC (`RTCDataChannel`)**, enabling direct browser-to-browser communication without relying on centralized storage servers.

---

## 🚀 Features

- **Direct Peer-to-Peer Transfer**: Zero server-side file storage using WebRTC data channels.
- **Client-Side Compression**: Custom Huffman coding algorithm (`compressor.js`) compresses files directly in the browser before streaming.
- **Chunked Data Streaming**: Adaptive file chunking (`chunker.js`) with backpressure control (`bufferedAmountLow`) to prevent memory overload.
- **Signaling Server**: Lightweight WebSocket signaling server (`backend/`) for room creation and ICE candidate exchange.
- **Automated Network Resilience Suite**: Python Playwright + CDP test suite (`tests/`) simulating real-world Wi-Fi degradation, high latency, bandwidth throttling, and socket drops.

---

## 🧪 WebRTC Network Resilience & Connectivity Test Suite

FileNacho includes an SDET test suite to benchmark WebRTC peer connections under lossy and degraded network conditions:

- **Dual-Peer Automation**: Uses Playwright to launch concurrent Sender and Receiver browser contexts.
- **CDP Network Emulation**: Controls Chrome DevTools Protocol (`Network.emulateNetworkConditions`) to inject 200ms+ latency, 3G throttling, and transient offline state.
- **Data Integrity Verification**: Asserts WebRTC reconnection and byte-for-byte file transfer integrity.

For test execution instructions, see [`tests/README.md`](tests/README.md).

---

## 🛠️ Project Structure

```
filenacho/
├── backend/                  # WebSocket signaling server (Node.js / Express / ws)
├── frontend/                 # WebRTC client interface (React / Vite / Tailwind)
└── tests/                    # WebRTC Network Resilience & Connectivity Test Suite (Python / Playwright / CDP)
```

---

## 💻 Quick Start

### Backend (Signaling Server)
```bash
cd backend
npm install
npm run dev
```

### Frontend (React Client)
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
pip install -r tests/requirements.txt
playwright install chromium
pytest
```

---

## 📜 License
ISC License
