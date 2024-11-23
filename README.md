# OpenDSS Power Flow Solver

## Overview

The **OpenDSS Power Flow Solver** is a Python-based application designed to calculate and compare power flow results using the `dss-python` library. It provides both a **command-line interface (CLI)** and a **graphical user interface (GUI)** with drag-and-drop functionality for analyzing `.dss` files.

---

## Features

1. **Command-Line Execution**:
   - Analyze `.dss` files directly from the console.
   - Compute power flow using both manual calculations (via Gauss-Seidel) and `dss-python`.
   - Compare results in a structured format.

2. **Graphical User Interface (GUI)**:
   - Drag and drop `.dss` files onto the application window.
   - Browse for `.dss` files using a file dialog.
   - Use a default `.dss` file if available.
   - View formatted results in the text area.

3. **Power Flow Analysis**:
   - Manual computation using Gauss-Seidel iterations.
   - Automated computation using `dss-python`.
   - Comparison of results to identify differences.

---

## Requirements

### Dependencies
Install the required Python libraries using pip:

```bash
pip install pyqt5 dss-python numpy
```

### Files
Ensure the following files are available in the project directory:
- `index.py`: Contains the `PowerFlowAnalysis` class for power flow calculations.
- `ui.py`: Provides the GUI for drag-and-drop file handling and results display.
- `.dss` files: Example `.dss` files to analyze (e.g., `circuit.dss`).

---

## Usage

### Command-Line Interface (CLI)
Run the `index.py` file to analyze `.dss` files directly from the terminal.

#### Steps:
1. Open the terminal and navigate to the project directory.
2. Run the following command:
   ```bash
   python index.py
   ```
3. The program will:
   - Read and parse the `.dss` file (`circuit.dss` by default).
   - Compute power flow using `dss-python` and manual methods.
   - Compare the results and display them in the terminal.

### Example CLI Output:
```plaintext
--- Comparison of Power Flow Results ---
Bus        Manual Voltage (pu)       DSS Voltage (pu)          Difference     
bus1       7620.9022                 7620.9022                 0.0000         
load1      7619.0261                 7619.0261                 0.0000         
bus2       7614.1039                 7614.1039                 0.0000         
```

---

### Graphical User Interface (GUI)
Run the `ui.py` file to launch the drag-and-drop GUI application.

#### Steps:
1. Open the terminal and navigate to the project directory.
2. Run the following command:
   ```bash
   python ui.py
   ```
3. Interact with the GUI:
   - Drag and drop a `.dss` file onto the application.
   - Or, click **Browse** to select a `.dss` file.
   - Or, click **Use Default File** to analyze `circuit.dss`.
4. Click **Solve** to compute power flow and view results in the text area.
5. Click **Clear** to reset the interface.

---

## File Structure

### `index.py`
Contains the core logic for power flow analysis:
- **`PowerFlowAnalysis` Class**:
  - `extract_system_data_from_dss`: Parses the `.dss` file and extracts system data.
  - `compute_power_flow_with_dss`: Computes power flow using `dss-python`.
  - `compute_power_flow_manual`: Computes power flow manually using Gauss-Seidel.
  - `compare_power_flows`: Compares the results of manual and `dss-python` computations.

### `ui.py`
Provides the graphical user interface using PyQt5:
- Drag-and-drop functionality for `.dss` files.
- Button-based file selection.
- Result display in a read-only text area.

### Example `.dss` File
```plaintext
clear
New Circuit.Ckt1
~ basekv=13.2 pu=1.0 MVAsc3=100000 MVAsc1=100000 bus1=Bus1

New Vsource.Slack Bus1=Bus1 BasekV=13.2 pu=1.0 Phase=3

New Line.Line1 Bus1=Bus1 Bus2=load1 R1=0.01 X1=0.1 R0=0.01 X0=0.1 Length=1 Units=kft
New Line.Line2 Bus1=Bus1 Bus2=bus2 R1=0.02 X1=0.15 R0=0.02 X0=0.15 Length=1 Units=kft

New Load.Load1 Bus1=load1 Phases=3 kV=13.2 kW=1000 pf=0.95
New Load.Load2 Bus1=bus2 Phases=3 kV=13.2 kW=2000 pf=0.90

New Generator.G1 Bus1=Bus2 kV=13.2 kW=1500 pf=1 Model=1

Set VoltageBases=[13.2]
CalcVoltageBases
Solve
```

---

## Troubleshooting

### Common Errors
1. **`circuit.dss` Not Found**:
   - Ensure `circuit.dss` exists in the current directory for default file processing.

2. **Invalid File Type**:
   - The application accepts only `.dss` files. Dragging or browsing other file types will result in an error.

3. **Missing Dependencies**:
   - Ensure all required libraries are installed:
     ```bash
     pip install pyqt5 dss-python numpy
     ```

4. **GUI Issues**:
   - If the GUI does not start, ensure PyQt5 is installed and properly configured.

5. **Some DSS Files are outdated**:
   - In this case, it tells you it cant process the circuit because of some elements in it, please contact developer(Me) or open issue and add the .dss file so it can be improved on.

---

## Future Enhancements
- Add support for more advanced power flow algorithms.
- Include real-time plotting of results.
- Extend file format compatibility beyond `.dss`.

---

## Contributors
- **Temitope**: Developed the core logic and GUI.

For any questions or issues, feel free to contact **logunbabatope@gmail.com**.
