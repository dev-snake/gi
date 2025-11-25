"""
Chụp screenshot trang
"""
async def take_screenshot(page, path):
    await page.screenshot(path=path)
