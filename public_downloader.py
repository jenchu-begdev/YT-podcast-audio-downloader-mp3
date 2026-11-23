import os
import sys
import re
import time
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

# Ensure UTF-8 console input and output with error tolerance
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

YOUTUBE_MAX_WORKERS = 2
PODCAST_MAX_WORKERS = 4

# ==================================================
# 共通工具函式 (Common Utilities)
# ==================================================

def clean_filename(title: str, default_name: str = "未命名") -> str:
    """替換 Windows 檔名中的非法字元為安全全形或等價字元"""
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '：',
        '*': '_',
        '?': '？',
        '"': "''",
        '<': '《',
        '>': '》',
        '|': '｜',
    }
    for char, rep in replacements.items():
        title = title.replace(char, rep)
    
    title = title.strip().rstrip('.')
    if not title:
        title = default_name
    return title

def ask_save_dir() -> str:
    """詢問使用者要儲存的資料夾路徑"""
    prompt = "請輸入要儲存的資料夾路徑（直接按 Enter 則預設儲存在當前資料夾）："
    target_dir_input = input(prompt).strip().strip('\'"')
    return target_dir_input

def determine_final_save_dir(target_dir_input: str, group_name: str, create_subfolder: bool = True) -> str:
    """決定最終儲存資料夾並自動建立"""
    base_dir = os.path.abspath(target_dir_input) if target_dir_input else os.getcwd()
    if create_subfolder:
        safe_folder_name = clean_filename(group_name)
        save_dir = os.path.join(base_dir, safe_folder_name)
    else:
        save_dir = base_dir
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

def select_items(items: list, item_name: str = "影片", unit: str = "部") -> list:
    """
    通用範圍選擇器（支援下載全部、最新 N 部/集、最舊 N 部/集、標題搜尋）。
    items 需為包含 'title' 鍵值的 dict 列表。
    """
    total = len(items)
    print("\n==================================================")
    print(f"請選擇下載範圍 (直接按 Enter 預設為 [1] 下載全部)：")
    print(f"  [1] 下載全部{item_name} (共 {total} {unit}，預設)")
    print(f"  [2] 下載最新 N {unit}")
    print(f"  [3] 下載最舊 N {unit}")
    print(f"  [4] 下載指定{item_name} / 主題分類 (輸入標題關鍵字搜尋)")
    print("==================================================")
    
    choice = input("請輸入選項 (1/2/3/4，直接按 Enter 預設 1)：").strip()
    if not choice or choice == "1":
        print(f"\n已選擇：下載全部{item_name} (共 {total} {unit})")
        return items

    if choice == "2":
        while True:
            n_str = input(f"請輸入要下載的最新{unit}數 N (1-{total})：").strip()
            if n_str.isdigit() and int(n_str) > 0:
                n = int(n_str)
                if n > total:
                    print(f"輸入數值大於總{item_name}數，將下載全部 {total} {unit}。")
                    n = total
                print(f"\n已選擇：下載最新 {n} {unit}")
                return items[:n]
            print("請輸入有效的正整數數字。")

    elif choice == "3":
        while True:
            n_str = input(f"請輸入要下載的最舊{unit}數 N (1-{total})：").strip()
            if n_str.isdigit() and int(n_str) > 0:
                n = int(n_str)
                if n > total:
                    print(f"輸入數值大於總{item_name}數，將下載全部 {total} {unit}。")
                    n = total
                print(f"\n已選擇：下載最舊 {n} {unit}")
                return items[-n:]
            print("請輸入有效的正整數數字。")

    elif choice == "4":
        while True:
            keyword = input(f"\n請輸入{item_name}標題關鍵字 (直接按 Enter 取消並返回下載全部)：").strip()
            if not keyword:
                print(f"未輸入關鍵字，預設下載全部{item_name}。")
                return items
            
            matched = [item for item in items if keyword.lower() in item['title'].lower()]
            if not matched:
                print(f"找不到標題包含「{keyword}」的{item_name}，請重新輸入關鍵字。")
                continue

            if len(matched) == 1:
                print(f"\n找到 1 {unit}符合{item_name}：{matched[0]['title']}")
                return matched

            # Multiple matches
            print(f"\n找到 {len(matched)} {unit}符合關鍵字「{keyword}」的{item_name}，請選擇：")
            print(f"  [1] 下載所有符合此關鍵字的{item_name} (共 {len(matched)} {unit})")
            for idx, item in enumerate(matched, 2):
                print(f"  [{idx}] {item['title']}")
            
            while True:
                sub_choice = input(f"\n請輸入序號 (1-{len(matched)+1}，複選可用逗號如 2,4,5，或按 0 重新搜尋)：").strip()
                if sub_choice == "0":
                    break
                
                # 支援全形與半形逗號，去除空白
                normalized = sub_choice.replace('，', ',')
                parts = [p.strip() for p in normalized.split(',') if p.strip()]
                
                if not parts or not all(p.isdigit() for p in parts):
                    print(f"輸入無效，請輸入 1 到 {len(matched)+1} 之間的數字，複選可用逗號隔開 (如 2,4,5)。")
                    continue
                
                nums = [int(p) for p in parts]
                
                if 1 in nums:
                    if len(nums) == 1:
                        print(f"\n已選擇：下載所有符合「{keyword}」的{item_name} (共 {len(matched)} {unit})")
                        return matched
                    else:
                        print(f"選項 [1] 為下載全部{item_name}。若要下載全部請單獨輸入 1；若要自選特定{item_name}，請輸入 2 以上的序號 (如 2,4,5)。")
                        continue
                
                # 檢查所有序號是否都在有效範圍內
                if all(2 <= num <= len(matched) + 1 for num in nums):
                    # 去除重複項並保持序號順序
                    valid_nums = sorted(list(set(nums)))
                    chosen_items = [matched[num - 2] for num in valid_nums]
                    if len(chosen_items) == 1:
                        print(f"\n已選擇：{chosen_items[0]['title']}")
                    else:
                        print(f"\n已選擇以下 {len(chosen_items)} {unit}{item_name}：")
                        for num, ci in zip(valid_nums, chosen_items):
                            print(f"  [{num}] {ci['title']}")
                    return chosen_items
                else:
                    print(f"輸入無效，序號必須在 1 到 {len(matched)+1} 之間。")
    else:
        print(f"輸入非有效選項，自動預設為下載全部{item_name}。")
        return items

