import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import {
  Paragraph,
  Modal,
  useHttp,
  Button,
  Select,
  Checkbox,
  SearchList,
  Radio,
  HistoryItem,
} from "../index";
import SearchIllustration from "../../data/empty-search.png";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


export default function History() {
  const { isLoading, isError, requester } = useHttp();
  const navigate = useNavigate();
  // STATES
  const [history, setHistory] = useState([]);
  // one time reload - or use ref instead
  const [channels, setChannels] = useState([]);
  const [tags, setTags] = useState([]);
  const [filteredChannels, setFilteredChannels] = useState(channels);
  const [filteredTags, setFilteredTags] = useState(tags);
  const filteredHistory = history.filter(
    (item) =>
      filteredChannels.includes(item.channel_title) &&
      filteredTags.includes(item.tag)
  );
  // filter states
  const [channelCheckbox, setChannelCheckbox] = useState([]);
  const [tagCheckbox, setTagCheckbox] = useState([]);
  const [isRecent, setIsRecent] = useState(true);

  useEffect(() => {
    requester(
      {
        url: "/api/history",
        body: {
          credentials: "include",
        },
      },
      (data) => {
        console.log(data)
        const newChannels = [];
        data.history.forEach((history) => {
          if (!newChannels.includes(history.channel_title)) {
            newChannels.push(history.channel_title);
          }
        });
        const newTags = [];
        data.history.forEach((history) => {
          if (!newTags.includes(history.tag)) {
            newTags.push(history.tag);
          }
        });
        setTags(newTags);
        setChannels(newChannels);
        setChannelCheckbox(
          new Array(newChannels.length + 1)
            .fill(false)
            .map((state, idx) => (idx === 0 ? !state : state))
        );
        setTagCheckbox(
          new Array(newTags.length + 1)
            .fill(false)
            .map((state, idx) => (idx === 0 ? !state : state))
        );
        setHistory(data.history);
      }
    );
  }, []);

  useEffect(() => {
    if (isError) {
      toast.dismiss();
      toast.error(isError || "something went wrong");
    }
  }, [isError]);


  // hooks for 'sort by' option
  useEffect(() => {
    if (channelCheckbox[0] === true) {
      setFilteredChannels(channels);
    } else {
      const newFilteredChannels = channelCheckbox
        .map((state, idx) => (state ? channels[idx - 1] : null))
        .filter((item) => item);
      setFilteredChannels(newFilteredChannels);
    }
  }, [channelCheckbox]);
  useEffect(() => {
    if (tagCheckbox[0] === true) {
      setFilteredTags(tags);
    } else {
      const newFilteredTags = tagCheckbox
        .map((state, idx) => (state ? tags[idx - 1] : null))
        .filter((item) => item);
      setFilteredTags(newFilteredTags);
    }
  }, [tagCheckbox]);

  const channelList = channels.map((channel, index) => (
    <Checkbox
      name={channel}
      key={channel}
      handleOnChange={checkboxChangeHandler}
      isChecked={channelCheckbox[index + 1]}
      index={index + 1}
      list={channelCheckbox}
      setList={setChannelCheckbox}
    />
  ));
  const tagList = tags.map((tag, index) => (
    <Checkbox
      name={tag}
      key={tag}
      handleOnChange={checkboxChangeHandler}
      isChecked={tagCheckbox[index + 1]}
      index={index + 1}
      list={tagCheckbox}
      setList={setTagCheckbox}
    />
  ));
  function checkboxChangeHandler(index, checkboxList, setCheckboxList) {
    if (index === 0) {
      const updatedList = new Array(checkboxList.length).fill(false);
      updatedList[0] = true;
      setCheckboxList(updatedList);
    } else {
      const updatedList = checkboxList.map((state, idx) =>
        idx === index ? !state : state
      );
      updatedList[0] = false;
      if (updatedList.filter((state) => state).length === 0) {
        updatedList[0] = true;
      }
      setCheckboxList(updatedList);
    }
  }

  function radioChangeHandler(e) {
    const isValueRecent = e.target.value === "Recent";

    // on Fetch array is sorted in recent order, so just reverse it when filter <changes></changes>
    if ((isValueRecent && !isRecent) || (!isValueRecent && isRecent)) {
      setHistory((history) => history.reverse());
    }
    if (e.target.value == "Recent") {
      setIsRecent(true);
    } else {
      setIsRecent(false);
    }
  }
  return (
    <div className="w-full pt-12 pb-20 lg:px-20 md:px-16 sm:px-10">
      {isLoading && <Modal />}
      <ToastContainer
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      <div className="mb-5">
        <h1 className="mb-3 text-2xl font-bold text-slate-700">
          Search History
        </h1>
        {!history.length ? (
          <div className="flex flex-col items-center justify-center gap-4 mx-auto my-10">
            <img
              src={SearchIllustration}
              alt="add subscription"
              className="block w-80"
            />
            <p className="max-w-xl text-sm font-medium text-center text-slate-500">
              No videos found yet! Don't worry our watchman has an eye on your
              preference! If you want to edit your subscriptions, select below.
            </p>
            <Button
              type="button"
              onClick={() => navigate("../subscription")}
              primary
            >
              Your Subscriptions
            </Button>
          </div>
        ) : (
          <div>
            <p className="max-w-lg mb-2 text-sm text-slate-600">
              Lorem ipsum dolor sit amet, consectetur adipisicing elit.
              Voluptatem facere provident eveniet rem ab accusamus, totam
              laboriosam adipisci ea expedita lorem
            </p>
            <div className="pl-3 pr-6">
              <div className="flex items-center justify-between p-2 px-4 text-base border-b-2 border-b-slate-50">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  className="w-7 h-7 stroke-gray-400"
                >
                  <path
                    // stroke
                    ecap="round"
                    strokeLinejoin="round"
                    d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"
                  />
                </svg>
                <div className="flex items-center gap-3 text-sm text-slate-500">
                  <Paragraph>Filter By</Paragraph>
                  <Select
                    title={
                      (channelCheckbox[0] === true
                        ? ""
                        : `${
                            channelCheckbox.filter((state) => state).length
                          } `) + "Channel"
                    }
                  >
                    <SearchList
                      placeholder="search channels"
                      list={channelList}
                      searchProperty="name"
                    >
                      <Checkbox
                        name="Select All"
                        key="Select All"
                        handleOnChange={checkboxChangeHandler}
                        isChecked={channelCheckbox[0]}
                        index={0}
                        list={channelCheckbox}
                        setList={setChannelCheckbox}
                        border
                      />
                    </SearchList>
                  </Select>
                  <Select
                    title={
                      (tagCheckbox[0] === true
                        ? ""
                        : `${tagCheckbox.filter((state) => state).length} `) +
                      "Tag"
                    }
                  >
                    <SearchList
                      placeholder="search channels"
                      list={tagList}
                      searchProperty="name"
                    >
                      <Checkbox
                        name="Select All"
                        key="Select All"
                        handleOnChange={checkboxChangeHandler}
                        isChecked={tagCheckbox[0]}
                        index={0}
                        list={tagCheckbox}
                        setList={setTagCheckbox}
                        border
                      />
                    </SearchList>
                  </Select>
                  <Select title={isRecent ? "Recent" : "Oldest"}>
                    <div onChange={radioChangeHandler}>
                      <Radio
                        checked={isRecent}
                        name="time-radio"
                        value="Recent"
                      />
                      <Radio
                        checked={!isRecent}
                        name="time-radio"
                        value="Oldest"
                      />
                    </div>
                  </Select>
                </div>
              </div>
              <p className="p-1 my-5 text-red-400">
                {filteredHistory.length} Findings
              </p>
              <div className="space-y-4 text-xs">
                {filteredHistory.map((history) => (
                  <HistoryItem key={history.video_title} item={history} />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
