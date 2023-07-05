import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { useCookies } from "react-cookie";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { userActions } from "../../store/user-store";
import { useHttp, Modal, Button } from "../index";

export default function Landing() {
  const user = useSelector((state) => state.user);
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

  return (
    <div>
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
      <h1 className="text-lg text-center text-gray-600">YT watchman</h1>
      {user.isLoggedIn ? (
        <div>
          <Button onClick={() => navigate("/user/dashboard")}>
            Go to Dashboard
          </Button>
        </div>
      ) : (
        <div>
          <h1>login please</h1>
          <GoogleLogin onSuccess={successHandler} onError={handleFailure} />
        </div>
      )}
    </div>
  );
}