def run_batch_download(items: list, save_dir: str, download_fn, max_workers: int,
                       item_name: str = "影片", unit: str = "部", extra_info: str = ""):
    """通用多線程下載協調器與結果統計輸出（支援中斷暫停與繼續）"""
    total_selected = len(items)
    remaining_tasks = []
    for new_idx, item in enumerate(items, 1):
        remaining_tasks.append((new_idx, item['title'], item, total_selected))

    prompt_suffix = f" {extra_info}" if extra_info else ""
    print(f"\n準備下載 {total_selected} {unit}{item_name}{prompt_suffix}...")
    print(f"開始多線程下載（同時下載數：{max_workers}）...")
    start_time = time.time()
    success_count = 0
    fail_count = 0

    while remaining_tasks:
        executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
            future_to_task = {executor.submit(download_fn, task, save_dir): task for task in list(remaining_tasks)}
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    res = future.result()
                except Exception as e:
                    res = f"[失敗] ({task[0]}/{task[3]}) {task[1]} - 錯誤: {e}"
                print(res)
                if "[完成]" in res or "[略過" in res:
                    success_count += 1
                else:
                    fail_count += 1
                if task in remaining_tasks:
                    remaining_tasks.remove(task)
            executor.shutdown(wait=True)
        except KeyboardInterrupt:
            executor.shutdown(wait=False, cancel_futures=True)
            print("\n\n==================================================")
            print("【已暫停下載，是否繼續下載】")
            print("  [1] 是 (繼續下載，預設)")
            print("  [2] 否 (離開程式)")
            print("==================================================")
            while True:
                try:
                    choice = input("請輸入選項 (1 或 2，直接按 Enter 預設 1)：").strip()
                except KeyboardInterrupt:
                    print("\n已結束並離開程式。")
                    sys.exit(0)
                if not choice or choice == "1":
                    print("\n繼續下載中...\n")
                    break
                elif choice == "2":
                    print("\n已結束並離開程式。")
                    sys.exit(0)
                else:
                    print("請輸入 1 或 2。")

    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"下載任務結束！耗時: {elapsed:.1f} 秒")
    print(f"成功: {success_count} / {total_selected}")
    if fail_count > 0:
        print(f"失敗: {fail_count} {unit}")
    print(f"檔案已全數存入：{save_dir}")
    print(f"==========================================")


# ==================================================
# YouTube 專屬邏輯 (YouTube Specific)
# ==================================================

def is_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://") or text.startswith("www.")

def is_single_video_url(url: str) -> bool:
    if "playlist?list=" in url:
        return False
    if "youtu.be/" in url or "watch?v=" in url or "/shorts/" in url:
        return True
    return False

