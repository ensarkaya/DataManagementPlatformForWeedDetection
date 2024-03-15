import React, { useState } from "react";
import { Button, message, Upload } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import { UploadChangeParam, UploadFile } from "antd/lib/upload";
import { useCreateUAVFlightMutation } from "../../store/flightsApi";

const UploadImages = ({
  fieldId,
  seasonId,
}: {
  fieldId: number;
  seasonId: number;
}) => {
  const [fileList, setFileList] = useState<UploadFile<any>[]>([]);
  const [createUAVFlight] = useCreateUAVFlightMutation();

  const handleFileInputChange = (info: UploadChangeParam<UploadFile<any>>) => {
    setFileList(info.fileList);
  };

  const handleUpload = () => {
    const formData = new FormData();
    fileList.forEach((file: UploadFile) => {
      if (file.originFileObj) {
        formData.append("images", file.originFileObj); // Changed to 'images' to match the backend expectation
      }
    });

    // Assuming backend expects flight_date and description for UAV flight creation
    // Modify these fields as per your actual API requirements
    formData.append("flight_date", new Date().toISOString());
    formData.append("description", "UAV flight description");

    createUAVFlight(formData)
      .unwrap()
      .then((response) => {
        message.success("UAV flight and images uploaded successfully");
        setFileList([]);
        // Here, handle linking UAV flight with field and season
        // You might need another API call or modify the createUAVFlight endpoint to handle this
      })
      .catch(() => {
        message.error("Upload failed");
      });
  };

  return (
    <>
      <Upload
        multiple
        onChange={handleFileInputChange}
        fileList={fileList}
        beforeUpload={() => false}
      >
        <Button
          icon={<UploadOutlined />}
          onClick={(e) => {
            e.stopPropagation();
          }}
        >
          Select Images
        </Button>
      </Upload>
      <Button
        type="primary"
        onClick={handleUpload}
        disabled={fileList.length === 0}
      >
        Upload
      </Button>
      {/* Display the selected file names */}
      {fileList.map((file, index) => (
        <div key={index}>{file.name}</div>
      ))}
    </>
  );
};

export default UploadImages;
