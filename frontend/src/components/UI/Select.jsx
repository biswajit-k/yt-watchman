import React from "react";

import { useComponentVisible } from "../index";
import { MdKeyboardArrowDown } from "react-icons/md";

export default function Select(props) {
  const { ref, isComponentVisible, setIsComponentVisible } =
    useComponentVisible(false);
  return (
    <div ref={ref} className="relative">
      {isComponentVisible && (
        <div className="absolute px-2 py-4 bg-white border rounded-md shadow-md border-slate-200 w-80 top-8 right-4">
          {props.children}
        </div>
      )}
      <div
        className={`relative flex items-center justify-between gap-1 px-3 py-1 rounded-md hover:cursor-pointer hover:bg-slate-50 ${
          isComponentVisible && "bg-slate-50"
        }`}
        onClick={() => setIsComponentVisible((state) => !state)}
      >
        <p className="select-none">{props.title}</p>
        <MdKeyboardArrowDown />
      </div>
    </div>
  );
}
