import os
import urllib
from tqdm import tqdm
from shutil import rmtree
from flickrapi import FlickrAPI

NUMBER_OF_IMAGES = 1000 # number of images to save
FOLDER = "snow" # folder name to save images
TEXT = "snowy road" # text keyword

KEY = "YOUR FLICKR KEY"
SECRET = "YOUR FLICKR SECRET"

def download_images(FLICKR_KEY: str, FLICKR_SECRET: str, folder: str, text: str, number_of_images: int, verbose: int = 1, overwrite_folder: bool = True) -> None:
	"""
		Download images from flickr for given text
		Format of downloaded images will be 00000.jpg, 00001.jpg, .... 

		Parameters
		----------
		FLICKR_KEY: str
			Key for flickr api
		FLICKR_SECRET: str
			Secret for flickr api
		folder: str
			Folder to save images
		text: str
			Text keyword for images
		number_of_images: int
			Number of images to download
		verbose: int
			Set 1 to display progress of downloading
		overwrite_folder: bool
			Set True to remove files in existing folder and save images

		Examples
		--------
		>>> KEY = "YOUR FLICKR KEY"
		>>> SECRET = "YOUR FLICKR SECRET"
		>>> download_images(KEY, SECRET, "snow", "snow highway", 5)
		5it [00:00, 2.05it/s]
	"""

	# Load flickrapi
	flickr = FlickrAPI(
		api_key = FLICKR_KEY,
		secret = FLICKR_SECRET
	)

	# search url links using api
	photos = flickr.walk(
		text = text,
		extras = "url_c",
		per_page = 100,
		sort = "relevance"
	)
	urls = []
	for i, photo in enumerate(photos):
		url = photo.get("url_c")
		if url:
			urls.append(url)

		if i > number_of_images:
			break
	
	# Set folder to save images
	if os.path.exists(folder):
		if overwrite_folder:
			rmtree(folder)
		else:
			raise ValueError("Folder {} already exists. Chnage folder or set overwrite_folder parameter True to save images.".format(folder))
	os.makedirs(folder)

	# save images to folder
	pbar = None
	if verbose:
		pbar = tqdm(total = number_of_images)

	for i, url in enumerate(urls):
		path = os.path.join(folder, "{:05d}.jpg".format(i))
		urllib.request.urlretrieve(url, path)
		if pbar:
			pbar.update(1)
	if pbar:
		pbar.close

if __name__ == "__main__":
	from Flickr_key import flickr_keys
	download_images(
		flickr_keys["key"],
		flickr_keys["secret"],
		"highway",
		"highway",
		1000,
	)