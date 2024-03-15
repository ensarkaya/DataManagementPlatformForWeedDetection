import React, { useState } from "react";
import { useCreateSeasonMutation } from "../../store/seasonsApi";
import { Form, Input, Button, DatePicker, message } from "antd";
import moment from "moment";
import { useNavigate } from "react-router-dom";

const CreateSeason = () => {
  const [createSeason] = useCreateSeasonMutation();
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const dateFormat = "YYYY/MM/DD";
  const onFinish = async (values: any) => {
    // Format dates to YYYY-MM-DD
    const formattedValues = {
      ...values,
      start_date: values.start_date.format("YYYY-MM-DD"),
      end_date: values.end_date.format("YYYY-MM-DD"),
    };
    // Check if start date is before end date
    if (
      moment(formattedValues.start_date).isAfter(
        moment(formattedValues.end_date)
      )
    ) {
      message.error("Start date must be before the end date");
      return;
    }
    try {
      await createSeason(formattedValues).unwrap();
      message.success("Season created successfully");
      form.resetFields();
      navigate("/seasons/list");
    } catch (error) {
      message.error("Error creating season");
    }
  };
  const onCancel = () => {
    navigate("/seasons/list");
  };

  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      <Form.Item name="name" label="Season Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item
        name="start_date"
        label="Start Date"
        rules={[{ required: true }]}
      >
        <DatePicker format={dateFormat} />
      </Form.Item>
      <Form.Item name="end_date" label="End Date" rules={[{ required: true }]}>
        <DatePicker format={dateFormat} />
      </Form.Item>
      <Form.Item name="description" label="Description">
        <Input.TextArea />
      </Form.Item>
      <Button onClick={onCancel} style={{ marginTop: "5px" }}>
        Cancel
      </Button>
      <Button
        type="primary"
        htmlType="submit"
        style={{ marginLeft: "5px", marginTop: "5px" }}
      >
        Create Season
      </Button>
    </Form>
  );
};

export default CreateSeason;
