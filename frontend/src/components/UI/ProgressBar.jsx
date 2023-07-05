import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  withStepProgress,
  useStepProgress,
  Step,
  StepProgressBar,
} from "react-stepz";
import "react-stepz/dist/index.css";
import { useGoogleLogin } from "@react-oauth/google";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { Button, Link, Input, useHttp, Modal } from "../index";
import styles from "./progress-bar.module.css";

const steps = [
  {
    label: "Comment Access",
  },
  {
    label: "Create Youtube Channel",
  },
  {
    label: "Add Comment",
  },
];

function ProgressBar() {
  const { isLoading, isError, requester } = useHttp();
  const dispatch = useDispatch();

  const googleLogin = useGoogleLogin({
    onSuccess: (response) => requestHandler(response),
    scope: "https://www.googleapis.com/auth/youtube.force-ssl",
    flow: "auth-code",
  });

  const { setStep, currentStep } = useStepProgress({
    steps,
    startingStep: 0,
  });

  useEffect(() => {
    fetchCommentStatus();
  }, []);

  useEffect(() => {
    if (isError) {
      toast.dismiss();
      toast.error("something went wrong");
    }
  }, [isError]);

  function requestHandler(response) {
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
        fetchCommentStatus();
      }
    );
  }

  function fetchCommentStatus() {
    requester(
      {
        url: "/api/comment_access",
        body: {
          credentials: "include",
        },
      },
      (data) => {
        if (data.error) {
          toast.error(data.error);
          return;
        }
        setStep(data.status);
      }
    );
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
        style={{ width: "auto", minWidth: "300px" }}
      />
      <div>
        <StepProgressBar
          className={"!p-0 mt-4 text-sm " + styles.wrapper}
          progressClass={"!mb-16 progress " + styles.progress}
          steps={steps}
          stepClass={"font-semibold text-[.8rem] step " + styles.step}
        />
        <Step step={0}>
          <div className="flex items-baseline justify-between gap-2">
            <p className="flex-1 mb-4 text-sm font-medium text-slate-600">
              We require comment access of your account to auto-comment for you.
            </p>
            <Button small onClick={googleLogin}>
              Give Access
            </Button>
          </div>
        </Step>
        <Step step={1}>
          <div className="flex justify-center">
            <div className="relative max-w-[30rem] py-4 rounded-lg bg-red-50">
              <div className="absolute top-0.5 bottom-0.5 left-[.04rem] w-1 bg-red-400"></div>
              <div>
                <h4 className="ml-6 text-[.9rem] font-semibold traking-wider text-slate-700">
                  No Channel Found!
                </h4>
                <div className="mt-2 ml-6 text-xs font-medium tracking-wider text-slate-500">
                  <p>
                    Go to{" "}
                    <Link
                      className="underline"
                      href="https://youtube.com"
                      target="_blank"
                    >
                      Youtube
                    </Link>{" "}
                    open settings and choose{" "}
                    <span className="italic font-semibold">
                      create a channel
                    </span>{" "}
                    or follow{" "}
                    <Link
                      className="underline"
                      href="https://support.google.com/youtube/answer/1646861?hl=en#:~:text=Create%20a%20personal%20channel"
                      target="_blank"
                    >
                      this
                    </Link>{" "}
                    guide
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Step>
        <Step step={2}>
          <div>
            <p className="mb-4 text-sm font-medium tracking-wider text-slate-600">
              Provide comment. We will notify you once the comment has been made
              on a video.
            </p>
            <Input
              textarea
              type="text"
              placeholder="Your Comment"
              name="comment"
              id="comment"
            />
          </div>
        </Step>
      </div>
    </div>
  );
}
export default withStepProgress(ProgressBar);
