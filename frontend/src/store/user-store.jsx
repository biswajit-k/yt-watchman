import { current, configureStore, createSlice } from "@reduxjs/toolkit";

const userSlice = createSlice({
  name: "user",

  initialState: {
    isLoggedIn: null,
    id: null,
    name: null,
    email: null,
    isGuest: null,
    availableRequest: null,
    hasToken: null,
  },

  reducers: {
    loginUser: (state, action) => {
      let newState = { isLoggedIn: true, ...action.payload };
      state.isLoggedIn = true;
      state.id = newState.id;
      state.name = newState.name;
      state.email = newState.email;
      state.isGuest = newState.is_guest;
      state.availableRequest = newState.available_request;
      state.hasToken = newState.has_token;
    },
    logoutUser: (state) => {
      return { isLoggedIn: false, ...userSlice.initialState };
    },
  },
});

export const userActions = userSlice.actions;

export const store = configureStore({
  reducer: { user: userSlice.reducer },
});
