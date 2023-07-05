import React from "react";

export default function Paragraph(props) {
  return (
    <p
      className={`text-sm text-slate-400 ${props.className} ${
        props.width || "max-w-md"
      }`}
    >
      {props.children}
    </p>
  );
}
