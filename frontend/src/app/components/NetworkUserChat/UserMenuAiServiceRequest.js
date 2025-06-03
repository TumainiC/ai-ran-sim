import { use, useEffect, useState } from "react";
import renderMessage from "./MessageRenderer";
import handleChatEvent from "../ChatEventHandler";
import handleUserActionResponse from "./ActionResponseHandler";
import dayjs from "dayjs";

const STEP_INTENT_PROFILING = "step_intent_profiling";
const STEP_SERVICE_SELECTION = "step_service_selection";
const STEP_SERVICE_DEPLOYMENT = "step_service_deployment";
const STEP_NETWORK_ADAPTATION = "step_network_adaptation";
const STEP_SERVICE_MONITORING = "step_service_monitoring";

export default function UserMenuAIServiceRequest({
  registerMessageHandler,
  sendMessage,
  setMessages,
  setCurrentMenu,
}) {
  const [optionButtonList, setOptionButtonList] = useState([]);
  const [chatDisabled, setChatDisabled] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);

  const hasInitialized = useState(false);

  console.log("rendering UserMenuAIServiceRequest");

  const initMenu = () => {
    console.log("Initializing AI Service Request Menu.");
    setMessages((prevMessages) => {
      console.log("set messages called: ");
      console.log(prevMessages);
      return [
        ...prevMessages,
        {
          role: "user",
          content: "I wish to request an AI service for my use case.",
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ];
    });
    setOptionButtonList([
      {
        label: "RESET",
        onClick: () => setCurrentMenu("main_menu"),
      },
    ]);
    setCurrentStep(STEP_INTENT_PROFILING);
  };

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    if (registerMessageHandler) {
      registerMessageHandler(
        "intelligence_layer",
        "network_user_chat_response",
        (streamedChatEvent) => {
          handleChatEvent(streamedChatEvent, setMessages);
        }
      );

      registerMessageHandler(
        "intelligence_layer",
        "network_user_action_response",
        (userActionResponse) => {
          handleUserActionResponse(userActionResponse, setMessages);
        }
      );
    }

    initMenu();
  }, []);

  useEffect(() => {
    if (!currentStep) return;
    setChatDisabled(true);

    if (currentStep === STEP_INTENT_PROFILING) {
      setMessages((prevMessages) => {
        console.log("set messages called: ");
        console.log(prevMessages);
        return [
          ...prevMessages,
          {
            role: "monotone",
            title: "Monotone",
            content: `Please describe the AI service you need or the use case you are working on.`,
            time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
          },
        ];
      });
      setChatDisabled(false);
    }
  }, [currentStep]);

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

      {/* Input Box */}
      <div className="p-4 border-t border-base-300 bg-base-100 flex items-center gap-2">
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
    </>
  );
}
