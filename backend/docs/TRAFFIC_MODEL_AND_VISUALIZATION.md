Wonderful! Let’s add two enhancements to your simulation:

---

## 🎯 **1. Traffic Model** – Simulate Uplink/Downlink Traffic

We'll add a `TrafficGenerator` class and extend `UE` and `BaseStation` to simulate:
- Constant Bit Rate (CBR) and Variable Bit Rate (VBR)
- Periodic packet generation and transfer
- Queue modeling for latency realism

---

## 📊 **2. QoS Visualization** – Plot Bitrate & Latency Over Time

Using `matplotlib`, we’ll show:
- Downlink & Uplink Bitrate (kbps)
- Latency (ms)
- Over a simulated time period

---

## ✅ Updated Classes & Code

### 🧮 **TrafficGenerator Class**

```python
import numpy as np

class TrafficGenerator:
    def __init__(self, ue, mode="CBR", duration=10, interval=1.0):
        self.ue = ue
        self.mode = mode
        self.duration = duration
        self.interval = interval  # seconds between packets
        self.time_series = []
        self.dl_rates = []
        self.ul_rates = []
        self.latencies = []

    def simulate(self):
        print(f"Simulating traffic for UE {self.ue.ue_id} in {self.mode} mode...")
        for t in range(0, self.duration):
            # Generate simulated traffic and QoS values
            if self.mode == "CBR":
                dl_bitrate = self.ue.bitrate['downlink']
                ul_bitrate = self.ue.bitrate['uplink']
                latency = self.ue.latency + np.random.uniform(-2, 2)
            elif self.mode == "VBR":
                dl_bitrate = self.ue.bitrate['downlink'] * np.random.uniform(0.5, 1.2)
                ul_bitrate = self.ue.bitrate['uplink'] * np.random.uniform(0.5, 1.1)
                latency = self.ue.latency + np.random.uniform(-5, 5)
            else:
                raise ValueError("Unknown traffic mode")

            # Store values
            self.time_series.append(t)
            self.dl_rates.append(dl_bitrate / 1e3)  # kbps
            self.ul_rates.append(ul_bitrate / 1e3)  # kbps
            self.latencies.append(max(latency, 0))

            time.sleep(self.interval)  # simulate time passage
```

---

### 📈 **Visualization Function**

```python
import matplotlib.pyplot as plt

def plot_qos_metrics(traffic_gen: TrafficGenerator):
    t = traffic_gen.time_series
    dl = traffic_gen.dl_rates
    ul = traffic_gen.ul_rates
    latency = traffic_gen.latencies

    plt.figure()
    plt.plot(t, dl, label="DL Bitrate (kbps)")
    plt.plot(t, ul, label="UL Bitrate (kbps)")
    plt.xlabel("Time (s)")
    plt.ylabel("Bitrate (kbps)")
    plt.title("Bitrate over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure()
    plt.plot(t, latency, label="Latency (ms)", color='orange')
    plt.xlabel("Time (s)")
    plt.ylabel("Latency (ms)")
    plt.title("Latency over Time")
    plt.grid(True)
    plt.legend()
    plt.show()
```

---

## 🧪 **How to Run the Traffic Simulation**

Here’s how to integrate it with your main script:

```python
if __name__ == "__main__":
    core = CoreNetwork()
    gnb = BaseStation(bs_id="gNB-1", core_network=core)

    ue1 = UE(ue_id="UE001", capabilities={'supports_5g': True})
    ue1.register(gnb)

    time.sleep(1)

    # Simulate traffic
    tg = TrafficGenerator(ue1, mode="VBR", duration=15, interval=0.5)
    tg.simulate()

    # Visualize the result
    plot_qos_metrics(tg)

    # Deregister
    ue1.deregister(gnb)
```

---

## 📌 Optional Enhancements:
- Add congestion simulation (increase latency if too many UEs).
- Implement packet queue at gNB and drop if full.
- Add `handover()` to UE and BaseStation for mobility.

Would you like help simulating multiple UEs or implementing a scheduler (e.g., Round Robin, Proportional Fair)?