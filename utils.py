from urllib.request import urlretrieve


def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    mb_downloaded = downloaded / (1024 * 1024)
    mb_total = total_size / (1024 * 1024) if total_size > 0 else 0
    percent = downloaded * 100 / total_size if total_size > 0 else 0
    print(f"\r{percent:.2f}% ({mb_downloaded:.2f} MB / {mb_total:.2f} MB)", end="")


def download(url, file):
    urlretrieve(url, file, reporthook=show_progress)
