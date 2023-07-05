import React from "react";
import Construction from "../../data/construction.png";

export default function UnderConstruction() {
  return (
    <div className="w-full pt-12 pb-20 lg:px-20 md:px-16 sm:px-10">
      <div className="flex flex-col items-center justify-center gap-5 mx-auto my-10">
        <img src={Construction} alt="add subscription" className="block w-80" />
        <p className="max-w-xl text-sm font-medium text-center text-slate-500">
          Feature under construction! Be patient while we are constantly working
          to setup this feature for you.
        </p>
      </div>
    </div>
  );
}
