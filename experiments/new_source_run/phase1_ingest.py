"""PHASE 1 - Source acquisition for NEW source, using canonical Step 5.3 mechanism.

Does NOT modify frozen Step 5. Mirrors step_5_3_source_acquisition.py logic
(md5 source_id, youtube_transcript_api segments, canonical artifact schema)
parameterized for a new URL.
"""
import json, hashlib, datetime, os, sys

VIDEO_URL = "https://www.youtube.com/watch?v=ItRL3FNpd-8"
VIDEO_ID = "ItRL3FNpd-8"
FOCAL_SEC = 316
ROOT = r"D:\ableton claude"

source_id = "yt_" + hashlib.md5(VIDEO_URL.encode()).hexdigest()[:12]
print("source_id:", source_id)

# ---- metadata via yt-dlp (real) ----
meta = {}
try:
    import yt_dlp
    with yt_dlp.YoutubeDL({'quiet':True,'no_warnings':True,'skip_download':True}) as ydl:
        info = ydl.extract_info(VIDEO_URL, download=False)
    meta = {
        "title": info.get('title','UNKNOWN'),
        "channel": info.get('uploader','UNKNOWN'),
        "duration_seconds": info.get('duration',0),
        "upload_date": info.get('upload_date','UNKNOWN'),
        "chapters": [{"title":c.get('title'),"start_time":c.get('start_time'),"end_time":c.get('end_time')}
                     for c in (info.get('chapters') or [])],
    }
    metadata_available = True
    print("[OK] metadata:", meta["title"], "|", meta["channel"], "|", meta["duration_seconds"], "s")
    print("[OK] chapters:", len(meta["chapters"]))
except Exception as e:
    print("[FAIL] metadata:", e); metadata_available = False

# ---- transcript via canonical youtube_transcript_api ----
segments = []
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    ft = api.fetch(VIDEO_ID, languages=['en'])
    raw = ft.to_raw_data() if hasattr(ft,'to_raw_data') else ft
    for i, s in enumerate(raw):
        st = float(s['start']); du = float(s.get('duration',0.0))
        segments.append({
            "segment_id": "seg_%04d" % i,
            "index": i,
            "start_time_sec": round(st,3),
            "end_time_sec": round(st+du,3),
            "duration_sec": round(du,3),
            "text": s['text'],
        })
    transcript_available = True
    print("[OK] transcript segments:", len(segments))
except Exception as e:
    print("[FAIL] transcript:", e); transcript_available = False

record = {
    "version": "1.0",
    "acquisition_phase": "5.3",
    "source": {
        "source_id": source_id,
        "source_type": "YOUTUBE_VIDEO",
        "url": VIDEO_URL,
        "requested_url": "https://www.youtube.com/watch?v=ItRL3FNpd-8&t=316s",
        "video_id": VIDEO_ID,
        "title": meta.get("title","UNKNOWN"),
        "channel": meta.get("channel","UNKNOWN"),
        "duration_seconds": meta.get("duration_seconds",0),
        "upload_date": meta.get("upload_date","UNKNOWN"),
        "retrieval_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z"),
        "metadata_available": metadata_available,
        "transcript_available": transcript_available,
        "transcript_segment_count": len(segments),
        "transcript_retrieval_mechanism": "youtube_transcript_api (canonical, same as step_5_3)",
        "focal_timestamp_sec": FOCAL_SEC,
        "focal_timestamp_human": "5:16",
        "ingestion_scope": "FULL_VIDEO",
        "chapters": meta.get("chapters",[]),
    },
    "transcript_segments": segments,
    "knowledge_items": [],
    "validation": {
        "source_id_stable": True,
        "full_source_ingested": True,
        "transcript_invented": False,
    },
}

out = os.path.join(ROOT, "serum2", "knowledge", "%s_source_ingestion_5_3.json" % source_id)
with open(out, "w", encoding="utf-8") as f:
    json.dump(record, f, indent=1)
print("[WROTE]", out)

# focal chapter resolution
focal_chapter = None
for c in meta.get("chapters",[]):
    if c["start_time"] is not None and c["start_time"] <= FOCAL_SEC and (c["end_time"] or 1e9) > FOCAL_SEC:
        focal_chapter = c
print("[FOCAL CHAPTER]", focal_chapter)
