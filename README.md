# 影音音訊通用下載器 / Media Audio Universal Downloader

[繁體中文](#繁體中文) | [English](#english)

---

<a name="繁體中文"></a>
## 繁體中文

一個輕量、快速且友善的終端機工具，內建直覺的互動式數字選單，非技術背景也能輕鬆上手。支援將 YouTube 影片、播放清單或頻道批次下載並轉為 MP3，以及搜尋並批次下載 Apple Podcast 節目單集音訊。。

---

### ✨ 核心特色

- **YouTube 下載支援**：
  - 支援關鍵字搜尋頻道名稱、頻道首頁網址、自訂代稱（`@channel_id`）、播放清單網址或單一影片網址。
  - 自動下載最高音質音訊並轉換為 192kbps MP3 格式。
- **Apple Podcast 下載支援**：
  - 官方 iTunes 介面搜尋節目名稱，自動解析最新公開 RSS Feed。
  - 完整保留單集原始音訊格式（MP3、M4A、AAC、WAV、OGG 等）。
- **完整下載防護與靈活挑選**：
  - **斷線防護機制（.tmp 暫存）**：下載 Podcast 時採用 `.tmp` 暫存寫入，下載完成後才會命名為正式音訊檔案；若遇網路斷線或異常，絕不留下損壞的半成品音訊。
  - **範圍與關鍵字挑選**：支援下載全部、最新 N 部/集、最舊 N 部/集，或輸入標題關鍵字進行篩選與複選（如 `2,4,5`）。
  - **自動清理檔名**：自動處理 Windows 不合法字元，保留乾淨易讀的檔案名稱。
  - **中斷續傳與多線程**：隨時可按 `Ctrl + C` 叫出暫停/繼續選單，並具備多線程加速與自動跳過已下載檔案功能。

---

### 📦 獨立執行檔使用說明（免安裝 Python）

若您是直接從 GitHub 的 **[Releases](../../releases)** 頁面下載已發布的 `影音音訊通用下載器.exe`，您**不需要安裝 Python 也不需設定 FFmpeg**（均已內建打包），下載後直接點擊即可執行。

#### ⚠️ 關於防毒軟體與 Windows SmartScreen 安全警告
> **重要說明**：
> 當您首次在 Windows 上執行本程式時，可能會出現 **「Windows 已保護您的電腦」** 或防毒軟體阻擋警告。
> 
> - **原因**：本工具是由開源專案自動打包成單一執行檔（PyInstaller），並沒有購買昂貴的商業組織數位簽章（Code Signing Certificate），因此 Windows Defender 或部分防毒軟體會將未簽章的未知程式標示為潛在風險。
> - **原始碼完全透明**：本專案所有 Python 程式碼完全公開開源於此倉庫，無任何後門或惡意行為。
> 
> **如何繼續執行**：
> 1. 當 Windows SmartScreen 彈出提示視窗時，點擊視窗上的 **「其他資訊 (More info)」**。
> 2. 接著點擊右下角出現的 **「仍要執行 (Run anyway)」** 按鈕。
> 3. 程式即可正常啟動並使用。

---

### 🛠️ 原始碼執行與環境需求（開發者適用）

若您想要直接使用 Python 原始碼執行或進行二次開發：

#### 先決條件
1. **Python 3.8+**
2. **FFmpeg**（YouTube 轉音訊必備）：
   - Windows (PowerShell):
     ```powershell
     winget install "FFmpeg (Essentials Build)"
     ```
   - macOS (Homebrew):
     ```bash
     brew install ffmpeg
     ```
   - Linux (Ubuntu/Debian):
     ```bash
     sudo apt update && sudo apt install -y ffmpeg
     ```

#### 安裝步驟
1. 複製本專案：
   ```bash
   git clone https://github.com/jenchu-begdev/YT-podcast-audio-downloader-mp3.git
   cd YT-podcast-audio-downloader-mp3
   ```
2. 安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```

#### 啟動程式
```bash
python public_downloader.py
```

---

### 🚀 操作流程

1. **選擇平台**：輸入 `1` 選擇 YouTube 或 `2` 選擇 Apple Podcast。
2. **設定目標**：
   - YouTube：輸入頻道名稱、網址或播放清單。
   - Apple Podcast：輸入欲搜尋的節目名稱。
3. **指定存放資料夾**：直接按 Enter 儲存於當前目錄，或自訂路徑。
4. **選擇下載範圍**：
   - `[1]` 下載全部
   - `[2]` 下載最新 N 集
   - `[3]` 下載最舊 N 集
   - `[4]` 依標題關鍵字搜尋挑選（支援複選如 `2,4,5`）
5. **開始下載**：程式將以多線程並行下載，隨時可按 `Ctrl + C` 叫出暫停/繼續選單。

---

### 🔨 重新封裝執行檔注意事項 (開發者參考)

> **說明**：一般使用者請直接由 Releases 下載打包好的 `.exe` 即可。若開發者自行修改原始碼後欲重新封裝：
> - 專案根目錄已提供 `影音音訊通用下載器.spec` 打包配置檔。
> - 自行打包時請留意本機 `ffmpeg.exe` 與 `ffprobe.exe` 的路徑需正確設定於 spec 檔中，或使用 `pyinstaller public_downloader.py` 進行基礎封裝。

---

### 📄 免責聲明與授權

- 本專案僅供個人備份、教育與技術研究使用。
- 請遵守各平台（YouTube、Apple 等）之服務條款，並尊重原創者版權與著作權。
- 本專案採用 [MIT License](LICENSE) 授權。

---
---

<a name="english"></a>
## English

A lightweight, fast, and user-friendly terminal tool featuring an interactive step-by-step menu—making it effortless even for non-technical users. Easily batch download YouTube videos, playlists, or channels as MP3s, and search or download Apple Podcast episodes.」   
---

### ✨ Features

- **YouTube Downloader**:
  - Supports search by channel name, channel URL, handle (`@channel_id`), playlist URL, or single video URL.
  - Automatically extracts the highest quality audio and converts it to 192kbps MP3.
- **Apple Podcast Downloader**:
  - Searches shows via official Apple iTunes Search API and parses the latest RSS feed.
  - Preserves original audio quality and formats (MP3, M4A, AAC, WAV, OGG, etc.).
- **Download Protection & Flexible Filtering**:
  - **Incomplete Download Protection (`.tmp` Staging)**: Downloads Podcast episodes via `.tmp` staging files. The file is renamed to the final audio format only when the download is 100% verified, ensuring no corrupted or incomplete files are left behind during network disconnects.
  - **Flexible Range Selection**: Download all, latest N items, oldest N items, or filter/multi-select by title keywords (e.g., `2,4,5`).
  - **Clean Filename Sanitization**: Automatically handles invalid characters for cross-platform and Windows compatibility.
  - **Pause/Resume & Multi-Threading**: Press `Ctrl + C` anytime to pause or resume; includes concurrent downloading and automatic skip for already downloaded files.

---

### 📦 Standalone Executable Guide (No Python Required)

If you downloaded the pre-compiled `影音音訊通用下載器.exe` from the **[Releases](../../releases)** tab, **you do not need to install Python or FFmpeg** (everything is bundled). Just double-click to launch.

#### ⚠️ Security Warning (Windows SmartScreen & Antivirus)
> **Notice**:
> When running the application for the first time on Windows, you might encounter a **"Windows protected your PC"** or antivirus prompt.
> 
> - **Why this happens**: This tool is packaged into a standalone binary using PyInstaller from open-source code. It does not possess an expensive commercial Code Signing Certificate. Therefore, Windows Defender or third-party antivirus software may flag unsigned executables as unknown/untrusted.
> - **100% Transparent & Safe**: The entire source code is available in this repository. There are no malicious scripts or telemetry.
> 
> **How to Run Anyway**:
> 1. Click on **"More info"** on the Windows SmartScreen dialog.
> 2. Click the **"Run anyway"** button that appears at the bottom.
> 3. The program will launch normally.

---

### 🛠️ Running from Source (For Developers)

#### Prerequisites
1. **Python 3.8+**
2. **FFmpeg** (Required for YouTube audio extraction):
   - Windows (PowerShell):
     ```powershell
     winget install "FFmpeg (Essentials Build)"
     ```
   - macOS (Homebrew):
     ```bash
     brew install ffmpeg
     ```
   - Linux (Ubuntu/Debian):
     ```bash
     sudo apt update && sudo apt install -y ffmpeg
     ```

#### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/jenchu-begdev/YT-podcast-audio-downloader-mp3.git
   cd YT-podcast-audio-downloader-mp3
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Usage
```bash
python public_downloader.py
```

---

### 🚀 Workflow

1. **Select Platform**: Press `1` for YouTube, or `2` for Apple Podcast.
2. **Provide Target**: Enter a channel name, channel URL, playlist URL, or video URL.
3. **Choose Save Directory**: Press Enter for current folder, or specify a custom path.
4. **Select Download Scope**:
   - `[1]` Download all
   - `[2]` Download latest N episodes
   - `[3]` Download oldest N episodes
   - `[4]` Search by keyword (multi-select supported, e.g., `2,4,5`)
5. **Start Download**: Files will be downloaded concurrently. Press `Ctrl + C` anytime to pause or resume.

---

### 🔨 Rebuilding the Executable (Developer Note)

> **Note**: General users should download the pre-built `.exe` directly from Releases. If developers modify the source code and want to rebuild:
> - The repository includes `影音音訊通用下載器.spec` for PyInstaller configuration.
> - Ensure local `ffmpeg.exe` and `ffprobe.exe` binary paths are properly referenced in the spec file, or build using standard `pyinstaller public_downloader.py`.

---

### 📄 Disclaimer & License

- This software is intended strictly for personal backup, research, and educational purposes.
- Please comply with the Terms of Service of content platforms (YouTube, Apple) and respect copyright regulations.
- Licensed under the [MIT License](LICENSE).
