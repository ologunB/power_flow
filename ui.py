import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog, QPushButton,
    QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from index import PowerFlowAnalysis

class OpenDSSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.selected_file = None
        self.clear_button = None
        self.solve_button = None
        self.default_button = None
        self.browse_button = None
        self.drag_label = None
        self.central_widget = None
        self.layout = None
        self.button_layout = None
        self.setWindowTitle("OpenDSS Drag-and-Drop Solver")
        self.setGeometry(200, 200, 800, 600)

        # Initialize UI components
        self.initUI()

    def initUI(self):
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Drag-and-drop label
        self.drag_label = QLabel("Drag and drop a .dss file here, click 'Browse', or use the default file")
        self.drag_label.setAlignment(Qt.AlignCenter)
        self.drag_label.setStyleSheet("background-color: lightgrey; border: 1px solid black;")
        self.drag_label.setFixedHeight(100)
        self.drag_label.setAcceptDrops(True)  # Enable drop functionality
        self.layout.addWidget(self.drag_label)

        # Buttons layout
        self.button_layout = QHBoxLayout()

        # Browse button
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.button_layout.addWidget(self.browse_button)

        # Default file button
        self.default_button = QPushButton("Use Default File")
        self.default_button.clicked.connect(self.use_default_file)
        self.button_layout.addWidget(self.default_button)

        # Solve button
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve)
        self.solve_button.setEnabled(False)  # Disabled until a file is selected
        self.solve_button.hide()  # Hidden until a file is selected
        self.button_layout.addWidget(self.solve_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_ui)
        self.clear_button.hide()  # Hidden initially
        self.button_layout.addWidget(self.clear_button)

        self.layout.addLayout(self.button_layout)

        # Result text area
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # Accept the drag event
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        if event.mimeData().hasUrls():
            # Get the first file path from the drop event
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.endswith(".dss"):
                self.handle_file(file_path)
            else:
                QMessageBox.warning(self, "Error", "Please drop a valid .dss file.")
        else:
            event.ignore()

    def browse_file(self):
        """Open a file dialog to select a DSS file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a DSS File", "", "DSS Files (*.dss);;All Files (*)"
        )
        if file_path:
            self.handle_file(file_path)

    def use_default_file(self):
        """Use the existing circuit.dss file in the current directory."""
        default_file_path = "circuit.dss"
        if os.path.exists(default_file_path):
            self.handle_file(default_file_path)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "The default file 'circuit.dss' does not exist in the current directory."
            )

    def handle_file(self, file_path):
        """Process the selected or dropped file."""
        self.selected_file = file_path
        self.drag_label.setText(f"Selected File: {file_path}")
        self.solve_button.setEnabled(True)  # Enable the Solve button
        self.solve_button.show()  # Show the Solve button
        self.clear_button.show()  # Show the Clear button
        self.default_button.hide()  # Hide the Default File button
        self.result_text.setPlainText('')

    def solve(self):
        """Parse the DSS file, solve power flow, and display results."""
        if not hasattr(self, 'selected_file') or not self.selected_file:
            QMessageBox.critical(self, "Error", "No file selected!")
            return

        try:
            power_flow = PowerFlowAnalysis(self.selected_file)
            power_flow.extract_system_data_from_dss()
            power_flow.compute_power_flow_with_dss()
            power_flow.compute_power_flow_manual()
            # Compare results
            comparison = PowerFlowAnalysis.compare_power_flows(power_flow.manual_results, power_flow.dss_results)
            # Display results
            self.result_text.setPlainText(comparison)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_ui(self):
        """Clear the UI components."""
        self.selected_file = None
        self.drag_label.setText("Drag and drop a .dss file here, click 'Browse', or use the default file")
        self.result_text.clear()
        self.solve_button.setEnabled(False)  # Disable the Solve button
        self.solve_button.hide()  # Hide the Solve button
        self.clear_button.hide()  # Hide the Clear button
        self.default_button.show()  # Show the Default File button


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenDSSApp()
    window.setAcceptDrops(True)  # Enable drag-and-drop for the main window
    window.show()
    sys.exit(app.exec_())
