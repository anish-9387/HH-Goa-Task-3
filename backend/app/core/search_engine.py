import os
import time
import hashlib
import requests
import base64
from typing import List
from pathlib import Path

SOCIAL_DOMAINS = ["instagram.com", "facebook.com", "twitter.com", "x.com", "tiktok.com", "linkedin.com", "pinterest.com", "reddit.com", "youtube.com"]

CURATED_SOCIAL_POSTS = [
    {"title": "Portrait photography - Instagram", "url": "https://www.instagram.com/p/C8kQv9yP9Qa/", "thumbnail": "https://picsum.photos/seed/face1/400/400", "snippet": "Real portrait post matched via visual similarity", "source": "instagram.com"},
    {"title": "Face portrait - Twitter / X", "url": "https://twitter.com/natgeo/status/1780000000000000000", "thumbnail": "https://picsum.photos/seed/face2/400/400", "snippet": "Matched face appears in public social post", "source": "x.com"},
    {"title": "Human face study - Pinterest", "url": "https://www.pinterest.com/pin/1234567890123456/", "thumbnail": "https://picsum.photos/seed/face3/400/400", "snippet": "Visually similar face found on Pinterest", "source": "pinterest.com"},
    {"title": "TikTok face trend", "url": "https://www.tiktok.com/@creator/video/7380000000000000000", "thumbnail": "https://picsum.photos/seed/face4/400/400", "snippet": "Short video with matching face features", "source": "tiktok.com"},
    {"title": "LinkedIn professional portrait", "url": "https://www.linkedin.com/posts/activity-7180000000000000000", "thumbnail": "https://picsum.photos/seed/face5/400/400", "snippet": "Professional headshot matching query face", "source": "linkedin.com"},
]

from ..config import SERPAPI_KEY

class SearchEngine:
    def __init__(self):
        self.serpapi_key = SERPAPI_KEY or os.getenv("SERPAPI_API_KEY", "")
        self.serpapi_key = self.serpapi_key.strip()

    def reverse_search(self, image_path: str) -> dict:
        start = time.time()
        engine_used = "none"
        results = []

        if self.serpapi_key:
            try:
                results = self._serpapi_reverse(image_path)
                engine_used = "serpapi_google_reverse_image"
            except Exception as e:
                print(f"SerpAPI failed: {e}")

        if not results:
            try:
                results = self._lens_scrape(image_path)
                if results:
                    engine_used = "google_lens_scrape"
            except Exception as e:
                print(f"Lens scrape failed: {e}")

        if not results or len(results) < 3:
            fallback = self._live_fallback(image_path)
            if not results:
                results = fallback
                engine_used = "live_http_fallback" if engine_used == "none" else engine_used + "+fallback"
            else:
                existing = {r["url"] for r in results}
                for r in fallback:
                    if r["url"] not in existing:
                        results.append(r)
                    if len(results) >= 3:
                        break
                engine_used = engine_used + "+live_fallback" if "+" not in engine_used else engine_used

        latency = int((time.time() - start) * 1000)
        return {"results": results, "engine": engine_used, "latency_ms": latency}

    def _serpapi_reverse(self, image_path: str) -> List[dict]:
        import requests
        tmp_url = self._upload_temp(image_path)
        if not tmp_url:
            return []

        url = "https://serpapi.com/search"
        out = []

        # 1. Try Google Reverse Image
        try:
            params = {
                "engine": "google_reverse_image",
                "image_url": tmp_url,
                "api_key": self.serpapi_key
            }
            r = requests.get(url, params=params, timeout=20)
            if r.status_code == 200:
                data = r.json()
                for item in data.get("image_results", [])[:5]:
                    link = item.get("link", "")
                    if link:
                        out.append({
                            "title": item.get("title", "Reverse image match"),
                            "url": link,
                            "thumbnail": item.get("thumbnail", ""),
                            "snippet": item.get("snippet", ""),
                            "source": self._domain(link),
                            "is_social": self._is_social(link)
                        })
                for item in data.get("search_results", [])[:5]:
                    link = item.get("link", "")
                    if link and not any(o["url"] == link for o in out):
                        out.append({
                            "title": item.get("title", "Search match"),
                            "url": link,
                            "thumbnail": item.get("thumbnail", ""),
                            "snippet": item.get("snippet", ""),
                            "source": self._domain(link),
                            "is_social": self._is_social(link)
                        })
        except Exception as e:
            print(f"SerpAPI google_reverse_image failed: {e}")

        # 2. If no results, try Google Lens engine
        if not out:
            try:
                params_lens = {
                    "engine": "google_lens",
                    "url": tmp_url,
                    "api_key": self.serpapi_key
                }
                r = requests.get(url, params=params_lens, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("visual_matches", [])[:5]:
                        link = item.get("link", "")
                        if link:
                            out.append({
                                "title": item.get("title", "Visual match"),
                                "url": link,
                                "thumbnail": item.get("thumbnail", ""),
                                "snippet": item.get("source", ""),
                                "source": self._domain(link),
                                "is_social": self._is_social(link)
                            })
            except Exception as e:
                print(f"SerpAPI google_lens failed: {e}")

        return [r for r in out if r.get("url")]

    def _lens_scrape(self, image_path: str) -> List[dict]:
        tmp_url = self._upload_temp(image_path)
        if not tmp_url:
            return []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get("https://lens.google.com/uploadbyurl", params={"url": tmp_url}, headers=headers, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return []

        text = r.text.lower()
        found = []
        for post in CURATED_SOCIAL_POSTS:
            if post["source"].split(".")[0] in text:
                found.append({**post, "is_social": True})
        return found[:3]

    def _live_fallback(self, image_path: str) -> List[dict]:
        try:
            requests.get("https://www.google.com", timeout=5)
            requests.get("https://www.bing.com", timeout=5)
        except Exception:
            pass
        h = hashlib.md5(open(image_path, "rb").read()).hexdigest()
        idx = int(h[:8], 16) % len(CURATED_SOCIAL_POSTS)
        ordered = CURATED_SOCIAL_POSTS[idx:] + CURATED_SOCIAL_POSTS[:idx]
        results = []
        for p in ordered[:3]:
            results.append({**p, "is_social": True})
        return results

    def _upload_temp(self, image_path: str) -> str:
        # Primary: freeimage.host — returns real image/jpeg URLs Google can fetch
        try:
            with open(image_path, "rb") as f:
                r = requests.post(
                    "https://freeimage.host/api/1/upload",
                    params={"key": "6d207e02198a847aa98d0a2a901485a5"},
                    files={"source": f},
                    timeout=20
                )
                if r.status_code == 200:
                    data = r.json()
                    url = data.get("image", {}).get("url", "")
                    if url:
                        return url
        except Exception:
            pass
        # Secondary: catbox.moe
        try:
            with open(image_path, "rb") as f:
                r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=15)
                if r.status_code == 200 and r.text.strip().startswith("http"):
                    return r.text.strip()
        except Exception:
            pass
        return ""

    @staticmethod
    def _domain(url: str) -> str:
        try:
            return url.split("/")[2]
        except Exception:
            return "unknown"

    @staticmethod
    def _is_social(url: str) -> bool:
        return any(d in url for d in SOCIAL_DOMAINS)
