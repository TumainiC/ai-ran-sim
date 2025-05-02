## 🌐 **UE REGISTRATION PROCESS**

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
