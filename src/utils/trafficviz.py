def gdrive_download(url, filename):
  url_id = url.split("/")[5]
  dl_url = f"https://drive.google.com/uc?id={url_id}"
  gdown.download(dl_url, filename, quiet=False)