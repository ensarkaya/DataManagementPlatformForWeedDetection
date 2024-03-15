import React, { useState, useEffect } from "react";
import { Button, Card, Col, Input, Row, message } from "antd";
import {
  MapContainer,
  Polygon,
  TileLayer,
  Marker,
  useMapEvents,
  useMap,
} from "react-leaflet";
import { useNavigate, useLocation } from "react-router-dom";
import { useAppSelector } from "../../store/hooks";
import { fieldProps } from "../../interfaces/fieldsProps";
import { useUpdateFieldMutation } from "../../store/fieldsApi";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css";
import "leaflet-defaulticon-compatibility";
import { LatLng, LatLngTuple } from "leaflet";
import { wktToCoords, wktToLeafletCoords } from "../../utils/mapUtils";
import { tile_layer_url } from "../../api/endpoints/endpoints";
export interface updateFieldProps {
  id: string | any;
  name: string;
  owner: string;
  location: LatLng[];
  description: string;
}
const UpdateFieldComponent: React.FC = () => {
  const location = useLocation();
  const auth = useAppSelector((state) => state.auth);
  const navigate = useNavigate();

  const initialField = location.state?.field as any;
  const [selectedField, setSelectedField] = useState<fieldProps | null>(
    initialField || null
  );
  const [fieldName, setFieldName] = useState(initialField?.name || "");
  const [fieldDescription, setFieldDescription] = useState(
    initialField?.description || ""
  );
  const [isMapClicked, setIsMapClicked] = useState(false);
  const [markers, setMarkers] = useState<LatLng[]>([]);
  const [polygonPositions, setPolygonPositions] = useState<any>();
  const [updateField] = useUpdateFieldMutation();

  useEffect(() => {
    if (selectedField && selectedField.location) {
      setPolygonPositions(selectedField.location);
    }
  }, [selectedField]);

  const handleUpdateField = () => {
    if (selectedField === null) {
      message.error("No field selected");
      return;
    }
    if (fieldName === "") {
      message.error("Please enter a field name");
      return;
    }
    if (fieldDescription === "") {
      message.error("Please enter a field description");
      return;
    }

    const newField = {
      id: selectedField.id,
      name: fieldName,
      description: fieldDescription,
      location:
        markers.length > 2
          ? markers
          : wktToCoords(selectedField.location as any),
      owner: auth.userId,
    };

    updateField({ field: newField })
      .unwrap()
      .then((res) => {
        message.success("Field updated successfully");
        resetField();
        setSelectedField({} as fieldProps);
        navigate("/fields/list");
      })
      .catch((err) => {
        message.error("Error updating field");
      });
  };
  const handleCancelUpdate = () => {
    resetField();
    setSelectedField({} as fieldProps);
    navigate("/fields/list");
  };
  const resetField = () => {
    setMarkers([]);
    setFieldName("");
    setFieldDescription("");
  };

  const renderMarkers = markers.map((marker, index) => (
    <Marker position={marker} key={`marker-${index}`} />
  ));
  const MapEvents = () => {
    useMapEvents({
      click(e) {
        setMarkers([...markers, e.latlng]);
      },
    });
    return null;
  };
  return (
    <Row style={{ width: "100%", height: "100vh" }}>
      <Col span={6} style={{ padding: "10px", marginTop: "10px" }}>
        <Card>
          <div>
            <div style={{ marginBottom: "10px" }}>
              <Input
                placeholder="Field Name"
                defaultValue={selectedField?.name ?? ""}
                value={fieldName}
                onChange={(e) => setFieldName(e.target.value)}
                style={{ width: 200, marginRight: 10 }}
              />
              <Input
                placeholder="Field Description"
                defaultValue={selectedField?.description ?? ""}
                value={fieldDescription}
                onChange={(e) => setFieldDescription(e.target.value)}
                style={{ width: 200 }}
              />
            </div>
            <div>
              <Button onClick={handleCancelUpdate}>Cancel</Button>
              <Button
                onClick={handleUpdateField}
                style={{ marginLeft: "10px" }}
              >
                Save Field
              </Button>
            </div>
          </div>
        </Card>
      </Col>
      <Col span={18} style={{ padding: "10px", marginLeft: "-10px" }}>
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
            key={"addFieldsMap"}
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
                  initialField
                    ? [
                        wktToLeafletCoords(initialField.location)[0][0],
                        wktToLeafletCoords(initialField.location)[0][1],
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

                <div style={{ height: "50vh", width: "70%" }}>
                  <MapEvents />
                  {renderMarkers}
                  {markers.length >= 3 && (
                    <Polygon
                      pathOptions={{ color: "red" }}
                      positions={markers}
                    />
                  )}
                </div>
                {polygonPositions && markers.length < 1 && (
                  <Polygon
                    pathOptions={{ color: "blue" }}
                    positions={wktToLeafletCoords(polygonPositions as any)}
                  />
                )}
              </MapContainer>
            </div>
          </Card>
        </div>
      </Col>
    </Row>
  );
};

export default UpdateFieldComponent;
