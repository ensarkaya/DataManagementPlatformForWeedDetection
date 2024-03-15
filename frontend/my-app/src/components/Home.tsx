import React from "react";
import { Button, Typography } from "antd";
import { useNavigate } from "react-router-dom";

const { Title, Paragraph } = Typography;

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <Title>Welcome to Our Application</Title>
      <Paragraph>
        Get started by signing in or creating a new account.
      </Paragraph>
      <Button
        type="primary"
        onClick={() => navigate("/login")}
        style={{ marginRight: "10px" }}
      >
        Login
      </Button>
      <Button onClick={() => navigate("/signup")}>Sign Up</Button>
    </div>
  );
};

export default HomePage;
