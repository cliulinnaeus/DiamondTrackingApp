import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, pyqtSignal


class ImageTrackingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window title
        self.setWindowTitle('Image Tracking with Points')
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add subtitle with bigger font
        subtitle = QLabel('Define Coordinates and Key Points')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 24px; font-weight: bold; margin: 15px;")
        main_layout.addWidget(subtitle)
        
        # Create horizontal layout for image panels
        image_layout = QHBoxLayout()
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title for the left panel
        left_title = QLabel('Reference (Microscope Image)')
        left_title.setAlignment(Qt.AlignCenter)
        left_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_layout.addWidget(left_title)
        
        # Left image label and controls
        self.left_image_label = ClickableLabel()
        self.left_image_label.setFixedSize(400, 300)
        self.left_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.left_image_label.setAlignment(Qt.AlignCenter)
        self.left_image_label.clicked.connect(lambda pos: self.show_coordinates(pos, 'left'))
        left_upload_btn = QPushButton('Upload Image')
        left_upload_btn.clicked.connect(lambda: self.upload_image('left'))
        self.left_coord_label = QLabel('Coordinates: ')
        left_layout.addWidget(self.left_image_label)
        left_layout.addWidget(left_upload_btn)
        left_layout.addWidget(self.left_coord_label)
        
        # Dropdown and Set Button
        self.left_dropdown = QComboBox()
        self.left_dropdown.addItems(['origin', 'axis 1', 'axis 2'])
        left_set_btn = QPushButton('Set')
        left_set_btn.clicked.connect(lambda: self.set_point('left'))
        left_controls = QHBoxLayout()
        left_controls.addWidget(self.left_dropdown)
        left_controls.addWidget(left_set_btn)
        left_layout.addLayout(left_controls)
        
        self.left_points_label = QLabel('')
        self.left_points_label.setStyleSheet("margin: 10px;")  # Add spacing
        left_layout.addWidget(self.left_points_label)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Title for the right panel
        right_title = QLabel('Feature (White Light Image)')
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(right_title)
        
        # Right image label and controls
        self.right_image_label = ClickableLabel()
        self.right_image_label.setFixedSize(400, 300)
        self.right_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.right_image_label.setAlignment(Qt.AlignCenter)
        self.right_image_label.clicked.connect(lambda pos: self.show_coordinates(pos, 'right'))
        right_upload_btn = QPushButton('Upload Image')
        right_upload_btn.clicked.connect(lambda: self.upload_image('right'))
        self.right_coord_label = QLabel('Coordinates: ')
        right_layout.addWidget(self.right_image_label)
        right_layout.addWidget(right_upload_btn)
        right_layout.addWidget(self.right_coord_label)
        
        # Dropdown and Set Button
        self.right_dropdown = QComboBox()
        self.right_dropdown.addItems(['origin', 'axis 1', 'axis 2'])
        right_set_btn = QPushButton('Set')
        right_set_btn.clicked.connect(lambda: self.set_point('right'))
        right_controls = QHBoxLayout()
        right_controls.addWidget(self.right_dropdown)
        right_controls.addWidget(right_set_btn)
        right_layout.addLayout(right_controls)
        
        self.right_points_label = QLabel('')
        self.right_points_label.setStyleSheet("margin: 10px;")  # Add spacing
        right_layout.addWidget(self.right_points_label)
        

        # Set default display with matching colors
        self.update_points_display(self.left_points_label, self.left_image_label)
        self.update_points_display(self.right_points_label, self.right_image_label)

        # Add panels to image layout
        image_layout.addWidget(left_panel)
        image_layout.addWidget(right_panel)
        
        # Add image layout to main layout
        main_layout.addLayout(image_layout)
        
        # Set window size and position
        self.setGeometry(100, 100, 850, 600)
        
    def upload_image(self, panel):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_name:
            image = QImage(file_name)
            pixmap = QPixmap.fromImage(image)
            
            if panel == 'left':
                self.left_image_label.set_image(pixmap, image.size())
            else:
                self.right_image_label.set_image(pixmap, image.size())

    def show_coordinates(self, pos, panel):
        if panel == 'left':
            label = self.left_image_label
            coord_label = self.left_coord_label
        else:
            label = self.right_image_label
            coord_label = self.right_coord_label
        
        if label.scale_factor:
            original_x = int(pos.x() * label.scale_factor[0])
            original_y = int(pos.y() * label.scale_factor[1])
            coord_label.setText(f'Coordinates: Row: {original_y}, Column: {original_x}')
        else:
            coord_label.setText('Coordinates: None')
    
    def set_point(self, panel):
        if panel == 'left':
            label = self.left_image_label
            dropdown = self.left_dropdown
            points_label = self.left_points_label
        else:
            label = self.right_image_label
            dropdown = self.right_dropdown
            points_label = self.right_points_label

        if not label.crosshair_pos:
            return

        # Get exact pixel coordinates
        if label.scale_factor:
            original_x = int(label.crosshair_pos.x() * label.scale_factor[0])
            original_y = int(label.crosshair_pos.y() * label.scale_factor[1])
        else:
            original_x = label.crosshair_pos.x()
            original_y = label.crosshair_pos.y()

        key = dropdown.currentText()
        label.set_marker(key, (original_x, original_y))
        self.update_points_display(points_label, label)

    def update_points_display(self, points_label, label):
        colors = {'origin': 'red', 'axis 1': 'green', 'axis 2': 'purple'}
        points_text = ""
        for key, pos in label.markers.items():
            color = colors[key]
            text = f"{key.capitalize()}: {pos if pos else 'None'}"
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

    def set_image(self, pixmap, original_size):
        # Scale the image to fit the label size while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

        # Store the scale factor for coordinate transformations
        self.scale_factor = (
            original_size.width() / scaled_pixmap.width(),
            original_size.height() / scaled_pixmap.height(),
        )

        # Calculate the position of the image within the label (centered if smaller)
        self.image_offset = QPoint(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2,
        )

        self.markers = {'origin': None, 'axis 1': None, 'axis 2': None}
        self.crosshair_pos = None
        self.update()

    def mousePressEvent(self, event):
        if not self.pixmap():
            return

        # Adjust click position relative to the image position
        click_pos = event.pos()
        relative_pos = QPoint(click_pos.x() - self.image_offset.x(), click_pos.y() - self.image_offset.y())

        # Check if the click is within the image boundaries
        if (0 <= relative_pos.x() < self.pixmap().width()) and (0 <= relative_pos.y() < self.pixmap().height()):
            self.crosshair_pos = QPoint(relative_pos.x(), relative_pos.y())
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
        return {key: (value[0], value[1]) if value else None for key, value in self.markers.items()}

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pixmap():
            return

        painter = QPainter(self)

        # Draw crosshair lines if a position is selected
        if self.crosshair_pos:
            pen = QPen(Qt.red, 1)
            painter.setPen(pen)
            painter.drawLine(0, self.crosshair_pos.y() + self.image_offset.y(), self.width(), self.crosshair_pos.y() + self.image_offset.y())
            painter.drawLine(self.crosshair_pos.x() + self.image_offset.x(), 0, self.crosshair_pos.x() + self.image_offset.x(), self.height())

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
