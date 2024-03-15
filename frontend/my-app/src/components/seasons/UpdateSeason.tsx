import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Button,
  Card,
  Col,
  Input,
  Row,
  message,
  DatePicker,
  Form,
  Space,
} from "antd";
import moment from "moment";
import { useAppSelector } from "../../store/hooks";
import { useUpdateSeasonMutation } from "../../store/seasonsApi";
import MyDatePicker from "../MyDatePicker";

interface SeasonProps {
  id: number;
  name: string;
  description: string;
  start_date: any;
  end_date: any;
}

const UpdateSeason: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const auth = useAppSelector((state) => state.auth);
  const initialSeason = location.state?.season as SeasonProps;
  const [form] = Form.useForm();
  const dateFormat = "YYYY/MM/DD";

  const [selectedSeason, setSelectedSeason] = useState<SeasonProps | null>(
    initialSeason || null
  );
  const [seasonName, setSeasonName] = useState(initialSeason?.name || "");
  const [seasonDescription, setSeasonDescription] = useState(
    initialSeason?.description || ""
  );
  const [startDate, setStartDate] = useState<any>(
    moment(initialSeason?.start_date)
  );
  const [endDate, setEndDate] = useState<any>(moment(initialSeason?.end_date));
  const [updateSeason] = useUpdateSeasonMutation();

  useEffect(() => {
    if (initialSeason) {
      setSelectedSeason(initialSeason);
    }
  }, [initialSeason]);

  const handleUpdateSeason = async (values: any) => {
    console.log("start date", startDate.format("YYYY-MM-DD"));
    console.log("end date", endDate.format("YYYY-MM-DD"));
    console.log("values", values);
    // Check if start date is before end date
    if (startDate.isAfter(endDate)) {
      message.error("Start date must be before the end date");
      return;
    }
    const payload = {
      season_id: selectedSeason?.id,
      name: seasonName,
      description: seasonDescription,
      start_date: startDate.format("YYYY-MM-DD"),
      end_date: endDate.format("YYYY-MM-DD"),
      ...values,
    };
    if (values.start_date) {
      payload.start_date = moment(values.start_date).format("YYYY-MM-DD");
    }
    if (values.end_date) {
      payload.end_date = moment(values.end_date).format("YYYY-MM-DD");
    }
    try {
      await updateSeason(payload).unwrap();
      message.success("Season updated successfully");
      navigate("/seasons/list");
    } catch (error) {
      message.error("Error updating season");
    }
  };

  const handleCancelUpdate = () => {
    navigate("/seasons/list");
  };

  return (
    <Row style={{ width: "100%", height: "100vh" }}>
      <Col span={24} style={{ padding: "10px" }}>
        <Card>
          <Form form={form} onFinish={handleUpdateSeason} layout="vertical">
            <Form.Item
              name="name"
              label="Season Name"
              initialValue={seasonName}
              rules={[{ required: true }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="start_date"
              label="Start Date"
              rules={[{ required: true }]}
              initialValue={startDate}
            >
              <MyDatePicker
                onChange={(value) => {
                  setStartDate(value);
                }}
                format={dateFormat}
              />
            </Form.Item>
            <Form.Item
              name="end_date"
              label="End Date"
              rules={[{ required: true }]}
              initialValue={endDate}
            >
              <MyDatePicker
                onChange={(value) => {
                  setEndDate(value);
                }}
                format={dateFormat}
              />
            </Form.Item>
            <Form.Item
              name="description"
              label="Description"
              initialValue={seasonDescription}
            >
              <Input.TextArea />
            </Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Save
              </Button>
              <Button onClick={handleCancelUpdate}>Cancel</Button>
            </Space>
          </Form>
        </Card>
      </Col>
    </Row>
  );
};

export default UpdateSeason;
