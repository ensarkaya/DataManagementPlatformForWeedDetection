import React from "react";
import { Dropdown, Layout, Menu, message } from "antd";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAppSelector } from "../store/hooks";
import { useLogoutUserMutation } from "../store/userApi";
import { UserOutlined } from "@ant-design/icons";

const { Header } = Layout;

const TopNavBar = () => {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [logoutUser] = useLogoutUserMutation();
  const authToken = useAppSelector((state) => state.auth.token);

  const handleLogout = () => {
    logoutUser(authToken)
      .unwrap()
      .then(() => {
        message.success("Logout successful");
        navigate("/");
      })
      .catch(() => {
        message.error("Logout failed");
      });
  };

  const userMenuProps = {
    items: [
      {
        key: "0",
        label: <Link to="/profile">Profile</Link>,
      },
      {
        key: "1",
        label: <a onClick={handleLogout}>Logout</a>,
      },
    ],
  };

  return (
    <Header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <div className="logo" />
      <Menu
        theme="dark"
        mode="horizontal"
        defaultSelectedKeys={["1"]}
        style={{ flex: 1 }}
      >
        <Menu.Item key="1">
          <Link to="/fields/list" state={{ from: pathname }}>
            Fields
          </Link>
        </Menu.Item>
        <Menu.Item key="2">
          <Link to="/seasons/list" state={{ from: pathname }}>
            Seasons
          </Link>
        </Menu.Item>
        <Menu.Item key="3">
          <Link to="/uav_flights/list" state={{ from: pathname }}>
            UAV Flights
          </Link>
        </Menu.Item>
      </Menu>
      <Dropdown menu={userMenuProps} trigger={["click"]}>
        <a className="ant-dropdown-link" onClick={(e) => e.preventDefault()}>
          <UserOutlined style={{ fontSize: "20px", color: "#fff" }} />
        </a>
      </Dropdown>
    </Header>
  );
};

export default TopNavBar;
