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
    <div className="flex-1">
      <button className="btn btn-outline mb-3" onClick={getKnowledgeRoutes}>
        Get Knowledge Routes
      </button>
      <div className="flex flex-row gap-3 items-center">
        <input
          className={"input w-[600]"}
          type="text"
          value={knowledgeQueryInput}
          onChange={(e) => setKnowledgeQueryInput(e.target.value)}
          placeholder="Enter your knowledge query key here, e.g., /net/ue/ue_1/attribute/downlink_cqi"
        />
        <button className="btn btn-outline" onClick={getKnowledgeValue}>
          Get Knowledge
        </button>
        <button className="btn btn-outline" onClick={explainKnowledgeValue}>
          Explain Knowledge
        </button>
      </div>
      <div>
        <div className="my-4">Knowledge Layer Response</div>
        <pre className="whitespace-pre-wrap">{knowledgeQueryResponse}</pre>
      </div>
    </div>
  );
}
