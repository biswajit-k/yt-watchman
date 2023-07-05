import React from "react";
import logo from "../../data/logo.jpg";

export default function Logo(props) {
  return (
    <>
      <div className="">
        <img className="block ml-4 w-40" src={logo} alt="logo" />
      </div>
    </>
    // <h1
    //   className={
    //     "text-lg font-semibold capitalize text-slate-600 " + props.className
    //   }
    // >
    //   YT <span className="text-red-400">watchman</span>
    // </h1>
  );
}
