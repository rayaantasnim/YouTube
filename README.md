# High-Performance Asynchronous Multi-Threaded Media Downloader

![Engine](https://img.shields.io/badge/Engine-yt--dlp-FF69B4.svg?style=for-the-badge&logo=youtube)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-green.svg?style=for-the-badge&logo=python)

> **Repository Location:** `https://github.com/rayaantasnim/YouTube`

---

<img src="https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg" width="100%" alt="System Banner"/>

## System Visual Architecture & Flow

The downloader orchestrates input payloads through an asynchronous, thread-managed pipeline designed to maximize throughput while preserving system stability and byte-level stream integrity.

```
+------------------------------------+
|   User Payload String/File Input   |
+------------------------------------+
                  |
                  v
+------------------------------------+
| Target Extraction Discovery Engine |
+------------------------------------+
                  |
                  v
+------------------------------------+
|  Thread Worker Allocation Manager  |
+------------------------------------+
                  |
                  v
+------------------------------------+
|    yt-dlp Stream Handshake Routine |
+------------------------------------+
                  |
                  v
+------------------------------------+
| Dynamic Multi-Format Multiplexing  |
|     / Post-processing via FFmpeg   |
+------------------------------------+
                  |
                  v
+------------------------------------+
|     Local Storage Persistence /    |
|        Audited Systems Logs        |
+------------------------------------+
```

<img src="https://images.pexels.com/photos/1089438/pexels-photo-1089438.jpeg" width="800px" alt="Data Flow Concept"/>

---

## Key Architectural Innovations

<details>
<summary><b>Asynchronous Concurrency Pipeline</b></summary>

### ThreadPoolExecutor Concurrency Control

The concurrency framework relies on Python's `concurrent.futures.ThreadPoolExecutor` to manage asynchronous network worker threads efficiently. The main event loop delegates extraction and download tasks to isolated thread workers, ensuring the primary thread remains fully responsive to runtime events and signal interrupts.

```
Main Thread (UI/Event Loop)
       |
       +---> [Worker Thread 1] ---> Network Handshake -> Byte Stream -> Persistence
       |
       +---> [Worker Thread 2] ---> Network Handshake -> Byte Stream -> Persistence
       |
       +---> [Worker Thread N] ---> Network Handshake -> Byte Stream -> Persistence
```

Workers execute tasks independently inside bound worker contexts. Thread pools restrict max concurrency thresholds based on hardware thread counts, preventing OS context-switching degradation or memory saturation during concurrent high-bitrate downloads.

</details>

<details>
<summary><b>Dynamic Stream Hook Extraction</b></summary>

### Real-Time Interceptor Architecture (`universal_progress_hook`)

Real-time telemetry feeds directly from `yt-dlp` down to internal state monitors using a non-blocking callback hook mechanism. The `universal_progress_hook` function intercepts data frames emitted at the byte stream layer.

```
yt-dlp Core Stream Output
           |
           v
  universal_progress_hook
           |
           +---> Calculate Delta Bytes & Latency
           +---> Compute Instantaneous Bandwidth
           +---> Emit Thread-Safe State Payload
```

#### Metrics Calculated Real-Time:
* **Byte Count Calculation:** Computes total downloaded bytes against total estimated byte sizes.
* **Instantaneous Bandwidth:** Calculates delta bytes over differential time vectors to provide smooth throughput readings.
* **ETA Estimation:** Evaluates moving averages of chunk arrival times to project exact completion windows.

</details>

<details>
<summary><b>Automated Post-Processor Multiplexing</b></summary>

### FFmpeg Demuxing and Encoding Integration

Upon completing raw stream retrieval, the system transfers processing to the FFmpeg post-processing layer. Video and audio tracks fetched in isolated streams undergo lossless container multiplexing or transcoded conversion.

```
[ Raw Video Stream (mp4/webm) ] --+
                                  |---> [ FFmpeg Engine ] ---> [ Multiplexed Output (MKV/MP4) ]
[ Raw Audio Stream (m4a/opus) ] --+
```

Audio extraction profiles automatically detach video metadata containers, piping raw PCM streams through FFmpeg libmp3lame encoders to output high-fidelity audio artifacts without artifacts or frame loss.

</details>

---

## Deep Technical Mechanism Overview

Engineering high-performance media download engines requires addressing real-world network instabilities and concurrency bottlenecks. This system uses precise thread management and IO handling patterns to maintain reliability at scale.

### Thread Lifecycle & Safety Strategy
Thread tasks operate within worker contexts managed by structured execution boundaries. The application prevents worker collision and thread leaking by trapping signals and systematically flushing task queues before tear-down operations.

### Non-Blocking Log Buffer Management
Thread workers route system outputs and telemetry streams through thread-safe `queue.Queue` buffers. Dedicated logging threads consume these queues asynchronously, preventing thread-bound file lock contend problems on local storage systems.

### Latency Tracking & Network Resilience
The system evaluates network transport latency during initial socket handshakes. Real-time metrics inform dynamic timeout calculations, allowing early detection of stalled TCP sockets.

### Frame Drop Recovery Mechanisms
If socket connections drop mid-transfer, the download pipeline detects incomplete byte ranges. It resumes downloading using HTTP range requests (`Range: bytes=X-Y`), avoiding redundant byte retrieval.

### Programmatic Error Parsing
`yt-dlp` standard errors pass through regex-based classification filters. The system categorizes errors as recoverable (e.g., HTTP 429 Rate Limits, socket drops) or unrecoverable (e.g., Geo-blocking, Removed Content), invoking automatic exponential backoff policies when appropriate.

---

## Operational Profiles & Streams

| Profile Index | Output Mode Designation | Codec Matrix | Target Stream Profile Details |
| :---: | :---: | :---: | :--- |
| **Profile 1** | Max Quality Video | AVC1/HEVC/AV1 + AAC/Opus | Downloads best available video and audio streams, multiplexing them into a single container without re-encoding quality loss. |
| **Profile 2** | High-Fidelity Audio | MP3 / 320 kbps VBR | Strips video data entirely, piping raw audio streams through FFmpeg to produce normalized 320 kbps MP3 files. |
| **Profile 3** | Low Storage Video | H.264 + AAC (capped at 720p) | Optimizes storage and bandwidth usage by picking standard definition H.264 streams, ideal for low-power devices. |

---

## Local Deployment & Execution Directives

### 1. Prerequisites Installation

Ensure FFmpeg is installed on your host system path, then install Python dependencies:

```bash
pip install yt-dlp
```

### 2. Launch Execution

Execute the core orchestrator script via your terminal:

```bash
python main.py
```

### 3. Execution Input Modes

`main.py` supports three flexible input payload formats:

#### Single Direct Stream URL Input
Pass a individual stream URL directly into the interactive CLI prompt:
```text
Enter Target URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

#### Space-Separated Bulk URL Parameters
Input multiple URL targets simultaneously separated by spaces to invoke concurrent thread pool extractions:
```text
Enter Target URL(s): https://youtu.be/example1 https://youtu.be/example2 https://youtu.be/example3
```

#### Local File Pointer Imports (`.txt` mapping arrays)
Provide a path to a plain text file containing one target URL per line:
```text
Enter Target URL or File Path: targets.txt
```

---

<hr/>

<div align="center">

Authorized by Rayaan Tasnim  
© 2026 All rights reserved.

</div>
