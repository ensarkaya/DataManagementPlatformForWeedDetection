import {
  MiddlewareAPI,
  isRejectedWithValue,
  isFulfilled,
} from "@reduxjs/toolkit";
import { message } from "antd";
/**
 * Log a warning and show a toast!
 */
export const rtkQueryResponseHandler =
  (api: MiddlewareAPI) => (next: any) => (action: any) => {
    // RTK Query uses `createAsyncThunk` from redux-toolkit under the hood, so we're able to utilize these use matchers!
    if (isRejectedWithValue(action)) {
      message.error(action.payload.error);
    }
    if (isFulfilled(action)) {
      if (
        action.meta &&
        action.meta.arg.type &&
        action.meta.arg.type !== "query"
      ) {
        message.success(action.payload.message);
      }
    }

    return next(action);
  };
