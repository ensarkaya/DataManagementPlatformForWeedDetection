// src/components/Login.tsx
import React from "react";
import { useDispatch } from "react-redux";
import { setCredentials } from "../../store/authSlice";
import { Form, Input, Button, message } from "antd";
import { useLoginUserMutation } from "../../store/userApi";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [loginUser, { isLoading }] = useLoginUserMutation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const onFinish = async (values: any) => {
    try {
      const data = await loginUser(values).unwrap();

      dispatch(
        setCredentials({
          token: data.token,
          username: data.username,
          userId: data.user_id,
        })
      );
      message.success("Login successful");
      // Redirect to the user's dashboard or home page
      navigate("/dashboard");
    } catch (err) {
      message.error("Login failed");
    }
  };

  return (
    <Form name="login" onFinish={onFinish}>
      <Form.Item
        name="username"
        rules={[{ required: true, message: "Please input your Username!" }]}
      >
        <Input placeholder="Username" />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: "Please input your Password!" }]}
      >
        <Input.Password placeholder="Password" />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" loading={isLoading}>
          Log in
        </Button>
        <Button
          type="primary"
          onClick={() => navigate("/")}
          loading={isLoading}
        >
          Go Back
        </Button>
      </Form.Item>
    </Form>
  );
};

export default Login;
