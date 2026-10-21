import concurrent.futures, json, pathlib, re, time, urllib.request, shutil
root=pathlib.Path("site")
root.mkdir(exist_ok=True)
h=pathlib.Path("index.html").read_text()
m=re.search(r'<script id="audio-data" type="application/json">(.*?)</script>',h,re.S)
audio=json.loads(m.group(1))
out=root/"audio";out.mkdir(exist_ok=True)
def download(item):
    key,clip=item
    for attempt in range(6):
        try:
            req=urllib.request.Request(clip["url"],headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=45) as response:
                data=response.read()
                assert "audio" in response.headers.get("Content-Type",""), "Not audio"
            assert len(data)>500, "Empty audio"
            (out/(key+".mp3")).write_bytes(data)
            return key
        except Exception as e:
            if attempt==5: raise RuntimeError(key+": "+str(e))
            time.sleep(2**attempt)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for n,key in enumerate(pool.map(download,audio.items()),1):
        if n%100==0: print(f"Downloaded {n}/{len(audio)}",flush=True)
for key,clip in audio.items():clip["url"]="audio/"+key+".mp3"
h=h[:m.start(1)]+json.dumps(audio,ensure_ascii=False)+h[m.end(1):]
h=h.replace("media-src data: blob: https://translate.google.com", "media-src 'self' data: blob:")
h=h.replace("clip.url.startsWith('https://translate.google.com/translate_tts?')","/^audio\\/[a-zA-Z0-9_-]+\\.mp3$/.test(clip.url)")
h=h.replace("Google audio · online","Google audio · GitHub")
h=h.replace("原有声音已移除，发音需联网。<br>Google 实播尚未在此环境验收。","音频随网站加载，播放无需连接 Google。")
h=h.replace("Google 在线音频版","GitHub 托管音频版")
h=h.replace("旧声音已移除；当前保存音频 0 / 1,320。发音需联网，Google 实际播放尚未验收。","1,320 段 Google 发音已保存，点击播放直接从本站加载。")
h=h.replace("Google Translate · online audio","Google Translate · GitHub hosted audio")
h=h.replace("Loading Google audio…","Loading audio…")
h=h.replace("$('#audioTranslate').classList.toggle('hidden',EMBEDDED_AUDIO);","$('#audioTranslate').classList.add('hidden');")
h=h.replace("Google audio could not load. Check your connection.","Audio could not load. Check your connection.")
h=h.replace("Audio request timed out. Retry or open Google Translate.","Audio request timed out. Please retry.")
h=h.replace("当前为在线版；只有点击播放的预设词语或例句会发送给 Google，学习档案和作品草稿不会上传。","音频已保存至本站；播放不会向 Google 发送请求。学习档案和作品草稿保留在本机。")
h=h.replace("This is the ONLINE edition: 0 Google recordings are bundled. The Google audio service could not be reached in the build environment, so live playback has NOT been verified. An audio URL is not proof that a recording has been downloaded.","All 1,320 Google audio files are hosted alongside this website. Playback does not connect to Google.")
h=h.replace("Online playback sends only the selected preset term or example to Google.","Playback loads saved MP3 files from this website.")
h=h.replace('"mode":"online"','"mode":"hosted"').replace('"saved_entries":0','"saved_entries":1320')
(root/"index.html").write_text(h)
(root/".nojekyll").touch()
assert len(list(out.glob("*.mp3")))==1320
print("All 1320 audio files validated and ready.",flush=True)
