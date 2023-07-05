import {
  AiOutlineDashboard,
  AiOutlineLogout,
  AiOutlineSetting,
  AiOutlineExperiment,
} from "react-icons/ai";
import { MdOutlineSubscriptions, MdOutlineHistory } from "react-icons/md";

export const links = [
  {
    title: "",
    items: [
      { icon: <AiOutlineDashboard />, name: "dashboard", to: "dashboard" },
    ],
  },
  {
    title: "activity",
    items: [
      {
        icon: <MdOutlineSubscriptions />,
        name: "subscription",
        to: "subscription",
      },
      { icon: <MdOutlineHistory />, name: "Search History", to: "history" },
      { icon: <AiOutlineExperiment />, name: "playground", to: "playground" },
    ],
  },
  {
    title: "account",
    items: [
      { icon: <AiOutlineSetting />, name: "settings", to: "settings" },
      { icon: <AiOutlineLogout />, name: "log out", to: "logout" },
    ],
  },
];
