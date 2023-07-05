import React from "react";

export default function Button({
  children,
  onClick,
  primary,
  type,
  disabled,
  small,
}) {
  const typeClass = primary
    ? "bg-red-400 text-white hover:bg-red-500"
    : "bg-slate-100 text-slate-700 hover:bg-slate-200";
  const disabledClass = disabled ? "cursor-not-allowed opacity-40" : "";
  const smallClass = small ? "!px-4 !py-2 text-[.72rem]" : " ";
  return (
    <button
      type={type || "button"}
      onClick={onClick}
      className={`px-5 py-3 rounded-md capitalize shadow-sm text-xs font-semibold  ${typeClass} ${disabledClass} ${smallClass}`}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
