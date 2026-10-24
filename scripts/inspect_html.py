import pathlib
import re

html = pathlib.Path(r"C:\Users\USER\AppData\Local\Temp\agapet-pets.html").read_text(
    encoding="utf-8", errors="replace"
)
srcs = re.findall(r'src="(/_next/static/chunks/[^"]+)"', html)
out = pathlib.Path(r"C:\Users\USER\AppData\Local\Temp\agapet-srcs.txt")
out.write_text("\n".join(srcs), encoding="utf-8")
print("chunks", len(srcs))
for kw in ["api.sanity.io", "groq", "useCdn", "projectId", "production", "query"]:
    print(kw, html.find(kw))

# Save RSC scripts separately
scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
rsc = pathlib.Path(r"C:\Users\USER\AppData\Local\Temp\agapet-rsc.txt")
rsc.write_text("\n\n=====SCRIPT=====\n\n".join(scripts), encoding="utf-8")
print("scripts", len(scripts), "rsc bytes", rsc.stat().st_size)
