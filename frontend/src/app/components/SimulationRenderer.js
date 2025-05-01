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
            //     "max_prbs": 106,
            //     "cell_radius": 300,
            //     "position_x": 200,
            //     "position_y": 200,
            //     "cell_radius": 150,
            // }
            const { position_x, position_y, cell_radius, carrier_frequency } = cellData;
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
                position_x, position_y, 0, // Inner circle (center, radius 0)
                position_x, position_y, cell_radius // Outer circle (center, radius)
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
        })

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

      // Draw dotted blue lines to the connected BSs
      if (ueData.connected && ueData.connected_BS_list) {
        ctx.strokeStyle = "rgba(70, 65, 230, 0.7)";
        ctx.setLineDash([5, 5]); // Dotted line
        ctx.lineWidth = 1;

        for (const bsId of ueData.connected_BS_list) {
          const connectedBS = simulationState.base_stations.find(
            (bs) => bs.bs_id === bsId
          );
          if (connectedBS) {
            ctx.beginPath();
            ctx.moveTo(ueData.position_x, ueData.position_y);
            ctx.lineTo(connectedBS.position_x, connectedBS.position_y);
            ctx.stroke();
          }
        }

        ctx.setLineDash([]); // Reset line dash
      }

      // Draw solid orange line to the BS that's serving the UE
      if (ueData.served_by_BS) {
        const servingBS = simulationState.base_stations.find(
          (bs) => bs.bs_id === ueData.served_by_BS
        );
        if (servingBS) {
          ctx.strokeStyle = "orange";
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(ueData.position_x, ueData.position_y);
          ctx.lineTo(servingBS.position_x, servingBS.position_y);
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
      <div className="gap-1 max-h-[90vh] overflow-auto flex-grow">
        <div className="divider">Network Dashboard</div>
        <div className="flex flex-row gap-2 items-center">
          <div className="stat">
            <div className="stat-title">Connected / Total UEs</div>
            <div className="stat-value">
              {simulationState.UE_list.filter((ue) => ue.connected).length}{" / "}
              {simulationState.UE_list.length}
            </div>
          </div>

          <div className="stat">
            <div className="stat-title">BSs</div>
            <div className="stat-value">
              {simulationState.base_stations.length}
            </div>
          </div>
        </div>

        {simulationState.base_stations.map((bs) => (
          <div key={bs.bs_id + "_stats"}>
            <div className="flex flex-row gap-2 items-center">
              <div key={bs.bs_id + "_id"} className="stat">
                <div className="stat-title">Base Station ID</div>
                <div className="stat-value">{bs.bs_id}</div>
              </div>
              <div key={bs.bs_id + "_connected_ue"} className="stat">
                <div className="stat-title">Served UEs</div>
                <div className="stat-value">{bs.ue_registry.length}</div>
              </div>
              <div key={bs.bs_id + "_allowcated_prb"} className="stat">
                <div className="stat-title">RPB (allocated / total)</div>
                <div className="stat-value">
                  <span
                    className={
                      bs.allocated_prb <= bs.max_prb * 0.8
                        ? "text-green-500"
                        : "text-red-500"
                    }>
                  {bs.allocated_prb} / {bs.max_prb}
                  </span>
                </div>
              </div>
              <div key={bs.bs_id + "_current_load"} className="stat">
                <div className="stat-title">Current Load</div>
                <div className="stat-value">
                  {Math.round(bs.current_load * 100)} %
                </div>
              </div>
            </div>
          </div>
        ))}

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
