import React from "react";

export default function Tag({ className, children, onClose, ...props }) {
  return (
    <div
      className={`flex items-center gap-1 p-2 my-1 mr-2 text-xs font-medium rounded-md text-slate-400 bg-slate-100 whitespace-nowrap ${className}`}
      {...props}
    >
      <div className="pr-2 ">{children}</div>

      {onClose && (
        <div className="pr-1 cursor-pointer" onClick={onClose}>
          x
        </div>
      )}
    </div>
  );
}
