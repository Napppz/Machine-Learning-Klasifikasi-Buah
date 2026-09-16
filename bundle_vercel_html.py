"""
bundle_vercel_html.py
Menyatukan CSS dan JS langsung ke dalam api/templates/index.html
Menjamin 0% resiko error 404 pada CSS/JS di Vercel CDN!
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

index_html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
style_css = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")
main_js = (ROOT / "static" / "js" / "main.js").read_text(encoding="utf-8")

# Inline CSS
inlined_style = f"<style>\n{style_css}\n</style>"
index_html = index_html.replace('<link rel="stylesheet" href="/static/css/style.css">', inlined_style)

# Make API endpoints dual-compatible (/predict and /api/predict)
main_js_patched = main_js.replace("'/predict'", "(window.location.pathname.startsWith('/api') ? '/api/predict' : '/predict')")
main_js_patched = main_js_patched.replace("'/samples'", "(window.location.pathname.startsWith('/api') ? '/api/samples' : '/samples')")
main_js_patched = main_js_patched.replace("`/static/samples/${sampleFile}`", "`/static/samples/${sampleFile}`")

# Inline JS
inlined_script = f"<script>\n{main_js_patched}\n</script>"
index_html = index_html.replace('<script src="/static/js/main.js"></script>', inlined_script)

out_file = ROOT / "api" / "templates" / "index.html"
out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text(index_html, encoding="utf-8")

print(f"Generated {out_file} successfully! Size: {out_file.stat().st_size / 1024:.1f} KB")
