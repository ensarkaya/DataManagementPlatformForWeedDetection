import React, { useState } from "react";
import { useCreateUAVFlightMutation } from "../../store/flightsApi";
import { Form, Input, Button, DatePicker, message, Upload } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import { UploadChangeParam, UploadFile } from "antd/lib/upload";
import { useNavigate } from "react-router-dom";

const CreateUAVFlight = () => {
  const [createUAVFlight, isLoading] = useCreateUAVFlightMutation();
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const [fileList, setFileList] = useState<UploadFile<any>[]>([]);
  const dateFormat = "YYYY/MM/DD";

  const handleFileInputChange = (info: UploadChangeParam<UploadFile<any>>) => {
    setFileList(info.fileList);
  };

  const onFinish = async (values: any) => {
    const formData = new FormData();
    fileList.forEach((file: UploadFile) => {
      if (file.originFileObj) {
        formData.append("images", file.originFileObj);
      }
    });

    formData.append("flight_date", values.flight_date.format("YYYY-MM-DD"));
    formData.append("description", values.description || "");

    try {
      await createUAVFlight(formData).unwrap();
      message.success("UAV flight and images uploaded successfully");
      form.resetFields();
      setFileList([]);
      navigate("/uav_flights/list");
    } catch (error) {
      message.error("Error creating UAV flight");
    }
  };

  const onCancel = () => {
    navigate("/uav_flights/list");
  };
  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      <Form.Item
        name="flight_date"
        label="Flight Date"
        rules={[{ required: true }]}
      >
        <DatePicker format={dateFormat} />
      </Form.Item>

      <Form.Item name="description" label="Description">
        <Input.TextArea />
      </Form.Item>
      <Upload
        multiple
        onChange={handleFileInputChange}
        fileList={fileList}
        beforeUpload={() => false}
        style={{ overflowY: 'auto', maxHeight: '200px' }}
      >
        <Button icon={<UploadOutlined />} style={{ marginBottom: "5px" }}>
          Select Images
        </Button>
      </Upload>


      <Button onClick={onCancel} style={{ marginTop: "5px" }}>
        Cancel
      </Button>
      <Button
        type="primary"
        htmlType="submit"
        loading={isLoading.isLoading}
        disabled={isLoading.isLoading}
        style={{ marginLeft: "5px", marginTop: "5px" }}
      >
        Create UAV Flight
      </Button>
    </Form>
  );
};

export default CreateUAVFlight;
