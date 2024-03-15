// src/components/SignUp.tsx
import React from "react";
import { Form, Input, Button, message, Radio } from "antd";
import { useRegisterUserMutation } from "../../store/userApi";
import { useNavigate } from "react-router-dom";

const SignUp = () => {
  const [registerUser, { isLoading }] = useRegisterUserMutation();
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    try {
      await registerUser(values).unwrap();
      message.success("Registration successful");
      // Redirect or do additional tasks
      navigate("/");
    } catch (err) {
      message.error("Registration failed");
    }
  };

  return (
    <Form name="register" onFinish={onFinish} scrollToFirstError>
      <Form.Item
        name="username"
        rules={[{ required: true, message: "Please input your Username!" }]}
      >
        <Input placeholder="Username" />
      </Form.Item>

      <Form.Item
        name="email"
        rules={[
          {
            required: true,
            message: "Please input your Email!",
            type: "email",
          },
        ]}
      >
        <Input placeholder="Email" />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: "Please input your Password!" }]}
      >
        <Input.Password placeholder="Password" />
      </Form.Item>

      <Form.Item
        name="first_name"
        rules={[{ required: true, message: "Please input your First Name!" }]}
      >
        <Input placeholder="First Name" />
      </Form.Item>

      <Form.Item
        name="last_name"
        rules={[{ required: true, message: "Please input your Last Name!" }]}
      >
        <Input placeholder="Last Name" />
      </Form.Item>

      <Form.Item
        name="role"
        rules={[{ required: true, message: "Please select your Role!" }]}
      >
        <Radio.Group>
          <Radio value="farmer">Farmer</Radio>
          <Radio value="admin">Admin</Radio>
        </Radio.Group>
      </Form.Item>

      <Form.Item>
      <Button
          type="default"
          onClick={() => navigate("/")}
          loading={isLoading}
        >
          Go Back
        </Button>
        <Button type="primary" htmlType="submit" loading={isLoading}>
          Register
        </Button>
      </Form.Item>
    </Form>
  );
};

export default SignUp;
