import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
import json
import random


def get_mosfate_state_high_side(y1_with_noise, y2_with_noise, y3_with_noise):
    # Implement Mosfet A State Logic Here
    mosfet_1 = [1000 if p1 > p3 and p1 > p2 else 0 for p1, p2, p3 in zip(y1_with_noise, y2_with_noise, y3_with_noise)]
    mosfet_2 = [1000 if p2 > p1 and p2 > p3 else 0 for p1, p2, p3 in zip(y1_with_noise, y2_with_noise, y3_with_noise)]
    mosfet_3 = [1000 if p3 > p1 and p3 > p2 else 0 for p1, p2, p3 in zip(y1_with_noise, y2_with_noise, y3_with_noise)]
    return [mosfet_1, mosfet_2, mosfet_3]


class RealTimeRectifierSimulator(QWidget):
    def __init__(self):
        super().__init__()

        self.freq = 10
        self.sample_rate = 60
        self.upscale = 1024
        self.number_of_sample = self.sample_rate * self.freq
        self.threshold = 0.85 * self.upscale
        self.noise_factor = 0.0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.freq_label = QLabel("Frequency: 10")
        self.noise_label = QLabel("Noise Amplitude: 0.0")

        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setMinimum(1)
        self.freq_slider.setMaximum(20)
        self.freq_slider.setValue(self.freq)
        self.freq_slider.valueChanged.connect(self.update_frequency)

        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setMinimum(0)
        self.noise_slider.setMaximum(5)
        self.noise_slider.setValue(int(self.noise_factor * 10))
        self.noise_slider.valueChanged.connect(self.update_noise)

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_slider)
        layout.addWidget(self.noise_label)
        layout.addWidget(self.noise_slider)
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)
        self.setWindowTitle('Real-Time Rectifier Signal Simulator')
        self.setGeometry(100, 100, 800, 600)

        self.plot_item_phase_1 = self.plot_widget.plot()
        self.plot_item_phase_2 = self.plot_widget.plot()
        self.plot_item_phase_3 = self.plot_widget.plot()
        self.plot_item_mosfet_1 = self.plot_widget.plot()
        self.plot_item_mosfet_2 = self.plot_widget.plot()
        self.plot_item_mosfet_3 = self.plot_widget.plot()

    def update_frequency(self):
        self.freq = self.freq_slider.value()
        self.freq_label.setText(f"Frequency: {self.freq}")
        self.generate_and_update_plot()

    def update_noise(self):
        self.noise_factor = self.noise_slider.value() / 10
        self.noise_label.setText(f"Noise Amplitude: {self.noise_factor}")
        self.generate_and_update_plot()

    def generate_and_update_plot(self):

        # Generate sinusoidal signals
        freq = self.freq
        noise_factor = self.noise_factor

        number_of_sample = self.number_of_sample
        upsacle = self.upscale
        threshold = self.threshold

        phase_1 = 0
        x1 = np.linspace(0 + phase_1, freq * 2 * np.pi, number_of_sample)
        y1 = np.int32(np.sin(x1) * upsacle)

        phase_2 = 2*np.pi/3
        x2 = np.linspace(0 - phase_2, freq * 2 * np.pi - phase_2, number_of_sample)
        y2 = np.int32(np.sin(x2) * upsacle)

        phase_3 = (2*np.pi/3) + (2*np.pi/3)
        x3 = np.linspace(0 - phase_3, freq * 2 * np.pi - phase_3, number_of_sample)
        y3 = np.int32(np.sin(x3) * upsacle)

        # Add spice noise to the signals
        noise_factor = self.noise_factor  # Adjust the noise level as needed
        noise1 = np.random.normal(0, noise_factor * upsacle, number_of_sample)
        noise2 = np.random.normal(0, noise_factor * upsacle, number_of_sample)
        noise3 = np.random.normal(0, noise_factor * upsacle, number_of_sample)

        y1_with_noise = y1 + noise1
        y2_with_noise = y2 + noise2
        y3_with_noise = y3 + noise3

        # Clip values to stay within the specified threshold
        y1_with_noise[threshold < y1_with_noise] = threshold
        y1_with_noise[-threshold > y1_with_noise] = -threshold

        y2_with_noise[threshold < y2_with_noise] = threshold
        y2_with_noise[-threshold > y2_with_noise] = -threshold

        y3_with_noise[threshold < y3_with_noise] = threshold
        y3_with_noise[-threshold > y3_with_noise] = -threshold
        # =====================

        mosfet_state = get_mosfate_state_high_side(y1_with_noise, y2_with_noise, y3_with_noise)

        # # Save Data to the File
        # phase_voltage = {"phase_1": y_with_noise.tolist(), "phase_2": y_with_noise.tolist(), "phase_3": y_with_noise.tolist()}
        # with open(f"phase_voltages_{random.randint(0, 10000)}.json", "w") as fp:
        #     json.dump(phase_voltage, fp)

        # Update the plots in real-time with different colors and set labels
        self.plot_item_phase_1.setData(x1, y1_with_noise, pen=pg.mkPen(color='r', width=2), name='Phase 1')
        self.plot_item_phase_2.setData(x1, y2_with_noise, pen=pg.mkPen(color='g', width=2), name='Phase 2')
        self.plot_item_phase_3.setData(x1, y3_with_noise, pen=pg.mkPen(color='b', width=2), name='Phase 3')
        self.plot_item_mosfet_1.setData(x1, mosfet_state[0], pen=pg.mkPen(color='r', width=3), name='MOSFET 1')
        self.plot_item_mosfet_2.setData(x1, mosfet_state[1], pen=pg.mkPen(color='g', width=3), name='MOSFET 2')
        self.plot_item_mosfet_3.setData(x1, mosfet_state[2], pen=pg.mkPen(color='b', width=3), name='MOSFET 3')

        self.plot_widget.setTitle('Real-Time Rectifier Signal Simulator')

        # Add a legend to the plot
        self.plot_widget.addLegend()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimeRectifierSimulator()
    window.show()
    sys.exit(app.exec_())
