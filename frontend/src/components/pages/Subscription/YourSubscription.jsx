import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { IoFilterOutline, IoAddOutline } from "react-icons/io5";

import { Modal, Alert, useHttp, Subscription, Button } from "../../index";
import AddIllustration from "../../../data/add-sub.jpg";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// STATIC DATA
const activeClass =
  "text-red-500 relative after:absolute after:bg-red-300 after:-left-1 after:-right-1 after:-bottom-0.5 after:top-full";
const inActiveClass = "hover:text-red-400 text-slate-400";

const modalMessage = {
  edit: {
    title: "edit subscription",
    desc: "The search history will not be impacted. Are you sure you want to edit?",
    button: "edit",
  },
  delete: {
    title: "delete subscription",
    desc: "The changes can't be reverted. Are you sure you want to delete?",
    button: "delete",
  },
  pause: {
    title: "pause subscription",
    desc: "The channel will be stopped watching. However, you can resume it anytime. Are you sure you want to pause?",
    button: "pause",
  },
  resume: {
    title: "resume subscription",
    desc: "The channel will be watched again. You will start receiving notifications. Are you sure you want to resume?",
    button: "resume",
  },
};

const initialModal = { type: null, subscription: null };

// subscriptions page
export default function YourSubscription() {
  // HOOKS
  const [modal, setModal] = useState(initialModal);
  const [isActive, setIsActive] = useState(true);
  const [subscriptions, setSubscriptions] = useState({
    active: [],
    paused: [],
  });
  const { isLoading, isError, requester } = useHttp();
  const navigate = useNavigate();

  useEffect(() => {
    // TODO: clean up fetch
    requestSubscription();
  }, []);

  useEffect(() => {
    if (isError) {
      toast.dismiss();
      toast.error(isError || "something went wrong");
    }
  }, [isError]);

  // HANDLERS
  function closeModal() {
    setModal(initialModal);
  }
  function openModal(name, subscription) {
    setModal({ type: name, subscription });
  }
  function requestSubscription() {
    requester(
      {
        url: "/api/subscription",
        body: {
          credentials: "include",
        },
      },
      (data) => {
        setSubscriptionsData(data);
      }
    );
  }
  function setSubscriptionsData(data) {
    setSubscriptions(data);
  }
  function subscriptionHandler(type, subscription) {
    requester(
      {
        url: `/api/subscription/${type}/${subscription.channel_id}`,
        body: {
          credentials: "include",
        },
      },
      requestSubscription
    );
    closeModal();
  }

  return (
    <div className="w-full pt-12 pb-20 lg:px-20 md:px-16 sm:px-10">
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
      {modal.type && (
        <Modal>
          {modal.type === "delete" && (
            <Alert
              {...modalMessage.delete}
              onCancel={closeModal}
              onPrimary={() =>
                subscriptionHandler(modal.type, modal.subscription)
              }
            />
          )}
          {modal.type === "edit" && (
            <Alert
              {...modalMessage.edit}
              onCancel={closeModal}
              onPrimary={() => {
                navigate("edit", {
                  state: { subscription: modal.subscription },
                });
              }}
            />
          )}
          {modal.type === "pause" && (
            <Alert
              {...modalMessage.pause}
              onCancel={closeModal}
              onPrimary={() =>
                subscriptionHandler(modal.type, modal.subscription)
              }
            />
          )}
          {modal.type === "resume" && (
            <Alert
              {...modalMessage.resume}
              onCancel={closeModal}
              onPrimary={() =>
                subscriptionHandler(modal.type, modal.subscription)
              }
            />
          )}
        </Modal>
      )}

      <h1 className="mb-3 text-2xl font-bold text-slate-700">
        Your Subscription
      </h1>
      {!subscriptions.active.length && !subscriptions.paused.length ? (
        <div className="flex flex-col items-center justify-center gap-5 mx-auto my-10">
          <img
            src={AddIllustration}
            alt="add subscription"
            className="block w-80"
          />
          <p className="max-w-xl text-sm font-medium text-center text-slate-500 leading-[1.35rem]">
            Opps! Looks like you don't have any subscriptions. Create one and let our watchman
            keep an eye on it
          </p>
          <Button type="button" onClick={() => navigate("add")} primary>
            Add Subscription
          </Button>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between py-10 mr-10">
            <p className="max-w-md text-sm text-slate-600 leading-[1.35rem]">
            Create customized subscriptions based on tags which allows and get
            notified through e-mail when these tags are found on the video title
            or description of new uploaded video on the channels
            </p>
            <Button type="button" onClick={() => navigate("add")} primary>
              <div className="flex items-center gap-1">
                <IoAddOutline className="w-5 h-5 fill-white " />{" "}
                <span className="tracking-wider">Create</span>
              </div>
            </Button>
          </div>

          <div className="space-x-5 text-base border-b-2 border-b-slate-50">
            <div
              className={`inline-block py-1 cursor-pointer ${
                isActive ? activeClass : inActiveClass
              }`}
              onClick={() => setIsActive(true)}
            >
              Active
            </div>
            <div
              className={`inline-block py-1 cursor-pointer ${
                !isActive ? activeClass : inActiveClass
              }`}
              onClick={() => setIsActive(false)}
            >
              Paused
            </div>
          </div>
          <div className="pl-3 pr-6">
            {(isActive && !subscriptions.active.length) ||
            (!isActive && !subscriptions.paused.length) ? (
              <p className="max-w-md my-5 text-slate-500">
                Opps! the list is empty
              </p>
            ) : (
              <div>
                <div className="flex items-center justify-between p-1 mt-5 mb-4">
                  <p className="text-red-400">
                    {isActive
                      ? subscriptions.active.length
                      : subscriptions.paused.length}{" "}
                    Subscription
                  </p>
                  <div className="flex items-center gap-3 px-4 py-2 text-sm rounded-md bg-slate-50">
                    <IoFilterOutline />
                    <select
                      className="bg-slate-50"
                      name="channel-sort"
                      id="channel-sort"
                    >
                      <option value="Latest">Latest</option>
                      <option value="Oldest">Oldest</option>
                      <option value="Pending">Pending</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-4 text-xs">
                  {isActive &&
                    (subscriptions.active.length
                      ? subscriptions.active.map((subscription) => (
                          <Subscription
                            key={subscription.title}
                            subscription={subscription}
                            openModal={openModal}
                          />
                        ))
                      : !isLoading && <div>empty sub</div>)}
                  {!isActive &&
                    subscriptions.paused.map((subscription) => (
                      <Subscription
                        key={subscription.title}
                        subscription={subscription}
                        openModal={openModal}
                      />
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
