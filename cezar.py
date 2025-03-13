import requests
import os
import pandas as pd
import shutil
from PIL import Image
from bing_image_downloader import downloader
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from rembg import remove

def resize_jgs(directory):
    new_size = (128, 128)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        image = Image.open(file_path)
        resized = image.resize(new_size)
        os.remove(file_path)
        resized.save(file_path)

def convert_to_jpg(file_path):
	image = Image.open(file_path)
	directory, filename = os.path.split(file_path)
	data_directory = os.path.join(directory, "Dataset")
	new_path = os.path.join(data_directory, filename)
 
	if file_path.endswith(".jpg"):
		image.save(new_path)
	else:
		#convert to RGB because jpg does not support transparancy
		image = image.convert("RGB")
		new_path = os.path.splitext(new_path)[0] + ".jpg"
		image.save(new_path, "JPEG")
	os.remove(file_path)

def is_site_accessible(url, timeout=10):
	try:
		response = requests.get(url, timeout=timeout)
		response.raise_for_status()
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
			convert_to_jpg(saved_icon)
		else:
			downloader.download(company_name + "_logo", limit = 1, output_dir = '.', adult_filter_off = True, force_replace = False, timeout = 60)
			#le scot din foldere
			download_folder = company_name + "_logo"
			if os.path.exists(download_folder):
				source_path = os.path.join(download_folder, "Image_1.jpg")
				renamed_source_path = os.path.join(download_folder, company_name + ".jpg")

				os.rename(source_path, renamed_source_path)

				destination_path = os.path.join(".", company_name + ".jpg")

				shutil.move(renamed_source_path, destination_path)

				if os.path.exists(download_folder):
					shutil.rmtree(download_folder)
			convert_to_jpg(destination_path)
		resize_jgs("Dataset")

		x += 1
		if x == 10:
			break