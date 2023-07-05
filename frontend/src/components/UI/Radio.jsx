import React from "react";

export default function Radio(props) {
  return (
    <div className="flex items-center p-2 rounded-md hover:bg-gray-100 text-slate-700">
      <input
        type="radio"
        id={"radio-" + props.value}
        value={props.value}
        name={props.name}
        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 "
        defaultChecked={props.checked}
      />
      <label
        htmlFor={"radio-" + props.value}
        className="ml-2 text-sm font-medium "
      >
        {props.value}
      </label>
    </div>
  );
}
