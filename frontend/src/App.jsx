import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Route, Routes, Navigate } from "react-router-dom";
import { GoogleOAuthProvider } from '@react-oauth/google';

import { userActions } from "./store/user-store";
import {
  UnderConstruction,
  DashboardLayout,
  Dashboard,
  AddSubscription,
  EditSubscription,
  YourSubscription,
  History,
  Modal,
  Settings,
  NotFound,
  useHttp,
  Front,
  Login,
} from "./components/index";

function ProtectedRoute({ children }) {
  const user = useSelector((state) => state.user);
  if (user.isLoggedIn === null) {
    return <Modal />;
  }
  return user.isLoggedIn ? children : <Navigate to="/" />;
}

function Logout() {
  const user = useSelector((state) => state.user);
  const dispatch = useDispatch();
  const { requester } = useHttp();
  useEffect(() => {
    requester(
      {
        url: "/api/logout",
        body: {
          credentials: "include",
        },
      },
      () => {
        dispatch(userActions.logoutUser());
      }
    );
  }, []);

  if (user.isLoggedIn !== false) {
    return <Modal />;
  }
  return <Navigate to="/" />;
}

export default function App() {
  const { requester } = useHttp();
  const dispatch = useDispatch();

  useEffect(() => {
    requester(
      {
        url: "/api/profile",
        body: {
          credentials: "include",
          mode: "cors",
        },
      },
      (data) => {
        if (data.id) {
          dispatch(userActions.loginUser(data));
          return;
        }
        dispatch(userActions.logoutUser());
      }
    );
  }, []);
  return (
    <GoogleOAuthProvider clientId="218676759648-6q3mjmfrb8rd1vep2sk9d5m5d6rssgbp.apps.googleusercontent.com">
      <Routes>
        <Route index element={<Front />} />
        {/* <Route path="/" element={<Front />} /> */}
        <Route path="/login" element={<Login />} />
        <Route
          path="/user"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route index path="dashboard" element={<Dashboard />} />
          <Route path="subscription" element={<YourSubscription />} />
          <Route path="subscription/add" element={<AddSubscription />} />
          <Route path="subscription/edit" element={<EditSubscription />} />
          <Route path="history" element={<History />} />
          <Route path="playground" element={<UnderConstruction />} />
          <Route path="settings" element={<Settings />} />
          <Route path="logout" element={<Logout />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </GoogleOAuthProvider>
  );
}
