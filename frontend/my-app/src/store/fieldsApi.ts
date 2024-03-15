import { createApi } from "@reduxjs/toolkit/query/react";
import {
  add_field,
  my_fields,
  update_field,
  delete_field,
} from "../api/endpoints/endpoints";
import reduxQueryHttpClient from "../api/httpClients/reduxQueryHttpClient";

export const fieldsApi = createApi({
  baseQuery: reduxQueryHttpClient,
  reducerPath: "fieldsApi",
  tagTypes: ["Field"],
  endpoints: (builder) => ({
    addField: builder.mutation({
      query: (data) => ({
        url: add_field,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Field", id: "LIST" }],
    }),
    getMyFields: builder.query({
      query: (user_id) => ({
        url: my_fields,
        method: "GET",
        params: user_id,
      }),
      providesTags: [{ type: "Field", id: "LIST" }],
    }),
    updateField: builder.mutation({
      query: (data) => ({
        url: update_field,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: [{ type: "Field", id: "LIST" }],
    }),
    deleteField: builder.mutation({
      query: (field_id) => ({
        url: delete_field,
        method: "DELETE",
        body: { field_id },
      }),
      invalidatesTags: [{ type: "Field", id: "LIST" }],
    }),
  }),
});

export const {
  useAddFieldMutation,
  useGetMyFieldsQuery,
  useUpdateFieldMutation,
  useDeleteFieldMutation,
} = fieldsApi;
