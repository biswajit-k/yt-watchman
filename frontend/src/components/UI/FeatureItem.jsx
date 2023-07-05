import React from "react";
import { Paragraph } from "../index";

export default function FeatureItem({ title, image, ...props }) {
  return (
    <div className="flex flex-col items-center gap-3 text-center drop-shadow-sm">
      <img src={image} className="block mb-3 w-36 h-36 " alt={title} />
      <h3 className="font-semibold capitalize">{title}</h3>
      <Paragraph width="max-w-xs">{props.children}</Paragraph>
    </div>
  );
}
