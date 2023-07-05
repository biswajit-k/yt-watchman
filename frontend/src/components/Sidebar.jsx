import React, { useState } from "react";
import { NavItem, Logo } from "../components/index";
import { links } from "../data/dummy";
export default function Sidebar() {
  const [activeLink, setActiveLink] = useState("dashboard");

  return (
    <div className="w-[15rem] relative shadow-sm shadow-slate-200 ">
      <div className="flex items-center h-20 bg-white">
        <Logo className="ml-8" />
      </div>
      <div className="mt-6 space-y-8">
        {links.map((topic) => (
          <div key={topic.title}>
            <div className="mb-2 text-xs font-medium tracking-widest uppercase ml-7 text-slate-400">
              {topic.title}
            </div>
            <div>
              {topic.items.map((item) => {
                return (
                  <NavItem
                    to={item.to}
                    key={item.name}
                    name={item.name}
                    ItemIcon={item.icon}
                    isActive={activeLink === item.name}
                    onClick={() => setActiveLink(item.name)}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
