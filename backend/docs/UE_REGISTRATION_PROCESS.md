Sure, let’s build a **detailed message flow architecture** for your 5G mobile network simulation in Python involving:

- **UE (User Equipment)**
- **gNB (Base Station)**
- **Core Network (AMF, SMF, UPF, NSSF, PCF components as needed for simulation)**

We'll follow a simplified 3GPP 5G system procedure, adapting it to your simulation and including all major events:

---

## 🌐 **5G Network Simulation: Detailed Message Flow**

### 🧩 Components Overview:
- **UE**: User device, initiates registration and service requests.
- **gNB (Next Gen NodeB)**: Radio base station, connects UE to the 5G core.
- **Core Network**:
  - **AMF (Access and Mobility Function)**: Manages registration, connection, mobility.
  - **SMF (Session Management Function)**: Sets up PDU sessions, assigns QoS.
  - **UPF (User Plane Function)**: Routes user traffic.
  - **NSSF (Network Slice Selection Function)**: Assigns network slices.
  - **PCF (Policy Control Function)**: Enforces policies like QoS.

We’ll break the message flow into **seven key stages**:

---

## ✅ 1. UE Registration (Initial Access)

### ➤ Flow:
1. **UE → gNB**: `RRCSetupRequest`  
2. **gNB ↔ UE**: `RRCSetup` / `RRCSetupComplete`
3. **gNB → AMF**: `InitialUEMessage` (includes IMSI, capability, etc.)
4. **AMF → UE**: `AuthenticationRequest`
5. **UE → AMF**: `AuthenticationResponse`
6. **AMF → UE**: `SecurityModeCommand`
7. **UE → AMF**: `SecurityModeComplete`
8. **AMF ↔ UE**: `RegistrationAccept` / `RegistrationComplete`

> Result: UE is authenticated and registered in the network.

---

## 🧬 2. Network Slice Selection (NSSF)

### ➤ Flow:
1. **AMF → NSSF**: `SliceSelectionRequest` (based on UE profile, DNN, S-NSSAI)
2. **NSSF → AMF**: `SliceSelectionResponse` (returns appropriate S-NSSAI)
3. **AMF assigns**: Selected slice to UE context

> Result: UE is now associated with a logical network slice (e.g., eMBB, URLLC, mMTC).

---

## 📶 3. QoS Flow and Session Setup (SMF, PCF)

### ➤ Flow:
1. **AMF → SMF**: `PDU Session Establishment Request` (includes S-NSSAI, DNN)
2. **SMF → PCF**: `PolicyRequest` (gets QoS parameters)
3. **PCF → SMF**: `PolicyDecision` (QoS profile, 5QI, ARP, GBR/MBR)
4. **SMF → UPF**: `PDU Session Setup` (user plane tunnel config)
5. **SMF → AMF**: `SessionSetupResponse`
6. **AMF → gNB**: `RRC Reconfiguration` with QoS config
7. **gNB ↔ UE**: Applies RRC config

> Result: A PDU session is created, with specific QoS flows (e.g., voice, video, data).

---

## 📡 4. PRB (Physical Resource Block) Assignment

### ➤ Flow:
1. **gNB Scheduler**:
   - Schedules PRBs based on QoS (GBR, non-GBR), channel conditions
   - Maintains PRB mapping table for each UE
  
2. **gNB → UE**: `Downlink Control Information (DCI)` over PDCCH
   - Assigns PRBs, MCS, HARQ processes

3. **UE ↔ gNB**: Transmit data using allocated PRBs

> Result: gNB ensures air-interface resource allocation per UE.

---

## 📈 5. Bitrate and Latency Estimation (DL/UL)

### ➤ Metrics:
- **Instantaneous bitrate**: Based on MCS × PRBs allocated × symbols per slot
- **Latency estimation**: Transmission time + queueing + propagation + processing delay

