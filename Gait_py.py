import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QFrame, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from skimage.transform import resize
from matplotlib.image import imread
import numpy as np
import matplotlib.pyplot as plt
import time
import serial
import re

class UpdateSignal(QObject):
    update_plot = pyqtSignal(np.ndarray)

class PressureMapApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Pressure Map Application')
        self.setWindowIcon(QIcon("Gait Analyser"))

        self.name_label = QLabel('Enter the patient\'s name:')
        self.name_entry = QLineEdit()
        self.create_folder_button = QPushButton('Create Folder')
        self.create_folder_button.clicked.connect(self.create_folder)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_entry)
        self.layout.addWidget(self.create_folder_button)

        self.setLayout(self.layout)

    def create_folder(self):
        patient_name = self.name_entry.text().strip()

        if not patient_name:
            QMessageBox.warning(self, 'Warning', 'Please enter a valid name.')
            return

        # Get the script directory
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Set the "Patient Directories" folder
        patient_directories_folder = os.path.join(script_directory, "Patient Directories")

        # Create the folder inside the "Patient Directories" folder
        folder_path = os.path.join(patient_directories_folder, patient_name)

        try:
            os.makedirs(folder_path, exist_ok=True)
            self.close()
            main_window = QMainWindow(patient_name)
            main_window.show()
            print(f'Folder created for patient: {patient_name}')
        except OSError as e:
            QMessageBox.critical(self, 'Error', f'Failed to create folder: {str(e)}')

class QMainWindow(QWidget):
    def __init__(self, patient_name):
        super().__init__()

        self.setWindowTitle(f'Pressure Map - {patient_name}')
        self.setGeometry(100, 100, 920, 920)
        self.setWindowIcon(QIcon("Gait Analyser"))

        # Store patient_name for later use
        self.patient_name = patient_name

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        self.image_label_left = QLabel(self)
        self.image_label_left.setAlignment(Qt.AlignCenter)
        self.image_label_left.setFixedSize(800, 800)
        vbox.addWidget(QLabel("The patient's Foot Mask", self))
        vbox.addWidget(self.image_label_left)

        get_path_button_left = QPushButton('Input Foot')
        get_path_button_left.clicked.connect(lambda: self.get_input_path(self.image_label_left))
        vbox.addWidget(get_path_button_left)

        show_distribution_button = QPushButton('Show Pressure Distribution')
        show_distribution_button.clicked.connect(self.show_pressure_distribution)
        vbox.addWidget(show_distribution_button)

        self.setLayout(vbox)

    def get_input_path(self, image_label):
        input_path, _ = QFileDialog.getOpenFileName(self, 'Select input.png', '', 'Image Files (*.png *.jpg *.bmp)')

        if input_path:
            output_path = f"Patient Directories/{self.patient_name}/{self.patient_name}'s_foot_Mask.png"
            Foot_Mask_Generator(input_path, output_path)

            pixmap = QPixmap(output_path)
            pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)
            image_label.show()
            print(f'Selected input.png path: {input_path}')

    def show_pressure_distribution(self):
        ser = serial.Serial('COM4', 9600, timeout=1)
        update_signal = UpdateSignal()

        update_signal.update_plot.connect(self.update_plot)

        update_heatmap(ser, f"Patient Directories/{self.patient_name}/{self.patient_name}'s_foot_Mask.png", update_signal, update_interval=0.03)

        ser.close()

    def update_plot(self, data):
        # Update the visualization with the incoming data
        # Add your code here to handle the data as needed for your application
        pass  # Replace this line with your actual code

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

# -------------------Foot_Mask_Generator----------------------------------------
def Foot_Mask_Generator(input_path, output_path):
    image = Image.open(input_path)
    image = image.convert('RGBA')

    data = image.getdata()
    new_data = []

    for item in data:
        if item[0] == item[1] == item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    image.putdata(new_data)
    image.save(output_path, format='PNG')

# -------------------Pressure_Map_Generator----------------------------------------

