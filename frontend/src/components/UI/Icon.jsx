import React, { forwardRef } from "react";

const Icon = forwardRef(({ className, children, onClick, ...props }, ref) => {
  return (
    <button
      {...props}
      ref={ref}
      className={`inline-block p-2 rounded-md hover:bg-slate-100 ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
});

export default Icon;
