import React from "react";

import { AiOutlineDelete, AiOutlinePause } from "react-icons/ai";
import { Tag } from "../index";
import { BsPencil, BsPlay } from "react-icons/bs";

// STATIC DATA
const iconClass =
  "hover:cursor-pointer fill-slate-300 hover:fill-red-300 hover:!scale-[1.3]";

export default function Subscription({ subscription, openModal }) {
  return (
    <div className="flex px-5 py-3 bg-white border border-slate-100">
      {/* {console.log(subscription)} */}
      <img
        src={subscription.imgUrl}
        alt="channel-icon"
        className="block w-16 h-16 mt-3 rounded-full"
      />
      <div className="ml-8 mr-auto">
        <div className="flex items-center gap-10 mb-1">
          <h2 className="text-base font-medium text-slate-800">
            {subscription.title}
          </h2>
          {subscription.comment.length !== 0 && (
            <div className="px-1 text-[.56rem] rounded-sm tracking-wider text-green-600 font-semibold uppercase border border-green-300">
              auto-comment
            </div>
          )}
        </div>
        <p className="text-[.7rem] text-slate-400">{subscription.created_at}</p>
        <div className="mt-5 space-y-2">
          <div>
            <p className="text-slate-500">Tags Applied</p>
            <div className="flex flex-wrap">
              {subscription.tags.map((tag) => (
                <Tag key={tag} className="text-xs">
                  {tag}
                </Tag>
              ))}
            </div>
          </div>
          <div>
            <p className="text-slate-500">Emails Applied</p>
            <div className="flex flex-wrap">
              {subscription.emails.map((email) => (
                <Tag key={email} className="text-xs">
                  {email}
                </Tag>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-col items-center justify-center gap-5 [&:hover>*]:scale-95 [&>*]:transition-all">
        {subscription.active ? (
          <AiOutlinePause
            className={iconClass + " w-5 h-5"}
            onClick={() => openModal("pause", subscription)}
          />
        ) : (
          <BsPlay
            className={iconClass + " w-5 h-5"}
            onClick={() => openModal("resume", subscription)}
          />
        )}

        <BsPencil
          className={iconClass + " w-4 h-4"}
          onClick={() => openModal("edit", subscription)}
        />
        <AiOutlineDelete
          className={iconClass + " w-5 h-5"}
          onClick={() => openModal("delete", subscription)}
        />
      </div>
    </div>
  );
}
