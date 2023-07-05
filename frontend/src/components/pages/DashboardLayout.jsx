import React from "react";
import { Outlet } from "react-router-dom";

import { Sidebar, Navbar } from "../index";

export default function DashboardLayout() {
  /* 
    STRUCTURE
      main- relative
      sidebar, navbar- fixed
      content(navbar + display) - relative
  */
  return (
    <div className="flex w-full h-full">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="h-[calc(100%-4rem)] overflow-y-scroll">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
