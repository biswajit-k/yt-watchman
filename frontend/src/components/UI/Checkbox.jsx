import React from "react";

export default function Checkbox(props) {
  return (
    <div
      className={`flex items-center p-2 hover:bg-gray-100 ${
        props.border && "border-b border-slate-200"
      }`}
    >
      <input
        onChange={() =>
          props.handleOnChange(props.index, props.list, props.setList)
        }
        type="checkbox"
        checked={props.isChecked}
        value={props.name}
        id={`checkbox-${props.name}`}
        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500focus:ring-2"
      />
      <label
        htmlFor={`checkbox-${props.name}`}
        className="w-full ml-2 text-sm font-medium text-gray-900 rounded dark:text-gray-300"
      >
        {props.name}
      </label>
    </div>
  );
}
