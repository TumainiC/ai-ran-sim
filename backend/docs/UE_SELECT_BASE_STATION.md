In real 5G networks, **UE selection of a serving base station (gNB)** during registration is a **radio-level decision** based on a combination of signal quality, load, and policies. Let's walk through the **correct process** and how to simulate it properly.

---

## ✅ **Correct Process: UE Selects Base Station to Register With**

When a UE powers on or moves into a new area, it performs the following steps:

### 1. **Cell Search and Synchronization**
- UE scans for nearby base stations (gNBs) via their Synchronization Signals (SSBs).
- Measures signal strength and quality for each detected gNB.

### 2. **Measure Signal Quality**
- UE calculates metrics like:
  - **RSRP** (Reference Signal Received Power)
  - **RSRQ** (Reference Signal Received Quality)
  - **SINR** (Signal-to-Interference-plus-Noise Ratio)

### 3. **Filter Candidate gNBs**
- UE filters out gNBs below a threshold (e.g., RSRP < -110 dBm).

### 4. **Select Best gNB**
- Typically selects the gNB with:
  - Highest RSRP **and**
  - Acceptable RSRQ/SINR
- Some implementations may include:
  - **Load balancing policies** (avoid congested cells)
  - **Priority rules** (e.g., macro > small cells)

### 5. **Initiate Registration**
- UE sends `RRCSetupRequest` to selected gNB.

---

## 🧠 **Simulation Strategy: Best Base Station Selection**

### 💡 Simulate the RSRP Calculation:
```python
def calculate_rsrp(ue_position, bs_position, transmit_power=40, path_loss_exponent=3.5):
    distance = ((ue_position[0] - bs_position[0])**2 + (ue_position[1] - bs_position[1])**2) ** 0.5
    if distance == 0:
        return transmit_power
    path_loss_db = 10 * path_loss_exponent * math.log10(distance)
    rsrp = transmit_power - path_loss_db  # in dBm
    return rsrp
```

### 🧩 Step-by-step:
1. Each gNB has a position and a transmit power.
2. UE measures RSRP from all reachable gNBs.
3. UE selects the gNB with the **highest RSRP** above a threshold.
4. Optional: Add randomness to simulate measurement error or bias.
5. Optional: Incorporate load-awareness or slicing preference (e.g., URLLC → edge gNB).

---

### 🧪 Example Usage:

```python
import math

# Define UE and base station locations
ue_pos = (100, 200)
base_stations = [
    {'id': 'gNB-1', 'position': (120, 180), 'load': 0.5},
    {'id': 'gNB-2', 'position': (300, 400), 'load': 0.2},
    {'id': 'gNB-3', 'position': (90, 210),  'load': 0.9},
]

# Select best base station
def select_best_gnb(ue_pos, gnb_list):
    candidates = []
    for gnb in gnb_list:
        rsrp = calculate_rsrp(ue_pos, gnb['position'])
        if rsrp > -110:  # Acceptable signal strength
            candidates.append((gnb, rsrp))
    if not candidates:
        return None
    # Sort by RSRP (and optionally inverse load)
    candidates.sort(key=lambda x: (x[1], -x[0]['load']), reverse=True)
    return candidates[0][0]  # Best gNB

best_gnb = select_best_gnb(ue_pos, base_stations)
print(f"UE selects base station: {best_gnb['id']}")
```

---

## 📦 Suggestions for Integration into Your Simulation:

1. Add `position` attributes to `UE` and `BaseStation`.
2. Extend `BaseStation` with methods to broadcast signal.
3. Add UE method like `scan_and_select_gnb(all_base_stations)`.

---

Would you like me to help you modify your existing UE and BaseStation classes to include position and signal-based selection?