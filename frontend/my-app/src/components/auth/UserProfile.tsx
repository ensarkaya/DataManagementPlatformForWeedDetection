import React, { useEffect, useState } from "react";
import { Form, Input, Button, message, Modal } from "antd";
import {
  useFetchProfileQuery,
  useUpdateProfileMutation,
  useChangePasswordMutation,
} from "../../store/userApi";
import { useAppSelector } from "../../store/hooks";

const UserProfile = () => {
  const [form] = Form.useForm();
  const [isPasswordModalVisible, setIsPasswordModalVisible] = useState(false);
  const auth = useAppSelector((state) => state.auth);

  const { data: userProfile } = useFetchProfileQuery(auth.userId);
  const [updateUserProfile, { isLoading }] = useUpdateProfileMutation();
  const [updatePassword] = useChangePasswordMutation();

  useEffect(() => {
    form.setFieldsValue(userProfile);
  }, [userProfile, form]);

  const onFinishProfileUpdate = async (values: any) => {
    try {
      await updateUserProfile(values).unwrap();
      message.success("Profile updated successfully");
    } catch (err) {
      message.error("Profile update failed");
    }
  };

  const onFinishPasswordChange = async (values: any) => {
    try {
      await updatePassword(values).unwrap();
      message.success("Password changed successfully");
      setIsPasswordModalVisible(false);
    } catch (err) {
      message.error("Password change failed");
    }
  };

  const showPasswordModal = () => {
    setIsPasswordModalVisible(true);
  };

  const handleCancel = () => {
    setIsPasswordModalVisible(false);
  };

  return (
    <div>
      <Form form={form} name="userProfile" onFinish={onFinishProfileUpdate}>
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
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={isLoading}>
            Update Profile
          </Button>
          <Button type="default" onClick={showPasswordModal}>
            Change Password
          </Button>
        </Form.Item>
      </Form>

      <Modal
        title="Change Password"
        open={isPasswordModalVisible}
        onCancel={handleCancel}
        footer={null}
      >
        <Form name="passwordChange" onFinish={onFinishPasswordChange}>
          <Form.Item
            name="current_password"
            rules={[
              {
                required: true,
                message: "Please input your current password!",
              },
            ]}
          >
            <Input.Password placeholder="Current Password" />
          </Form.Item>
          <Form.Item
            name="new_password"
            rules={[
              { required: true, message: "Please input your new password!" },
            ]}
          >
            <Input.Password placeholder="New Password" />
          </Form.Item>
          <Form.Item
            name="confirm_new_password"
            dependencies={["new_password"]}
            rules={[
              { required: true, message: "Please confirm your new password!" },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("new_password") === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(
                    new Error(
                      "The two passwords that you entered do not match!"
                    )
                  );
                },
              }),
            ]}
          >
            <Input.Password placeholder="Confirm New Password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Change Password
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserProfile;
