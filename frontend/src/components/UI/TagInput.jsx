import React, { useReducer } from "react";

const initInput = {
  tags: [],
  input: "",
  isReleased: true,
};

function inputReducer(state, action) {
  switch (action.type) {
    case "change":
      return { ...state, input: action.event.target.value };

    case "keydown":
      const { key } = action.event;
      const trimmedInput = state.input.trim();

      let newState = { ...state, isReleased: false };

      if (
        (key === "," || key === "Enter" || key === "Tab") &&
        trimmedInput.length &&
        !state.tags.includes(trimmedInput)
      ) {
        action.event.preventDefault();
        newState.tags = [...state.tags, trimmedInput];
        newState.input = "";
      } else if (
        key === "Backspace" &&
        !state.input.length &&
        state.tags.length &&
        state.isReleased
      ) {
        const tagsCopy = [...state.tags];
        const poppedTag = tagsCopy.pop();
        action.event.preventDefault();
        newState.tags = tagsCopy;
        newState.input = poppedTag;
      }

      return newState;

    case "keyup":
      return { ...state, isReleased: true };

    case "blur":
      let resultState = { ...state, isReleased: true };
      const trimInput = state.input.trim();

      if (trimInput.length) {
        resultState.tags.push(trimInput);
        resultState.input = "";
      }
      return resultState;

    case "delete":
      return {
        ...state,
        tags: state.tags.filter((tag, i) => i !== action.index),
      };

    default:
      break;
  }
}

export default function TagInput({ placeholder }) {
  const [inputState, dispatch] = useReducer(inputReducer, initInput);

  function changeHandler(e) {
    dispatch({ type: "change", event: e });
  }
  function keyDownHandler(e) {
    dispatch({ type: "keydown", event: e });
  }
  function keyUpHandler() {
    dispatch({ type: "keyup" });
  }
  function blurHandler() {
    dispatch({ type: "blur" });
  }
  const deleteTag = (index) => {
    dispatch({ type: "delete", index: index });
  };

  return (
    <div
      className={`flex flex-wrap ${
        !inputState.tags.length && "py-[.39rem]"
      } w-full max-w-full px-2 text-sm border rounded-md shadow-sm border-slate-300 placeholder-slate-400 focus-within:outline-none focus-within:border-sky-500 focus-within:ring-1 focus-within:ring-sky-500 invalid:border-pink-500 invalid:text-pink-600 focus-within:invalid:border-pink-500 focus-within:invalid:ring-pink-500`}
    >
      {inputState.tags.map((tag, index) => (
        <div
          key={tag}
          className="flex items-center gap-1 p-2 my-1 mr-2 text-xs font-medium rounded-md text-slate-400 bg-slate-100 whitespace-nowrap"
        >
          <div className="pr-2 ">{tag}</div>
          <div className="pr-1 cursor-pointer" onClick={() => deleteTag(index)}>
            x
          </div>
        </div>
      ))}
      <input
        className="min-w-[30%] focus:outline-none m-1"
        value={inputState.input}
        onChange={changeHandler}
        onKeyDown={keyDownHandler}
        onKeyUp={keyUpHandler}
        onBlur={blurHandler}
        placeholder={placeholder}
      />
    </div>
  );
}
