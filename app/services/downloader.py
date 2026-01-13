"""Video Downloader - OPTIMALLASHTIRILGAN"""
import yt_dlp
import os
import asyncio
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)
os.makedirs('temp', exist_ok=True)


class Downloader:

    @staticmethod
    async def get_info(url: str) -> Optional[dict]:
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'socket_timeout': 15
            }

            def _get():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _get)

            if not info:
                return None

            return {
                'title': info.get('title', 'Unknown')[:100],
                'duration': Downloader._format_duration(info.get('duration', 0)),
                'views': Downloader._format_number(info.get('view_count', 0)),
                'uploader': info.get('uploader', 'Unknown'),
                'platform': Downloader._get_platform(url)
            }
        except Exception as e:
            logger.error(f"Info xato: {e}")
            return None

    @staticmethod
    async def download(url: str, quality: str = '720p') -> Optional[Tuple[str, int]]:
        try:
            # TO'G'RI formatlar!
            formats = {
                '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]',
                '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]',
                '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',
                '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]'
            }

            ydl_opts = {
                'format': formats.get(quality, formats['720p']),
                'outtmpl': 'temp/%(id)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
                # TEZLIK UCHUN
                'concurrent_fragment_downloads': 4,
                'http_chunk_size': 10485760,  # 10MB
                'buffer_size': 16384,
                # Merge uchun
                'merge_output_format': 'mp4',
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-movflags', '+faststart'
                ]
            }

            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info)

            loop = asyncio.get_event_loop()
            filepath = await loop.run_in_executor(None, _download)

            if not os.path.exists(filepath):
                return None

            file_size = os.path.getsize(filepath)

            if file_size > 2_000_000_000:
                os.remove(filepath)
                return None

            return filepath, file_size
        except Exception as e:
            logger.error(f"Download xato: {e}")
            return None

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if not seconds:
            return "Unknown"
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"

    @staticmethod
    def _format_number(num: int) -> str:
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)

    @staticmethod
    def _get_platform(url: str) -> str:
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'facebook.com' in url:
            return 'facebook'
        return 'other'