### ➤ Implementation Flow:
1. **gNB/UE keeps counters**: for bytes sent, time elapsed → compute throughput
2. **Estimation Function (Python):**
   ```python
   bitrate = (total_bytes * 8) / time_interval  # bits per second
   latency = propagation_delay + tx_time + queuing_delay
   ```
3. **DL/UL reports** sent periodically or on demand:
   - **gNB → UE/Core**: `QoS Monitoring Report`
   - **UE → gNB**: `CQI/PMI/RI` feedback

> Result: Real-time or averaged DL/UL bitrate and latency are tracked.

---

## ❌ 6. UE Deregistration

### ➤ Flow:
1. **UE → AMF**: `DeregistrationRequest`
2. **AMF → SMF**: `PDU Session Release`
3. **SMF → UPF**: `Teardown Session`
4. **SMF → PCF**: `PolicyRelease`
5. **gNB → UE**: `ReleaseResources`
6. **AMF → UE**: `DeregistrationAccept`

> Result: UE context, sessions, slices, and resources are released.

---

## 🧠 Summary of Major Python Responsibilities by Class:

### `UE` Class:
- Initiate registration
- Provide subscription info
- Handle QoS and PRB feedback
- Generate traffic
- Receive QoS metrics and report

### `BaseStation` (gNB) Class:
- Handle RRC, NAS signaling
- PRB scheduling & CQI mapping
- Estimate bitrate & latency
- Interface with AMF/SMF for session setup

### `CoreNetwork` Class (may have submodules like AMF, SMF):
- Manage UE context
- Select slice via NSSF
- Assign QoS with PCF
- Set up sessions and tunnels via SMF and UPF
- Handle deregistration

---

## 🔁 Optional Enhancements for Realism:
- **Timer-based scheduler** in gNB
- **Mobility support** (handover triggering)
- **gNodeB load balancing**
- **Queue modeling** for latency realism
- **MIMO** or beamforming abstraction
- **Traffic models** (CBR, VBR, bursty)

---

Awesome! Here's a **Python class-level skeleton** that implements the simulation framework based on the **5G message flow architecture** we discussed. It includes the core entities and methods representing UE registration, slice selection, QoS assignment, PRB scheduling, bitrate/latency estimation, and deregistration.

---

## 🧱 **Python Simulation Skeleton for 5G Architecture**

