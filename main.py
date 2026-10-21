import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

# --- CONFIGURATION CONSTANTS ---
MAX_PARALLEL_DOWNLOADS = 3  # Maximum concurrent downloads allowed
DEFAULT_DOWNLOAD_DIR = "Downloads"

# Status mapping dictionary for UI state translation
STATUS_MAP = {
    'downloading': "Processing Stream Data 📥",
    'finished': "Finalizing & Merging Packages 🛠️",
    'error': "Execution Interrupted ❌",
    'complete': "Download Finalized Successfully ✅"
}

def log_system_event(message: str, filename: str = "ytdlp_system_log.txt"):
    """Appends structural timestamps and event logs to a local file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except IOError:
        pass

def universal_progress_hook(d):
    """
    Interceptors for live stream download hooks.
    Updates terminal UI dynamically without printing endless new lines.
    """
    if d['status'] == 'downloading':
        filename = os.path.basename(d.get('filename', 'Unknown File'))
        # Truncate title strings safely for the console output matrix
        short_title = filename[:30] + '...' if len(filename) > 33 else filename
        
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)
        
        percent = (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0.0
        speed = d.get('speed', 0) or 0
        speed_mb = speed / (1024 * 1024)
        
        # Clear line and print packed status matrix
        sys.stdout.write(
            f"\r⏳ [Active] {short_title:<33} | Progress: {percent:>6.2f}% | Speed: {speed_mb:>5.2f} MB/s"
        )
        sys.stdout.flush()
        
    elif d['status'] == 'finished':
        print(f"\n⚙️ {STATUS_MAP['finished']} - Please wait...")

def fetch_media_metadata(url: str) -> dict:
    """
    Extracts deep JSON video profiles using the target URL 
    without triggering actual stream payload downloads.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "success": True,
                "title": info.get('title', 'Unknown Title'),
                "duration": info.get('duration', 0),
                "uploader": info.get('uploader', 'Unknown Uploader'),
                "formats": info.get('formats', [])
            }
        except yt_dlp.utils.DownloadError as e:
            return {"success": False, "error_msg": str(e)}

def executing_download_worker(url: str, choice_mode: str, output_path: str) -> dict:
    """
    Core download engine isolated for multi-threaded parallel queues.
    Configures format selectors based on the user's high/low profile choice.
    """
    # Configure download definitions dynamically
    if choice_mode == '1':
        # Best video quality combined with best audio quality
        format_selector = 'bestvideo+bestaudio/best'
    elif choice_mode == '2':
        # Audio extraction only
        format_selector = 'bestaudio/best'
    else:
        # Standard fast compression video
        format_selector = 'worstvideo+worstaudio/worst'

    ydl_opts = {
        'format': format_selector,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [universal_progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    # Inject explicit extraction options if user requested pure audio extraction
    if choice_mode == '2':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    meta = {"url": url, "title": "Unknown", "status": "Failed", "error": "None"}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Re-fetch structural properties safely inside the thread
            info = ydl.extract_info(url, download=True)
            meta["title"] = info.get('title', 'Unknown Title')
            meta["status"] = STATUS_MAP['complete']
            log_system_event(f"SUCCESS: Download Completed -> Title: {meta['title']}")
            return meta
    except Exception as network_err:
        meta["error"] = str(network_err)
        log_system_event(f"ERROR: Failed extraction on link {url} -> Details: {str(network_err)}")
        return meta

def pipeline_manager(input_data: str, quality_profile: str):
    """
    Parses structural inputs (multi-link arrays vs batch configuration text documents), 
    allocates workers inside the ThreadPool, and manages terminal tables.
    """
    targets = []
    
    # Target Discovery: Check if input references a physical storage path file
    if os.path.isfile(input_data):
        try:
            with open(input_data, 'r', encoding='utf-8') as f:
                targets = [line.strip() for line in f if line.strip()]
        except IOError as e:
            print(f"❌ Failed to parse storage file payload: {e}")
            return
    else:
        # Split plain space-separated text entries
        targets = [t for t in input_data.split() if t]

    if not targets:
        print("⚠️ Queue Empty. No target strings recognized.")
        return

    # Provision output folder footprint
    if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
        os.makedirs(DEFAULT_DOWNLOAD_DIR)

    print(f"\n🚀 Initializing Multi-Threaded Engine for {len(targets)} targets.")
    print(f"📦 Output Destination Path: '{os.path.abspath(DEFAULT_DOWNLOAD_DIR)}'\n")

    # Construct OS thread pools for parallel download extraction
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_DOWNLOADS) as pool:
        futures_map = {
            pool.submit(executing_download_worker, url, quality_profile, DEFAULT_DOWNLOAD_DIR): url 
            for url in targets
        }
        
        for future in as_completed(futures_map):
            result_meta = future.result()
            print(f"\n📌 Title: {result_meta['title'][:40]}")
            print(f"   Status: {result_meta['status']}")
            if result_meta['error'] != "None":
                print(f"   Trace Info: {result_meta['error'][:75]}...")
            print("-" * 65)

def main():
    print("=" * 65)
    print("      DEEP ARCHITECTURE ASYNCHRONOUS YT-DLP DOWNLOAD CONSOLE       ")
    print("=" * 65)
    print("💡 Drop Input Modes:")
    print("   • Single Link : https://youtube.com")
    print("   • Multi-Links : URL_1 URL_2 URL_3 (Separated by spaces)")
    print("   • Target File : paths.txt (Relative/absolute line-split configuration text)")
    print("   • Command     : Type 'exit' to terminate engine loops.\n")

    while True:
        try:
            payload = input("🔍 Enter Download Target Payload >> ").strip()
            if not payload:
                continue
            if payload.lower() == 'exit':
                print("🛑 Shutting down downloader threads. System offline.")
                break

            print("\n📊 SELECT TARGET STREAMS PROFILE:")
            print("  [1] Max Quality Definition Video (Requires ffmpeg for HD blends)")
            print("  [2] High Fidelity MP3 Audio Extract Only")
            print("  [3] Standard Definition Low Storage Video Profile")
            profile_selection = input("⚙️ Select Profile Index [1-3] >> ").strip()
            
            if profile_selection not in ['1', '2', '3']:
                print("⚠️ Invalid Profile selected. Defaulting to Profile [3].")
                profile_selection = '3'

            pipeline_manager(payload, profile_selection)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Active processes safely interrupted by user signal. Exiting.")
            break

if __name__ == "__main__":
    main()
