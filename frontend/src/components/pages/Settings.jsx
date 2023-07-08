import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {  IoAddOutline } from "react-icons/io5";
import { AiOutlineDelete, AiOutlineInfoCircle, AiOutlineStop } from "react-icons/ai";

import { Modal, Button, useHttp, useImage, useProfile } from "../index";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// STATIC DATA
const activeClass =
  "text-red-500 relative after:absolute after:bg-red-300 after:-left-1 after:-right-1 after:-bottom-0.5 after:top-full";
const inActiveClass = "hover:text-red-400 text-slate-400";
const statusClass =
  "w-2 h-2 rounded-full m-1 inline-block translate-y-[.2rem] ";

export default function Settings() {

  const [history, setHistory] = useState([]);
  const [subscriptionStats, setSubscriptionStats] = useState({active: 0, paused: 0});

  const { isError, requester, isLoading } = useHttp();
  const user = useProfile(requester);
  const { image } = useImage(user.id, user.isGuest);
  const navigate = useNavigate();

  useEffect(() => {
    requester(
      {
        url: "/api/history",
        body: {
          credentials: "include",
        },
      },
      (data) => {
        if(data.history) setHistory(data.history);
        else {
          toast.dismiss();
          toast.error('something went wrong');
        } 
          
      }
    )
  }, []);

  useEffect(() => {
    requester(
      {
        url: "/api/subscription/stats",
        body: {
          credentials: "include",
        },
      },
      (data) => setSubscriptionStats(data)
    )
  }, []);

  useEffect(() => {
    if (isError) {
      toast.dismiss();
      toast.error(isError);
    }
  }, [isError]);

  return (
    <div className="w-full pt-12 pb-20 lg:px-16 md:px-12 sm:px-8">
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
      {isLoading && <Modal />}
      <div className="relative w-full h-40 bg-gray-100 rounded">
        <img
          referrerPolicy="no-referrer"
          src={image}
          className="absolute -bottom-8 -left-[.6rem] h-24 w-24 block clip-circle"
          alt="profile"
        />
      </div>

      <div className="relative flex h-full">
        <div className="relative">
          <div className="sticky top-0 bottom-0 left-0 flex flex-col pt-20">
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
                  value={user ? user.availableRequest / (!user.isGuest ? 4 : 2): 0}
                ></progress>
                <div>
                  <AiOutlineInfoCircle className="inline-block w-3 h-3 fill-slate-400"/>
                  <p className="inline-block ml-1 text-xs text-slate-400">Refreshed Daily</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="relative h-full ml-10">
          <div className="sticky top-0 z-10 pt-8 pb-4 pl-12 text-base bg-white shadow-sm space-x-7 shadow-slate-50">
            <div
              className={`inline-block py-1 cursor-pointer ${ activeClass}`}
            >
              Overview
            </div>
          </div>
          <div className="p-5 py-8 space-y-4 overflow-y-scroll pb">
            <div>
              <h2 className="py-1 text-xl font-semibold border-b border-b-gray-100">
                Subscriptions
              </h2>
              <div className="px-2 py-4 space-y-4 text-sm font-medium">
                <p className="font-normal">
                  This section contains the details of your subscription by
                  their active or paused status
                </p>
                <div className="flex items-center justify-between mx-3">
                  <div>
                    Total Subscriptions: <span className="font-normal">{subscriptionStats.active + subscriptionStats.paused }</span>
                    <div className="mt-2 space-x-6">
                      <div className="inline-block">
                        <div className={statusClass + " bg-green-500"}></div>
                        Active Subscriptions:{" "}
                        <span className="font-normal">{subscriptionStats.active}</span>
                      </div>
                      <div className="inline-block mb-3">
                        <div className={statusClass + " bg-yellow-400"}></div>
                        Paused Subscriptions:{" "}
                        <span className="font-normal">{subscriptionStats.paused}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    type="button"
                    onClick={() => navigate("/user/subscription/add")}
                    primary
                    small
                  >
                    <div className="flex items-center gap-1">
                      <IoAddOutline className="w-5 h-5 fill-white " />{" "}
                      <span className="tracking-wider">Add</span>
                    </div>
                  </Button>
                </div>
              </div>
            </div>
            <div>
              <h2 className="py-1 text-xl font-semibold border-b border-b-gray-100">
                Search History
              </h2>
              <div className="px-2 py-4 space-y-4 text-sm">
                <p>
                  Search history contains the videos of your subscriptions which
                  are matched according to your preference
                </p>
                <div className="flex items-center justify-between mx-3">
                  <div className="font-medium">
                    Total Searches: <span className="font-normal">{history.length}</span>
                  </div>
                  <Button
                    type="button"
                    // onClick={() => navigate("add")}
                    small
                    disabled
                  >
                    <div className="flex items-center gap-1">
                      <AiOutlineDelete className="w-5 h-5 hover:cursor-pointer hover:fill-red-300" />{" "}
                      <span className="tracking-wider">Clear History</span>
                    </div>
                  </Button>
                </div>
              </div>
            </div>
            <div>
              <h2 className="py-1 text-xl font-semibold border-b border-b-gray-100">
                Comments
              </h2>
              <div className="px-2 py-4 space-y-4 text-sm font-medium">
              <div>This section contains details about auto-comments you have enabled on your subscriptions</div>
                <div className="flex items-center justify-between mx-3">
                  <div>
                    <div className="mb-2 font-medium">
                    Comments Made: <span className="font-normal">{history.filter(h => h.comment_id.length > 0).length}</span>
                    </div>
                    <div className="font-medium">
                        Auto-comment Set: <span className="font-normal">{subscriptionStats.auto_comments}</span>
                      </div>
                  </div>
                  <Button
                    type="button"
                    // onClick={() => navigate("add")}
                    disabled
                    small
                  >
                    <div className="flex items-center gap-1">
                      <AiOutlineStop className="w-5 h-5 " />{" "}
                      <span className="tracking-wider">Revoke Access</span>
                    </div>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
