import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, 
                             QMessageBox, QLineEdit)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QCursor, QDoubleValidator
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
import numpy as np


class ImageTrackingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.motor_axis_1 = None
        self.motor_axis_2 = None
        self.transformation_matrix = None
        self.origin = None

    def initUI(self):
        # Set window title
        self.setWindowTitle("Image Tracking with Points")

        # Set window size to 60% of the screen
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen_geometry.width() * 0.6)
        window_height = int(screen_geometry.height() * 0.6)
        self.setGeometry(
            int(screen_geometry.width() * 0.2),
            int(screen_geometry.height() * 0.2),
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
        subtitle.setStyleSheet("font-size: 20px; font-weight: bold; margin: 8px;")
        main_layout.addWidget(subtitle)

        # Create horizontal layout for image panels
        image_layout = QHBoxLayout()

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 8, 0, 0)

        left_title = QLabel("Reference (Microscope Image) / Original White Light Image")
        left_title.setAlignment(Qt.AlignCenter)
        left_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 6px;")
        left_layout.addWidget(left_title)

        # Reduce the size of the left image label
        self.left_image_label = ClickableLabel()
        self.left_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.left_image_label.setFixedSize(600, 400)
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
        right_layout.setContentsMargins(0, 8, 0, 0)

        right_title = QLabel("Feature (White Light Image) / Displaced White Light Image")
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 6px;")
        right_layout.addWidget(right_title)

        # Reduce the size of the right image label
        self.right_image_label = ClickableLabel()
        self.right_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.right_image_label.setFixedSize(600, 400)
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


        # Save Transformation Matrix button
        self.save_matrix_button = QPushButton("Save Origin and Transformation Matrix")
        self.save_matrix_button.clicked.connect(self.handle_solve_transformation)
        main_layout.addWidget(self.save_matrix_button)

        # Add controls for motor displacement
        displacement_controls = QHBoxLayout()

        # Dropdown menu for selecting motor axis
        self.displacement_dropdown = QComboBox()
        self.displacement_dropdown.addItems(["motor_axis_1", "motor_axis_2"])
        displacement_controls.addWidget(self.displacement_dropdown)

        # Add label "Enter motor displacement"
        enter_displacement_label = QLabel("Enter motor displacement")
        displacement_controls.addWidget(enter_displacement_label)

        # Text input for motor displacement
        self.motor_displacement_input = QLineEdit()
        self.motor_displacement_input.setPlaceholderText("0000")  # Example placeholder
        self.motor_displacement_input.setValidator(QDoubleValidator())  # Restrict to floats and ints
        self.motor_displacement_input.setFixedWidth(60)  # Resize for 4-digit input
        displacement_controls.addWidget(self.motor_displacement_input)

        # Label for units
        units_label = QLabel("arbitrary motor units")
        displacement_controls.addWidget(units_label)

        # Save displacement button
        save_displacement_button = QPushButton("Save Image Displacement and Motor Displacement")
        save_displacement_button.clicked.connect(self.save_displacement)
        displacement_controls.addWidget(save_displacement_button)

        # Add to main layout
        main_layout.addLayout(displacement_controls)

        # Display motor axis 1 and motor axis 2 values
        self.motor_axis_1_label = QLabel("<b>Motor Axis 1:</b> Image Displacement (pixels): [None, None]; Motor Displacement (a.u.): None")
        self.motor_axis_2_label = QLabel("<b>Motor Axis 2:</b> Image Displacement (pixels): [None, None]; Motor Displacement (a.u.): None")
        main_layout.addWidget(self.motor_axis_1_label)
        main_layout.addWidget(self.motor_axis_2_label)

        # Add "Launch Interactive Map" button
        launch_map_button = QPushButton("Launch Interactive Map")
        launch_map_button.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        launch_map_button.clicked.connect(self.launch_interactive_map)

        # Center-align the button
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Add stretchable space on the left
        button_layout.addWidget(launch_map_button)
        button_layout.addStretch(1)  # Add stretchable space on the right

        main_layout.addLayout(button_layout)



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

    def handle_solve_transformation(self):
        """
        Handles solving the transformation matrix between the points.
        """
        # Retrieve points from the left and right panels
        left_markers = self.left_image_label.get_marker_coordinates()
        right_markers = self.right_image_label.get_marker_coordinates()

        # Check if all required points are set
        for label, markers in [("Left", left_markers), ("Right", right_markers)]:
            if not (markers.get("origin") and markers.get("axis 1") and markers.get("axis 2")):
                self.show_message(f"{label} panel is missing points. Set origin, axis 1, and axis 2.")
                return
        # saved as (column, row)    
        # print(left_markers["axis 1"])
        # Extract corresponding points
        u1 = np.array(left_markers["axis 1"]) - np.array(left_markers["origin"])
        u2 = np.array(left_markers["axis 2"]) - np.array(left_markers["origin"])

        v1 = np.array(right_markers["axis 1"]) - np.array(right_markers["origin"])
        v2 = np.array(right_markers["axis 2"]) - np.array(right_markers["origin"])

        try:
            # saves origin
            self.origin = np.array(left_markers["origin"])
            # Solve transformation
            self.transformation_matrix = solve_transformation(u1, u2, v1, v2)
            self.show_message(f"Transformation Matrix:\n{self.transformation_matrix}")
        except Exception as e:
            self.show_message(f"Error solving transformation: {e}")

    def handle_solve_displacement(self):
        """
        Handles solving the average displacement vector between points.
        """
        # Retrieve points from the left and right panels
        left_markers = self.left_image_label.get_marker_coordinates()
        right_markers = self.right_image_label.get_marker_coordinates()

        # Check if all required points are set
        for label, markers in [("Left", left_markers), ("Right", right_markers)]:
            if not (markers.get("origin") and markers.get("axis 1") and markers.get("axis 2")):
                self.show_message(f"{label} panel is missing points. Set origin, axis 1, and axis 2.")
                return

        # Extract corresponding points
        p1, p2, p3 = left_markers["origin"], left_markers["axis 1"], left_markers["axis 2"]
        p4, p5, p6 = right_markers["origin"], right_markers["axis 1"], right_markers["axis 2"]

        try:
            # Solve displacement
            displacement_vector = solve_image_displacement(p1, p2, p3, p4, p5, p6)
            self.show_message(f"Displacement Vector:\n{displacement_vector}")
        except Exception as e:
            self.show_message(f"Error solving displacement: {e}")

    def show_message(self, message):
        """
        Display a message in a dialog box.
        """
        msg_box = QMessageBox(self)
        msg_box.setText(message)
        msg_box.exec_()


    def save_displacement(self):
        """
        Save the displacement vector and motor displacement value
        for the selected motor axis.
        """
        # Retrieve selected motor axis
        motor_axis = self.displacement_dropdown.currentText()

        # Check if displacement is calculated
        try:
            # Retrieve points from the left and right panels
            left_markers = self.left_image_label.get_marker_coordinates()
            right_markers = self.right_image_label.get_marker_coordinates()

            # Extract corresponding points
            p1, p2, p3 = left_markers["origin"], left_markers["axis 1"], left_markers["axis 2"]
            p4, p5, p6 = right_markers["origin"], right_markers["axis 1"], right_markers["axis 2"]

            # Calculate displacement vector
            displacement_vector = solve_image_displacement(p1, p2, p3, p4, p5, p6)

            # Retrieve motor displacement value
            motor_displacement_value = self.motor_displacement_input.text()
            if not motor_displacement_value:
                self.show_message("Please enter a motor displacement value.")
                return

            motor_displacement_value = float(motor_displacement_value)

            # Save the result
            if motor_axis == "motor_axis_1":
                self.motor_axis_1 = (displacement_vector, motor_displacement_value)
                self.motor_axis_1_label.setText(
                    f"<b>Motor Axis 1:</b> Image Displacement (pixels): [{displacement_vector[0]:.2f}, {displacement_vector[1]:.2f}]; "
                    f"Motor Displacement (a.u.): {motor_displacement_value:.2f}"
                )
            elif motor_axis == "motor_axis_2":
                self.motor_axis_2 = (displacement_vector, motor_displacement_value)
                self.motor_axis_2_label.setText(
                    f"<b>Motor Axis 2:</b> Image Displacement (pixels): [{displacement_vector[0]:.2f}, {displacement_vector[1]:.2f}]; "
                    f"Motor Displacement (a.u.): {motor_displacement_value:.2f}"
                )

            self.show_message(f"Displacement and motor value saved to {motor_axis}: {displacement_vector}, {motor_displacement_value} units")
        except Exception as e:
            self.show_message(f"Error saving displacement: {e}")


    def launch_interactive_map(self):
        """
        Launch the interactive map window.
        """
        if self.transformation_matrix is not None and self.motor_axis_1 is not None and self.motor_axis_2 is not None:
            self.interactive_map_window = InteractiveMapWindow(self.origin, self.transformation_matrix, 
                                                            self.motor_axis_1, self.motor_axis_2)
            self.interactive_map_window.show()



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
        self.drag_start = None

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
        self._update_scaled_image(center_on_frame=True)


    def _update_scaled_image(self, center_on_frame=False):
        if not self.original_pixmap:
            return

        # Calculate the center of the frame in original image coordinates
        if self.scale_factor is not None and not center_on_frame:
            current_center_x = (self.width() / 2 - self.image_offset.x()) * self.scale_factor[0]
            current_center_y = (self.height() / 2 - self.image_offset.y()) * self.scale_factor[1]
        else:
            # Default to the center of the image for initial upload
            current_center_x = self.original_size.width() / 2
            current_center_y = self.original_size.height() / 2

        # Scale the image based on the current zoom level
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

        # Adjust the image offset
        if center_on_frame:
            # Center the image for initial upload
            self.image_offset = QPoint(
                (self.width() - scaled_pixmap.width()) // 2,
                (self.height() - scaled_pixmap.height()) // 2,
            )
        else:
            # Maintain the current position during zoom
            new_center_x = current_center_x / self.scale_factor[0]
            new_center_y = current_center_y / self.scale_factor[1]
            self.image_offset = QPoint(
                self.width() // 2 - new_center_x,
                self.height() // 2 - new_center_y,
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
        if event.button() == Qt.LeftButton:
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
        elif event.button() == Qt.RightButton:
            self.drag_start = event.pos()


    def mouseMoveEvent(self, event):
        if not self.original_pixmap:  # Ensure actions only occur when an image is uploaded
            return

        if self.drag_start is not None:  # Dragging in progress
            delta = event.pos() - self.drag_start
            self.drag_start = event.pos()

            # Calculate the current image size
            scaled_width = self.original_size.width() * self.current_scale
            scaled_height = self.original_size.height() * self.current_scale

            # Calculate allowable offsets
            min_offset_x = self.width() // 2 - scaled_width
            max_offset_x = self.width() // 2
            min_offset_y = self.height() // 2 - scaled_height
            max_offset_y = self.height() // 2

            # Update image offset and clamp within bounds
            new_offset_x = max(min_offset_x, min(max_offset_x, self.image_offset.x() + delta.x()))
            new_offset_y = max(min_offset_y, min(max_offset_y, self.image_offset.y() + delta.y()))
            self.image_offset = QPoint(new_offset_x, new_offset_y)
            self.update()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            # Stop dragging with right mouse button
            self.drag_start = None


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
        # Avoid default rendering that causes multiple images
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the pixmap with the current offset
        if self.pixmap():
            painter.drawPixmap(self.image_offset, self.pixmap())

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

        # Draw a border around the panel
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


class InteractiveMapWindow(QMainWindow):
    def __init__(self, origin, transformation_matrix, motor_axis_1, motor_axis_2):
        super().__init__()
        self.initUI()
        self.origin = origin
        self.transformation_matrix = transformation_matrix
        self.motor_axis_1 = motor_axis_1
        self.motor_axis_2 = motor_axis_2

    def initUI(self):
        self.setWindowTitle("Interactive Map")

        # Set size to match the original window
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen_geometry.width() * 0.8)
        window_height = int(screen_geometry.height() * 0.8)
        self.setGeometry(
            int(screen_geometry.width() * 0.1),
            int(screen_geometry.height() * 0.1),
            window_width,
            window_height,
        )

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Image panel (ClickableLabel)
        self.image_label = ClickableLabel()
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.image_label.setFixedSize(window_width * 0.8, window_height * 0.9)
        self.image_label.clicked.connect(self.update_coordinate_display)
        main_layout.addWidget(self.image_label)

        # Right panel with upload button and coordinate display
        right_panel = QVBoxLayout()

        # Upload button
        upload_button = QPushButton("Upload Image")
        upload_button.clicked.connect(self.upload_image)
        right_panel.addWidget(upload_button)

        # Coordinate display
        self.coordinate_display = QLabel("Coordinates: None")
        self.coordinate_display.setAlignment(Qt.AlignLeft)
        right_panel.addWidget(self.coordinate_display)

        # Motor Axis 1 and 2 displays
        self.motor_axis_1_display = QLabel("Motor Axis 1: None")
        self.motor_axis_1_display.setAlignment(Qt.AlignLeft)
        self.motor_axis_1_display.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_panel.addWidget(self.motor_axis_1_display)

        self.motor_axis_2_display = QLabel("Motor Axis 2: None")
        self.motor_axis_2_display.setAlignment(Qt.AlignLeft)
        self.motor_axis_2_display.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_panel.addWidget(self.motor_axis_2_display)


        # Add right panel to main layout
        main_layout.addLayout(right_panel)

    def upload_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_path:
            pixmap = QPixmap(file_path)
            image = QImage(file_path)
            self.image_label.set_image(pixmap, image.size())  # Use set_image to initialize scale_factor

    def update_coordinate_display(self):
        if self.image_label.crosshair_pos:
            x, y = self.image_label.crosshair_pos.x(), self.image_label.crosshair_pos.y()
            self.coordinate_display.setText(f"Coordinates: Row {int(y)}, Column {int(x)}")
            motor_axis_1, motor_axis_2 = self.solve_motor_values()
            self.motor_axis_1_display.setText(f"Motor Axis 1: {motor_axis_1:.2f}")
            self.motor_axis_2_display.setText(f"Motor Axis 2: {motor_axis_2:.2f}")

        else:
            self.coordinate_display.setText("Coordinates: None")
            self.motor_axis_1_display.setText("Motor Axis 1: None")
            self.motor_axis_2_display.setText("Motor Axis 2: None")

    def solve_motor_values(self):
        x, y = self.image_label.crosshair_pos.x(), self.image_label.crosshair_pos.y()
        v = np.array([x, y]) - self.origin   # image vector

        motor_axis_1_displacement = self.motor_axis_1[1]
        motor_axis_2_displacement = self.motor_axis_2[1]
        image_axis_1_displacement = self.motor_axis_1[0]
        image_axis_2_displacement = self.motor_axis_2[0]        

        u = self.transformation_matrix @ v    # feature map vector
        B = np.column_stack((image_axis_1_displacement, image_axis_2_displacement))
        B_inv = np.linalg.inv(B)
        c = B_inv @ u
        motor_axis_1_value = c[0] * motor_axis_1_displacement
        motor_axis_2_value = c[1] * motor_axis_2_displacement
        return motor_axis_1_value, motor_axis_2_value


# M @ u1 = v1; M @ u2 = v2, solve for M
# transformation that maps a coord in ref to feature
def solve_transformation(u1, u2, v1, v2):
    U = np.column_stack((u1, u2))
    V = np.column_stack((v1, v2))
    # M U = V so M = V @ U^{-1}
    M = V @ np.linalg.inv(U)
    return M

# compute average of p4 - p1, p5 - p2, p6 - p4
def solve_image_displacement(p1, p2, p3, p4, p5, p6):
    v1 = np.array(p4) - np.array(p1)
    v2 = np.array(p5) - np.array(p2)
    v3 = np.array(p6) - np.array(p3)
    return np.round((v1 + v2 + v3) / 3).astype(int)




def main():
    app = QApplication(sys.argv)
    ex = ImageTrackingApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
