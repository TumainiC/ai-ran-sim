import dayjs from "dayjs";

export default function handleUserActionResponse(
  userActionResponse,
  setMessages
) {
  if (!userActionResponse) return;

  const actionType = userActionResponse.action_type;

  if ("error" in userActionResponse) {
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        role: "assistant",
        content: `Error: ${userActionResponse.error}`,
        time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
      },
    ]);
    return;
  }

  switch (actionType) {
    case "query_knowledge": {
      const query_response = userActionResponse.query_response;
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: query_response,
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ]);
      break;
    }
    default: {
      console.error("Unknown action type:", actionType);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: `Unknown action type: ${actionType}`,
          time: dayjs().format("{YYYY} MM-DDTHH:mm:ss SSS [Z] A"),
        },
      ]);
      break;
    }
  }
}
