"""
Videod API - Video link extractor using yt-dlp
Deploy to Vercel: install Vercel CLI, then run `vercel --prod`
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import re

app = Flask(__name__)
CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])

PLATFORM_MAP = {
    "youtube": "YouTube",
    "youtu.be": "YouTube",
    "tiktok": "TikTok",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "fb.watch": "Facebook",
    "twitter": "X",
    "x.com": "X",
}


def get_platform(url):
    url_lower = url.lower()
    for key, name in PLATFORM_MAP.items():
        if key in url_lower:
            return name
    return "Video"


def extract_info(url):
    """Extract video metadata and direct URLs using yt-dlp."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


def build_links(info):
    """Build a clean links dict from yt-dlp format info."""
    links = {}
    formats = info.get("formats", [])
    if not formats:
        direct = info.get("url")
        if direct:
            links["Direct"] = direct
        return links

    video_formats = []
    audio_formats = []

    for f in formats:
        url = f.get("url")
        if not url:
            continue

        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        height = f.get("height") or 0
        ext = f.get("ext", "mp4")
        note = f.get("format_note", "")

        if vcodec != "none" and height:
            label = note if note else f"{height}p"
            video_formats.append({
                "url": url,
                "quality": label,
                "height": height,
                "ext": ext,
                "has_audio": acodec != "none",
            })
        elif acodec != "none" and vcodec == "none":
            abr = f.get("abr") or 0
            audio_formats.append({
                "url": url,
                "abr": abr,
                "ext": ext,
                "quality": f"{int(abr)}kbps" if abr else "Audio",
            })

    video_formats.sort(key=lambda x: x["height"], reverse=True)
    audio_formats.sort(key=lambda x: x["abr"], reverse=True)

    best_with_audio = [f for f in video_formats if f["has_audio"]]
    if best_with_audio:
        best = best_with_audio[0]
        links[f"Best Video ({best['quality']})"] = best["url"]
    elif video_formats:
        best = video_formats[0]
        links[f"Best Video ({best['quality']})"] = best["url"]

    if audio_formats:
        best_a = audio_formats[0]
        links[f"Best Audio ({best_a['quality']})"] = best_a["url"]

    seen = set()
    for f in video_formats[:6]:
        key = f"{f['quality']} Video"
        if key not in seen:
            seen.add(key)
            links[key] = f["url"]

    return links


@app.route("/api", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Videod API is running"}), 200


@app.route("/api", methods=["POST"])
def resolve():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "Missing 'url' in JSON body."}), 400

    if not re.match(r"^https?://", url, re.IGNORECASE):
        return jsonify({"success": False, "error": "Invalid URL. Must start with http:// or https://"}), 400

    try:
        info = extract_info(url)

        if not info:
            return jsonify({"success": False, "error": "Could not extract any info from the URL."}), 400

        links = build_links(info)

        if not links:
            return jsonify({
                "success": False,
                "error": "No downloadable media URL found. The post may be private, geo-blocked, or requires login."
            }), 400

        response = {
            "success": True,
            "title": info.get("title") or info.get("fulltitle") or "Untitled",
            "platform": info.get("extractor") or get_platform(url),
            "author": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "",
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail") or "",
            "links": links,
        }

        return jsonify(response), 200

    except yt_dlp.utils.DownloadError as e:
        err_msg = str(e)
        if "Private" in err_msg or "private" in err_msg:
            friendly = "This content is private or requires login."
        elif "not available" in err_msg or "unavailable" in err_msg:
            friendly = "This video is unavailable, deleted, or region-blocked."
        elif "Unsupported URL" in err_msg:
            friendly = "This URL is not supported. Please use a supported platform."
        else:
            friendly = err_msg
        return jsonify({"success": False, "error": friendly}), 400

    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


try:
    from vercel_wsgi import handle_request
    def handler(environ, start_response):
        return handle_request(app, environ, start_response)
except ImportError:
    handler = app
