import React from "react";
import { useField } from "formik";

function isAddable(trimmedTag, tagList, error, max) {
  const isAddable =
    trimmedTag.length &&
    !tagList.includes(trimmedTag) &&
    !error &&
    (!max || tagList.length < max);
  return isAddable;
}

export default function VTagInput({ min, max, fieldName, ...props }) {
  const [{ value, onBlur, ...field }, meta, { setValue, setTouched }] =
    useField(fieldName);
  // console.log(fieldName, meta.touched);

  function keyDownHandler(event) {
    const { key } = event;
    // if (fieldName === "tags") console.log(meta);
    let trimmedInput = event.target.value.trim();
    let newTags = [...value.tags];

    if (
      (key === "," || key === "Enter" || key === "Tab") &&
      isAddable(trimmedInput, value.tags, meta.error, max)
    ) {
      event.preventDefault();
      newTags.push(trimmedInput);
      setTouched(false);
      setValue({
        tags: newTags,
        input: "",
        isReleased: false,
      });
    } else if (
      key === "Backspace" &&
      !trimmedInput.length &&
      newTags.length > parseInt(min) &&
      value.isReleased
    ) {
      event.preventDefault();
      trimmedInput = newTags.pop();
      setValue({ tags: newTags, input: trimmedInput, isReleased: false });
    }
  }
  function keyUpHandler(event) {
    setValue({ ...value, isReleased: true });
  }
  function blurHandler(event) {
    onBlur(fieldName)(event); // onBlur('email') returns a function
    const trimmedInput = event.target.value.trim();
    if (isAddable(trimmedInput, value.tags, meta.error, max)) {
      let newTags = [...value.tags];
      newTags.push(trimmedInput);

      setValue({
        isReleased: true,
        input: "",
        tags: newTags,
      });
    }
  }
  function deleteTag(index) {
    setValue({ ...value, tags: value.tags.filter((tag, i) => i !== index) });
  }

  const errClass =
    meta.error && meta.touched ? "border-pink-500 ring-pink-500" : "";

  return (
    <div>
      <div
        className={`${errClass} flex flex-wrap ${
          !value.tags.length && "py-[.39rem]"
        } w-full max-w-full px-2 text-sm border rounded-md shadow-sm border-slate-300 placeholder-slate-400 focus-within:outline-none focus-within:border-sky-500 focus-within:ring-1 focus-within:ring-sky-500`}
      >
        {value.tags.map((tag, index) => (
          <div
            key={tag}
            className="flex items-center gap-1 p-2 my-1 mr-2 text-xs font-medium rounded-md text-slate-400 bg-slate-100 whitespace-nowrap"
          >
            <div className="pr-2 ">{tag}</div>
            {index + 1 > parseInt(min) && (
              <div
                className="pr-1 cursor-pointer"
                onClick={() => deleteTag(index)}
              >
                x
              </div>
            )}
          </div>
        ))}
        <input
          className="min-w-[40%] focus:outline-none m-1 text-slate-500"
          value={value.input}
          onKeyDown={keyDownHandler}
          onKeyUp={keyUpHandler}
          onBlur={blurHandler}
          {...field}
          {...props}
        />
      </div>
      {meta.error && meta.touched && (
        <div className="mt-1 ml-1 text-xs text-red-400">
          {meta.error.input || meta.error.tags}
        </div>
      )}
    </div>
  );
}
