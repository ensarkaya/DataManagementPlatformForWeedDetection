import React from "react";
import { Layout, Menu } from "antd";
import MapView from "./components/MapView";
import "./App.css";

const { Content } = Layout;

const MapPage: React.FC = () => {
  return (
    <Layout className="layout">
      <Content style={{ padding: "0 50px" }}>
        <div className="site-layout-content">
          <MapView />
        </div>
      </Content>
    </Layout>
  );
};

export default MapPage;
