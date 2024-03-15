import { createApi } from "@reduxjs/toolkit/query/react";
import reduxQueryHttpClient from "../api/httpClients/reduxQueryHttpClient";
import {
  start_analysis,
  get_generated_images_for_uav_flight,
  uav_flights_with_completed_analysis,
} from "../api/endpoints/endpoints";

export const aiAnalysisApi = createApi({
  baseQuery: reduxQueryHttpClient,
  reducerPath: "aiAnalysisApi",
  tagTypes: ['AI Analysis', 'UAVFlight'],
  endpoints: (builder) => ({
    startAnalysis: builder.mutation({
      query: (data: any) => ({
        url: start_analysis,
        method: "POST",
        body: data,
      }),
      // Assume `data` includes `uav_flight_id` to specifically invalidate related tags
      invalidatesTags: (_result: any, _error: any, { uav_flight_id }: any) => [
        { type: 'AI Analysis', id: "LIST" },
        { type: 'UAVFlight', id: uav_flight_id }, // Invalidate specific UAV flight
      ],
    }),
    getGeneratedImagesForUAVFlight: builder.query({
      query: (uav_flight_id: any) => ({
        url: get_generated_images_for_uav_flight,
        method: "GET",
        params: { uav_flight_id },
      }),
      providesTags: (_result: any, _error: any, uav_flight_id: any) => [
        { type: 'UAVFlight', id: uav_flight_id }, // Tag with specific ID
      ],
    }),
    uavFlightsWithCompletedAnalysis: builder.query({
      query: () => ({
        url: uav_flights_with_completed_analysis,
        method: "GET",
      }),
      providesTags: [{ type: 'AI Analysis', id: "LIST" }],
    }),
  }),
});

export const {
    useGetGeneratedImagesForUAVFlightQuery,
    useStartAnalysisMutation,
    useUavFlightsWithCompletedAnalysisQuery,
} = aiAnalysisApi;