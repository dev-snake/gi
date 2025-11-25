"""
Automatic Performance Analysis
Phân tích các vấn đề hiệu năng dựa trên dữ liệu từ scanner
"""

def analyze(data):
    issues = []
    suggestions = []

    m = data["metrics"]
    v = data["vitals"]
    resources = data["resources"]
    total_size = data["total_size"]
    total_requests = data["total_requests"]

    # -------------------------------------------------------------
    # 1. Server Slow (TTFB)
    # -------------------------------------------------------------
    if m["ttfb"] > 600:
        issues.append("⚠️ TTFB chậm (Server phản hồi chậm)")
        suggestions.append("Kiểm tra hosting/server hoặc tối ưu backend xử lý.")

    # -------------------------------------------------------------
    # 2. DOM Load chậm
    # -------------------------------------------------------------
    if m["dom"] > 2000:
        issues.append("⚠️ DOM Load quá lâu (>2000ms)")
        suggestions.append("Trang có nhiều JS nặng hoặc DOM phức tạp.")

    # -------------------------------------------------------------
    # 3. Full Load chậm
    # -------------------------------------------------------------
    if m["load"] > 3000:
        issues.append("⚠️ Trang load khá chậm (>3000ms)")
        suggestions.append("Kiểm tra ảnh, JS, font và request dư thừa.")

    # -------------------------------------------------------------
    # 4. LCP chậm
    # -------------------------------------------------------------
    if v["LCP"] > 2500:
        issues.append(f"⚠️ LCP cao ({v['LCP']}ms)")
        suggestions.append("Phần hero chính render chậm, ảnh hero quá lớn hoặc render blocking.")

    # -------------------------------------------------------------
    # 5. CLS cao
    # -------------------------------------------------------------
    if v["CLS"] > 0.1:
        issues.append(f"⚠️ CLS cao ({v['CLS']})")
        suggestions.append("Layout bị nhảy; thêm kích thước cố định cho ảnh, banner, video.")

    # -------------------------------------------------------------
    # 6. FID cao
    # -------------------------------------------------------------
    if v["FID"] > 100:
        issues.append(f"⚠️ FID cao ({v['FID']}ms)")
        suggestions.append("JS block main-thread hoặc event handler nặng.")

    # -------------------------------------------------------------
    # 7. Too Many Requests
    # -------------------------------------------------------------
    if total_requests > 120:
        issues.append("⚠️ quá nhiều request (>120)")
        suggestions.append("Gộp file JS/CSS. Dùng minify. Loại bỏ tài nguyên không cần thiết.")

    # -------------------------------------------------------------
    # 8. Page too heavy
    # -------------------------------------------------------------
    if total_size > 2 * 1024 * 1024:
        MB = total_size / (1024 * 1024)
        issues.append(f"⚠️ Trang quá nặng ({MB:.1f}MB)")
        suggestions.append("Nén ảnh, bật gzip/brotli, giảm bundle JS.")

    # -------------------------------------------------------------
    # 9. Large images
    # -------------------------------------------------------------
    large_imgs = [
        r for r in resources
        if r.get("initiatorType") == "img" and r.get("transferSize", 0) > 250*1024
    ]
    if large_imgs:
        issues.append(f"⚠️ Có {len(large_imgs)} ảnh lớn (>250KB)")
        suggestions.append("Dùng WebP/AVIF. Giảm chất lượng ảnh.")

    # -------------------------------------------------------------
    # 10. Heavy JS files
    # -------------------------------------------------------------
    heavy_js = [
        r for r in resources
        if r.get("initiatorType") == "script" and r.get("duration", 0) > 300
    ]
    if heavy_js:
        issues.append(f"⚠️ Có {len(heavy_js)} file JS chạy chậm (>300ms)")
        suggestions.append("Tách code (split), lazy load, loại bỏ JS không dùng.")

    # -------------------------------------------------------------
    # 11. Render-blocking resources
    # -------------------------------------------------------------
    render_blockers = [
        r for r in resources
        if r.get("initiatorType") in ("css", "script") and r.get("duration", 0) > 200
    ]
    if render_blockers:
        issues.append(f"⚠️ Có {len(render_blockers)} tài nguyên chặn render")
        suggestions.append("Dùng media=print, async/defer, tối ưu critical path.")

    # -------------------------------------------------------------
    # 12. Slow fonts
    # -------------------------------------------------------------
    slow_fonts = [
        r for r in resources
        if r.get("initiatorType") == "font" and r.get("duration", 0) > 150
    ]
    if slow_fonts:
        issues.append("⚠️ Font load chậm")
        suggestions.append("Dùng font-display: swap; preload font; nén woff2.")

    # -------------------------------------------------------------
    return {
        "issues": issues,
        "suggestions": suggestions,
    }