def search_youtube_channels(keyword: str):
    print(f"\n正在 YouTube 官方搜尋與「{keyword}」相關的頻道...")
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            res = ydl.extract_info(f"ytsearch25:{keyword}", download=False)
        except Exception as e:
            print(f"搜尋發生錯誤：{e}")
            return []
    
    entries = res.get('entries', []) or []
    channels = {}
    for entry in entries:
        name = entry.get('channel') or entry.get('uploader')
        url = entry.get('channel_url') or entry.get('uploader_url')
        views = entry.get('view_count') or 0
        if not name or not url:
            continue
        if name not in channels:
            channels[name] = {
                'name': name,
                'url': url,
                'views': views,
                'count': 1
            }
        else:
            channels[name]['views'] += views
            channels[name]['count'] += 1

    return sorted(channels.values(), key=lambda x: x['views'], reverse=True)

def get_channel_videos_url(url: str) -> str:
    clean = url.rstrip('/')
    if not any(clean.endswith(tab) for tab in ['/videos', '/streams', '/shorts', '/playlists']):
        return f"{clean}/videos"
    return clean

def extract_youtube_videos_list(url: str):
    print("\n正在快速解析影片清單...")
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            res = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"解析失敗：{e}")
            return None, []

    if not res:
        return None, []

    if res.get('_type') != 'playlist' and 'entries' not in res:
        title = res.get('title', '未知標題')
        video_id = res.get('id', '')
        video_url = res.get('webpage_url') or res.get('url') or url
        return title, [{'title': title, 'url': video_url, 'id': video_id}]

    title = res.get('title') or res.get('channel') or res.get('uploader') or "YouTube清單"
    raw_entries = res.get('entries', []) or []
    
    videos = []
    for entry in raw_entries:
        if not entry:
            continue
        v_title = entry.get('title')
        v_id = entry.get('id')
        v_url = entry.get('url') or f"https://www.youtube.com/watch?v={v_id}"
        if v_title and (v_id or v_url):
            videos.append({'title': v_title, 'url': v_url, 'id': v_id})
    
    return title, videos

def get_ffmpeg_dir():
    """取得打包單一執行檔環境或同級目錄下的 FFmpeg 路徑"""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        if os.path.exists(os.path.join(base_dir, 'ffmpeg.exe')):
            return base_dir
        exe_dir = os.path.dirname(sys.executable)
        if os.path.exists(os.path.join(exe_dir, 'ffmpeg.exe')):
            return exe_dir
    return None

def download_youtube_single_mp3(task, save_dir):
    idx, title, item, total = task
    url = item['url']
    safe_title = clean_filename(title, default_name="未命名影片")
    mp3_filename = f"{safe_title}.mp3"
    target_path = os.path.join(save_dir, mp3_filename)

    if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
        return f"[略過 (已存在)] ({idx}/{total}) {mp3_filename}"

    outtmpl_pattern = os.path.join(save_dir, f"{safe_title}.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl_pattern,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'windowsfilenames': True,
    }

    ffmpeg_dir = get_ffmpeg_dir()
    if ffmpeg_dir:
        ydl_opts['ffmpeg_location'] = ffmpeg_dir

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(target_path):
            size_mb = os.path.getsize(target_path) / (1024 * 1024)
            return f"[完成] ({idx}/{total}) {mp3_filename} ({size_mb:.1f} MB)"
        else:
            return f"[失敗] ({idx}/{total}) {mp3_filename} (未產生 mp3 檔案)"
    except Exception as e:
        return f"[失敗] ({idx}/{total}) {mp3_filename} - 錯誤: {e}"

