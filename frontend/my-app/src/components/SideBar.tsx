import React from "react";
import { Link } from "react-router-dom";
import { Layout, Menu } from "antd";

const { Sider } = Layout;

const SideBar = () => {
  return (
    <Sider width={200} className="site-layout-background">
      <Menu mode="inline" style={{ height: "100%", borderRight: 0 }}>
        <Menu.Item key="3">
          <Link to="/fields/list">Fields</Link>
        </Menu.Item>
        <Menu.Item key="7">
          <Link to="/seasons/list">Seasons</Link>
        </Menu.Item>
        <Menu.SubMenu key="sub3" title="UAV Flights">
          <Menu.Item key="9">
            <Link to="/uav_flights/list">List UAV Flights</Link>
          </Menu.Item>
          <Menu.Item key="10">
            <Link to="/uav_flights/analysis">AI Analysis</Link>
          </Menu.Item>
        </Menu.SubMenu>
      </Menu>
    </Sider>
  );
};

export default SideBar;
