# AI-RAN Simulator Backend

The **AI-RAN Simulator Backend** is a Python-based simulation engine designed to model and analyze the behavior of 5G Radio Access Networks (RAN). It supports advanced features such as network slicing, mobility management, and intelligent control via xApps. This backend is part of a larger project that includes a frontend for visualization and interaction.

## 🚀 Features

- **5G RAN Simulation**
  - Models base stations, cells, and user equipment (UE)
  - Supports intra-frequency and inter-frequency handover
  - Implements realistic channel models and path loss calculations

- **Network Slicing**
  - Configurable slices for eMBB, URLLC, and mMTC
  - QoS-aware resource allocation based on slice requirements

- **Mobility Management**
  - Implements RRC measurement events (e.g., A3, A5) for handover decisions
  - Simulates UE movement and signal strength monitoring

- **RIC Integration**
  - Supports Near-RT RIC with xApps for intelligent control
  - Includes example xApps like blind handover based on RRC events

- **WebSocket Communication**
  - Provides real-time simulation state updates to the frontend
  - Accepts commands to start, stop, and query the simulation

- **Visualization Support**
  - Outputs simulation state in JSON format for frontend rendering

---

## 📁 Project Structure
backend/
├── core_network.py # Core network logic for UE  registration and deregistration
├── main.py # Entry point for the WebSocket server
├── ran.py # Models base stations and cells
├── ric.py # Near-RT RIC implementation
├── simulation_engine.py # Main simulation engine
├── ue.py # UE behavior and mobility logic
├── utils/ # Utility functions and classes
├── xApps/ # xApp implementations for RIC
├── settings/ # Configuration files for the simulation
├── docs/ # Documentation for RRC events, handovers, etc.
└── tests.py # Test scripts for simulation parameters

---

## 📦 Requirements

- Python 3.12 or higher  
- Install dependencies using:

```bash
pip install -r requirements.txt
```

## 🛠️ Usage
1. Start the WebSocket Server <br>Run the backend server to enable communication with the frontend:

    ```bash
    python main.py
    ```

2. Start the frontend <br> 

    ```bash
    cd frontend
    npm run dev
    ```
    
--- 

## 🧠 Example xApps

Example xApps are located in the `xApps/` directory:

* Blind Handover xApp: Implements handover decisions based on RRC Event A3.

To load custom xApps, add them to the xApps/ directory and ensure they inherit from the xAppBase class.

---

## 📝 License
This project is licensed under the MIT License. See the LICENSE file for details.

--- 

## 🤝 Contributing
Contributions are welcome! Please open issues or submit pull requests to improve the simulator.

--- 

## 📬 Contact
For questions or support, please feel free to open issues.