def process_youtube():
    print("==================================================")
    print("       YouTube 轉 MP3 音訊通用下載器")
    print("==================================================")
    
    # 1. 使用者輸入目標
    user_input = input("請輸入頻道名稱、頻道連結、播放清單或影片網址：").strip().strip('\'"')
    if not user_input:
        print("未輸入內容，程式結束。")
        return

    # 2. 儲存資料夾路徑輸入
    target_dir_input = ask_save_dir()

    # 3. 解析目標網址或搜尋頻道
    target_url = None
    collection_name = None
    is_single_video = False

    if is_url(user_input):
        target_url = user_input
        if is_single_video_url(target_url):
            is_single_video = True
            print("\n偵測到單一影片連結...")
        elif "playlist?list=" in target_url:
            print("\n偵測到播放清單連結...")
        else:
            print("\n偵測到頻道連結...")
            target_url = get_channel_videos_url(target_url)
    elif user_input.startswith("@"):
        target_url = f"https://www.youtube.com/{user_input}/videos"
    else:
        channels = search_youtube_channels(user_input)
        if not channels:
            print(f"查無與「{user_input}」相關的頻道，請確認名稱後重試。")
            return

        if len(channels) == 1:
            selected_ch = channels[0]
            print(f"\n找到頻道：{selected_ch['name']}")
        else:
            print(f"\n共找到 {len(channels)} 個相關頻道（已按熱門度排序）：")
            for i, ch in enumerate(channels, 1):
                view_str = f"{ch['views']:,}" if ch['views'] else "未提供"
                print(f"  [{i}] {ch['name']} (搜尋熱度: {view_str} 次觀看)")

            while True:
                choice = input(f"\n請選擇頻道序號 (1-{len(channels)})，或輸入 0 取消：").strip()
                if choice == "0":
                    print("已取消操作。")
                    return
                if choice.isdigit() and 1 <= int(choice) <= len(channels):
                    selected_ch = channels[int(choice) - 1]
                    break
                print("輸入無效，請重新輸入。")

        collection_name = selected_ch['name']
        target_url = get_channel_videos_url(selected_ch['url'])

    # 4. 解析影片列表
    detected_title, videos = extract_youtube_videos_list(target_url)
    if not videos:
        print("未能在該目標中找到任何影片。")
        return

    group_name = collection_name or detected_title or "YouTube下載"
    save_dir = determine_final_save_dir(target_dir_input, group_name, create_subfolder=(not is_single_video))

    # 5. 單一影片與多影片處理
    if len(videos) == 1:
        print(f"\n找到 1 部影片：{videos[0]['title']}")
        print(f"存放資料夾：{save_dir}")
        selected_videos = videos
    else:
        print(f"\n共解析出 {len(videos)} 部影片。")
        print(f"目標名稱：{group_name}")
        print(f"存放資料夾：{save_dir}")
        selected_videos = select_items(videos, item_name="影片", unit="部")

    if not selected_videos:
        print("未選取任何影片，程式結束。")
        return

    # 6. 多線程下載並轉 MP3
    run_batch_download(
        items=selected_videos,
        save_dir=save_dir,
        download_fn=download_youtube_single_mp3,
        max_workers=YOUTUBE_MAX_WORKERS,
        item_name="影片音訊",
        unit="部",
        extra_info="並轉為 MP3"
    )
    return True


# ==================================================
# Apple Podcast 專屬邏輯 (Podcast Specific)
# ==================================================

def guess_extension(url: str, mime_type: str = "") -> str:
    clean_url = url.split("?")[0].lower()
    if clean_url.endswith(".m4a") or "x-m4a" in mime_type or "audio/mp4" in mime_type:
        return ".m4a"
    elif clean_url.endswith(".mp3") or "audio/mpeg" in mime_type or "audio/mp3" in mime_type:
        return ".mp3"
    elif clean_url.endswith(".aac") or "audio/aac" in mime_type:
        return ".aac"
    elif clean_url.endswith(".wav") or "audio/wav" in mime_type:
        return ".wav"
    elif clean_url.endswith(".ogg") or "audio/ogg" in mime_type:
        return ".ogg"
    return ".mp3"

def search_podcast(name: str):
    search_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(name)}&entity=podcast&limit=10"
    req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("results", [])
    except Exception as e:
        print(f"搜尋失敗，錯誤訊息：{e}")
        return []

def download_podcast_single_audio(task, save_dir):
    idx, title, item, total = task
    url = item['url']
    mime_type = item.get('mime_type', '')
    safe_title = clean_filename(title, default_name="未命名單集")
    ext = guess_extension(url, mime_type)
    filename = f"{safe_title}{ext}"
    dest_path = os.path.join(save_dir, filename)
    temp_path = dest_path + ".tmp"

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
        return f"[略過 (已存在)] ({idx}/{total}) {filename}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = resp.read(1024 * 64)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                
                if total_size > 0 and downloaded < total_size:
                    raise IOError(f"Incomplete download ({downloaded}/{total_size} bytes)")
                
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                os.rename(temp_path, dest_path)
                
                size_mb = downloaded / (1024 * 1024)
                return f"[完成] ({idx}/{total}) {filename} ({size_mb:.1f} MB)"
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            if attempt < max_retries:
                time.sleep(2)
            else:
                return f"[失敗] ({idx}/{total}) {filename} - 錯誤: {e}"

