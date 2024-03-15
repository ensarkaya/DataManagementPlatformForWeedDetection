import { fetchBaseQuery } from "@reduxjs/toolkit/query";
import { getApiHost } from "./essentials";
import { RootState } from "../../store/store";

export default fetchBaseQuery({
  baseUrl: getApiHost(),
  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootState;
    const token = state.auth.token;
    if (token) {
      headers.set("Authorization", `Token ${token}`);
    }
    return headers;
  },
});
