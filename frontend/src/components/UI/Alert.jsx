import React from "react";
import { Button } from "../index";

export default function Alert(props) {
  return (
    <div className="overflow-hidden bg-white rounded-sm">
      <div className="p-4 text-sm font-semibold tracking-wider uppercase bg-gray-100 text-slate-600">
        {props.title}
      </div>
      <div className="p-4">
        <div className="max-w-md mb-8 text-sm text-slate-500">{props.desc}</div>
        <div className="flex justify-end gap-4">
          <Button small onClick={props.onCancel}>
            Cancel
          </Button>
          <Button onClick={props.onPrimary} small primary>
            {props.button}
          </Button>
        </div>
      </div>
    </div>
  );
}
