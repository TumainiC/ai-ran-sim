import { useState } from "react";

export default function KnowledgeLayerDashboard({
  sendMessage,
  knowledgeQueryResponse,
}) {
  const [knowledgeQueryInput, setKnowledgeQueryInput] = useState("");
  const getKnowledgeRoutes = () => {
    if (!sendMessage) {
      console.error("websocket is not connected");
      return;
    }
    sendMessage("knowledge_layer", "get_routes");
  };

  const getKnowledgeValue = () => {
    if (!sendMessage) {
      console.error("WebSocket is not connected");
      return;
    }
    if (!knowledgeQueryInput.trim()) {
      console.error("Knowledge query input is empty");
      return;
    }
    sendMessage("knowledge_layer", "get_value", knowledgeQueryInput.trim());
  };

  const explainKnowledgeValue = () => {
    if (!sendMessage) {
      console.error("WebSocket is not connected");
      return;
    }
    if (!knowledgeQueryInput.trim()) {
      console.error("Knowledge query input is empty");
      return;
    }
    sendMessage("knowledge_layer", "explain_value", knowledgeQueryInput.trim());
  };

  return (
    <div>
      <div className="flex flex-row gap-3 items-center">
        <button className="btn btn-outline" onClick={getKnowledgeRoutes}>
          Get Knowledge Routes
        </button>
        <input
          className={"input w-[600]"}
          type="text"
          value={knowledgeQueryInput}
          onChange={(e) => setKnowledgeQueryInput(e.target.value)}
          placeholder="Enter your knowledge query key here, e.g., /net/ue/ue_1/attribute/downlink_cqi"
        />
        <button className="btn btn-outline" onClick={getKnowledgeValue}>
          Get Knowledge Value
        </button>
        <button className="btn btn-outline" onClick={explainKnowledgeValue}>
          Explain Knowledge Value
        </button>
      </div>
      <div>
        <div className="my-4">Knowledge Layer Response</div>
        <pre className="whitespace-pre-wrap">{knowledgeQueryResponse}</pre>
      </div>
    </div>
  );
}
