import { useEffect, useRef, useCallback } from "react";

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
      bsData.cells.forEach((cellData) => {
        // cellData = {
        //     "frequency_band": "n1",
        //     "carrier_frequency": 2100,  // in MHz, e.g., from 700 to 28000)
        //     "bandwidth": 20e6,
        //     "max_prb": 106,
        //     "cell_radius": 300,
        //     "position_x": 200,
        //     "position_y": 200,
        //     "cell_radius": 150,
        // }
        const { position_x, position_y, cell_radius, carrier_frequency } =
          cellData;
        // Determine the fill color based on the frequency
        let fillColor;
        if (carrier_frequency < 3000) {
          fillColor = "rgba(135, 206, 250, 0.5)"; // Light blue for low frequencies
        } else if (carrier_frequency < 20000) {
          fillColor = "rgba(144, 238, 144, 0.5)"; // Light green for mid frequencies
        } else {
          fillColor = "rgba(255, 182, 193, 0.5)"; // Light pink for high frequencies
        }

        // Create a radial gradient
        const gradient = ctx.createRadialGradient(
          position_x,
          position_y,
          0, // Inner circle (center, radius 0)
          position_x,
          position_y,
          cell_radius // Outer circle (center, radius)
        );
        gradient.addColorStop(0, fillColor); // Inner color
        gradient.addColorStop(1, "rgba(255, 255, 255, 0)"); // Outer transparent color

        // Draw the circle with the gradient
        ctx.beginPath();
        ctx.arc(position_x, position_y, cell_radius, 0, 2 * Math.PI, false);
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
      const { bs_id, position_x, position_y } = bsData;
      ctx.font = "14px Arial";
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.fillText(`${bs_id}`, position_x, position_y - 10); // Label above the base station
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
      // Draw the UE as a small 'b' character
      ctx.font = "20px 'Smooch Sans'";
      ctx.fillStyle = "black";
      ctx.fillText("b", ueData.position_x, ueData.position_y);

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
          ctx.moveTo(ueData.position_x, ueData.position_y);
          ctx.lineTo(servingCell.position_x, servingCell.position_y);
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
        <div className="divider">Network Dashboard</div>

        {/* bs_id, cell_id, carrier_frequency, allocated_prb/max_prb/load, prb_ue_allocation_dict */}
        <div className="grid grid-cols-4 gap-2 items-center px-6">
          {simulationState.base_stations.map((bs) => (
            <div
              key={bs.bs_id + "_bs"}
              className="border-1 border-gray-300 p-2 rounded-md"
            >
              <div className="text-center">Base Station: {bs.bs_id}</div>
              {bs.cells.map((cell) => (
                <div key={cell.cell_id + "_cell"}>
                  <div className="divider">Cell: {cell.cell_id}</div>
                  <div className="grid grid-cols-2 gap-2 items-center">
                    <div>
                      Carrier Freq. <br /> / BW.{" "}
                    </div>
                    <div>
                      {cell.carrier_frequency} / {cell.bandwidth / 1e6} MHz
                    </div>
                    <div>
                      Alloc. / Max PRB <br />
                    </div>
                    <div>
                      {cell.allocated_prb} / {cell.max_prb}
                    </div>
                    <div>
                      Load
                    </div>
                    <div className="stats">
                      <div className="stat">
                      <div className="stat-value">
                      {(cell.current_load * 100).toFixed(1)} %
                      </div>
                      </div>
                    </div>
                    <div>Cell Radius</div>
                    <div>{cell.cell_radius * 10} m</div>
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

  return (
    <div>
      <div className="canvas-container relative my-5 w-[1000px] h-[800px]">
        <canvas
          ref={backgroudCanvasRef}
          width={1000}
          height={800}
          id="background_canvas"
          style={{ position: "absolute", top: 0, left: 0 }}
        />
        <canvas
          ref={bsCanvasRef}
          width={1000}
          height={800}
          id="bs_canvas"
          style={{ position: "absolute", top: 0, left: 0 }}
        />
        <canvas
          ref={ueCanvasRef}
          width={1000}
          height={800}
          id="ue_canvas"
          style={{ position: "absolute", top: 0, left: 0 }}
        />
      </div>
      {statsRendered}
    </div>
  );
}
