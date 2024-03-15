import { createApi } from "@reduxjs/toolkit/query/react";
import reduxQueryHttpClient from "../api/httpClients/reduxQueryHttpClient";
import {
  create_uav_flight,
  link_uav_flight_to_field_season,
  get_uav_flights_for_field_season,
  get_images_for_uav_flight,
  get_uav_flights_by_owner,
  delete_uav_flight,
  start_analysis,
} from "../api/endpoints/endpoints";

export const flightsApi = createApi({
  baseQuery: reduxQueryHttpClient,
  reducerPath: "flightsApi",
  tagTypes: ["Flights"],
  endpoints: (builder) => ({
    createUAVFlight: builder.mutation({
      query: (data) => ({
        url: create_uav_flight,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Flights", id: "LIST" }],
    }),
    deleteUAVFlight: builder.mutation({
      query: (uav_flight_id) => ({
        url: delete_uav_flight,
        method: "DELETE",
        body: { uav_flight_id },
      }),
      invalidatesTags: [{ type: "Flights", id: "LIST" }],
    }),
    linkUAVFlightToFieldSeason: builder.mutation({
      query: (data) => ({
        url: link_uav_flight_to_field_season,
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Flights", id: "LIST" }],
    }),
    getUAVFlightsForFieldSeason: builder.query({
      query: (data) => ({
        url: get_uav_flights_for_field_season,
        method: "GET",
        params: data,
      }),
      providesTags: [{ type: "Flights", id: "LIST" }],
    }),
    getImagesForUAVFlight: builder.query({
      query: (data) => ({
        url: get_images_for_uav_flight,
        method: "GET",
        params: data,
      }),
      providesTags: [{ type: "Flights", id: "LIST" }],
    }),
    getUAVFlightsByOwner: builder.query({
      query: () => ({
        url: get_uav_flights_by_owner,
        method: "GET",
      }),
      providesTags: [{ type: "Flights", id: "LIST" }],
    }),
    startAnalysis: builder.mutation({
      query: (data) => ({
        url: start_analysis,
        method: "POST",
        body: data,
      }),
    }),
  }),
});

export const {
  useCreateUAVFlightMutation,
  useLinkUAVFlightToFieldSeasonMutation,
  useGetUAVFlightsForFieldSeasonQuery,
  useGetImagesForUAVFlightQuery,
  useGetUAVFlightsByOwnerQuery,
  useDeleteUAVFlightMutation,
  useStartAnalysisMutation,
} = flightsApi;
