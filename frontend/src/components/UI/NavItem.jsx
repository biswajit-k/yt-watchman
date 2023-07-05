import React from "react";
import { NavLink } from "react-router-dom";

export default function NavItem({ ItemIcon, name, isActive, ...props }) {
  return (
    <NavLink
      {...props}
      // TODO- add focus color for navigation thru tab
      className={`relative block focus:outline-none text-sm ${
        isActive ? "bg-red-50 text-red-400" : "hover:bg-slate-50 text-slate-700"
      }`}
    >
      {isActive && (
        <div className="absolute top-0 bottom-0 w-1 bg-red-400 "></div>
      )}
      <div className={`ml-7 h-11 flex items-center gap-3`}>
        {ItemIcon}
        <p className="capitalize">{name}</p>
      </div>
    </NavLink>
  );
}
