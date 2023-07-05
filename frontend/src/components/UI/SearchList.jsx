import React, { useState } from "react";

import { AiOutlineSearch } from "react-icons/ai";

// provide list of componets to render, searchProperty, wrap components which are default in list
export default function SearchList({
  placeholder,
  searchProperty,
  list,
  ...props
}) {
  const [inputText, setInputText] = useState("");
  const filteredList = list.filter(
    (item) =>
      inputText.length === 0 ||
      item.props[searchProperty].toLowerCase().includes(inputText)
  );

  function inputChangeHandler(e) {
    setInputText(e.target.value);
  }

  return (
    <div>
      <div className="p-3">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <AiOutlineSearch className="w-4 h-4" />
          </div>
          <input
            type="text"
            id="input-group-search"
            className="outline-none bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:border-sky-500 focus:ring-1 focus:ring-sky-500 block w-full pl-10 p-2.5"
            placeholder={placeholder}
            onChange={inputChangeHandler}
            value={inputText}
          />
        </div>
      </div>
      <ul className="h-48 px-3 pb-3 overflow-y-auto text-sm text-gray-700 dark:text-gray-200">
        {props.children}
        {filteredList}
      </ul>
    </div>
  );
}
