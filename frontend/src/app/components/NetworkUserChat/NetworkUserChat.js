"use client";

import React, { useState } from "react";
import UserMenuMain from "./UserMenuMain";

export default function NetworkUserChat({ sendMessage, streamedChatEvent, userActionResponse }) {
  const [currentMenu, setCurrentMenu] = useState("main");

  switch (currentMenu) {
    case "main":
      return (
        <UserMenuMain
          sendMessage={sendMessage}
          streamedChatEvent={streamedChatEvent}
          userActionResponse={userActionResponse}
          setCurrentMenu={setCurrentMenu}
          currentMenu={currentMenu}
        />
      );
    default:
      return (
        <UserMenuMain
          sendMessage={sendMessage}
          streamedChatEvent={streamedChatEvent}
          userActionResponse={userActionResponse}
          setCurrentMenu={setCurrentMenu}
          currentMenu={currentMenu}
        />
      );
  }
}
