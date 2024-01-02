import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { GoogleLogin} from "@react-oauth/google";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { userActions } from "../../store/user-store";
import { useHttp, Modal, Button, Logo, Paragraph } from "../index";
import login from "../../data/login.svg";

export default function Login() {
  const dispatch = useDispatch();

  const { isLoading, requester } = useHttp();
  const navigate = useNavigate();

  function successHandler(googleData) {
    requester(
      {
        url: "/api/login",
        body: {
          method: "POST",
          mode: "cors",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: googleData.credential }),
          credentials: "include",
        },
      },
      (data) => {
        if (data.id) {
          dispatch(userActions.loginUser(data));
          navigate("/user/dashboard");
          return;
        }
        dispatch(userActions.logoutUser());
      }
    );
  }
  function handleFailure() {
    toast.error("Opps! Login Failed. Please try again!");
  }

  function guestLoginHandler() {
    requester(
      {
        url: "/api/login/guest",
        body: {
          mode: 'cors',
          credentials: "include",
        },
      },
      (data) => {
        if (data.id) {
          dispatch(userActions.loginUser(data));
          navigate("/user/dashboard");
          return;
        }
        dispatch(userActions.logoutUser());
      }
    );
  }

  useEffect(() => {
    if(isError) {
      toast.dismiss();
      toast.error(isError || "something went wrong");
    }
  }, [isError])
  
  return (
    <div className="flex items-center justify-center w-full px-16 py-10 overflow-y-scroll bg-gray-50">
      {isLoading && <Modal />}
      <ToastContainer
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      <div className="flex justify-between w-full h-full bg-white">
        <div className="p-6 basis-full">
          <Logo />
          <div className="flex flex-col items-center gap-5 mt-20">
            <div className="text-center">
              <h2 className="text-2xl font-medium text-slate-700">
                Great to have you!
              </h2>
              <Paragraph className="mb-8">
                Please sign in from below options to proceed
              </Paragraph>
            </div>
            <GoogleLogin onSuccess={successHandler} onError={handleFailure} />
            <div className="relative my-6 border w-[19rem] border-slate-100">
              <div className="bg-white p-2 text-slate-400 absolute left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%]">
                or
              </div>
            </div>
            <Button type="button" onClick={guestLoginHandler} primary>
              Login as guest
            </Button>
          </div>
        </div>

        <div className="flex items-center justify-center h-full bg-red-300 basis-full">
          <img src={login} className="w-80 h-80" alt="login" />
        </div>
      </div>
    </div>
  );
}
