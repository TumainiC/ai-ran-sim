import { useEffect, useRef, useCallback } from "react";

export function formatBitrate(bps) {
  if (bps >= 1e9) {
    return (bps / 1e9).toFixed(2) + " Gbps";
  } else if (bps >= 1e6) {
    return (bps / 1e6).toFixed(2) + " Mbps";
  } else if (bps >= 1e3) {
    return (bps / 1e3).toFixed(2) + " Kbps";
  } else {
    return bps + " bps";
  }
}

export default function SimulationRenderer({ simulationState }) {
  const backgroudCanvasRef = useRef(null);
  const bsCanvasRef = useRef(null);
  const ueCanvasRef = useRef(null);

  const renderBackground = () => {
    const canvas = backgroudCanvasRef.current;
    const ctx = canvas.getContext("2d");

    // Set the background color to white
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw the light gray grid
    ctx.strokeStyle = "#D3D3D3";
    ctx.lineWidth = 0.5;

    const gridSize = 20;
    for (let x = 0; x <= canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }

    for (let y = 0; y <= canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }
  };

  const renderCells = useCallback(() => {
    if (!simulationState || !simulationState.base_stations) {
      return;
    }
    console.log("rendering BS cells ...");
    const canvas = bsCanvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    simulationState.base_stations.forEach((bsData) => {
      bsData.cell_list.forEach((cellData) => {
        // cellData = {
        //     "frequency_band": "n1",
        //     "carrier_frequency_MHz": 2100,  // in MHz, e.g., from 700 to 28000)
        //     "bandwidth_Hz": 20e6,
        //     "max_prb": 106,
        //     "cell_radius": 300,
        //     "vis_position_x": 200,
        //     "vis_position_y": 200,
        //     "cell_radius": 150,
        // }
        const {
          vis_position_x,
          vis_position_y,
          vis_cell_radius,
          carrier_frequency_MHz,
        } = cellData;
        // Determine the fill color based on the frequency
        let fillColor;
        if (carrier_frequency_MHz < 3000) {
          fillColor = "rgba(135, 206, 250, 0.5)"; // Light blue for low frequencies
        } else if (carrier_frequency_MHz < 20000) {
          fillColor = "rgba(144, 238, 144, 0.5)"; // Light green for mid frequencies
        } else {
          fillColor = "rgba(255, 182, 193, 0.5)"; // Light pink for high frequencies
        }

        // Create a radial gradient
        const gradient = ctx.createRadialGradient(
          vis_position_x,
          vis_position_y,
          0, // Inner circle (center, radius 0)
          vis_position_x,
          vis_position_y,
          vis_cell_radius // Outer circle (center, radius)
        );
        gradient.addColorStop(0, fillColor); // Inner color
        gradient.addColorStop(1, "rgba(255, 255, 255, 0)"); // Outer transparent color

        // Draw the circle with the gradient
        ctx.beginPath();
        ctx.arc(
          vis_position_x,
          vis_position_y,
          vis_cell_radius,
          0,
          2 * Math.PI,
          false
        );
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw the circle's border
        ctx.setLineDash([5, 5]); // Set the dash pattern: 5px dash, 5px gap
        ctx.lineWidth = 1;
        ctx.strokeStyle = "lightgray";
        ctx.stroke();
        ctx.setLineDash([]); // Reset the dash pattern to solid for future drawings
      });

      // Draw the base station's label
      const { bs_id, vis_position_x, vis_position_y } = bsData;
      ctx.font = "14px Arial";
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.fillText(`${bs_id}`, vis_position_x, vis_position_y - 10); // Label above the base station
    });
  }, [simulationState]);

  const renderUEs = useCallback(() => {
    if (!simulationState || !simulationState.UE_list) {
      return;
    }

    const canvas = ueCanvasRef.current;
    const ctx = canvas.getContext("2d");

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const ueData of simulationState.UE_list) {
      // Draw the UE as a small 'b' character with the ue id below it
      ctx.font = "20px 'Smooch Sans'";
      ctx.fillStyle = "black";
      ctx.fillText("b", ueData.vis_position_x, ueData.vis_position_y);
      ctx.fillText(
        "[" + ueData.ue_imsi + "]",
        ueData.vis_position_x - ueData.ue_imsi.length * 4,
        ueData.vis_position_y + 16
      ); // Label above the UE

      // Draw solid orange line to the BS that's serving the UE
      if (ueData.current_cell) {
        const servingCell = simulationState.cells.find(
          (cell) => cell.cell_id === ueData.current_cell
        );
        if (servingCell) {
          // Determine the stroke color based on the frequency
          let strokeColor;
          if (ueData.current_cell.includes("low_freq")) {
            strokeColor = "rgba(135, 206, 250, 0.7)"; // Lighter blue for low frequency
          } else if (ueData.current_cell.includes("mid_freq")) {
            strokeColor = "rgba(144, 238, 144, 0.7)"; // Lighter green for mid frequency
          } else if (ueData.current_cell.includes("high_freq")) {
            strokeColor = "rgba(255, 99, 71, 0.7)"; // Lighter red for high frequency
          } else {
            strokeColor = "rgba(169, 169, 169, 0.7)"; // Lighter gray for default
          }

          ctx.strokeStyle = strokeColor;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(ueData.vis_position_x, ueData.vis_position_y);
          ctx.lineTo(servingCell.vis_position_x, servingCell.vis_position_y);
          ctx.stroke();
        }
      }
    }
  }, [simulationState]);

  useEffect(() => {
    renderBackground();
  }, []);

  useEffect(() => {
    console.log("simulation state changed.");
    console.log(simulationState);
    renderCells();
    renderUEs();
  }, [simulationState, renderCells, renderUEs]);

  let statsRendered = <div>Simulation Status Not Available Yet.</div>;
  if (
    simulationState !== null &&
    simulationState.base_station !== null &&
    simulationState.UE_list !== null
  ) {
    statsRendered = (
      <div className="gap-1">
        <div className="divider">UE Dashboard</div>
        <div className="overflow-x-auto overflow-y-auto max-h-100">
          <table className="table table-xs table-pin-rows table-pin-cols">
            <thead>
              <tr>
                <th>UE IMSI</th>
                <td>Current Cell</td>
                <td>Position</td>
                <td>Slice / QoS</td>
                <td>Downlink Bitrate</td>
                <td>Downlink Signals</td>
                <td>Downlink SINR / CQI</td>
                <td>Downlink MCS Index / MCS Data</td>
              </tr>
            </thead>
            <tbody>
              {simulationState.UE_list.map((ue) => (
                <tr key={ue.ue_imsi}>
                  <th>{ue.ue_imsi}</th>
                  <td>{ue.current_cell}</td>
                  <td>
                    X: {ue.vis_position_x}, Y: {ue.vis_position_y}
                  </td>
                  <td>
                    Slice: {ue.slice_type} <br /> 5QI: {ue.qos_profile["5QI"]}{" "}
                    <br /> GBR_DL: {formatBitrate(ue.qos_profile["GBR_DL"])}{" "}
                    <br /> GBR_UL: {formatBitrate(ue.qos_profile["GBR_UL"])}
                  </td>
                  <td>{formatBitrate(ue.downlink_bitrate)}</td>
                  <td>
                    {Object.keys(ue.downlink_received_power_dBm_dict).map(
                      (cell_id) => {
                        const frequency_priority = ue.downlink_received_power_dBm_dict[
                          cell_id
                        ].frequency_priority;

                        const received_power_dBm = ue.downlink_received_power_dBm_dict[
                          cell_id
                        ].received_power_dBm;
                        return <div key={cell_id}>{cell_id}: frequency priority: {frequency_priority} signal power: {received_power_dBm} dBm</div>;
                      }
                    )}
                  </td>
                  <td>
                    {ue.downlink_sinr} dB <br /> CQI: {ue.downlink_cqi}
                  </td>
                  <td>
                    MCS Index: {ue.downlink_mcs_index} <br />{" "}
                    {JSON.stringify(ue.downlink_mcs_data)}
                  </td>
                </tr>
              ))}
              <tr>
                <th>1</th>
                <td>Cy Ganderton</td>
                <td>Quality Control Specialist</td>
                <td>Littel, Schaden and Vandervort</td>
                <td>Canada</td>
                <td>12/16/2020</td>
                <td>Blue</td>
                <th>1</th>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="divider">Network Dashboard</div>

        {/* bs_id, cell_id, carrier_frequency_MHz, allocated_prb/max_prb/load, prb_ue_allocation_dict */}
        <div className="grid grid-cols-3 gap-2 items-center px-6">
          {simulationState.base_stations.map((bs) => (
            <div
              key={bs.bs_id + "_bs"}
              className="border-1 border-gray-300 p-2 rounded-md"
            >
              <div className="text-center">Base Station: {bs.bs_id}</div>
              {bs.cell_list.map((cell) => (
                <div key={cell.cell_id + "_cell"}>
                  <div className="divider">Cell: {cell.cell_id}</div>
                  <div className="grid grid-cols-2 gap-2 items-center">
                    <div>
                      Carrier Freq. <br /> / BW.{" "}
                    </div>
                    <div>
                      {cell.carrier_frequency_MHz} / {cell.bandwidth_Hz / 1e6}{" "}
                      MHz
                    </div>
                    <div>
                      Alloc. / Max PRB <br />
                    </div>
                    <div>
                      {cell.allocated_prb} / {cell.max_prb}
                    </div>
                    <div>Load</div>
                    <div className="stats">
                      <div className="stat">
                        <div className="stat-value">
                          {(cell.current_load * 100).toFixed(1)} %
                        </div>
                      </div>
                    </div>
                    <div>Cell Radius</div>
                    <div>{cell.vis_cell_radius * 2} m</div>
                    <div>UE served</div>
                    <div>{Object.keys(cell.prb_ue_allocation_dict).length}</div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>

        <div className="divider">Logs</div>
        <div className="log-container">
          {simulationState.logs.map((log, index) => (
            <div key={"log_" + index} className="log">
              {log}
            </div>
          ))}
        </div>
      </div>
    );
  }

  const canvasWidth = 2000;
  const canvasHeight = 1000;

  return (
    <div>
      <div
        className="canvas-container relative my-5"
        style={{ width: `${canvasWidth}px`, height: `${canvasHeight}px` }}
      >
        <canvas
          ref={backgroudCanvasRef}
          width={canvasWidth}
          height={canvasHeight}
          id="background_canvas"
          style={{ position: "absolute", top: 0, left: 0 }}
        />
        <canvas
          ref={bsCanvasRef}
          width={canvasWidth}
          height={canvasHeight}
          id="bs_canvas"
          style={{ position: "absolute", top: 0, left: 0 }}
        />
        <canvas
          ref={ueCanvasRef}
          width={canvasWidth}
          height={canvasHeight}
          id="ue_canvas"
          style={{ position: "absolute", top: 0, left: 0 }}
        />
      </div>
      {statsRendered}
    </div>
  );
}
