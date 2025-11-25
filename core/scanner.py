import json
import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

"""
Scanner – WebSpeed PRO
Quét toàn bộ tốc độ web:
 - Navigation Timing
 - Resource Timing
 - WebVitals (LCP, FID, CLS)
 - Screenshot
 - Advanced metrics (redirect, dns, tcp, tls…)
"""

# -----------------------------------------------------------
# HÀM CHÍNH DÙNG BÊN NGOÀI
# -----------------------------------------------------------
def scan(url: str, screenshot_path: str = None, save_to_db: bool = True) -> dict:
    data = asyncio.run(_scan_async(url, screenshot_path))
    if save_to_db:
        _try_save_scan(data)
    return data


async def scan_async(
    url: str, screenshot_path: str = None, save_to_db: bool = True
) -> dict:
    """
    Async-friendly wrapper used when a running event loop already exists.
    """
    data = await _scan_async(url, screenshot_path)
    if save_to_db:
        _try_save_scan(data)
    return data


# -----------------------------------------------------------
# HÀM BÊN TRONG (ASYNC)
# -----------------------------------------------------------
async def _scan_async(url: str, screenshot_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Load WebVitals script
        script_path = Path(__file__).resolve().parent.parent / "vitals.js"
        with open(script_path, "r", encoding="utf-8") as f:
            script = f.read()

        await page.add_init_script(script)

        start_time = time.time()

        # Navigate and wait until fully loaded
        await page.goto(url, wait_until="load")

        # Optional screenshot
        if screenshot_path:
            await page.screenshot(path=screenshot_path, full_page=True)

        # PERFORMANCE TIMING
        timing_raw = await page.evaluate(
            "() => JSON.stringify(window.performance.timing)"
        )
        nav_entries = await page.evaluate(
            "() => JSON.stringify(window.performance.getEntriesByType('navigation'))"
        )
        resource_entries = await page.evaluate(
            "() => JSON.stringify(window.performance.getEntriesByType('resource'))"
        )
        vitals_raw = await page.evaluate(
            "() => JSON.stringify(window.getVitals())"
        )

        browser_close_time = time.time()

        # Parse JSON
        timing = json.loads(timing_raw)
        navigation = json.loads(nav_entries)
        resources = json.loads(resource_entries)
        vitals = json.loads(vitals_raw)

        # -----------------------------------------------------------
        # BASIC METRICS
        # -----------------------------------------------------------
        dns = timing["domainLookupEnd"] - timing["domainLookupStart"]
        tcp = timing["connectEnd"] - timing["connectStart"]
        ttfb = timing["responseStart"] - timing["requestStart"]
        dom = timing["domContentLoadedEventEnd"] - timing["navigationStart"]
        load = timing["loadEventEnd"] - timing["navigationStart"]

        redirect = timing["redirectEnd"] - timing["redirectStart"]
        tls = timing["connectEnd"] - timing["secureConnectionStart"] if timing["secureConnectionStart"] > 0 else 0

        # -----------------------------------------------------------
        # RESOURCE METRICS
        # -----------------------------------------------------------
        total_size = sum(r.get("transferSize", 0) for r in resources)
        total_requests = len(resources)

        # Breakdown
        type_breakdown = {}
        for r in resources:
            t = r.get("initiatorType", "other")
            type_breakdown.setdefault(t, {"count": 0, "size": 0, "duration": 0})
            type_breakdown[t]["count"] += 1
            type_breakdown[t]["size"] += r.get("transferSize", 0)
            type_breakdown[t]["duration"] += r.get("duration", 0)

        # Long-running resources
        slow_resources = sorted(
            resources,
            key=lambda x: x.get("duration", 0),
            reverse=True
        )[:10]

        # -----------------------------------------------------------
        # BUILD FINAL PAYLOAD
        # -----------------------------------------------------------
        result = {
            "url": url,
            "scan_start": start_time,
            "scan_end": browser_close_time,
            "scan_duration": round((browser_close_time - start_time) * 1000),

            # BASIC METRICS
            "metrics": {
                "dns": dns,
                "tcp": tcp,
                "tls": tls,
                "redirect": redirect,
                "ttfb": ttfb,
                "dom": dom,
                "load": load,
            },

            # RESOURCE
            "resources": resources,
            "total_size": total_size,
            "total_requests": total_requests,
            "breakdown": type_breakdown,
            "slowest": slow_resources,

            # WEB VITALS
            "vitals": {
                "LCP": vitals.get("LCP", 0),
                "FID": vitals.get("FID", 0),
                "CLS": round(vitals.get("CLS", 0), 4)
            },

            # FUTURE OPTIONS
            "screenshot": screenshot_path if screenshot_path else None
        }

        return result


def _try_save_scan(data: dict):
    """
    Persist scan result to history, but avoid breaking the scan flow
    if the DB write fails.
    """
    try:
        from core.database import save_scan

        save_scan(data)
    except Exception:
        # ignore to keep scanning resilient
        pass
