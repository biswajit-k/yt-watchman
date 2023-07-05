import React from "react";

export default function Link({ children, active, className, ...props }) {
  const activeClass = active
    ? " text-slate-800 font-semibold "
    : " text-slate-400 font-medium ";
  return (
    <a
      {...props}
      className={
        "text-sm tracking-wider cursor-pointer" +
        activeClass +
        (className ? className : "")
      }
    >
      {children}
    </a>
  );
}
