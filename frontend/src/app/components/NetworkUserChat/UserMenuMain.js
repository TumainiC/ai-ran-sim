import { useEffect, useState } from "react";
import renderMessage from "./MessageRenderer";
import handleChatEvent from "../ChatEventHandler";
import handleUserActionResponse from "./ActionResponseHandler";
import dayjs from "dayjs";

export default function UserMenuMain({
  currentMenu,
  setCurrentMenu,
  sendMessage,
  streamedChatEvent,
  userActionResponse,
}) {
  const [messages, setMessages] = useState([]);
  const [optionButtonList, setOptionButtonList] = useState([]);
  const [chatDisabled, setChatDisabled] = useState(false);

  const onOverviewAIService = () => {
    // append a new message first
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        role: "user",
        content: "What AI services are available?",
        time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
      },
    ]);
    sendMessage("intelligence_layer", "network_user_action", {
      action_type: "query_knowledge",
      query: "/ai_services",
    });
  };

  const resetMenu = () => {
    setChatDisabled(true);
    setMessages([
      {
        role: "assistant",
        content: `Thank you for choosing our network.

We offer a range of AI services ready-to-deploy across our base stations for your connected user equipments.
Simply describe what applications or use cases you have in mind or you're currently building,
and our AI assistant will help you deploy the services you need across our edge/cloud clusters.`,
        time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
      },
      {
        role: "monotone",
        title: "Monotone",
        content: "Select an option below to get started.",
        time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
      },
    ]);
    setOptionButtonList([
      {
        label: "What AI services are available?",
        onClick: onOverviewAIService,
      },
    ]);
  };

  useEffect(() => {
    handleChatEvent(streamedChatEvent, setMessages);
  }, [streamedChatEvent]);

  useEffect(() => {
    handleUserActionResponse(userActionResponse, setMessages);
  }, [userActionResponse]);

  useEffect(() => {
    resetMenu();
  }, []);

  return (
    <div className="flex flex-col h-full flex-1">
      {/* Messages */}
      <div className="overflow-y-auto p-4 space-y-4 flex-1">
        {messages.map((msg, index) => renderMessage(index, msg))}
      </div>

      {/* Options */}
      <div className="p-4 border-t border-base-300 bg-base-100">
        <div className="flex flex-row gap-2">
          {optionButtonList.map((option, index) => (
            <button
              key={index}
              onClick={option.onClick}
              className="btn btn-info"
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-base-300 bg-base-100 flex items-center gap-2">
        <button
          onClick={resetMenu}
          className="btn btn-success h-full w-20"
          type="button"
        >
          <span className="text-xl">NEW</span>
        </button>
        <textarea
          // value={input}
          // onChange={(e) => setInput(e.target.value)}
          // onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          className="textarea textarea-bordered flex-1 resize-none"
          rows={1}
          disabled={chatDisabled}
        />
        <button
          // onClick={handleSend}
          className="btn btn-primary h-full w-20 "
          disabled={chatDisabled}
        >
          <span className="text-xl">SEND</span>
        </button>
      </div>
    </div>
  );
}
