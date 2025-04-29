import { useEffect, useRef } from "react";



export default function SimulationRenderer({ simulationState }) {
    const backgroudCanvasRef = useRef(null);
    const ruCanvasRef = useRef(null);
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
    }

    const renderRUs = () => {
        if (!simulationState) {
            return;
        }
        if (!simulationState.base_station) {
            return;
        }
        if (!simulationState.base_station.RU_list) {
            return;
        }

        const canvas = ruCanvasRef.current;
        const ctx = canvas.getContext("2d");

        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (const ruData of simulationState.base_station.RU_list) {

            // Draw the RU
            ctx.beginPath();
            ctx.arc(ruData.position_x, ruData.position_y, ruData.radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = 'rgba(255, 192, 203, 0.5)'; // Transparent pink fill
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = 'pink'; // Solid pink outline
            ctx.stroke();

            // Draw the center of the RU as an outline circle with solid pink outline and no fill
            ctx.beginPath();
            ctx.arc(ruData.position_x, ruData.position_y, 5, 0, 2 * Math.PI, false);
            ctx.lineWidth = 2;
            ctx.strokeStyle = 'pink'; // Solid pink outline
            ctx.stroke();
        }
    }

    const renderUEs = () => {
        if (!simulationState) {
            return;
        }
        if (!simulationState.UE_list) {
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

            // Draw dotted blue lines to the connected RUs
            if (ueData.connected && ueData.connected_RU_list) {
                ctx.strokeStyle = 'rgba(70, 65, 230, 0.7)';
                ctx.setLineDash([5, 5]); // Dotted line
                ctx.lineWidth = 1;

                for (const ruId of ueData.connected_RU_list) {
                    const connectedRU = simulationState.base_station.RU_list.find(ru => ru.ru_id === ruId);
                    if (connectedRU) {
                        ctx.beginPath();
                        ctx.moveTo(ueData.position_x, ueData.position_y);
                        ctx.lineTo(connectedRU.position_x, connectedRU.position_y);
                        ctx.stroke();
                    }
                }

                ctx.setLineDash([]); // Reset line dash
            }

            // Draw solid orange line to the RU that's serving the UE
            if (ueData.served_by_RU) {
                const servingRU = simulationState.base_station.RU_list.find(ru => ru.ru_id === ueData.served_by_RU);
                if (servingRU) {
                    ctx.strokeStyle = 'orange';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(ueData.position_x, ueData.position_y);
                    ctx.lineTo(servingRU.position_x, servingRU.position_y);
                    ctx.stroke();
                }
            }
        }
    }

    useEffect(() => {
        renderBackground();
    }, []);

    useEffect(() => {
        console.log("simulation state changed.");
        console.log(simulationState);
        renderRUs();
        renderUEs();
    }, [simulationState]);

    let statsRendered = <div>Simulation Status Not Available Yet.</div>;
    if (simulationState !== null && simulationState.base_station !== null && simulationState.UE_list !== null) {
        statsRendered = <div className="gap-1 max-h-[90vh] overflow-auto flex-grow">

            <div className="divider">General</div>
            <div className="flex flex-row gap-2 items-center">
                <div className="stat">
                    <div className="stat-title">Served / Conn. / Total UEs</div>
                    <div className="stat-value">{simulationState.UE_list.filter(ue => ue.served_by_RU !== null).length} /
                        {simulationState.UE_list.filter(ue => ue.connected).length}
                        / {simulationState.UE_list.length}</div>
                </div>

                <div className="stat">
                    <div className="stat-title">RUs</div>
                    <div className="stat-value">{simulationState.base_station.RU_list.length}</div>
                </div>
            </div>

            {simulationState.base_station.RU_list.map(ru => (
                <div key={ru.ru_id + "_stats"}>
                    <div key={ru.ru_id + "_divider"} className="divider">{ru.ru_id}</div>
                    <div className="flex flex-row gap-2 items-center">
                        <div key={ru.ru_id + "_connected_ue"} className="stat">
                            <div className="stat-title">Served / Con. UEs</div>
                            <div className="stat-value">{ru.served_UE_list.length} / {ru.connected_UE_list.length}</div>
                        </div>
                        <div key={ru.ru_id + "_allowcated_prb"} className="stat">
                            <div className="stat-title">RPB (demanded / allocated / allocable / total)</div>
                            <div className="stat-value"><span className={ru.demanded_prb <= ru.allocated_prb ? "text-green-500" : "text-red-500"}>{ru.demanded_prb}</span> / {ru.allocated_prb} / {ru.allocable_prb} / {ru.max_prb}</div>
                        </div>
                        <div key={ru.ru_id + "_current_load"} className="stat">
                            <div className="stat-title">Current Load</div>
                            <div className="stat-value">{Math.round(ru.current_load * 100)} %</div>
                        </div>
                    </div>
                </div>
            ))}

            <div className="divider">Logs</div>
            <div className="log-container">
                {simulationState.logs.map((log, index) => (
                    <div key={"log_" + index} className="log">{log}</div>
                ))}
            </div>
        </div>;
    }

    return (
        <div className="flex flex-row gap-1 items-start justify-between">
            {statsRendered}
            <div className="canvas-container relative my-5 w-[1000px] h-[800px]">
                <canvas ref={backgroudCanvasRef} width={1000} height={800} id="background_canvas" style={{ position: 'absolute', top: 0, left: 0 }} />
                <canvas ref={ruCanvasRef} width={1000} height={800} id="ru_canvas" style={{ position: 'absolute', top: 0, left: 0 }} />
                <canvas ref={ueCanvasRef} width={1000} height={800} id="ue_canvas" style={{ position: 'absolute', top: 0, left: 0 }} />
            </div>
        </div>
    );
}