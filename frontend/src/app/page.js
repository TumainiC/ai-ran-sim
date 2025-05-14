"use client";

import { useState, useRef } from "react";
import SimulationRenderer from "./components/SimulationRenderer";
import UEDashboard from "./components/UEDashboard";
import BaseStationDashboard from "./components/BaseStationDashboard";
import LogDashboard from "./components/LogDashboard";
import KnowledgeLayerDashboard from "./components/KnowledgeLayerDashboard";

export default function Home() {
  const [websocket, setWebsocket] = useState(null);
  const [wsConnectionStatus, setWsConnectionStatus] = useState("disconnected");
  const [simulationState, setSimulationState] = useState(null);
  const [knowledgeQueryResponse, setKnowledgeQueryResponse] = useState(null);
  const memoryRef = useRef([]);

  const wsMessageHandler = (event) => {
    console.log("WebSocket message received:", event);
    if (event.data) {
      const messageData = JSON.parse(event.data);
      if (messageData.type === "simulation_state") {
        console.log("Received simulation state:", messageData.data);
        setSimulationState(messageData.data);
        // Save the message to memory
        memoryRef.current.push(messageData.data);
        if (memoryRef.current.length > 1000) {
          memoryRef.current.shift(); // Maintain fixed size of 1000
        }
      } else if (messageData.type === "knowledge_layer/routes") {
        console.log(messageData.data);
      } else if (messageData.type === "knowledge_layer/value_response") {
        console.log("Knowledge Layer Value Response:", messageData.data);
        setKnowledgeQueryResponse(messageData.data);
      } else if (messageData.type === "knowledge_layer/explanation_response") {
        console.log("Knowledge Layer Explain Response:", messageData.data);
        setKnowledgeQueryResponse(messageData.data);
      }
    }
  };

  const connectWebSocket = () => {
    const ws = new WebSocket("ws://localhost:8765");
    setWebsocket(ws);

    ws.onopen = () => {
      setWsConnectionStatus("connected");
    };

    ws.onclose = () => {
      setWsConnectionStatus("disconnected");
    };

    ws.onerror = () => {
      setWsConnectionStatus("error");
    };

    ws.onmessage = wsMessageHandler;
  };

  const onStartSimulation = () => {
    websocket.send("start_simulation");
  };

  const onStopSimulation = () => {
    websocket.send("stop_simulation");
  };

  const saveMemoryToFile = () => {
    const dataStr = JSON.stringify(memoryRef.current, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "simulation_memory.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-4 flex flex-col gap-2">
      <div className="flex flex-row gap-4 items-center">
        <button
          className="btn btn-outline"
          onClick={connectWebSocket}
          disabled={wsConnectionStatus === "connected"}
        >
          Connect To Simulation Server
        </button>
        <p>Status: {wsConnectionStatus}</p>

        <button
          className="btn btn-outline"
          onClick={onStartSimulation}
          disabled={wsConnectionStatus !== "connected"}
        >
          Start Simulation
        </button>

        <button
          className="btn btn-outline"
          onClick={onStopSimulation}
          disabled={wsConnectionStatus !== "connected"}
        >
          Stop Simulation
        </button>

        <button
          className="btn btn-outline"
          onClick={() => websocket.send("get_simulation_state")}
          disabled={wsConnectionStatus !== "connected"}
        >
          Get Simulation State
        </button>

        <button
          className="btn btn-outline"
          onClick={saveMemoryToFile}
          disabled={memoryRef.current.length === 0}
        >
          Save Memory to JSON
        </button>
      </div>

      <SimulationRenderer simulationState={simulationState} />
      <KnowledgeLayerDashboard websocket={websocket} knowledgeQueryResponse={knowledgeQueryResponse}/>
      <UEDashboard simulationState={simulationState} />
      <BaseStationDashboard simulationState={simulationState} />
      <LogDashboard simulationState={simulationState} />
    </div>
  );
}
