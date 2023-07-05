import React from "react";

export default function Description({ title, desc, className }) {
  return (
    <div className={className ? className : ""}>
      <h3 className="font-semibold text-slate-500 text-[.9rem] mb-1">
        {title}
      </h3>
      <p className="mb-1 text-xs text-slate-500">{desc}</p>
    </div>
  );
}
