import React from "react";
import { Layout } from "antd";
import TopNavBar from "./TopNavBar";
import SideBar from "./SideBar";
import { Routes, Route } from "react-router-dom";
import FieldsPage from "../pages/fields/FieldsPage";
import SeasonsPage from "../pages/seasons/SeasonsPage";
import { Content } from "antd/es/layout/layout";
import { useAppSelector } from "../store/hooks";
import CreateSeason from "./seasons/CreateSeason";
import ListSeasons from "./seasons/ListSeasons";
import CreateUAVFlight from "./uav_flight/CreateUAVFlight";
import ListUAVFlights from "./uav_flight/ListUAVFlights";
import UserProfile from "./auth/UserProfile";
import AddFieldComponent from "./fields/AddFieldComponent";
import UpdateFieldComponent from "./fields/UpdateFieldComponent";
import ListFieldsComponent from "./fields/ListFieldsComponent";
import UpdateSeason from "./seasons/UpdateSeason";
import AIAnalysisPage from "./uav_flight/AIAnalysis";

const Dashboard = () => {
  const isAuthenticated = useAppSelector((state) => state.auth.token) !== null;

  if (!isAuthenticated) {
    return null; // Or a fallback component
  }

  return (
    <Layout>
      <TopNavBar />
      <Layout>
        <SideBar />
        <Content>
          <Routes>
            <Route path="/fields" element={<FieldsPage />} />
            <Route path="/fields/add" element={<AddFieldComponent />} />
            <Route path="/fields/update" element={<UpdateFieldComponent />} />
            <Route path="/fields/list" element={<ListFieldsComponent />} />
            <Route path="/seasons" element={<SeasonsPage />} />
            <Route path="/seasons/create" element={<CreateSeason />} />
            <Route path="/seasons/list" element={<ListSeasons />} />
            <Route path="/seasons/update" element={<UpdateSeason />} />
            <Route path="/uav_flights" element={<div>UAV Flights</div>} />
            <Route
              path="/uav_flights/create"
              element={<CreateUAVFlight></CreateUAVFlight>}
            />
            <Route
              path="/uav_flights/list"
              element={<ListUAVFlights></ListUAVFlights>}
            />
            <Route
              path="/uav_flights/analysis"
              element={<AIAnalysisPage></AIAnalysisPage>}
            />

            <Route path="/profile" element={<UserProfile></UserProfile>} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default Dashboard;
