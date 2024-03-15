import { configureStore } from "@reduxjs/toolkit";
import { fieldsApi } from "./fieldsApi";
import fieldsReducer from "./fieldsSlice";
import authReducer from "./authSlice";
import { userApi } from "./userApi";
import { tokenMiddleware } from "./tokenMiddleware";
import { seasonsApi } from "./seasonsApi";
import { flightsApi } from "./flightsApi";
import { aiAnalysisApi } from "./aiAnalysisApi";

const store = configureStore({
  reducer: {
    auth: authReducer,
    fieldStates: fieldsReducer,
    [fieldsApi.reducerPath]: fieldsApi.reducer,
    [userApi.reducerPath]: userApi.reducer,
    [seasonsApi.reducerPath]: seasonsApi.reducer,
    [flightsApi.reducerPath]: flightsApi.reducer,
    [aiAnalysisApi.reducerPath]: aiAnalysisApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(userApi.middleware)
      .concat(fieldsApi.middleware)
      .concat(seasonsApi.middleware)
      .concat(flightsApi.middleware)
      .concat(aiAnalysisApi.middleware)
      .concat(tokenMiddleware),
});

export default store;
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
