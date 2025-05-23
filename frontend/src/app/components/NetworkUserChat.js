import React, { useState, useEffect, useRef } from "react";
import dayjs from "dayjs";
import Image from "next/image";
import agent_icon from "../../assets/agent_icon.png";
import tool_icon from "../../assets/tool_icon.png";

// Simple SVG icons for repo link and bulb
const RepoIcon = () => (
  <svg width="16" height="16" fill="currentColor" style={{ display: "inline", verticalAlign: "middle", marginRight: 4 }}>
    <path d="M2 2v12h12V2H2zm1 1h10v10H3V3zm2 2v2h2V5H5zm0 3v2h2V8H5zm3-3v2h2V5H8zm0 3v2h2V8H8z"/>
  </svg>
);
const BulbIcon = () => (
  <svg width="16" height="16" fill="gold" style={{ display: "inline", verticalAlign: "middle", marginRight: 4 }}>
    <path d="M8 1a5 5 0 0 0-3 9c.01.5.13 1.02.36 1.47.23.45.56.86.97 1.18V14a1 1 0 0 0 2 0v-1.35c.41-.32.74-.73.97-1.18.23-.45.35-.97.36-1.47A5 5 0 0 0 8 1zm0 12a3 3 0 0 1-3-3h6a3 3 0 0 1-3 3z"/>
  </svg>
);

/**
 * ThinkingMessage subcomponent: animated dots
 */
function ThinkingMessage() {
  return (
    <div className="flex items-center gap-2">
      <span className="font-semibold text-gray-400">Assistant is thinking</span>
      <span className="dot-flashing" style={{
        display: "inline-block",
        width: 24,
        height: 12,
        position: "relative"
      }}>
        <span style={{
          position: "absolute",
          left: 0,
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: "#888",
          animation: "dotFlashing 1s infinite linear alternate"
        }} />
        <span style={{
          position: "absolute",
          left: 9,
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: "#888",
          animation: "dotFlashing 1s infinite linear alternate 0.3s"
        }} />
        <span style={{
          position: "absolute",
          left: 18,
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: "#888",
          animation: "dotFlashing 1s infinite linear alternate 0.6s"
        }} />
        <style>
          {`
          @keyframes dotFlashing {
            0% { opacity: 0.2; }
            50%, 100% { opacity: 1; }
          }
          `}
        </style>
      </span>
    </div>
  );
}

