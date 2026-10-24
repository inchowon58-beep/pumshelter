import json
import os
import urllib.request

key = os.environ["GEMINI_API_KEY"]
request = urllib.request.Request(
    "https://generativelanguage.googleapis.com/v1beta/models?pageSize=100",
    headers={"x-goog-api-key": key},
)
with urllib.request.urlopen(request, timeout=30) as response:
    payload = json.load(response)
names = []
for model in payload.get("models", []):
    name = model.get("name", "")
    methods = ",".join(model.get("supportedGenerationMethods") or [])
    if any(word in name.lower() for word in ("image", "imagen", "flash", "3.8", "3.1")):
        names.append(f"{name} [{methods}]")
path = r"f:\강아지보호소품으로\data\models.txt"
open(path, "w", encoding="utf-8").write("\n".join(names))
print(len(names))
