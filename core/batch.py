import asyncio
from core.scanner import scan_async


async def _scan_one(url: str, index: int, callback_progress=None):
    """
    Scan 1 URL, có callback báo tiến trình lên UI.
    """
    try:
        data = await scan_async(url)
        if callback_progress:
            callback_progress(index, url, "done", data)
        return data

    except Exception as e:
        if callback_progress:
            callback_progress(index, url, f"error: {e}", None)
        return None


async def _scan_list(urls: list, callback_progress=None):
    """
    Scan list URL theo hàng đợi tuần tự (sequential).
    """
    results = []
    for idx, url in enumerate(urls):
        if callback_progress:
            callback_progress(idx, url, "scanning", None)

        data = await _scan_one(url, idx, callback_progress)
        results.append((url, data))
    return results


def batch_scan(urls: list, callback_progress=None):
    """
    Wrapper chạy async trong sync context.
    """
    return asyncio.run(_scan_list(urls, callback_progress))