// CuratedConfigMessage subcomponent
function CuratedConfigMessage({ content, onDeploy, chatDisabled }) {
  const [networkSlice, setNetworkSlice] = useState(content.network_slice || "");
  const [deploymentLocation, setDeploymentLocation] = useState(content.deployment_location || "");
  const [selectedModel, setSelectedModel] = useState("");
  const [okClicked, setOkClicked] = useState(false);

  const networkSliceOptions = ["eMBB", "uRLLC", "mMTC"];
  const deploymentLocationOptions = ["Edge", "cloud"];
  const modelOptions = content.models?.map((m) => m.model_name) || [];

  const canSubmit = networkSlice && deploymentLocation && selectedModel && !okClicked && !chatDisabled;

  const handleOk = () => {
    setOkClicked(true);
    // Find the selected model object
    const selectedModelObj = (content.models || []).find(
      (m) => m.model_name === selectedModel
    );
    const logPayload = {
      network_slice: networkSlice,
      deployment_location: deploymentLocation,
      model: selectedModel,
      model_id: selectedModelObj ? selectedModelObj.id : undefined,
    };
    // Placeholder API call
    console.log("Deploying selection:", logPayload);
    if (onDeploy) {
      onDeploy(logPayload);
    }
  };

  return (
    <div className="space-y-4">
      <div className="font-semibold">Here is the curated config for your requirement</div>
      <div className="flex flex-col gap-2">
        <label>
          Network Slice:
          <select
            className="select select-bordered ml-2"
            style={{ color: "#fff", backgroundColor: "#222" }}
            value={networkSlice}
            onChange={(e) => setNetworkSlice(e.target.value)}
            disabled={okClicked || chatDisabled}
          >
            {networkSliceOptions.map((opt, idx) => (
              <option
                key={opt}
                value={opt}
                style={{ color: "#fff", backgroundColor: "#222" }}
              >
                {`${idx + 1}. ${opt}`}
              </option>
            ))}
          </select>
        </label>
        <label>
          Deployment Location:
          <select
            className="select select-bordered ml-2"
            style={{ color: "#fff", backgroundColor: "#222" }}
            value={deploymentLocation}
            onChange={(e) => setDeploymentLocation(e.target.value)}
            disabled={okClicked || chatDisabled}
          >
            {deploymentLocationOptions.map((opt, idx) => (
              <option
                key={opt}
                value={opt}
                style={{ color: "#fff", backgroundColor: "#222" }}
              >
                {`${idx + 1}. ${opt}`}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="font-semibold mt-2">Here are the models selected for you</div>
      <select
        className="select select-bordered w-full"
        style={{ color: "#fff", backgroundColor: "#222" }}
        value={selectedModel}
        onChange={(e) => setSelectedModel(e.target.value)}
        disabled={okClicked || chatDisabled}
      >
        <option value="" disabled style={{ color: "#bbb", backgroundColor: "#222" }}>
          Select a model
        </option>
        {modelOptions.map((model, idx) => (
          <option
            key={model}
            value={model}
            style={{ color: "#fff", backgroundColor: "#222" }}
          >
            {`${idx + 1}. ${model}`}
          </option>
        ))}
      </select>
      <button
        className="btn btn-primary mt-2"
        onClick={handleOk}
        disabled={!canSubmit}
      >
        OK
      </button>
      <div className="mt-4">
        {content.models?.map((model, idx) => (
          <div key={model.id || idx} className="border rounded p-2 mb-2 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="font-semibold">{`${idx + 1}. ${model.model_name}`}</span>
              <a
                href={
                  model.repository_url.startsWith("http://") ||
                  model.repository_url.startsWith("https://")
                    ? model.repository_url
                    : `https://${model.repository_url.replace(/^\/+/, "")}`
                }
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-600 hover:underline flex items-center"
                title="Repository URL"
              >
                <RepoIcon />
                Repo
              </a>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <BulbIcon />
              <span>
                {`${idx + 1}. ${model.model_name} -> ${model.rationale}`}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// UserChat is a chat interface similar to NetworkEngineerChat, but with its own user history context.
// The sendMessage function should use a different identifier to keep histories separate.

export default function UserChat({ sendMessage, streamedChatEvent }) {
  const [messages, setMessages] = useState([]);
  const [chatDisabled, setChatDisabled] = useState(false);
  const [input, setInput] = useState("");
  const messageContainerRef = useRef(null);

  function checkAndHandleMessages(message_output, prevMessages) {
    // Detect curated config structure: has models, network_slice, deployment_location
    if (
      message_output &&
      Array.isArray(message_output.models) &&
      message_output.network_slice &&
      message_output.deployment_location
    ) {
      return [
        ...prevMessages,
        {
          role: "curated_config",
          content: message_output,
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ];
    }
    let output =
      typeof message_output == "string"
        ? message_output
        : message_output.questions
        ? message_output.questions
        : message_output.message;
    if (output) {
      return [
        ...prevMessages,
        {
          role: "assistant",
          content: output,
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ];
    } else {
      // fallback: log unexpected structure
      console.log("received some other response ", message_output);
    }
  }

  useEffect(() => {
    if (!streamedChatEvent) return;

    // Use streamedChatEvent directly as the event object
    const event = streamedChatEvent;

    const eventType = event.event_type;

    if (eventType === "response_text_delta_event") {
      const response_text_delta = event.response_text_delta;
      setMessages((prevMessages) => {
        const lastMessage = prevMessages[prevMessages.length - 1];
        if (lastMessage && lastMessage.role === "assistant") {
          return [
            ...prevMessages.slice(0, -1),
            {
              ...lastMessage,
              content: lastMessage.content + response_text_delta,
              time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
            },
          ];
        }
        return [
          ...prevMessages,
          {
            role: "assistant",
            content: response_text_delta,
            time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
          },
        ];
      });
    } else if (eventType === "agent_updated_stream_event") {
      const agent_name = event.agent_name;
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "monotone",
          content: agent_name,
          title: "Agent Activated:",
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ]);
    } else if (eventType === "tool_call_item") {
      const tool_name = event.tool_name;
      const tool_call_item = event.tool_args;
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "monotone",
          content: `${tool_name}(${tool_call_item})`,
          title: "Tool Call",
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ]);
    } else if (eventType === "tool_call_output_item") {
      const tool_output = event.tool_output;
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "monotone",
          content: tool_output,
          title: "Tool Output",
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ]);
    } else if (eventType === "message_output_item") {
      const message_output = event.message_output;
      setMessages((prevMessages) => {
        // Remove any "thinking" message before adding the new one
        const filtered = prevMessages.filter((msg) => msg.role !== "thinking");
        const lastMessage = filtered[filtered.length - 1];
        // If it's a curated config, always add a new message
        if (
          message_output &&
          Array.isArray(message_output.models) &&
          message_output.network_slice &&
          message_output.deployment_location
        ) {
          return checkAndHandleMessages(message_output, filtered);
        }
        if (!lastMessage || lastMessage.role !== "assistant") {
          return checkAndHandleMessages(message_output, filtered);
        } else if (lastMessage.content !== message_output) {
          // replace the last message with the new one
          const updatedMessages = [...filtered];
          updatedMessages[updatedMessages.length - 1] = {
            ...lastMessage,
            content: message_output,
            time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
          };
          return updatedMessages;
        }
        return filtered;
      });
      setChatDisabled(false);
    } else {
      console.log("Unknown event type:", eventType);
    }
  }, [streamedChatEvent]);

  useEffect(() => {
    const container = messageContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const chatHistory = [];
    for (let i = 0; i < messages.length; i++) {
      const message = messages[i];
      if (message.role === "user" || message.role === "assistant") {
        chatHistory.push({
          role: message.role,
          content: message.content,
        });
      } else if (message.role === "monotone") {
        chatHistory.push({
          role: "assistant",
          content: `${message.title} ${message.content}`,
        });
      }
    }
    chatHistory.push({
      role: "user",
      content: input,
    });
    // Use a different identifier for user chat history
    // Send the message using the correct signature for the backend API
    sendMessage(
      "intelligence_layer",
      "network_user_chat",
      chatHistory.map(({ role, content }) => ({ role, content }))
    );
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: input,
        time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
      },
    ]);
    setInput("");
    setChatDisabled(true);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderChatMessage = (msg, index) => {
    const isUser = msg.role === "user";
    const isAssistant = msg.role === "assistant";
    const isMonotone = msg.role === "monotone";
    const isCuratedConfig = msg.role === "curated_config";
    const time = msg.time;

    if (isCuratedConfig) {
      return (
        <div key={index} className="chat chat-start">
          <div className="chat-image avatar">
            <Image
              alt="Agent Icon"
              src={agent_icon}
              className="w-10 h-10 object-cover"
              width={40}
              height={40}
            />
          </div>
          <div className="chat-header">
            Assistant
            <time className="text-xs opacity-50">{time}</time>
          </div>
          <div
            className="chat-bubble chat-bubble-success whitespace-pre-wrap"
            style={{ minWidth: 320, maxWidth: 600 }}
          >
            <CuratedConfigMessage
              content={msg.content}
              chatDisabled={chatDisabled}
              onDeploy={({ network_slice, deployment_location, model, model_id }) => {
                // Add deployment message and disable chat, then add thinking animation
                setMessages((prev) => [
                  ...prev,
                  {
                    role: "assistant",
                    content: "Your selection will be deployed in some time",
                    time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
                  },
                  {
                    role: "thinking",
                    content: "",
                    time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
                    id: "__thinking__"
                  }
                ]);
                setChatDisabled(true);
              }}
            />
          </div>
        </div>
      );
    }

    if (msg.role === "thinking") {
      return (
        <div key={index} className="chat chat-start">
          <div className="chat-image avatar">
            <Image
              alt="Agent Icon"
              src={agent_icon}
              className="w-10 h-10 object-cover"
              width={40}
              height={40}
            />
          </div>
          <div className="chat-header">
            Assistant
            <time className="text-xs opacity-50">{time}</time>
          </div>
          <div className="chat-bubble chat-bubble-success whitespace-pre-wrap" style={{ minWidth: 200, maxWidth: 400 }}>
            <ThinkingMessage />
          </div>
        </div>
      );
    }

    return (
      <div key={index} className={`chat ${isUser ? "chat-end" : "chat-start"}`}>
        {(isAssistant ||
          (isMonotone && msg.title && msg.title === "Agent Activated:")) && (
          <div className="chat-image avatar">
            <Image
              alt="Agent Icon"
              src={agent_icon}
              className="w-10 h-10 object-cover"
              width={40}
              height={40}
            />
          </div>
        )}
        {isMonotone && msg.title && msg.title.includes("Tool") && (
          <div className="chat-image avatar">
            <Image
              alt="Tool Icon"
              src={tool_icon}
              className="w-10 h-10 object-cover"
              width={40}
              height={40}
            />
          </div>
        )}
        <div className="chat-header">
          {isUser ? "User" : isAssistant ? "Assistant" : msg.title}
          <time className="text-xs opacity-50">{time}</time>
        </div>
        <pre
          className={`chat-bubble whitespace-pre-wrap ${
            isUser
              ? "chat-bubble-info"
              : isAssistant
              ? "chat-bubble-success"
              : "bg-base-200 text-base-content"
          }`}
        >
          {msg.content}
        </pre>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full flex-1">
      {/* Chat Messages */}
      <div
        className="overflow-y-auto p-4 space-y-4 flex-1"
        ref={messageContainerRef}
      >
        {messages.map(renderChatMessage)}
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-base-300 bg-base-100 flex items-center gap-2">
        <button
          onClick={() => {
            setMessages([]);
            setChatDisabled(false);
          }}
          className="btn btn-success h-full w-20"
          type="button"
        >
          <span className="text-xl">NEW</span>
        </button>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          className="textarea textarea-bordered flex-1 resize-none"
          rows={1}
        />
        <button
          onClick={handleSend}
          className="btn btn-primary h-full w-20 "
          disabled={chatDisabled}
        >
          <span className="text-xl">SEND</span>
        </button>
      </div>
    </div>
  );
}