def process_podcast():
    print("==================================================")
    print("        Apple Podcast 通用下載器")
    print("==================================================")
    
    # 1. 使用者輸入頻道名稱
    channel_name = input("請輸入頻道名稱(注意不要有錯字)：").strip()
    if not channel_name:
        print("未輸入頻道名稱，程式結束。")
        return

    # 2. 儲存資料夾路徑輸入
    target_dir_input = ask_save_dir()

    # 3. 搜尋頻道
    print(f"\n正在 Apple 官方搜尋「{channel_name}」...")
    results = search_podcast(channel_name)
    if not results:
        print("查無此頻道，請確認頻道名稱是否有誤後重試。")
        return

    selected_podcast = None
    if len(results) == 1:
        selected_podcast = results[0]
        print(f"找到頻道：{selected_podcast.get('collectionName')}")
    else:
        print(f"\n共找到 {len(results)} 個相關頻道，請選擇：")
        for i, item in enumerate(results, 1):
            name = item.get("collectionName", "未知")
            artist = item.get("artistName", "未知創作者")
            track_count = item.get("trackCount", 0)
            print(f"[{i}] {name} (創作者: {artist} / 集數約: {track_count} 集)")
        
        while True:
            choice = input(f"\n請輸入序號 (1-{len(results)})，或輸入 0 取消：").strip()
            if choice == "0":
                print("已取消操作。")
                return
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                selected_podcast = results[int(choice) - 1]
                break
            print("輸入無效，請重新輸入。")

    feed_url = selected_podcast.get("feedUrl")
    podcast_title = selected_podcast.get("collectionName", channel_name)
    if not feed_url:
        print("該頻道未提供公開 RSS Feed，無法下載。")
        return

    save_dir = determine_final_save_dir(target_dir_input, podcast_title)

    # 4. 解析 RSS XML 單集清單
    print(f"\n正在讀取頻道資料：{feed_url}")
    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read()
    except Exception as e:
        print(f"無法讀取 RSS 內容：{e}")
        return

    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"解析 RSS XML 失敗：{e}")
        return

    channel = root.find("channel")
    if channel is None:
        print("RSS 格式錯誤，找不到 channel。")
        return

    items = channel.findall("item")
    total_count = len(items)
    print(f"共解析出 {total_count} 個單集。")
    print(f"存放資料夾：{save_dir}\n")

    episodes = []
    for idx, item in enumerate(items, 1):
        title_el = item.find("title")
        title = title_el.text if title_el is not None and title_el.text else f"Episode_{idx}"
        enclosure = item.find("enclosure")
        if enclosure is not None:
            url = enclosure.get("url")
            mime_type = enclosure.get("type", "")
            if url:
                episodes.append({'title': title, 'url': url, 'mime_type': mime_type})

    if not episodes:
        print("未在頻道中找到可下載的音訊連結。")
        return

    # 5. 選擇下載範圍
    selected_episodes = select_items(episodes, item_name="單集", unit="集")
    if not selected_episodes:
        print("未選取任何單集，程式結束。")
        return

    # 6. 多線程下載音訊
    run_batch_download(
        items=selected_episodes,
        save_dir=save_dir,
        download_fn=download_podcast_single_audio,
        max_workers=PODCAST_MAX_WORKERS,
        item_name="單集",
        unit="集"
    )
    return True


# ==================================================
# 主入口 (Main Entry Point)
# ==================================================

def main():
    while True:
        print("==================================================")
        print("              影音音訊通用下載器")
        print("==================================================")
        print("請選擇要下載的平台：")
        print("  [1] YouTube (支援頻道名稱/頻道連結/播放清單/影片網址，下載為 MP3，預設)")
        print("  [2] Apple Podcast (支援頻道名稱搜尋，下載原始音訊)")
        print("==================================================")
        
        platform_choice = input("請輸入選項 (1 或 2，直接按 Enter 預設 1)：").strip()
        success = False
        if not platform_choice or platform_choice == "1":
            print("\n已選擇平台：[1] YouTube\n")
            success = process_youtube()
        elif platform_choice == "2":
            print("\n已選擇平台：[2] Apple Podcast\n")
            success = process_podcast()
        else:
            print(f"無效的選項「{platform_choice}」，程式結束。")
            break

        if success:
            print("\n下載已完成！")
            print("是否想繼續下載其他內容？")
            print("  [1] 是")
            print("  [2] 否")
            again = input("請輸入選項 (1 是 / 2 否，直接按 Enter 關閉程式)：").strip()
            if again in ["1", "是", "y", "Y"]:
                print("\n" + "=" * 50 + "\n")
                continue
        print("\n程式結束。")
        break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已離開程式。")
