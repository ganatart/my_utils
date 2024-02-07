import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple

def save_image(img: np.ndarray, path: str) -> None:
	"""
		Save numpy array image to given path

		Parameters
		----------
		img: np.ndarray
			Numpy array image to save. should be one of (H, W) or (H, W, C).
		path: str
			Path to save image

		Examples
		--------
		>>> img = Image.open("sample.png")
		>>> img_np = np.array(img)
		>>> img_np_float = img.astype(np.float32) / 255
		>>> save_image(img_np, "img1.png")
		>>> save_image(img_np_float, "img2.png")
	"""

	if img.dtype == float:
		img = (np.crop(img, 0, 1) * 255).astype(np.uint8)
	
	img = Image.fromarray(img)
	img.save(path)

def crop_center(img: np.ndarray, size: Union[int, Tuple[int, int]], resize: bool = True) -> np.ndarray:
	"""
		Crop center of given image

		Parameters
		----------
		img: np.ndarray
			Image to crop center, should be one of (H, W) or (H, W, C)
		size: int | tuple[int, int]
			Size of image after crop.
			Int for square image and tuple[int, int] for rectangle image
		resize: bool
			Set true to resize the image according to "size" parameter
		
		Returns
		-------
		res: np.ndarray
			Result of cropped image, same dimension to given image
		
		Examples
		--------
		>>> img = Image.open("sample.png")
		>>> img_np = np.array(img)
		>>> img.shape
		(800, 712)
		>>> img_cropped = crop_center(img, 512)
		>>> img_cropped.shape
		(512, 512)
	"""

	# check size of image
	if img.ndim == 2:
		H, W = img.shape
	elif img.ndim == 3:
		H, W, _ = img.shape
	else:
		raise ValueError("Shape of given image should be one of (H, W) or (H, W, C)")

	# check target size of image
	if type(size) == int:
		tarH = tarW = size
	else:
		tarH, tarW = size

	#  resize image
	if resize:
		ratioH = tarH / H
		ratioW = tarW / W
		ratio = max(ratioH, ratioW)
		newH = int(H * ratio + 0.01)
		newW = int(W * ratio + 0.01)
		img = cv2.resize(img, (newH, newW))

		if img.ndim == 2:
			H, W = img.shape
		elif img.ndim == 3:
			H, W, _ = img.shape
	
	# crop image
	if H < tarH or W < tarW:
		raise ValueError("Given image shape ({}, {}) is smaller than cropped image shape ({}, {}). Adjust cropped size or set resize parameter True".format(H, W, tarH, tarW))
	startH = (H - tarH) // 2
	startW = (W - tarW) // 2
	if img.ndim == 2:
		img = img[startH:startH + tarH, startW:startW + tarW]
	elif img.ndim == 3:
		img = img[startH:startH + tarH, startW:startW + tarW, :]

	# return cropped image
	return img
	
if __name__ == "__main__":
	PATH = "sample.jpg"
	img = Image.open(PATH)
	img = np.array(img)

	img = crop_center(img, 256, True)
	save_image(img, "test.png")