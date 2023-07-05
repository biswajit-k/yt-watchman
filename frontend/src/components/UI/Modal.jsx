import React from "react";
import ReactDOM from "react-dom";
import { Lottie } from "@crello/react-lottie";
import loading from "./../../data/loading.json";

const defaultOptions = {
  loop: true,
  autoplay: true,
  animationData: loading,
};

function Loading() {
  return (
    <div className="flex items-center justify-center">
      <Lottie
        config={defaultOptions}
        className="bg-transparent"
        height={50}
        width={50}
      />
    </div>
  );
}

function Backdrop(props) {
  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center w-full h-full">
      <div
        className={`absolute inset-0 w-full h-full -z-10` + props.background}
      ></div>
      {props.children}
    </div>
  );
}

export default function Modal(props) {
  return ReactDOM.createPortal(
    props.children ? (
      <Backdrop background=" bg-black opacity-30">{props.children}</Backdrop>
    ) : (
      <Backdrop background=" bg-white opacity-70">
        <Loading />
      </Backdrop>
    ),
    document.getElementById("modal-box")
  );
}
