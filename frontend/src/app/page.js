"use client";

import { useState, useRef } from "react";
import SimulationRenderer from "./components/SimulationRenderer";
import UEDashboard from "./components/UEDashboard";
import BaseStationDashboard from "./components/BaseStationDashboard";
import LogDashboard from "./components/LogDashboard";
import KnowledgeLayerDashboard from "./components/KnowledgeLayerDashboard";
import ChatInterface from "./components/ChatInterface";

export default function Home() {
  const [websocket, setWebsocket] = useState(null);
  const [wsConnectionStatus, setWsConnectionStatus] = useState("disconnected");
  const [simulationState, setSimulationState] = useState(null);
  const [knowledgeQueryResponse, setKnowledgeQueryResponse] = useState(null);
  const [streamedChatEvent, setStreamedChatEvent] = useState(null);
  const [bottomTabListIndex, setBottomTabListIndex] = useState("ue_dashboard");
  const [rightTabListIndex, setRightTabListIndex] = useState("chat_interface");
  const memoryRef = useRef([]);

  const wsMessageHandler = (event) => {
    console.log("WebSocket message received:", event);
    if (event.data) {
      const messageData = JSON.parse(event.data);

      const { layer, command, response, error } = messageData;

      if (error) {
        console.error(`Error from ${layer}: ${error}`);
        return;
      }
      if (layer === "network_layer") {
        if (command === "simulation_state_update") {
          console.log("Simulation State Update:", response);
          setSimulationState(response);
          memoryRef.current.push(response);
          // Maintain fixed size of 1000
          if (memoryRef.current.length > 1000) {
            memoryRef.current.shift();
          }
        }
        if (command === "get_simulation_state") {
          console.log("Simulation State:", response);
        }
      } else if (layer === "knowledge_layer") {
        if (command === "get_routes") {
          console.log("Knowledge Layer Routes:", response);
        } else if (command === "get_value") {
          console.log("Knowledge Layer Value Response:", response);
          setKnowledgeQueryResponse(response);
        } else if (command === "explain_value") {
          console.log("Knowledge Layer Explain Response:", response);
          setKnowledgeQueryResponse(response);
        }
      } else if (layer === "intelligence_layer") {
        if (command === "chat_event_stream") {
          console.log("Chat Event Stream:", response);
          setStreamedChatEvent(response);
        } else {
          console.error(`Unknown command from intelligence_layer: ${command}`);
        }
      } else {
        console.error(`Unknown layer: ${layer}`);
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

  const sendMessage = (layer, command, data = {}) => {
    if (websocket && wsConnectionStatus === "connected") {
      websocket.send(
        JSON.stringify({
          layer,
          command,
          data,
        })
      );
    } else {
      console.error("WebSocket is not connected.");
    }
  };

  const onStartSimulation = () => {
    sendMessage("network_layer", "start_simulation");
  };

  const onStopSimulation = () => {
    sendMessage("network_layer", "stop_simulation");
  };

  const onGetSimulationState = () => {
    sendMessage("network_layer", "get_simulation_state");
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
          onClick={onGetSimulationState}
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

      <div className="flex flex-row gap-4">
        <SimulationRenderer simulationState={simulationState} />
        <div className="flex flex-col gap-3 h-[1000px] my-5 flex-1">
          <div role="tablist" className="tabs tabs-border">
            <a
              role="tab"
              className={
                "tab " +
                (rightTabListIndex === "chat_interface" ? "tab-active" : "")
              }
              onClick={() => setRightTabListIndex("chat_interface")}
            >
              Talk to the Network
            </a>
            <a
              role="tab"
              className={
                "tab " +
                (rightTabListIndex === "knowledge_dashboard"
                  ? "tab-active"
                  : "")
              }
              onClick={() => setRightTabListIndex("knowledge_dashboard")}
            >
              Knowledge Dashboard
            </a>
            <a
              role="tab"
              className={
                "tab " +
                (rightTabListIndex === "log_dashboard" ? "tab-active" : "")
              }
              onClick={() => setRightTabListIndex("log_dashboard")}
            >
              Log Dashboard
            </a>
          </div>
          <div
            className={
              rightTabListIndex === "chat_interface"
                ? "flex-1 flex min-h-0"
                : "hidden"
            }
          >
            <ChatInterface
              streamedChatEvent={streamedChatEvent}
              setStreamedChatEvent={setStreamedChatEvent}
              sendMessage={sendMessage}
            />
          </div>
          <div
            className={
              rightTabListIndex === "knowledge_dashboard" ? "" : "hidden"
            }
          >
            <KnowledgeLayerDashboard
              sendMessage={sendMessage}
              knowledgeQueryResponse={knowledgeQueryResponse}
            />
          </div>
          <div
            className={rightTabListIndex === "log_dashboard" ? "" : "hidden"}
          >
            <LogDashboard simulationState={simulationState} />
          </div>
        </div>
      </div>
      <div className="flex flex-col gap-3">
        <div role="tablist" className="tabs tabs-border">
          <a
            role="tab"
            className={
              "tab " +
              (bottomTabListIndex === "ue_dashboard" ? "tab-active" : "")
            }
            onClick={() => setBottomTabListIndex("ue_dashboard")}
          >
            UE Dashboard
          </a>
          <a
            role="tab"
            className={
              "tab " +
              (bottomTabListIndex === "base_station_dashboard"
                ? "tab-active"
                : "")
            }
            onClick={() => setBottomTabListIndex("base_station_dashboard")}
          >
            Base Station Dashboard
          </a>
        </div>
        <div className={bottomTabListIndex === "ue_dashboard" ? "" : "hidden"}>
          <UEDashboard simulationState={simulationState} />
        </div>
        <div
          className={
            bottomTabListIndex === "base_station_dashboard" ? "" : "hidden"
          }
        >
          <BaseStationDashboard simulationState={simulationState} />
        </div>
      </div>
    </div>
  );
}
