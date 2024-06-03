import { useState } from "react";


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
        let errorMessage = "Something went wrong";
        const contentType = response.headers.get("content-type");

        // if response is returned by my api(i.e json) then set its message as error
        if (contentType && contentType.indexOf("application/json") !== -1) {
          const msg = await response.json();
          errorMessage = msg.error;
        }

        throw new Error(errorMessage);
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
