import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

class ImageTrackingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window title
        self.setWindowTitle("Image Tracking with Points")

        # Set window size to 80% of the screen
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen_geometry.width() * 0.8)
        window_height = int(screen_geometry.height() * 0.8)
        self.setGeometry(
            int(screen_geometry.width() * 0.1),
            int(screen_geometry.height() * 0.1),
            window_width,
            window_height,
        )

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add subtitle with bigger font and move it up
        subtitle = QLabel("Define Coordinates and Key Points")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(subtitle)

        # Create horizontal layout for image panels
        image_layout = QHBoxLayout()

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 10, 0, 0)  # Move content upward

        # Title for the left panel
        left_title = QLabel("Reference (Microscope Image)")
        left_title.setAlignment(Qt.AlignCenter)
        left_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(left_title)

        # Left image label and controls
        self.left_image_label = ClickableLabel()
        self.left_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.left_image_label.setFixedSize(800, 600)
        self.left_image_label.clicked.connect(lambda pos: self.show_coordinates(pos, "left"))
        left_layout.addWidget(self.left_image_label)

        left_upload_btn = QPushButton("Upload Image")
        left_upload_btn.clicked.connect(lambda: self.upload_image("left"))
        left_layout.addWidget(left_upload_btn)

        self.left_coord_label = QLabel("Coordinates: ")
        left_layout.addWidget(self.left_coord_label)

        self.left_dropdown = QComboBox()
        self.left_dropdown.addItems(["origin", "axis 1", "axis 2"])
        left_set_btn = QPushButton("Set")
        left_set_btn.clicked.connect(lambda: self.set_point("left"))
        left_controls = QHBoxLayout()
        left_controls.addWidget(self.left_dropdown)
        left_controls.addWidget(left_set_btn)
        left_layout.addLayout(left_controls)

        self.left_points_label = QLabel("")
        self.update_points_display(self.left_points_label, self.left_image_label)
        left_layout.addWidget(self.left_points_label)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 10, 0, 0)  # Move content upward

        # Title for the right panel
        right_title = QLabel("Feature (White Light Image)")
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(right_title)

        # Right image label and controls
        self.right_image_label = ClickableLabel()
        self.right_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.right_image_label.setFixedSize(800, 600)
        self.right_image_label.clicked.connect(lambda pos: self.show_coordinates(pos, "right"))
        right_layout.addWidget(self.right_image_label)

        right_upload_btn = QPushButton("Upload Image")
        right_upload_btn.clicked.connect(lambda: self.upload_image("right"))
        right_layout.addWidget(right_upload_btn)

        self.right_coord_label = QLabel("Coordinates: ")
        right_layout.addWidget(self.right_coord_label)

        self.right_dropdown = QComboBox()
        self.right_dropdown.addItems(["origin", "axis 1", "axis 2"])
        right_set_btn = QPushButton("Set")
        right_set_btn.clicked.connect(lambda: self.set_point("right"))
        right_controls = QHBoxLayout()
        right_controls.addWidget(self.right_dropdown)
        right_controls.addWidget(right_set_btn)
        right_layout.addLayout(right_controls)

        self.right_points_label = QLabel("")
        self.update_points_display(self.right_points_label, self.right_image_label)
        right_layout.addWidget(self.right_points_label)

        # Add panels to image layout
        image_layout.addWidget(left_panel)
        image_layout.addWidget(right_panel)

        # Add image layout to main layout
        main_layout.addLayout(image_layout)

    def upload_image(self, panel):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )

        if file_name:
            image = QImage(file_name)
            pixmap = QPixmap.fromImage(image)

            if panel == "left":
                self.left_image_label.set_image(pixmap, image.size())
            else:
                self.right_image_label.set_image(pixmap, image.size())

    def show_coordinates(self, pos, panel):
        if panel == "left":
            label = self.left_image_label
            coord_label = self.left_coord_label
        else:
            label = self.right_image_label
            coord_label = self.right_coord_label

        if pos:
            coord_label.setText(f"Coordinates: Row: {pos.y()}, Column: {pos.x()}")
        else:
            coord_label.setText("Coordinates: None")

    def set_point(self, panel):
        if panel == "left":
            label = self.left_image_label
            dropdown = self.left_dropdown
            points_label = self.left_points_label
        else:
            label = self.right_image_label
            dropdown = self.right_dropdown
            points_label = self.right_points_label

        if not label.crosshair_pos:
            return

        original_x = int(label.crosshair_pos.x())
        original_y = int(label.crosshair_pos.y())
        key = dropdown.currentText()
        label.set_marker(key, (original_x, original_y))
        self.update_points_display(points_label, label)


    def update_points_display(self, points_label, label):
        colors = {'origin': 'red', 'axis 1': 'green', 'axis 2': 'purple'}
        points_text = ""
        for key in ['origin', 'axis 1', 'axis 2']:
            color = colors[key]
            pos = label.get_marker_coordinates().get(key, None)
            if pos:
                text = f"{key.capitalize()}: Row: {pos[1]}, Column: {pos[0]}"
            else:
                text = f"{key.capitalize()}: None"
            points_text += f'<div style="color: {color};">{text}</div>'
        points_label.setText(points_text)



class ClickableLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self):
        super().__init__()
        self.markers = {'origin': None, 'axis 1': None, 'axis 2': None}
        self.crosshair_pos = None
        self.scale_factor = None
        self.image_offset = QPoint(0, 0)  # Position of the image within the panel
        self.current_scale = 1.0  # Current zoom level
        self.original_pixmap = None  # Store original pixmap for resetting
        self.original_size = None  # Store original image size
        self.setAlignment(Qt.AlignCenter)

    def set_image(self, pixmap, original_size):
        self.original_pixmap = pixmap
        self.original_size = original_size

        # Reset zoom and scale factors
        self.current_scale = min(
            self.width() / original_size.width(),
            self.height() / original_size.height(),
        )  # Ensure the image is fully visible by default
        self.scale_factor = (1.0, 1.0)

        # Scale and display the image
        self._update_scaled_image()

    def _update_scaled_image(self):
        if not self.original_pixmap:
            return

        # Scale the image based on the current scale
        scaled_pixmap = self.original_pixmap.scaled(
            self.original_size.width() * self.current_scale,
            self.original_size.height() * self.current_scale,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.setPixmap(scaled_pixmap)

        # Update the scale factor
        self.scale_factor = (
            self.original_size.width() / scaled_pixmap.width(),
            self.original_size.height() / scaled_pixmap.height(),
        )

        # Center the image in the label
        self.image_offset = QPoint(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2,
        )
        self.update()

    def wheelEvent(self, event):
        if not self.original_pixmap:
            return  # Do not allow zoom if no image is uploaded

        # Check if the mouse is within the image boundaries
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        if not (self.image_offset.x() <= cursor_pos.x() < self.image_offset.x() + self.pixmap().width() and
                self.image_offset.y() <= cursor_pos.y() < self.image_offset.y() + self.pixmap().height()):
            return  # Do not zoom if the cursor is outside the image

        # Zoom in or out based on the scroll direction
        zoom_factor = 0.2  # Faster zoom
        if event.angleDelta().y() > 0:  # Scroll up (zoom in)
            self.current_scale += zoom_factor
        elif self.current_scale > min(
            self.width() / self.original_size.width(),
            self.height() / self.original_size.height(),
        ):  # Scroll down (zoom out)
            self.current_scale = max(
                min(self.width() / self.original_size.width(),
                    self.height() / self.original_size.height()),
                self.current_scale - zoom_factor,
            )

        # Update the scaled image
        self._update_scaled_image()

    def mousePressEvent(self, event):
        if not self.pixmap():
            return

        # Adjust click position relative to the image position
        click_pos = event.pos()
        relative_pos = QPoint(click_pos.x() - self.image_offset.x(), click_pos.y() - self.image_offset.y())

        # Check if the click is within the image boundaries
        if (0 <= relative_pos.x() < self.pixmap().width()) and (0 <= relative_pos.y() < self.pixmap().height()):
            # Convert to original image coordinates and store
            self.crosshair_pos = QPoint(
                int(relative_pos.x() * self.scale_factor[0]),
                int(relative_pos.y() * self.scale_factor[1])
            )
            self.clicked.emit(self.crosshair_pos)
            self.update()



    def set_marker(self, key, pos):
        # Store marker in original image coordinates
        if isinstance(pos, QPoint):
            x, y = pos.x(), pos.y()
        elif isinstance(pos, tuple):
            x, y = pos
        else:
            raise ValueError("Position must be a QPoint or a tuple.")
        self.markers[key] = (x, y)
        self.update()

    def get_marker_coordinates(self):
        # Return original coordinates of markers
        return {key: value if value else None for key, value in self.markers.items()}


    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pixmap():
            return

        painter = QPainter(self)

        # Draw crosshair lines if a position is selected
        if self.crosshair_pos:
            pen = QPen(Qt.red, 1)
            painter.setPen(pen)

            # Convert original coordinates to scaled coordinates for drawing
            scaled_cross_x = int(self.crosshair_pos.x() / self.scale_factor[0]) + self.image_offset.x()
            scaled_cross_y = int(self.crosshair_pos.y() / self.scale_factor[1]) + self.image_offset.y()

            painter.drawLine(0, scaled_cross_y, self.width(), scaled_cross_y)  # Horizontal
            painter.drawLine(scaled_cross_x, 0, scaled_cross_x, self.height())  # Vertical

        # Draw markers for origin, axis 1, and axis 2
        colors = {'origin': Qt.red, 'axis 1': Qt.green, 'axis 2': Qt.magenta}
        for key, pos in self.markers.items():
            if pos:
                # Convert original pixel coordinates to scaled coordinates for display
                scaled_x = int(pos[0] / self.scale_factor[0]) + self.image_offset.x()
                scaled_y = int(pos[1] / self.scale_factor[1]) + self.image_offset.y()
                pen.setColor(colors[key])
                pen.setWidth(3)
                painter.setPen(pen)
                painter.drawEllipse(QPoint(scaled_x, scaled_y), 5, 5)



def main():
    app = QApplication(sys.argv)
    ex = ImageTrackingApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