```python
import random
import time

# --- Constants for QoS and Network Slices ---
NETWORK_SLICES = {
    'eMBB': {'5QI': 9, 'GBR': 100e6, 'latency': 20},
    'URLLC': {'5QI': 1, 'GBR': 10e6, 'latency': 1},
    'mMTC': {'5QI': 5, 'GBR': 1e6, 'latency': 50},
}

# --- User Equipment (UE) Class ---
class UE:
    def __init__(self, ue_id, capabilities):
        self.ue_id = ue_id
        self.capabilities = capabilities
        self.slice = None
        self.qos_profile = None
        self.prbs = 0
        self.connected = False
        self.bitrate = {'downlink': 0, 'uplink': 0}
        self.latency = 0

    def register(self, base_station):
        print(f"UE {self.ue_id}: Initiating registration...")
        base_station.handle_registration(self)

    def receive_qos_config(self, qos_profile):
        self.qos_profile = qos_profile
        print(f"UE {self.ue_id}: Received QoS profile: {qos_profile}")

    def update_performance_metrics(self, dl_bitrate, ul_bitrate, latency):
        self.bitrate['downlink'] = dl_bitrate
        self.bitrate['uplink'] = ul_bitrate
        self.latency = latency

    def deregister(self, base_station):
        print(f"UE {self.ue_id}: Sending deregistration request.")
        base_station.handle_deregistration(self)

# --- Base Station (gNB) Class ---
class BaseStation:
    def __init__(self, bs_id, core_network):
        self.bs_id = bs_id
        self.core_network = core_network
        self.ue_registry = {}

    def handle_registration(self, ue):
        print(f"gNB {self.bs_id}: Handling registration for UE {ue.ue_id}")
        self.ue_registry[ue.ue_id] = ue
        self.core_network.authenticate_and_register(ue, self)

    def configure_qos(self, ue, qos_profile):
        print(f"gNB {self.bs_id}: Configuring QoS for UE {ue.ue_id}")
        prbs_assigned = random.randint(5, 25)
        ue.prbs = prbs_assigned
        ue.receive_qos_config(qos_profile)
        self.estimate_bitrate_and_latency(ue)

    def estimate_bitrate_and_latency(self, ue):
        mcs_efficiency = 5  # bits/symbol as example
        subcarriers = 12  # per PRB
        symbol_duration = 0.0005  # 0.5 ms
        bandwidth = ue.prbs * subcarriers * mcs_efficiency
        dl_bitrate = bandwidth / symbol_duration  # simplistic estimation
        ul_bitrate = dl_bitrate * 0.8  # assume UL is a bit lower

        latency = ue.qos_profile.get('latency', 20) + random.uniform(1, 5)

        ue.update_performance_metrics(dl_bitrate, ul_bitrate, latency)
        print(f"gNB {self.bs_id}: Estimated DL bitrate: {dl_bitrate:.2f} bps, "
              f"UL bitrate: {ul_bitrate:.2f} bps, Latency: {latency:.2f} ms")

    def handle_deregistration(self, ue):
        self.core_network.deregister_ue(ue)
        if ue.ue_id in self.ue_registry:
            del self.ue_registry[ue.ue_id]
        print(f"gNB {self.bs_id}: UE {ue.ue_id} deregistered and resources released.")

# --- Core Network Class ---
class CoreNetwork:
    def __init__(self):
        self.active_ues = {}

    def authenticate_and_register(self, ue, base_station):
        print(f"CoreNetwork: Authenticating UE {ue.ue_id}...")
        time.sleep(0.1)  # Simulate processing
        ue.connected = True

        slice_info = self.select_network_slice(ue)
        qos_profile = self.assign_qos(ue, slice_info)

        self.active_ues[ue.ue_id] = {'slice': slice_info, 'qos': qos_profile}
        ue.slice = slice_info
        base_station.configure_qos(ue, qos_profile)

    def select_network_slice(self, ue):
        # Simple logic: random or capability-based
        selected_slice = random.choice(list(NETWORK_SLICES.keys()))
        print(f"CoreNetwork: Assigned slice '{selected_slice}' to UE {ue.ue_id}")
        return selected_slice

    def assign_qos(self, ue, slice_info):
        qos_profile = NETWORK_SLICES[slice_info]
        print(f"CoreNetwork: Assigned QoS for slice '{slice_info}' to UE {ue.ue_id}")
        return qos_profile

    def deregister_ue(self, ue):
        if ue.ue_id in self.active_ues:
            print(f"CoreNetwork: Deregistering UE {ue.ue_id}")
            del self.active_ues[ue.ue_id]
        ue.connected = False
```

---

## 🚀 **How to Use This Simulation:**

```python
if __name__ == "__main__":
    core = CoreNetwork()
    gnb = BaseStation(bs_id="gNB-1", core_network=core)

    ue1 = UE(ue_id="UE001", capabilities={'supports_5g': True})
    ue1.register(gnb)

    time.sleep(1)  # Simulate session duration
    ue1.deregister(gnb)
```

---

## 🔧 What You Can Extend:
- Implement `TrafficGenerator` to simulate uplink/downlink data flow.
- Add channel conditions (e.g. SINR, CQI) to vary bitrate/latency.
- Use NumPy for vectorized PRB scheduling among multiple UEs.
- Integrate handover logic between gNBs (multi-cell simulation).
- Store logs of KPIs for visualization.

Would you like help with adding a traffic model or visualizing QoS performance over time?