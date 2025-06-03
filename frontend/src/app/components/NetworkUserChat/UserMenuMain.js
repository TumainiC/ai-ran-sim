import { useEffect, useState } from "react";

import handleChatEvent from "../ChatEventHandler";
import handleUserActionResponse from "./ActionResponseHandler";
import dayjs from "dayjs";

export default function UserMenuMain({
  registerMessageHandler,
  getDefaultMessages,
  setMessages,
  setCurrentMenu,
  sendMessage,
}) {
  const [optionButtonList, setOptionButtonList] = useState([]);
  const hasInitialized = useState(false);

  const onOverviewAIService = () => {
    console.log("running onOverviewAIService");
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

  const onRequestAIService = () => {
    console.log("Switching to Request AI Service Menu.");
    setCurrentMenu("request_ai_service_menu");
  };

  const initMessages = () => {
    setMessages(() => [
      ...getDefaultMessages(),
      {
        role: "monotone",
        title: "Monotone",
        content: `Choose an option below to get started.`,
      },
    ]);
  };

  const initMenu = () => {
    initMessages();
    setOptionButtonList([
      {
        label: "RESET",
        onClick: initMessages,
      },
      {
        label: "What AI services are available?",
        onClick: onOverviewAIService,
      },
      {
        label: "I wish to request an AI service for my use case.",
        onClick: onRequestAIService,
      },
    ]);
  };

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    if (registerMessageHandler) {
      registerMessageHandler(
        "intelligence_layer",
        "network_user_chat_response",
        (streamedChatEvent) => {
          console.log(
            "Calling handleChatEvent with streamedChatEvent:",
            streamedChatEvent
          );
          handleChatEvent(streamedChatEvent, setMessages);
        }
      );

      registerMessageHandler(
        "intelligence_layer",
        "network_user_action_response",
        (userActionResponse) => {
          console.log(
            "Calling handleUserActionResponse with userActionResponse:",
            userActionResponse
          );
          handleUserActionResponse(userActionResponse, setMessages);
        }
      );
    }

    initMenu();
  }, []);

  return (
    <>
      {/* Options */}
      <div className="p-4 border-t border-base-300 bg-base-100">
        <div className="flex flex-row gap-2 items-center">
          <span>OPTIONS</span>
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
    </>
  );
}
