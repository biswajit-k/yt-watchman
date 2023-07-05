import React, { useState } from "react";


// custom hook to make http requests
export default function useHttp() {
  const [isError, setIsError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const requester = async (reqConfig, applyData) => {
    try {
      setIsError(false);
      setIsLoading(true);

      const response = await fetch(reqConfig.url, reqConfig.body);

      if (!response.ok) {
        throw new Error(response.message || "Something went wrong!");
      }

      const data = await response.json();
      applyData(data);
    } catch (e) {
      setIsError(e.message);
    }

    setIsLoading(false);
  }

  return { isError, isLoading, requester, setIsError };
}
