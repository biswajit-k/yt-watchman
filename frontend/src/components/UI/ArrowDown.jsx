import React from "react";
import { IoChevronDownOutline } from "react-icons/io5";

export default function ArrowDown(props) {
  return (
    <div className={"flex flex-col " + props.className}>
      <IoChevronDownOutline className="w-9 h-9 stroke-slate-200" />
      <IoChevronDownOutline className="-mt-[1.11rem] w-9 h-9 stroke-slate-500" />
    </div>
  );
}
