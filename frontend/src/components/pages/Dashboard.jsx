import React, { useState, useEffect } from "react";
import { useNavigate, Link, isRouteErrorResponse } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";

import {
  MdOutlineKeyboardArrowRight,
  MdKeyboardArrowLeft,
  MdKeyboardArrowRight,
} from "react-icons/md";
import { IoAddSharp } from "react-icons/io5";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import {
  AiOutlineComment,
  AiOutlineCloudUpload,
  AiOutlineEye,
  AiOutlineMail,
} from "react-icons/ai";
import { Modal, useHttp, Button, useImage, useProfile } from "../index";

//TODO: keep toast container in global div, so that it could be accessed from any file using ref or something
// then, set toast error message within use-http requester itself instead of useeffect(isError) in every file
// also, toast for sucess messages

export default function Dashboard() {
  const navigate = useNavigate();
  const [token, setToken] = useState({});
  const [history, setHistory] = useState([]);
  const [subIdx, setSubIdx] = useState(0);
  const { isLoading, requester, isError } = useHttp();
  const [subscriptions, setSubscriptions] = useState({});
  const user = useProfile(requester, true);
  const { image } = useImage(user.id, user.isGuest);
  // youtube comment access flow by oauth
  const googleLogin = useGoogleLogin({
    onSuccess: (response) => {
      setTokenHandler(response);
    },
    scope: "https://www.googleapis.com/auth/youtube.force-ssl",
    flow: "auth-code",
  });

  useEffect(() => {
    requester(
      {
        url: "/api/token_status",
        body: {
          credentials: "include",
        },
      },
      (token) => setToken(token)
    );
    requester(
      {
        url: "/api/subscription",
        body: {
          credentials: "include",
        },
      },
      (subscriptions) =>
        setSubscriptions(subscriptions.active.concat(subscriptions.paused))
    );
  }, []);

  useEffect(() => {
    requester(
      {
        url: "/api/history",
        body: {
          credentials: "include",
        },
      },
      (data) => {
        setHistory(data.history);
      }
    )
  }, []);
  useEffect(() => setSubIdx(0), [subscriptions]);
  
  useEffect(() => {
    if(isError) {
      toast.dismiss();
      toast.error(isError || "something went wrong");
    }
  }, [isError])

  function setTokenHandler(response) {
    requester(
      {
        url: "/api/set_token",
        body: {
          method: "POST",
          mode: "cors",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(response),
          credentials: "include",
        },
      },
      () => {
        toast.dismiss();
        toast.success("Comment access granted successfully");
      }
    );
  }

  const currentSubscription =
    subscriptions.length > 0 ? (
      <>
        <img
          src={subscriptions[subIdx].imgUrl}
          referrerPolicy="no-referrer"
          alt=""
          className="block w-16 h-16 mx-auto mt-3 rounded-full"
        />
        <h3 className="mt-4 mb-1 font-semibold text-slate-700">
          {subscriptions[subIdx].title}
        </h3>
        <p className="text-xs text-slate-500">
          {subscriptions[subIdx].created_at}
        </p>
        {subscriptions[subIdx].comment && (
          <p className="px-3 my-6 italic">{subscriptions[subIdx].comment}</p>
        )}
        {!subscriptions[subIdx].comment && (
          <div className="inline-block my-6 px-2 text-[.7rem] rounded-sm tracking-wider text-yellow-600 font-semibold uppercase border border-yellow-300">
            auto-comment disabled
          </div>
        )}
      </>
    ) : (
      <>
        <div className="inline-flex items-center justify-center w-24 h-24 bg-gray-200 border-2 border-gray-400 border-dashed rounded-full">
          <div
            className="w-10 h-10 overflow-hidden rounded-full hover:cursor-pointer"
            onClick={() => navigate("/user/subscription/add")}
          >
            <IoAddSharp className="w-full h-full p-1 text-red-400 hover:bg-red-200" />
          </div>
        </div>
        <p className="px-3 my-6 text-sm text-slate-500">
          No subscriptions, create one to see watchman in action
        </p>
      </>
    );

  return (
    <div>
      {user.isGuest && (
        <p className="p-1 text-sm text-center text-white bg-red-300">
          <span className="font-semibold">Limited access to features...</span>{" "}
          details not permanant, sign in to enjoy full access!
        </p>
      )}
      <div className="p-3 my-5 mb-20 ml-2 md:ml-12 lg:ml-18">
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
          style={{ width: "auto", minWidth: "300px" }}
        />
        {isLoading && <Modal />}
        <div className="mb-20">
          <h1 className="mb-5 text-2xl font-bold tracking-wide text-slate-600">
            Welcome back,{" "}
            <span className="capitalize text-slate-700">{user.name}!</span>
          </h1>
          <p className="text-sm text-slate-600">
            Pick up where you left off, start with a new subscription or have a
            look at your search history!
          </p>
        </div>
        <div className="flex justify-between gap-12 pr-6">
          <div className="relative w-[20rem] px-8 pt-20 pb-8 border border-gray-100 rounded">
            <div className="absolute top-0 flex items-center justify-center p-4 -translate-y-1/2 bg-white border rounded w-22 h-22 z-1 left-6 border-slate-100">
              <img
                referrerPolicy="no-referrer"
                src={image}
                className="block w-16 clip-circle"
                alt=""
              />
            </div>
            <h1 className="text-xl font-semibold text-slate-600">
              {user.name}
            </h1>
            {!user.isGuest ? (
              <p className="mt-3 text-sm text-slate-500">{user.email}</p>
            ) : (
              <div className="inline-block my-6 px-2 text-[.7rem] rounded-sm tracking-wider text-yellow-600 font-semibold uppercase border border-yellow-300">
                guest
              </div>
            )}
            <div className="mt-8 space-y-3">
              <div className="mb-8">
                <label
                  htmlFor="file"
                  className="flex items-center justify-between w-56 text-xs text-slate-500"
                >
                  <span>Request Left</span>
                  <span>
                    {user.availableRequest} / {!user.isGuest ? 400 : 200}
                  </span>
                </label>
                <progress
                  id="file"
                  className={"w-56 h-[.4rem] rounded shadow"}
                  max="100"
                  value={user ? user.availableRequest / (!user.isGuest ? 4 : 2) : 0}
                ></progress>
              </div>
              <QuickLink name="Your Subscription" to="/user/subscription" />
              <QuickLink name="Search History" to="/user/history" />
              <QuickLink name="Settings" to="/user/settings" />
            </div>
          </div>
          <div className="grid flex-grow grid-cols-2 grid-rows-2 gap-4 px-auto">
            <Metric
              name="Request Made"
              value={(!user.isGuest ? 400 : 200) - user.availableRequest}
              Icon={AiOutlineCloudUpload}
            />
            <Metric name="Video Watched" value={history.length} Icon={AiOutlineEye} />
            <Metric name="Mail Sent" value={history.length} Icon={AiOutlineMail} />
            <Metric name="Comment Made" value={history.filter(h => h.comment_id.length > 0).length} Icon={AiOutlineComment} />
          </div>
        </div>
        <div className="flex gap-4 mt-12">
          <div className="mr-12">
            <h2 className="mb-2 font-bold tracking-wide text-center text-black">
              Subscriptions
            </h2>
            <div className="py-4 text-center border rounded w-[20rem] border-gray-100">
              {currentSubscription}
            </div>
            {subscriptions.length > 0 && (
              <div className="flex justify-center gap-3 mt-2">
                <MdKeyboardArrowLeft
                  width="2rem"
                  height="2rem"
                  className="text-red-400 scale-125 hover:cursor-pointer"
                  onClick={() =>
                    setSubIdx(
                      (i) =>
                        (i - 1 + subscriptions.length) % subscriptions.length
                    )
                  }
                />
                <MdKeyboardArrowRight
                  className="text-red-400 scale-125 hover:cursor-pointer"
                  onClick={() =>
                    setSubIdx((i) => (i + 1) % subscriptions.length)
                  }
                />
              </div>
            )}
          </div>
          <div className="max-w-sm">
            <h3 className="relative inline-block mb-2 font-bold tracking-wide text-black">
              Auto Comment
              <span
                className={
                  "absolute right-[-.72rem] top-[.4rem] w-[.35rem] h-[.35rem] rounded-full " +
                  (token.available
                    ? "bg-green-500"
                    : token.reset
                    ? "bg-yellow-400"
                    : "bg-red-400")
                }
              ></span>
            </h3>
            {!token.available && !token.reset && (
              <div className="flex items-baseline justify-between gap-3">
                <p className="flex-1 text-sm font-slate-400">
                  We don't have auto-comment access for your account
                </p>
                <Button small onClick={googleLogin}>
                  Give Access
                </Button>
              </div>
            )}
            {token.available && (
              <p className="flex-1 text-sm font-slate-400">
                Auto comment active
              </p>
            )}
            {token.reset && (
              <p className="flex-1 text-sm font-slate-400">
                Resets in {token.reset}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickLink({ to, name }) {
  return (
    <Link
      to={to}
      className="flex items-center justify-between py-0 text-sm 5 text-slate-500"
    >
      {name}
      <MdOutlineKeyboardArrowRight className="w-4 h-4 mr-4" />
    </Link>
  );
}

function Metric({ name, value, Icon }) {
  return (
    <div className="relative flex items-center justify-between px-8 py-5 border border-gray-100 rounded">
      <Icon className="absolute w-6 h-6 top-4 right-4 fill-slate-400" />
      <div>
        <p className="mb-3 text-4xl font-medium text-red-400">{value}</p>
        <p>{name}</p>
      </div>
    </div>
  );
}
