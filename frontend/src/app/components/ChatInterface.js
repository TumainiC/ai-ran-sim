import React, { useState, useEffect, useRef } from "react";

export default function ChatInterface({ sendMessage, chatResponse }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  // const chatEndRef = useRef(null);
  const messageContainerRef = useRef(null);

  useEffect(() => {
    if (chatResponse) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: chatResponse.role, content: chatResponse.content },
      ]);
    }
  }, [chatResponse]);

  useEffect(() => {
    const container = messageContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    sendMessage("intelligence_layer", "chat", userMessage);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full flex-1">
      {/* Chat Messages */}
      <div
        className="overflow-y-auto p-4 space-y-4 flex-1"
        ref={messageContainerRef}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat ${
              msg.role === "user" ? "chat-end" : "chat-start"
            }`}
          >
            <div
              className={`chat-bubble ${
                msg.role === "user"
                  ? "bg-primary text-white"
                  : "bg-base-200 text-base-content"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {/* <div ref={chatEndRef} /> */}
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
        />
        <button onClick={handleSend} className="btn btn-primary">
          Send
        </button>
      </div>
    </div>
  );
}
