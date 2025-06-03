"use client";

import React, { useState, useEffect } from "react";
import UserMenuMain from "./UserMenuMain";
import UserMenuAIServiceRequest from "./UserMenuAiServiceRequest";
import dayjs from "dayjs";
import renderMessage from "./MessageRenderer";

function getDefaultMessages() {
  return [
    {
      role: "monotone",
      title: "Monotone",
      content: `Thank you for choosing our network.
  
We offer a range of AI services ready-to-deploy across our base stations for your connected user equipments.
Simply describe what applications or use cases you have in mind or you're currently building,
and our AI assistant will help you deploy the services you need across our edge/cloud clusters.`,
      time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
    },
  ];
}

export default function NetworkUserChat({
  sendMessage,
  registerMessageHandler,
}) {
  const [currentMenu, setCurrentMenu] = useState("main_menu");
  const [messages, setMessageList] = useState([]);

  let renderedMenu = null;

  const setMessages = (newMessages_or_callback) => {
    console.log("setMessages called with:", newMessages_or_callback);

    if (typeof newMessages_or_callback === "function") {
      setMessageList((prevMessages) => newMessages_or_callback(prevMessages));
    } else {
      setMessageList(newMessages_or_callback);
    }
  };

  switch (currentMenu) {
    case "main_menu":
      renderedMenu = (
        <UserMenuMain
          registerMessageHandler={registerMessageHandler}
          getDefaultMessages={getDefaultMessages}
          sendMessage={sendMessage}
          setMessages={setMessages}
          setCurrentMenu={setCurrentMenu}
        />
      );
      break;
    case "request_ai_service_menu":
      renderedMenu = (
        <UserMenuAIServiceRequest
          registerMessageHandler={registerMessageHandler}
          sendMessage={sendMessage}
          setMessages={setMessages}
          setCurrentMenu={setCurrentMenu}
        />
      );
      break;
    default:
      renderedMenu = (
        <UserMenuMain
          registerMessageHandler={registerMessageHandler}
          getDefaultMessages={getDefaultMessages}
          sendMessage={sendMessage}
          setMessages={setMessages}
          setCurrentMenu={setCurrentMenu}
        />
      );
      break;
  }

  console.log("Current Menu:", currentMenu);

  useEffect(() => {
    console.log("Messages updated:", messages);
  }, [messages]);

  return (
    <div className="flex flex-col h-full flex-1">
      {/* Messages */}
      <div className="overflow-y-auto p-4 space-y-4 flex-1">
        {messages.map((msg, index) => renderMessage(index, msg))}
      </div>
      {renderedMenu}
    </div>
  );
}
