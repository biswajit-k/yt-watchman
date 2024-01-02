import React, { useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useSelector } from "react-redux";

import { Formik } from "formik";
import * as Yup from "yup";

import {
  Button,
  VTagInput,
  Input,
  Description,
  Modal,
  useHttp,
  ProgressBar,
} from "../../index";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


// edit subscription page
export default function EditSubscription() {
  const { isLoading, isError, requester } = useHttp();
  const [channel, setChannel] = useState(null);
  const navigate = useNavigate();
  const { state } = useLocation();
  const [isSubLoading, setIsSubLoading] = useState(true);
  const [isAutoComment, setIsAutoComment] = useState(false);
  const formRef = useRef();
  const user = useSelector((state) => state.user);

  function submitResponsehandler(data) {
    toast.success(data.message);
    navigate("../subscription");
  }

  function submitHandler(subscriptionData) {
    toast.dismiss();
    requester(
      {
        url: `/api/subscription/edit/${state.subscription.channel_id}`,
        body: {
          method: "POST",
          mode: "cors",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(subscriptionData),
          credentials: "include",
        },
      },
      submitResponsehandler
    );
  }

  function setChannelData(data) {
    setChannel(data);
    toast.success("Yay! Channel Found");
  }
  function enableAutoCommentHandler() {
    setIsAutoComment((state) => !state);
  }

  async function fetchChannel(url) {
    toast.dismiss();
    setChannel(null);
    await requester(
      {
        url: "/api/get_channel",
        body: {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url }),
        },
      },
      setChannelData
    );
  }
  useEffect(() => {
    if (isError) {
      toast.dismiss();
      toast.error(isError || "something went wrong");
    }
  }, [isError]);

  useEffect(() => {
    if (state) {
      setIsSubLoading(false);
    }
  }, [state]);
  
  // re-validate form when auto-comment is toggled
  useEffect(() => {
    if (formRef.current) {
      formRef.current.validateForm();
    }
  }, [isAutoComment]);

  return (
    <>
      {isSubLoading ? (
        <Modal />
      ) : (
        <Formik
          innerRef={formRef}
          initialValues={{
            comment: state.subscription.comment,
            channelId:
              "https://youtube.com/channel/" + state.subscription.channel_id,
            emails: {
              input: "",
              tags: state.subscription.emails,
              isReleased: true,
            },
            tags: {
              input: "",
              tags: state.subscription.tags,
              isReleased: true,
            },
          }}
          onSubmit={(values) => {
            const subscriptionData = {
              channelId: channel.id,
              tags: values.tags.tags,
              emails: values.emails.tags,
              comment: values.comment,
            };
            submitHandler(subscriptionData);
          }}
          validationSchema={Yup.object().shape({
            comment: isAutoComment
              ? Yup.string().required("comment can't be empty")
              : Yup.string(),
            channelId: Yup.string()
              .required("url can't be empty")
              .url("invalid link"),
            emails: Yup.object().shape({
              input: Yup.string().email("invalid email address"),
              tags: Yup.array()
                .of(Yup.string())
                .when("input", {
                  is: (input) => input !== undefined,
                  then: (schema) => schema.min(0),
                  otherwise: (schema) => schema.min(1, "Email can't be empty"),
                }),
            }),
            tags: Yup.object().shape({
              input: Yup.string(),
              tags: Yup.array()
                .of(Yup.string())
                .when("input", {
                  is: (input) => input !== undefined,
                  then: (schema) => schema.min(0),
                  otherwise: (schema) => schema.min(1, "Tags can't be empty"),
                }),
            }),
          })}
        >
          {(props) => (
            <div className="max-w-lg p-3 my-5 mb-20 ml-3 md:ml-16 lg:ml-24">
              {isLoading && <Modal />}
              {/* {console.log(props.errors)} */}
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
              <div className="mb-5">
                <h1 className="mb-3 text-2xl font-bold text-slate-700">
                  Edit Subscription
                </h1>
                <p className="text-sm text-slate-600">
                  Edit your added subscription by changing tags or enabling/disabling auto-comment functionality
                </p>
              </div>
              <form onSubmit={props.handleSubmit} className="space-y-8">
                <div>
                  <Description
                    title="Channel Link"
                    desc="Channel which you want to watch, channel link is the link of channel dashboard"
                  />
                  <div className="flex items-baseline justify-between gap-2">
                    <Input
                      type="url"
                      id="channelId"
                      name="channelId"
                      placeholder="https://..."
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      onClick={() => fetchChannel(props.values.channelId)}
                      disabled={!props.values.channelId.trim().length}
                    >
                      Find Channel
                    </Button>
                  </div>
                  {channel && (
                    <div className="relative mt-2 rounded-lg bg-green-50">
                      <div className="absolute top-0.5 bottom-0.5 left-0.5 w-1 bg-green-200"></div>
                      <div className="flex items-center gap-4 py-4 pl-4">
                        <img
                          src={channel.imgUrl}
                          className="block h-16 rounded-full"
                          alt="channel-image"
                        />
                        <div>
                          <h4>{channel.title}</h4>
                          <p className="mt-2 text-xs text-slate-400">
                            {channel.subscribers} subscribers
                            &nbsp;&middot;&nbsp;
                            {channel.videos} videos
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div>
                  <Description
                    title="Tags"
                    desc="keywords you want to watch on the channel, eg- football, blockchain, unboxing, minecraft speedrun"
                  />
                  <VTagInput
                    placeholder="enter tags"
                    name="tags.input"
                    fieldName="tags"
                    type="text"
                    min={0}
                  />
                </div>
                <div>
                  <Description
                    title="Email for subscription"
                    desc="Recipients receive instant email notification whenever any upload with specified tags is present in the title or description of video"
                  />
                  <VTagInput
                    placeholder="enter emails"
                    name="emails.input"
                    fieldName="emails"
                    type="email"
                    min={user.email.length > 0 ? 1 : 0}
                    max={5}
                  />
                </div>
                <div className="flex items-baseline justify-between gap-2">
                  <Description
                    className="flex-1"
                    title="Enable Auto Comment"
                    desc="Automatically comment on the matching videos from your account when they are uploaded"
                  />
                  <label
                    htmlFor="auto-comment"
                    className="relative cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      id="auto-comment"
                      className="sr-only peer"
                      onChange={enableAutoCommentHandler}
                      checked={isAutoComment}
                    />
                    <div className="w-9 h-5 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-red-400"></div>
                  </label>
                </div>
                {/* { */}
                {isAutoComment && <ProgressBar />}
                <div className="flex items-center gap-4 pt-3">
                  <Button
                    type="button"
                    onClick={() => props.submitForm()}
                    disabled={
                      !Object.keys(props.touched).length ||
                      Object.keys(props.errors).length !== 0 ||
                      !channel
                    }
                    primary
                  >
                    Edit Subscription
                  </Button>
                  <Button
                    type="button"
                    onClick={() => navigate("/user/subscription")}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </div>
          )}
        </Formik>
      )}
    </>
  );
}
