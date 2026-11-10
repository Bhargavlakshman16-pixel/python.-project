with open(r"C:\Users\Bhargav Lakshman\Desktop\project\dump_verified.html", "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

import re
root = re.search(r'<div id="root">([\s\S]*?)</div>\s*<!-- React', text)
if root:
    out = root.group(1)[:1000].encode("ascii", "replace").decode("ascii")
    print("SUCCESSFUL DOM RENDER:")
    print(out)
