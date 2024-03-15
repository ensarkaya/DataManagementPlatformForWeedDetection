import React, { useState, useEffect } from "react";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css";
import "leaflet-defaulticon-compatibility";
import {
  MapContainer,
  TileLayer,
  Polygon,
  useMap,
  Marker,
} from "react-leaflet";
import { Button, Card, List, Modal, Space, message,Row, Tooltip } from "antd";
import { fieldProps } from "../../interfaces/fieldsProps";
import {
  useGetUAVFlightsByOwnerQuery,
  useGetUAVFlightsForFieldSeasonQuery,
  useLinkUAVFlightToFieldSeasonMutation,
} from "../../store/flightsApi";
import {
  useListFieldsInSeasonQuery,
  useRemoveFieldFromSeasonMutation,
} from "../../store/seasonsApi";
import { useAppSelector } from "../../store/hooks";
import {
  DeleteOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { wktToLeafletCoords } from "../../utils/mapUtils";
import { UAVFlightProps } from "../../interfaces/flightProps";
import { tile_layer_url } from "../../api/endpoints/endpoints";
import { useStartAnalysisMutation } from "../../store/aiAnalysisApi";
import {
  PlayCircleOutlined,
} from "@ant-design/icons";

const { confirm } = Modal;

const ViewFieldsInSeason = ({ seasonId, drawerVisible }: { seasonId: number, drawerVisible: boolean }) => {
  const [displayModal, setDisplayModal] = useState<boolean>(false);
  const [selectedField, setSelectedField] = useState<fieldProps>(
    {} as fieldProps
  );
  const [selectedUAVFlights, setSelectedUAVFlights] = useState<
    UAVFlightProps[]
  >([]);

  const auth = useAppSelector((state) => state.auth);
  const { data: uavFlights, isLoading:isLoadingUavFlights } = useGetUAVFlightsByOwnerQuery(
    auth.userId
  );
  const { data: fields, isFetching: isFetchingSeason } =
    useListFieldsInSeasonQuery(seasonId);
  const [removeFieldFromSeason] = useRemoveFieldFromSeasonMutation();
  const [linkUAVFlightToFieldSeason] = useLinkUAVFlightToFieldSeasonMutation();
  const { data: uavFlightsForSelectedField, isLoading: isLoadingFlights } =
    useGetUAVFlightsForFieldSeasonQuery({
      season_id: seasonId,
      field_id: selectedField.id,
    });
  const [runAnalysis, { isLoading, isError, error }] = useStartAnalysisMutation();
  const showModal = () => {
    setDisplayModal(true);
  };

  const handleCancel = () => {
    setDisplayModal(false);
  };

  const handleOk = () => {
    setDisplayModal(false);
  };

  const handleRemoveField = (field_id: any) => {
    confirm({
      title: "Do you want to delete this field?",
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        try {
          await removeFieldFromSeason({
            season_id: seasonId,
            field_id: field_id,
          }).unwrap();
          message.success("Field deleted successfully");
          setSelectedField({} as fieldProps);
        } catch (err) {
          message.error("Error deleting field");
        }
      },
    });
  };

  const HandleFieldSelect = (field: fieldProps) => {
    if (field.id === selectedField.id) {
      setSelectedField({} as fieldProps);
      return;
    }
    setSelectedField(field);
  };

  const MapEffect = ({ selectedField, drawerVisible }: { selectedField: any, drawerVisible: boolean }) => {
    const map = useMap();
    useEffect(() => {
      if (selectedField?.location) {
        const edgeCoordList = wktToLeafletCoords(selectedField.location);

        const coord = edgeCoordList[0];
        map.setView([coord[0], coord[1]], map.getZoom());
      }
    }, [selectedField, map]);

    useEffect(() => {
      if (drawerVisible) {
        // Adjust the timeout to ensure it runs after the drawer animation completes
        const timeoutId = setTimeout(() => {
          map.invalidateSize();
        }, 50);
  
        return () => clearTimeout(timeoutId);
      }
    }, [drawerVisible, map]);

    return null;
  };

  const handleAddUAVFlight = () => {
    linkUAVFlightToFieldSeason({
      season_id: seasonId,
      field_id: selectedField.id,
      uav_flight_ids: selectedUAVFlights.map((flight) => flight.id),
    })
      .unwrap()
      .then((res) => {
        message.success("UAV Flight added to field successfully");
        setSelectedUAVFlights([]);
        setDisplayModal(false);
      })
      .catch((err) => {
        message.error("Error adding UAV Flight to field");
      });
  };

  const isFlightSelected = (flightId: number): boolean => {
    return selectedUAVFlights.some((flight) => flight.id === flightId);
  };

  const handleFlightSelect = (flight: UAVFlightProps) => {
    if (isFlightSelected(flight.id)) {
      setSelectedUAVFlights(
        selectedUAVFlights.filter((f) => f.id !== flight.id)
      );
    } else {
      setSelectedUAVFlights([...selectedUAVFlights, flight]);
    }
  };

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
    <div style={{ display: "flex", width: "100%" }}>
      <div style={{ width: "30%", padding: "10px" }}>
        {fields?.map((field: fieldProps) => (
          <Card
            key={field.id}
            onClick={() => HandleFieldSelect(field)}
            style={{
              marginBottom: "10px",
              cursor: "pointer",
              border:
                field.id === selectedField?.id
                  ? "2px solid blue"
                  : "1px solid #f0f0f0",
            }}
            title={field.name}
            actions={[
              <Tooltip title="Add UAV Flights to this field">
                <PlusOutlined
                  key="add"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedField(field);
                    showModal();
                  }}
                  style={{ fontSize: "20px" }}
                />
              </Tooltip>
,
            <Tooltip title="Delete this field from season">

              <DeleteOutlined
                key="delete"
                onClick={() => {
                  handleRemoveField(field.id);
                }}
                style={{ fontSize: "20px" }}
              />
              </Tooltip>
              ,
            ]}
          >
            {field.id === selectedField?.id && (
              <>
                <List
                  size="small"
                  dataSource={uavFlightsForSelectedField?.uav_flights}
                  renderItem={(flight: UAVFlightProps) => (
                    <List.Item>
                      <Row>
                        <div>
                          {flight.flight_date ? flight.flight_date : ""}
                          <Tooltip title="Run analysis for this flight">
                            <PlayCircleOutlined
                              key={"all"}
                              onClick={() => handleRunAnalysisForAllImages(flight.id)}
                              style={{ fontSize: "20px" }}
                            />
                          </Tooltip>
                        </div>
                      </Row>
                    </List.Item>
                  )}
                />
              </>
            )}
          </Card>
        ))}
      </div>
      <div
        style={{
          height: "90vh",
          width: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "10px",
          marginTop: "-33px",
        }}
      >
        <Card
          key={"listFieldsMap"}
          style={{
            width: "90%",
            height: "80vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <MapContainer
              center={
                selectedField?.location
                  ? [
                      wktToLeafletCoords(
                        selectedField.location.toString()
                      )[0][0],
                      wktToLeafletCoords(
                        selectedField.location.toString()
                      )[0][1],
                    ]
                  : [48.864, 12.61601]
              }
              zoom={13.5}
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                      attribution='&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                      url= {tile_layer_url}
              />
              {fields &&
                fields.map((field: any) => (
                  <Polygon
                    key={field.id}
                    pathOptions={
                      field.id === selectedField?.id
                        ? { color: "blue" }
                        : { color: "green" }
                    }
                    positions={wktToLeafletCoords(field.location)}
                  >
                    <Tooltip >{field.name}</Tooltip>
                  </Polygon>
                ))}

              {uavFlightsForSelectedField &&
                selectedField?.id &&
                isLoadingFlights === false &&
                uavFlightsForSelectedField.uav_flights.map((flight: any) =>
                  flight.images.map((image: any) => (
                    <Marker
                      key={image.id}
                      position={[image.gps_latitude, image.gps_longitude]}
                    >
                      <Tooltip >{flight.flight_date}</Tooltip>
                    </Marker>
                  ))
                )}

              <MapEffect selectedField={selectedField} drawerVisible={drawerVisible} />

            </MapContainer>
          </div>
        </Card>
      </div>
      <div>
        <Modal
          open={displayModal}
          title="UAV Flights"
          onOk={handleOk}
          onCancel={handleCancel}
          width={1000}
          footer={[
            <Button key="back" onClick={handleCancel}>
              Cancel
            </Button>,
            <Button key="submit" type="primary" onClick={handleAddUAVFlight}>
              Add
            </Button>,
          ]}
        >
          <List
            grid={{ gutter: 16, column: 4 }}
            dataSource={uavFlights}
            renderItem={(flight: UAVFlightProps) => (
              <List.Item>
                <Card
                  title={`${flight.flight_date}`}
                  style={{
                    cursor: "pointer",
                    border: isFlightSelected(flight.id)
                      ? "2px solid blue"
                      : "1px solid #f0f0f0",
                  }}
                  onClick={() => handleFlightSelect(flight)}
                >
                  {isFlightSelected(flight.id) && (
                    <Space direction="vertical">
                      <Row>
                        <div>{flight.description ? flight.description : ""}</div>
                      </Row>
                    </Space>
                  )}
                </Card>
              </List.Item>
            )}
          />
        </Modal>
      </div>
    </div>
  );
};

export default ViewFieldsInSeason;
