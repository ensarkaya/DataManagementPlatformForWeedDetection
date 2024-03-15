import { createApi } from "@reduxjs/toolkit/query/react";
import reduxQueryHttpClient from "../api/httpClients/reduxQueryHttpClient";
import {
  create_season,
  list_seasons,
  update_season,
  delete_season,
  add_field_to_season,
  remove_field_from_season,
  list_fields_in_season,
  add_image_to_field_season,
  add_processing_result_to_field_image,
} from "../api/endpoints/endpoints";

// Define a service using a base URL and expected endpoints
export const seasonsApi = createApi({
  reducerPath: "seasonsApi",
  baseQuery: reduxQueryHttpClient,
  tagTypes: ["Season"],
  endpoints: (builder) => ({
    createSeason: builder.mutation({
      query: (data) => ({
        url: create_season,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
    listSeasons: builder.query({
      query: (user_id) => ({
        url: list_seasons,
        method: "GET",
        params: user_id,
      }),
      providesTags: [{ type: "Season", id: "LIST" }],
    }),
    updateSeason: builder.mutation({
      query: (data) => ({
        url: update_season,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
    deleteSeason: builder.mutation({
      query: (season_id) => ({
        url: delete_season,
        method: "DELETE",
        body: { season_id },
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
    addFieldsToSeason: builder.mutation({
      query: (data) => ({
        url: add_field_to_season,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
    removeFieldFromSeason: builder.mutation({
      query: (data) => ({
        url: remove_field_from_season,
        method: "DELETE",
        body: data,
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
    listFieldsInSeason: builder.query({
      query: (season_id) => ({
        url: list_fields_in_season,
        method: "GET",
        params: { season_id },
      }),
      providesTags: [{ type: "Season", id: "LIST" }],
    }),
    addImagesToFieldSeason: builder.mutation({
      query: (data) => ({
        url: add_image_to_field_season,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
    addProcessingResultToFieldImage: builder.mutation({
      query: (data) => ({
        url: add_processing_result_to_field_image,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Season", id: "LIST" }],
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  useCreateSeasonMutation,
  useListSeasonsQuery,
  useUpdateSeasonMutation,
  useDeleteSeasonMutation,
  useAddFieldsToSeasonMutation,
  useRemoveFieldFromSeasonMutation,
  useListFieldsInSeasonQuery,
  useAddImagesToFieldSeasonMutation,
  useAddProcessingResultToFieldImageMutation,
} = seasonsApi;
