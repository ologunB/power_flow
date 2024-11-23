import numpy as np
import dss

class PowerFlowAnalysis:
    def __init__(self, dss_file_path):
        self.dss_file_path = dss_file_path
        self.system_data = None
        self.manual_results = None
        self.dss_results = None

    def extract_system_data_from_dss(self):
        """Extract system data using dss-python."""
        dss_engine = dss.DSS
        dss_engine.ClearAll()
        
        try:
            dss_engine.Text.Command = f"Compile [{self.dss_file_path}]"
            print(f"DSS file '{self.dss_file_path}' compiled successfully!")
        except Exception as e:
            print(f"Error compiling DSS file: {e}")
            return None

        circuit = dss_engine.ActiveCircuit
        if not circuit:
            print("Error: Unable to access the circuit from the DSS file.")
            return None

        self.system_data = {
            "buses": [],
            "lines": [],
            "loads": [],
            "generators": [],
            "voltages": {}
        }

        # Extract buses
        self.system_data["buses"] = circuit.AllBusNames

        # Extract lines
        for element_name in circuit.Lines.AllNames:
            circuit.Lines.Name = element_name
            self.system_data["lines"].append({
                "name": element_name,
                "from": circuit.Lines.Bus1,
                "to": circuit.Lines.Bus2,
                "impedance": complex(circuit.Lines.R1, circuit.Lines.X1)
            })

        # Extract loads
        for element_name in circuit.Loads.AllNames:
            circuit.Loads.Name = element_name
            bus_names = circuit.Loads.AllNames
            if bus_names:
                bus = bus_names[0]  # Primary bus for the load
            else:
                bus = "Unknown"

            self.system_data["loads"].append({
                "bus": bus,
                "p": circuit.Loads.kW,
                "q": circuit.Loads.kvar
            })

        # Extract generators
        for element_name in circuit.Generators.AllNames:
            circuit.Generators.Name = element_name
            generator_data = {
                "bus": circuit.Generators.Bus1.split('.')[0],  # Remove phase information
                "p": circuit.Generators.kW,
                "q": circuit.Generators.kvar
            }
            self.system_data["generators"].append(generator_data)

        # Extract bus voltages
        for bus in circuit.AllBusNames:
            bus_voltage = circuit.Buses(bus).VMagAngle  # Voltage magnitude and angle
            self.system_data["voltages"][bus] = bus_voltage

    def compute_power_flow_with_dss(self):
        """Compute power flow using dss-python."""
        dss_engine = dss.DSS
        dss_engine.ClearAll()
        dss_engine.Text.Command = f"Compile [{self.dss_file_path}]"

        circuit = dss_engine.ActiveCircuit
        circuit.Solution.Solve()

        self.dss_results = {
            bus: circuit.Buses(bus).VMagAngle for bus in circuit.AllBusNames
        }

    def compute_power_flow_manual(self):
        """Compute power flow manually using Gauss-Seidel."""
        if not self.system_data:
            raise ValueError("System data is not extracted. Call `extract_system_data_from_dss` first.")

        buses = self.system_data['buses']
        lines = self.system_data['lines']
        loads = self.system_data['loads']
        generators = self.system_data['generators']

        slack_bus = self.system_data.get("slack_bus", None)
        num_buses = len(buses)
        Y_bus = np.zeros((num_buses, num_buses), dtype=complex)

        # Build Y-bus
        for line in lines:
            from_bus = buses.index(line['from'])
            to_bus = buses.index(line['to'])
            impedance = line['impedance']
            admittance = 1 / impedance

            Y_bus[from_bus, from_bus] += admittance
            Y_bus[to_bus, to_bus] += admittance
            Y_bus[from_bus, to_bus] -= admittance
            Y_bus[to_bus, from_bus] -= admittance

        # Initialize voltages
        V = np.ones(num_buses, dtype=complex)
        for i, bus in enumerate(buses):
            voltage_data = self.system_data["voltages"].get(bus, [1.0, 0.0])
            magnitude, angle = voltage_data[:2]
            V[i] = magnitude * np.exp(1j * np.radians(angle))

        # Initialize powers
        P = np.zeros(num_buses)
        Q = np.zeros(num_buses)
        for load in loads:
            bus_idx = buses.index(load['bus'])
            P[bus_idx] -= load['p'] / 1000.0
            Q[bus_idx] -= load['q'] / 1000.0
        for generator in generators:
            bus_idx = buses.index(generator['bus'])
            P[bus_idx] += generator['p'] / 1000.0
            Q[bus_idx] += generator['q'] / 1000.0

        # Gauss-Seidel
        max_iterations = 100
        tolerance = 1e-6
        for _ in range(max_iterations):
            V_prev = V.copy()
            for i in range(num_buses):
                if slack_bus and i == buses.index(slack_bus["bus"]):
                    continue
                sum_YV = sum(Y_bus[i, j] * V[j] for j in range(num_buses) if j != i)
                V[i] = ((P[i] - 1j * Q[i]) / np.conj(V[i]) - sum_YV) / Y_bus[i, i]
            if np.max(np.abs(V - V_prev)) < tolerance:
                break

        self.manual_results = {
            bus: np.array([abs(V[i]), np.degrees(np.angle(V[i])), abs(V[i]), np.degrees(np.angle(V[i]) - 120),
                           abs(V[i]), np.degrees(np.angle(V[i]) + 120)]) for i, bus in enumerate(buses)
        }

    @staticmethod
    def compare_power_flows(manual_results, dss_results):
        """Compare manual and DSS power flow results and return as a string."""
        output = []
        output.append("\n--- Comparison of Power Flow Results ---")
        output.append(f"{'Bus':<10} {'Manual Voltage (pu)':<25} {'DSS Voltage (pu)':<25} {'Difference':<15}")
        for bus in manual_results:
            manual_v = abs(manual_results[bus][0])
            dss_v = abs(dss_results.get(bus, [0])[0])
            diff = abs(manual_v - dss_v)
            output.append(f"{bus:<10} {manual_v:<25.4f} {dss_v:<25.4f} {diff:<15.4f}")
        return "\n".join(output)


if __name__ == "__main__":
    dss_file_path = "circuit.dss"

    power_flow = PowerFlowAnalysis(dss_file_path)
    power_flow.extract_system_data_from_dss()
    power_flow.compute_power_flow_with_dss()
    power_flow.compute_power_flow_manual()

    # Compare results
    comparison = PowerFlowAnalysis.compare_power_flows(power_flow.manual_results, power_flow.dss_results)
    print(comparison)
