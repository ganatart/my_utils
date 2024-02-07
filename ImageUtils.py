import numpy as np
from typing import Union, Tuple

def crop_center(img: np.ndarray, size: Union[int, Tuple[int, int]], resize: bool = True) -> np.ndarray:
	"""
		Crop center of given image

		Parameters
		----------
		img: np.ndarray
			Image to crop center, should be one of (H, W), (H, W, C) or (N, H, W, C)
		size: int | tuple[int, int]
			Size of image after crop.
			Int for square image and tuple[int, int] for rectangle image
		resize: bool
			Set true to resize image automatically
	"""