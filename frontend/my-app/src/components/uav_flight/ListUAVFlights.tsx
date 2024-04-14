import React, { useState } from "react";
import {
  List,
  Card,
  Modal,
  Space,
  Image,
  message,
  Pagination,
  Row,
  Tooltip,
} from "antd";
import {
  useGetUAVFlightsByOwnerQuery,
  useDeleteUAVFlightMutation,
} from "../../store/flightsApi";
import { useStartAnalysisMutation } from "../../store/aiAnalysisApi";
import { useAppSelector } from "../../store/hooks";
import { useNavigate } from "react-router-dom";
import moment from "moment";
import {
  PlusOutlined,
  ExclamationCircleOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
} from "@ant-design/icons";
import { getApiHost } from "../../api/httpClients/essentials";
interface UAVFlightProps {
  id: number;
  flight_date: string;
  description: string;
  images: string[];
}

const { confirm } = Modal;

const ListUAVFlights = () => {
  const auth = useAppSelector((state) => state.auth);
  const navigate = useNavigate();
  const [deleteUAVFlight] = useDeleteUAVFlightMutation();
  const [runAnalysis, { isLoading, isError, error }] = useStartAnalysisMutation();
  const { data: uavFlights, isLoading:isLoadingUAVFlightsByOwner } = useGetUAVFlightsByOwnerQuery(
    auth.userId
  );
  const [selectedFlight, setSelectedFlight] = useState<UAVFlightProps | null>(
    null
  );
  const pageSize = 6; 
  const imagesPerPage = 3; 
  const [currentImagePage, setCurrentImagePage] = useState<number>(1);

  const handleImagePageChange = (page: number): void => {
    setCurrentImagePage(page);
  };

  // Function to get the images for the current page
  const getCurrentPageImages = (images: string[]): string[] => {
    const startIndex = (currentImagePage - 1) * imagesPerPage;
    return images.slice(startIndex, startIndex + imagesPerPage);
  };

  const handleFlightSelect = (flight: UAVFlightProps) => {
    if (!selectedFlight || flight.id !== selectedFlight.id) {
      setCurrentImagePage(1); // Reset the image pagination to page 1
    }
    setSelectedFlight(flight);
  };

  const handleCreateUAVFlight = () => {
    navigate("/uav_flights/create");
  };

  const handleDeleteUAVFlight = (id: number) => {
    confirm({
      title: "Do you want to delete this flight?",
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        try {
          await deleteUAVFlight(id).unwrap();
          message.success("Flight deleted successfully");
          setSelectedFlight({} as UAVFlightProps); // Reset selection
        } catch (error) {
          message.error("Error deleting flight");
        }
      },
    });
  };

  if (isLoadingUAVFlightsByOwner) return <p>Loading...</p>;

  const getDataSource = () => {
    return [
      { id: -1, special: true }, // Special entry for 'Create Season' card
      ...(uavFlights || []), // Include all seasons
    ];
  };

  function handleRunAnalysis(
    flight_id: number,
    image: any,
    index: number
  ): void {
    message.info(`Running analysis on image ${index}`);
    runAnalysis({ uav_flight_id: flight_id, image_id: image.id })
      .unwrap()
      .then((response:any) => {
        // Handle successful analysis start here
        // For example, navigate to the analysis page or show a success message
        message.success('Analysis started successfully.');
      })
      .catch((err:any) => {
        // err is an object that contains the error information
        // Display the error message from the server response
        message.error(err.data?.error || 'An unexpected error occurred.');
      });
  }
  
  function handleRunAnalysisForAllImages(flight_id: number): void {
    message.info(`Running analysis on all images for flight`);
    runAnalysis({ uav_flight_id: flight_id })
      .unwrap()
      .then((response:any) => {
        // Handle successful analysis start here
        message.success('Analysis for all images started successfully.');
      })
      .catch((err:any) => {
        // Display the error message from the server response
        message.error(err.data?.error || 'An unexpected error occurred.');
      });
  }
  

  return (
    <List
      grid={{ gutter: 16, column: 4 }}
      dataSource={getDataSource()}
      pagination={{
        pageSize: pageSize,
        position: "bottom",
      }}
      renderItem={(flight: UAVFlightProps) =>
        flight.id === -1 ? (
          <List.Item>
            <Card
              style={{
                borderStyle: "dashed",
                cursor: "pointer",
              }}
              onClick={handleCreateUAVFlight}
              bodyStyle={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                height: "100%",
                fontSize: "20px",
              }}
            >
              <PlusOutlined
                key="create"
                style={{ fontSize: "24px", marginBottom: "8px" }}
                onClick={() => handleCreateUAVFlight()}
              />
              Create UAV Flight
            </Card>
          </List.Item>
        ) : (
          <List.Item key={flight.id}>
            <Card
              title={`${moment(flight.flight_date).format("YYYY-MM-DD")}`}
              style={{
                cursor: "pointer",
                border:
                  flight.id === selectedFlight?.id
                    ? "2px solid blue"
                    : "1px solid #f0f0f0",
              }}
              onClick={() => handleFlightSelect(flight)}
              actions={[
                <DeleteOutlined
                  key="delete"
                  onClick={() => handleDeleteUAVFlight(flight.id)}
                  style={{ fontSize: "20px" }}
                />,
                <Tooltip title="Run analysis for this flight">
                  <PlayCircleOutlined
                    key={"all"}
                    onClick={() => handleRunAnalysisForAllImages(flight.id)}
                    style={{ fontSize: "20px" }}
                  />
                </Tooltip>,
              ]}
            >
              {flight.id === selectedFlight?.id && (
                <>
                  <Space direction="vertical">
                    <div>Description: {flight.description}</div>
                    {getCurrentPageImages(flight.images).map(
                      (image: any, index:number) => (
                        <Row>
                          <Image
                            key={index}
                            width={200}
                            src={`${getApiHost()}${image.resized_image}`}                            
                            alt={`Flight Image ${index}`}
                          />
                          <Tooltip title="Run analysis for this image">
                            <PlayCircleOutlined
                              key={index}
                              onClick={() =>
                                handleRunAnalysis(flight.id, image, index)
                              }
                              style={{ fontSize: "22px", marginLeft: "4px" }}
                            />
                          </Tooltip>
                        </Row>
                      )
                    )}
                  </Space>
                  <Pagination
                    simple
                    current={currentImagePage}
                    onChange={handleImagePageChange}
                    total={flight.images.length}
                    pageSize={imagesPerPage}
                    showSizeChanger={false}
                  />
                </>
              )}
            </Card>
          </List.Item>
        )
      }
    />
  );
};

export default ListUAVFlights;
