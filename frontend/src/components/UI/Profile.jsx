import React from "react";
import { useSelector } from "react-redux";
import { Link } from "react-router-dom";

export default function Profile({ image }) {
  const user = useSelector((state) => state.user);

  return (
    <div className="absolute pb-3 text-sm bg-white border rounded-md w-64 shadow-lg border-slate-50 top-[3.4rem] right-10 z-10">
      <div className="flex flex-col items-center gap-1 p-8 pb-4">
        <img
          src={image}
          alt="Avatar"
          className="block w-12 h-12 mb-3 rounded-full"
          referrerPolicy="no-referrer"
        />
        <p className="font-semibold text-slate-600">{user.name}</p>
        {user.email.length > 0 ? (
          <p className="text-[.8rem] font-medium text-slate-500">
            {user.email}
          </p>
        ) : (
          <div className="inline-block my-6 px-2 text-[.7rem] rounded-sm tracking-wider text-yellow-600 font-semibold uppercase border border-yellow-300">
            guest
          </div>
        )}
      </div>
      <Link
        to="/user/logout"
        className="block px-3 text-center py-3 text-[.8rem] text-slate-500 hover:bg-gray-50"
      >
        Log Out
      </Link>
    </div>
  );
}
