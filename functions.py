import requests


def save_image(url, path="file.jpg", headers=None, timeout=15, chunk_size=8192):
    headers = headers or {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, stream=True, timeout=timeout)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size):
            if chunk:
                f.write(chunk)

    return path
