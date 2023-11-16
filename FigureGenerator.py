import os
import sys
import numpy as np
from PIL import Image

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import (
    QImage,
	QPixmap,
	QIcon,
)

from PyQt6.QtWidgets import (
	QApplication,
	QMainWindow,
	QLabel,
	QWidget,
	QPushButton,
	QFileDialog,
	QSlider,
	QColorDialog,
)

class FigureManager(QMainWindow):
	def __init__(self, args: dict):
		super().__init__()

		self._window_title = args["window_title"]
		self._window_size = args["window_size"]
		self._initUI(args)
	
	def _initUI(self, args: dict):
		# set basic window setting
		if "window_title" in args:
			self.setWindowTitle(self._window_title)
		if "window_size" in args:
			self.setFixedSize(*self._window_size)

		# open image button
		self._button_open_image = QPushButton(text = "Open Image", parent = self)
		self._button_open_image.clicked.connect(self._open_image)
		self._set_coord(self._button_open_image, (0.03, 0.05), (0.035, 0.12))

		# save images button
		self._button_save_images = QPushButton(text = "Save Images", parent = self)
		self._button_save_images.clicked.connect(self._save_images)
		self._set_coord(self._button_save_images, (0.03, 0.175), (0.035, 0.12))

		# draw square button
		self._button_draw_square = QPushButton(text = "Draw Square", parent = self)
		self._button_draw_square.setCheckable(True)
		self._button_draw_square.clicked.connect(self._button_draw_square_clicked)
		self._set_coord(self._button_draw_square, (0.2, 0.5), (0.035, 0.16))

		# draw rectangle button
		self._button_draw_rectangle = QPushButton(text = "Draw Rectangle", parent = self)
		self._button_draw_rectangle.setCheckable(True)
		self._button_draw_rectangle.clicked.connect(self._button_draw_rectangle_clicked)
		self._set_coord(self._button_draw_rectangle, (0.24, 0.5), (0.035, 0.16))
		self._rectangle_start_pos = None
		self._rectangle_pos = None

		# rectangle color button
		self._button_rectangle_color = QPushButton(text = "Select Color", parent = self)
		self._button_rectangle_color.clicked.connect(self._button_rectangle_color_clicked)
		self._set_coord(self._button_rectangle_color, (0.28, 0.5), (0.035, 0.16))
		self._color = (255, 0, 0)

		# clear rectangle button
		self._button_clear_rectangle = QPushButton(text = "Clear Rectangle", parent = self)
		self._button_clear_rectangle.clicked.connect(self._button_clear_rectangle_clicked)
		self._set_coord(self._button_clear_rectangle, (0.32, 0.5), (0.035, 0.16))

		# rectangle position buttons
		self._button_position_LU = QPushButton(text = "LU", parent = self)
		self._button_position_LU.clicked.connect(self._button_position_clicked("LU"))
		self._set_coord(self._button_position_LU, (0.2, 0.67), (0.08, 0.06))
		self._button_position_RU = QPushButton(text = "RU", parent = self)
		self._button_position_RU.clicked.connect(self._button_position_clicked("RU"))
		self._set_coord(self._button_position_RU, (0.2, 0.738), (0.08, 0.06))
		self._button_position_LD = QPushButton(text = "LD", parent = self)
		self._set_coord(self._button_position_LD, (0.29, 0.67), (0.08, 0.06))
		self._button_position_LD.clicked.connect(self._button_position_clicked("LD"))
		self._button_position_RD = QPushButton(text = "RD", parent = self)
		self._set_coord(self._button_position_RD, (0.29, 0.738), (0.08, 0.06))
		self._button_position_RD.clicked.connect(self._button_position_clicked("RD"))
		self._scaled_rectangle_pos = "LD"
		
		# scale slider 
		self._text_scale_slider = QLabel(text = "Rectangle Scale: x1.00", parent = self)
		self._set_coord(self._text_scale_slider, (0.51, 0.5), (0.05, 0.3))

		self._scale_slider = QSlider(Qt.Orientation.Horizontal, parent = self)
		self._scale_slider.setRange(100, 500)
		self._scale_slider.setValue(100)
		self._scale_slider.valueChanged.connect(self._scale_slider_value_changed)
		self._set_coord(self._scale_slider, (0.5, 0.5), (0.02, 0.3))
		self._rectangle_scale = 1.0

		# thickness slider
		self._text_thickness_slider = QLabel(text = "Rectangle Thickness: 5", parent = self)
		self._set_coord(self._text_thickness_slider, (0.61, 0.5), (0.05, 0.3))

		self._thickness_slider = QSlider(Qt.Orientation.Horizontal, parent = self)
		self._thickness_slider.setRange(1, 20)
		self._thickness_slider.setValue(5)
		self._thickness_slider.valueChanged.connect(self._thickness_slider_value_changed)
		self._set_coord(self._thickness_slider, (0.6, 0.5), (0.02, 0.3))
		self._thickness = 5

		# main image label
		self._main_image = None
		self._label_main_image = QLabel(parent = self)
		self._label_main_image.mousePressEvent = self._main_image_clicked
		self._set_coord(self._label_main_image, (0.2, 0.05), (0.5, 0.4))

		# bottom image buttons
		self._images: list[Image.Image] = []
		self._image_names: list[str] = []
		self._image_buttons: list[QPushButton] = []
		self._image_bar = 0
		for i in range(5):
			btn = QPushButton(parent = self)
			btn.hide()
			btn.clicked.connect(self._images_button_clicked)
			self._set_coord(btn, (0.75, 0.05 + i * 0.18), (0.2, 0.16))
			self._image_buttons.append(btn)
		
		self.show()
	
	def _open_image(self):
		filename = QFileDialog.getOpenFileName(self, "Open Image", filter = "Image(*.png *.jpg)")[0]
		if filename:
			self._images.append(Image.open(filename).convert("RGB"))
			self._image_names.append(os.path.basename(filename))
			self._display_image_bar()
			self.show()
	
	def _save_images(self):
		folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		for img, filename in zip(self._images, self._image_names):
			filename = os.path.join(folder, filename)
			if self._rectangle_pos is not None:
				img = self._get_image_with_rectangle(img)
			name, _, ext = filename.rpartition(".")
			number = None
			
			while os.path.exists(filename):
				if number is None:
					number = 1
				else:
					number += 1
				filename = name + str(number) + "." + ext

			img.save(filename)

	def _set_coord(self, obj: QWidget, pos: tuple[float, float], size: tuple[float, float]):
		h, w = self._window_size
		pos = (int(pos[1] * h), int(pos[0] * w))
		size = (int(size[1] * h), int(size[0] * w))
		obj.move(*pos)
		obj.resize(*size)
	
	def _display_image_bar(self):
		for i in range(5):
			if i < len(self._images):
				self._image_buttons[i].show()
				self._display_image(self._image_buttons[i], self._images[i + self._image_bar])
			else:
				self._image_buttons[i].hide()

	def _display_image(self, obj: QLabel | QPushButton, image: Image.Image):
		h, w = obj.height(), obj.width()
		image = image.resize((w, h))
		data = image.tobytes("raw", "RGB")
		qim = QImage(data, w, h, QImage.Format.Format_RGB888)
		pixmap = QPixmap.fromImage(qim)
		if type(obj) == QPushButton:
			obj.setIcon(QIcon(pixmap))
			obj.setIconSize(QSize(w, h))
		elif type(obj) == QLabel:
			obj.setPixmap(pixmap)
		self.show()

	def _images_button_clicked(self):
		index = self._image_buttons.index(self.sender())
		self._main_image = index + self._image_bar
		self._display_main_image()
	
	def _button_draw_square_clicked(self):
		if self._button_draw_square.isChecked():
			self._rectangle_start_pos = None
			if self._button_draw_rectangle.isChecked():
				self._button_draw_rectangle.click()

	def _button_draw_rectangle_clicked(self):
		if self._button_draw_rectangle.isChecked():
			self._rectangle_start_pos = None
			if self._button_draw_square.isChecked():
				self._button_draw_square.click()
	
	def _main_image_clicked(self, event):
		if self._button_draw_rectangle.isChecked() or self._button_draw_square.isChecked():
			if self._rectangle_start_pos is None:
				self._rectangle_start_pos = (event.pos().y(), event.pos().x())
			else:
				self._rectangle_pos = (self._rectangle_start_pos, (event.pos().y(), event.pos().x()))

				# convert rectangle position into square position
				if self._button_draw_square.isChecked():
					pos = self._rectangle_pos
					dist = max(pos[1][0] - pos[0][0], pos[1][1] - pos[0][1])
					self._rectangle_pos = (
						pos[0],
						(pos[0][0] + dist, pos[0][1] + dist)
					)
					self._button_draw_square.click()
				else:
					self._button_draw_rectangle.click()

				self._display_main_image()

	def _get_image_with_rectangle(self, img : Image.Image) -> Image.Image:
		img = np.array(img)

		# calculate position based on label coordination
		r1, c1, _ = img.shape
		r2, c2 = self._label_main_image.height(), self._label_main_image.width()
		pos = self._rectangle_pos
		pos = (
			(int(r1 / r2 * pos[0][0]), int(c1 / c2 * pos[0][1])),
			(int(r1 / r2 * pos[1][0]), int(c1 / c2 * pos[1][1]))
		)

		# draw rectangle
		pr = [pos[0][0] - self._thickness // 2, pos[0][0] + (self._thickness + 1) // 2, pos[1][0] - self._thickness // 2, pos[1][0] + (self._thickness + 1) // 2]
		pc = [pos[0][1] - self._thickness // 2, pos[0][1] + (self._thickness + 1) // 2, pos[1][1] - self._thickness // 2, pos[1][1] + (self._thickness + 1) // 2]
		img[pr[0]:pr[1], pc[0]:pc[3], :] = self._color
		img[pr[2]:pr[3], pc[0]:pc[3], :] = self._color
		img[pr[0]:pr[3], pc[0]:pc[1], :] = self._color
		img[pr[0]:pr[3], pc[2]:pc[3], :] = self._color

		# draw small image
		small_img = img[pr[1]:pr[2], pc[1]:pc[2], :]
		h, w = int((pr[2] - pr[1]) * self._rectangle_scale), int((pc[2] - pc[1]) * self._rectangle_scale)
		small_img = Image.fromarray(small_img)
		small_img = small_img.resize((w, h))
		small_img = np.array(small_img)

		small_img = [np.pad(small_img[:, :, i], self._thickness, constant_values = self._color[i]) for i in range(3)]
		small_img = np.stack(small_img, axis = 2)
		h += self._thickness * 2
		w += self._thickness * 2

		if self._scaled_rectangle_pos == "LU":
			img[:h, :w, :] = np.array(small_img)
		elif self._scaled_rectangle_pos == "RU":
			img[:h, -w:, :] = np.array(small_img)
		elif self._scaled_rectangle_pos == "LD":
			img[-h:, :w, :] = np.array(small_img)
		elif self._scaled_rectangle_pos == "RD":
			img[-h:, -w:, :] = np.array(small_img)
	
		img = Image.fromarray(img)
		return img

	def _display_main_image(self):
		# get main image
		if self._main_image is not None:
			img = self._images[self._main_image]
			if self._rectangle_pos is not None:
				img = self._get_image_with_rectangle(img)
		
			# display image
			self._display_image(self._label_main_image, img)
	
	def _scale_slider_value_changed(self):
		self._rectangle_scale = self._scale_slider.value() / 100
		self._text_scale_slider.setText("Rectangle Scale: x{:.2f}".format(self._rectangle_scale))
		self._display_main_image()
			
	def _button_clear_rectangle_clicked(self):
		self._rectangle_pos = None
		self._display_main_image()
	
	def _button_rectangle_color_clicked(self):
		color = QColorDialog.getColor()
		self._color = color.getRgb()[:3]
		self._display_main_image()

	def _thickness_slider_value_changed(self):
		self._thickness = self._thickness_slider.value()
		self._text_thickness_slider.setText("Rectangle Thickness: {}".format(self._thickness))
		self._display_main_image()
	
	def _button_position_clicked(self, position: str):
		def func():
			self._scaled_rectangle_pos = position
			self._display_main_image()
		return func

def main():
	# window setting
	args = {}
	args["window_title"] = "Figure Manager"
	args["window_size"] = (1000, 800)

	app = QApplication(sys.argv)
	window = FigureManager(args)
	sys.exit(app.exec())

if __name__ == "__main__":
	main()