// src/services/userApi.ts
import { createApi } from "@reduxjs/toolkit/query/react";
import reduxQueryHttpClient from "../api/httpClients/reduxQueryHttpClient";
import {
  signup,
  login,
  logout,
  user,
  user_update,
  user_delete,
  change_password,
} from "../api/endpoints/endpoints";

// Define a service using a base URL and expected endpoints
export const userApi = createApi({
  reducerPath: "userApi",
  baseQuery: reduxQueryHttpClient,
  endpoints: (builder) => ({
    loginUser: builder.mutation({
      query: (data) => ({
        url: login,
        method: "POST",
        body: data,
      }),
    }),
    registerUser: builder.mutation({
      query: (newUser) => ({
        url: signup,
        method: "POST",
        body: newUser,
      }),
    }),
    logoutUser: builder.mutation({
      query: (auth_token) => ({
        url: logout,
        method: "POST",
        body: { auth_token },
      }),
    }),
    fetchProfile: builder.query({
      query: () => ({
        url: user,
        method: "GET",
      }),
    }),
    updateProfile: builder.mutation({
      query: (updatedProfile) => ({
        url: user_update,
        method: "PUT",
        body: updatedProfile,
      }),
    }),
    deleteProfile: builder.mutation({
      query: () => ({
        url: user_delete,
        method: "DELETE",
      }),
    }),
    changePassword: builder.mutation({
      query: (newPassword) => ({
        url: change_password,
        method: "POST",
        body: newPassword,
      }),
    }),
  }),
});

export const {
  useLoginUserMutation,
  useRegisterUserMutation,
  useLogoutUserMutation,
  useDeleteProfileMutation,
  useFetchProfileQuery,
  useUpdateProfileMutation,
  useChangePasswordMutation,
} = userApi;