# Create a custom colormap from blue to cyan to green to yellow to red
cdict = {
    'red': [(0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.5, 0.0, 0.0), (0.75, 1.0, 1.0), (1.0, 1.0, 1.0)],
    'green': [(0.0, 0.0, 0.0), (0.25, 1.0, 1.0), (0.5, 1.0, 1.0), (0.75, 1.0, 0.0), (1.0, 0.0, 0.0)],
    'blue': [(0.0, 1.0, 1.0), (0.25, 1.0, 0.0), (0.5, 0.0, 0.0), (0.75, 0.0, 0.0), (1.0, 0.0, 0.0)]
}

cmap = LinearSegmentedColormap('custom_cmap', cdict, N=256)

def create_smoothed_heatmap(sensor_values, sensor_positions, mask_image_path):
    # Create an example matrix
    example_matrix = np.zeros((300, 300))

    # Assign sensor values to the corresponding positions in the matrix
    for value, (x, y) in zip(sensor_values, sensor_positions):
        example_matrix[x, y] = value

    # Smooth the matrix using Gaussian filter to create a smoother gradient effect
    example_matrix_smoothed = gaussian_filter(example_matrix, sigma=20)

    # Load the foot shape mask from the PNG image
    foot_mask = imread(mask_image_path)[:, :, 0]  # Use only the first channel for a grayscale mask
    foot_mask = 1 - foot_mask  # Invert the mask

    # Resize the mask to match the shape of the example_matrix
    foot_mask = resize(foot_mask, example_matrix.shape, anti_aliasing=True)

    # Apply the foot mask to the smoothed matrix
    example_matrix_smoothed *= foot_mask

    # Set values outside the foot mask to zero
    example_matrix_smoothed *= foot_mask
    
    return example_matrix_smoothed

def read_arduino_values(ser):
    # Read data from Arduino
    arduino_data = ser.readline().decode('utf-8')

    # Extract values from the received string
    values = re.findall(r'\d+', arduino_data)
    
    if len(values) == 7:
        return list(map(int, values))
    else:
        return None

def update_heatmap(ser, mask_image_path, update_signal, update_interval=0.2):
    # Example sensor positions
    sensor_positions = [(252,140),(205,162),(147,169),(95,177),(69,125),(36,166),(31,117)]

    plt.ion()  # Enable interactive mode

    # Create a single figure with 2x5 subplots
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle('Real-time Pressure Updates')

    try:
        while True:
            # Read values from Arduino
            sensor_values = read_arduino_values(ser)

            if sensor_values is not None:
                # Create heatmap
                example_matrix_smoothed = create_smoothed_heatmap(sensor_values, sensor_positions, mask_image_path)

                # Clear the previous plot
                plt.clf()

                # Plot the updated heatmap on the same subplot
                im = plt.imshow(example_matrix_smoothed, cmap=cmap, aspect='auto', interpolation='nearest', origin='upper')
                ax.set_title('Real-time Pressure Updates')

                # Add contours with intensity based on the sensor values
                levels = np.linspace(0, 4095, 10)
                contours = ax.contour(example_matrix_smoothed, levels=levels, colors='white', linewidths=2, linestyles='solid')

                # Add coordinates as labels on the left and bottom
                ax.set_xticks(range(0, 301, 50))
                ax.set_yticks(range(0, 301, 50))
                ax.set_xticklabels(range(0, 301, 50))
                ax.set_yticklabels(range(0, 301, 50))

                # Add labels to the left and bottom of the heatmap
                ax.set_xlabel('X Coordinate')
                ax.set_ylabel('Y Coordinate')

                plt.pause(update_interval)  # Pause for the specified interval before the next update

                # Emit the signal to update the plot in the QMainWindow
                update_signal.update_plot.emit(example_matrix_smoothed)

                # Check if the user closed the main window
                if not plt.get_fignums():
                    break

    except KeyboardInterrupt:
        pass
    finally:
        plt.ioff()  # Disable interactive mode

        # Close the matplotlib window
        plt.close()

        # Show the final plot
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = PressureMapApp()
    main_app.show()
    sys.exit(app.exec_())
