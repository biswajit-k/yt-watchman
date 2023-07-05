import React from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import {
  AiOutlineBell,
  AiOutlineSetting,
  AiOutlineSearch,
} from "react-icons/ai";
import { Icon, useComponentVisible, Profile, useImage } from "./index";

export default function Navbar() {
  const user = useSelector((state) => state.user);
  const { ref, isComponentVisible, setIsComponentVisible } =
    useComponentVisible(false);
  const { image } = useImage(user.id, user.isGuest);
  const navigate = useNavigate();

  return (
    <div className="z-100 flex items-center justify-between h-16 pb-2 pl-3 pr-12 bg-white border-b shadow-sm border-b-slate-50 shadow-slate-50">
      <div className="relative">
        <AiOutlineSearch className="absolute w-5 h-6 top-2 right-3 fill-slate-300" />
        <input
          type="text"
          placeholder="Search"
          className="p-2 text-sm rounded-md pr-9 bg-gray-50 text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-200"
        />
      </div>
      <div className="flex items-center gap-5">
        <Icon onClick={() => navigate('/user/settings')}>
          <AiOutlineSetting className="w-[1.1rem] h-[1.1rem]" />
        </Icon>
        <Icon>
          <AiOutlineBell className="w-[1.1rem] h-[1.1rem]" />
        </Icon>
        <Icon ref={ref} className={isComponentVisible ? "bg-slate-100" : ""}>
          <img
            onClick={() => {
              setIsComponentVisible((state) => !state);
            }}
            src={image}
            alt="Avatar"
            className="block h-6 rounded-full cursor-pointer"
            referrerPolicy="no-referrer"
          />
          {isComponentVisible && <Profile image={image} />}
        </Icon>
      </div>
    </div>
  );
}
