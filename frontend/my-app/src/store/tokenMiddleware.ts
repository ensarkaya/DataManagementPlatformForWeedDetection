import { Middleware } from "@reduxjs/toolkit";

export const tokenMiddleware: Middleware = (store) => (next) => (action) => {
  if (action.type.endsWith("/fulfilled") && action.meta?.arg?.headers) {
    const token = store.getState().auth.token;
    console.log("tokenMiddleware: token", token);
    if (token) {
      action.meta.arg.headers["Authorization"] = `Token ${token}`;
    }
  }
  return next(action);
};
