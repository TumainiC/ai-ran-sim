import { use, useEffect, useRef, useState } from "react";
import renderMessage from "./MessageRenderer";
import handleChatEvent from "../ChatEventHandler";
import handleUserActionResponse from "./ActionResponseHandler";
import dayjs from "dayjs";

const STEP_SERVICE_NEED_PROFILING = "step_service_need_profiling";
const STEP_SERVICE_DEPLOYMENT = "step_service_deployment";
const STEP_NETWORK_ADAPTATION = "step_network_adaptation";
const STEP_SERVICE_MONITORING = "step_service_monitoring";

export default function UserMenuAIServiceRequest({
  registerMessageHandler,
  deregisterMessageHandler,
  sendMessage,
  setMessages,
  setCurrentMenu,
}) {
  const [optionButtonList, setOptionButtonList] = useState([]);
  const [chatDisabled, setChatDisabled] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);
  const [input, setInput] = useState("");
  const messageSent = useRef(false);

  // this is to handle the strict mode of React double rendering.
  const initialMessageAdded = useRef(false);

  const initMenu = () => {
    console.log("Initializing AI Service Request Menu.");
    if (!initialMessageAdded.current) {
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
      initialMessageAdded.current = true;
    }
    setOptionButtonList([
      {
        label: "RESET",
        onClick: () => setCurrentMenu("main_menu"),
      },
    ]);
    setCurrentStep(STEP_SERVICE_NEED_PROFILING);
  };

  const onSelectAIService = (aiServiceName) => {
    console.log(`Selected AI Service: ${aiServiceName}`);
    setCurrentStep(STEP_SERVICE_DEPLOYMENT);
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        role: "user",
        content: `I would like to deploy the AI service: ${aiServiceName}.`,
        time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
      },
    ]);
    sendMessage("intelligence_layer", "ai_service_pipeline", {
      current_step: STEP_SERVICE_DEPLOYMENT,
      ai_service_name: aiServiceName,
    });
  };

  const onRequestOtherServices = () => {
    setCurrentStep(STEP_SERVICE_NEED_PROFILING);
    messageSent.current = false; // Reset message sent flag
    setMessages((prevMessages) => {
      const newMessages = [
        ...prevMessages,
        {
          role: "user",
          content: "Show me other AI service candidates please.",
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ];
      // the setMessage callback is called twice in React strict mode
      if (!messageSent.current) {
        sendMessage("intelligence_layer", "ai_service_pipeline", {
          current_step: STEP_SERVICE_NEED_PROFILING,
          messages: [
            {
              role: "user",
              content: "Show me other AI service candidates please.",
            },
          ],
        });
        messageSent.current = true; // Set flag to true after sending the message
      }
      return newMessages;
    });
  };

  const streamedChatEventHandler = (streamedChatEvent) => {
    if (!streamedChatEvent) return;
    const eventType = streamedChatEvent.event_type;

    if (eventType === "ai_services_recommendation") {
      const ai_service_names = streamedChatEvent.ai_service_names;
      const ai_service_descriptions = streamedChatEvent.ai_service_descriptions;

      if (!ai_service_names || !ai_service_descriptions) {
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            role: "assistant",
            content: "No AI services available at the moment.",
            time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
          },
        ]);
        return;
      }

      setOptionButtonList([
        {
          label: "RESET",
          onClick: () => setCurrentMenu("main_menu"),
        },
        ...ai_service_names.map((name, index) => ({
          label: `Select: ${name}`,
          onClick: () => onSelectAIService(name),
        })),
        {
          label: "Show me other AI service candidates please.",
          onClick: onRequestOtherServices,
        },
      ]);

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: `Recommended AI Services: 

${ai_service_descriptions.join("\n\n")}

Please select one of the above AI serivces that you would like to deploy.`,
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ]);

      return;
    }

    handleChatEvent(streamedChatEvent, setMessages);
  };

  const UserActionResponseHandler = (userActionResponse) => {
    handleUserActionResponse(userActionResponse, setMessages);
  };

  useEffect(() => {
    if (registerMessageHandler) {
      registerMessageHandler(
        "intelligence_layer",
        "ai_service_pipeline_response",
        streamedChatEventHandler
      );

      registerMessageHandler(
        "intelligence_layer",
        "network_user_action_response",
        UserActionResponseHandler
      );
    }

    initMenu();

    return () => {
      if (deregisterMessageHandler) {
        deregisterMessageHandler(
          "intelligence_layer",
          "ai_service_pipeline_response"
        );
        deregisterMessageHandler(
          "intelligence_layer",
          "network_user_action_response"
        );
      }
      console.log("UserMenuAIServiceRequest cleanup done.");
    };
  }, []);

  useEffect(() => {
    if (!currentStep) return;
    setChatDisabled(true);

    if (currentStep === STEP_SERVICE_NEED_PROFILING) {
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

  const handleSend = () => {
    setMessages((prevMessages) => {
      const updatedMessages = [
        ...prevMessages,
        {
          role: "user",
          content: input,
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ];
      if (!messageSent.current) {
        sendMessage("intelligence_layer", "ai_service_pipeline", {
          current_step: currentStep,
          messages: updatedMessages.map((msg) => {
            if (msg.role !== "monotone") {
              return {
                role: msg.role,
                content: msg.content,
              };
            } else {
              return {
                role: "assistant", // Convert monotone messages to assistant role
                content: msg.content,
              };
            }
          }),
        });
        messageSent.current = true; // Set flag to true after sending the message
      }

      return updatedMessages;
    });

    setInput("");
    setChatDisabled(true);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() === "") return;
      handleSend();
      return;
    }
    if (e.key === "Escape") {
      setInput("");
    }
  };

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
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          className="textarea textarea-bordered flex-1 resize-none"
          rows={1}
          disabled={chatDisabled}
        />
        <button
          onClick={handleSend}
          className="btn btn-primary h-full w-20 "
          disabled={chatDisabled}
        >
          <span className="text-xl">SEND</span>
        </button>
      </div>
    </>
  );
}
