import React from "react";
import { useField } from "formik";

export default function Input({ className, Button, textarea, ...props }) {
  const [field, meta] = useField(props);
  const inputClass =
    "block w-full px-3 py-2 text-sm bg-white border rounded-md shadow-sm border-slate-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500";
  const textAreaClass =
    "w-[29rem] p-2 text-sm rounded-md bg-slate-50 text-slate-500 focus:outline-none ring-1 ring-slate-200 focus:bg-white  min-h-[6rem]";
  const errClass =
    meta.error && meta.touched ? "!border-pink-500 !ring-pink-500" : "";

  return (
    <>
      <div className={className}>
        {textarea ? (
          <textarea
            className={`${textAreaClass} ${errClass}`}
            {...props}
            {...field}
          />
        ) : (
          <input
            {...props}
            {...field}
            className={`${inputClass} ${errClass}`}
          />
        )}

        {meta.error && meta.touched && (
          <div className="mt-1 ml-1 text-xs text-red-400">{meta.error}</div>
        )}
      </div>
    </>
  );
}
