import urllib.request
print("Downloading cloudflared...")
urllib.request.urlretrieve("https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe", "cloudflared.exe")
print("Done!")
