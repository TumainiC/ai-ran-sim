import settings
import numpy as np
import matplotlib.pyplot as plt
from utils import get_pass_loss_model

##################################
#   Ues the plot below to tune the cell qrx_level_min against the cell radius.
##################################

test_cells = settings.RAN_BS_DEFAULT_CELLS("bs_test")

# Get the path loss model
pass_loss_model = get_pass_loss_model(settings.CHANNEL_PASS_LOSS_MODEL)

# Define distances (in meters)
distances = np.linspace(1, 6000, 500)  # From 1m to 500m

# Plot received power for each cell
plt.figure(figsize=(10, 6))
for cell in test_cells:
    received_powers = []
    for distance in distances:
        # Calculate received power
        received_power = (
            cell["transmit_power"]
            - pass_loss_model(distance_m=distance, frequency_in_ghz=cell["carrier_frequency"] / 1000)
            + cell["cell_individual_offset"]
        )
        received_powers.append(received_power)
    
    # Plot the results
    plt.plot(distances, received_powers, label=f"{cell['cell_id']} ({cell['carrier_frequency']} MHz)")

# Add labels, legend, and title
plt.xlabel("Distance (m)")
plt.ylabel("Received Power (dBm)")
plt.title("Received Power vs Distance for Test Cells")
plt.legend()
plt.grid()
plt.show()