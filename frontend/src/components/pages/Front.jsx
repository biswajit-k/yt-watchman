import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";

import {AiOutlineGithub} from 'react-icons/ai'

import {
  Button,
  Link,
  Paragraph,
  ArrowDown,
  FeatureItem,
  Logo,
} from "../index";
import search from "../../data/search.svg";
import preference from "../../data/preference.svg";
import indbox from "../../data/indbox.svg";
import contact from "../../data/contact.svg";

const inputClass =
  "max-w-sm p-2 text-sm rounded-md bg-gray-50 text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-200";

const scroll = (id) => {
  const section = document.querySelector("#" + id);
  section.scrollIntoView({ behavior: "smooth", block: "start" });
};

export default function Front() {
  const [isWipVisible, setIsWipVisible] = useState(true);
  const navigate = useNavigate();
  const user = useSelector((state) => state.user);

  return (
    <div className="w-full overflow-y-scroll">
      {isWipVisible && (
        <div className="flex items-center p-2 text-sm text-center text-white bg-red-400">
          <p className="grow-1 basis-full">
            <span className="font-semibold">Work in progress...</span> This site
            under construction. However, you can still access most of the
            features.
          </p>
          <div
            className="self-end pr-5 text-base hover:cursor-pointer"
            onClick={() => setIsWipVisible(false)}
          >
            x
          </div>
        </div>
      )}
      <div id="home" className="flex items-center justify-between px-16 pt-8">
        <Logo />
        <div className="flex items-center gap-28">
          <div className="flex items-center justify-between gap-8">
            <Link active onClick={() => scroll("home")}>
              Home
            </Link>
            <Link onClick={() => scroll("features")}>Features</Link>
            {/* <Link onClick={() => scroll("demo")}>Demo</Link> */}
            <Link onClick={() => scroll("contact")}>Contact</Link>
          </div>
          {!user.isLoggedIn ? (
            <Button type="button" onClick={() => navigate("/login")} primary>
              Sign In
            </Button>
          ) : (
            <Button
              type="button"
              onClick={() => navigate("/user/dashboard")}
              primary
            >
              Go to dashboard
            </Button>
          )}
        </div>
      </div>
      <div className="flex flex-col items-center gap-8 px-16 mt-32 text-center">
        <h1 className="text-4xl font-bold text-slate-700">
          Your assistant at fingertips
        </h1>
        <p className="max-w-lg text-base text-slate-400">
          Sit back and relax while your YT assistant is ready to serve you all
          the time including search, personal preference and much more
        </p>
        <div className="flex items-center justify-between gap-6">
          {!user.isLoggedIn ? (
            <Button type="button" onClick={() => navigate("/login")} primary>
              Sign In
            </Button>
          ) : (
            <Button
              type="button"
              onClick={() => navigate("/user/dashboard")}
              primary
            >
              Go to dashboard
            </Button>
          )}
          <Button
                    type="button"
                    // onClick={() => navigate("add")}
                  >
                    <a href="https://github.com/biswajit-k/yt-watchman" target="_blank">
                    <div className="flex items-center gap-1">
                      <AiOutlineGithub className="hover:cursor-pointer
                      w-5 h-5" />{" "}
                      <span className="tracking-wider">See Code</span>
                    </div>
                    </a>
                  </Button>
        </div>
        <ArrowDown className="mt-4 mr-6" />
      </div>
      <div id="features" className="flex p-6 px-16 my-10 justify-evenly">
        <FeatureItem title="create" image={search}>
          Create subscriptions based on tags of your needs
        </FeatureItem>
        <FeatureItem title="customize" image={preference}>
          Subscriptions are customizable to allow full control on what 
          shoud be notified
        </FeatureItem>
        <FeatureItem title="get notified" image={indbox}>
          Informs you as soon as a matching video is found through e-mail,
          also automatically comments on your behaf if enabled
        </FeatureItem>
      </div>
      {/* features */}
      <div id="contact" className="px-24 py-10">
        <h2 className="mb-10 text-xl font-bold text-slate-700">Contact Us</h2>
        <div className="flex gap-6">
          <div className="flex flex-col gap-3 grow">
            <input type="text" className={inputClass} placeholder="Name" />
            <input type="email" className={inputClass} placeholder="Email" />
            <textarea
              type="text"
              className={inputClass + " min-h-[6rem]"}
              placeholder="Message"
            />
            <div>
              <Button primary type="button">
                Submit
              </Button>
            </div>
          </div>
          <img src={contact} className="w-40 h-40 grow" alt="" />
        </div>
      </div>
      <div className="p-10 mt-20 text-sm text-center bg-slate-100">
        <p className="tracking-wider">
          &copy; All rights reserved by YT-Watchman LLC
        </p>
      </div>
    </div>
  );
}
