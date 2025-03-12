import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import pandas as pd
from bing_image_downloader import downloader

def is_site_accessible(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        #response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return False


def download_website_icon(url, output_filename="icon"):

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    html_content = response.text

    # Parse the HTML to find potential icon links
    soup = BeautifulSoup(html_content, "html.parser")
    icon_link = None

    for rel_value in ["icon", "shortcut icon", "apple-touch-icon", "apple-touch-icon-precomposed"]:
        link = soup.find("link", rel=lambda x: x and rel_value in x.lower())
        if link and link.get("href"):
            icon_link = link["href"]
            break

    # If no icon link was found, assume /favicon.ico
    if not icon_link:
        icon_link = "/favicon.ico"

    # Construct full URL if relative
    icon_url = urljoin(url, icon_link)

    icon_response = requests.get(icon_url, timeout=10)
    icon_response.raise_for_status()

    # Determine an extension from the URL or resort to .ico
    parsed_path = urlparse(icon_url).path
    _, ext = os.path.splitext(parsed_path)
    if not ext:
        ext = ".ico"

    filename = output_filename + ext
    with open(filename, "wb") as f:
        f.write(icon_response.content)

    return filename

if __name__ == "__main__":
	df = pd.read_parquet("logos.snappy.parquet")
	x = 0
	for url in df.iloc[:, 0]:
		company_name = url
		url = "https://" + url;
		if (is_site_accessible(url)):
			saved_icon = download_website_icon(url, output_filename=urlparse(url).netloc)
			print(url)
		else:
			downloader.download(company_name + " logo", limit = 1, output_dir = '.',
                    adult_filter_off = True, force_replace = False, timeout = 60)
            #le scot din foldere
            #download_folder = 
            #if os.path.exists(download_folder):
		x += 1
		if x == 10:
			break