import React from "react";

import { Tag } from "../index";

const openInNewTab = (url) => {
  window.open(url, "_blank", "noopener,noreferrer");
};

export default function HistoryItem({ item }) {
  return (
    <div className="flex px-5 py-3 bg-white border border-slate-100">
      <img
        onClick={() =>
          openInNewTab(`https://www.youtube.com/watch?v=${item.video_id}`)
        }
        src={item.imgUrl}
        alt="channel-icon"
        className="block rounded-sm h-36 hover:cursor-pointer"
      />
      <div className="ml-8 mr-auto">
        <div className="flex items-center gap-10 mb-1">
          <h2
            className="text-base font-medium text-slate-800 hover:text-red-400 hover:cursor-pointer"
            onClick={() =>
              openInNewTab(`https://www.youtube.com/watch?v=${item.video_id}`)
            }
          >
            {item.title}
          </h2>
          {item.comment_id.length !== 0 && (
            <a
              href={`https://www.youtube.com/watch?v=${item.video_id}&lc=${item.comment_id}`}
              target="_blank"
              className="px-1 text-[.6rem] rounded-sm tracking-wider hover:text-red-600 font-semibold uppercase border hover:border-red-300 border-green-300 text-green-600"
            >
              commented
            </a>
          )}
        </div>
        <p className="text-[.7rem] text-slate-400">
          <span
            className="hover:underline hover:cursor-pointer"
            onClick={() =>
              openInNewTab(`https://www.youtube.com/channel/${item.channel_id}`)
            }
          >
            {item.channel_title}
          </span>{" "}
          &middot; {item.found_at}
        </p>
        <div className="mt-5 space-y-2">
          <div>
            <p className="text-slate-500">Tag Found</p>
            <div className="flex flex-wrap">
              <Tag>{item.tag}</Tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
