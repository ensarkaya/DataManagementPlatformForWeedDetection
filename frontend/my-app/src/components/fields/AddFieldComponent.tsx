import React, { useState } from "react";
import { Button, Card, Col, Input, Row, message } from "antd";
import {
  MapContainer,
  Marker,
  Polygon,
  TileLayer,
  useMapEvents,
} from "react-leaflet";
import { useAppSelector, useAppDispatch } from "../../store/hooks";
import { useAddFieldMutation } from "../../store/fieldsApi";
import { setAddingNewField } from "../../store/fieldsSlice";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css";
import "leaflet-defaulticon-compatibility";
import { useNavigate } from "react-router-dom";
import { tile_layer_url } from "../../api/endpoints/endpoints";

const AddFieldComponent: React.FC = () => {
  const auth = useAppSelector((state) => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [fieldName, setFieldName] = useState("");
  const [fieldDescription, setFieldDescription] = useState("");
  const [markers, setMarkers] = useState<L.LatLng[]>([]);
  const [addField] = useAddFieldMutation();

  const resetField = () => {
    setMarkers([]);
    setFieldName("");
    setFieldDescription("");
    dispatch(setAddingNewField(false));
  };

  const saveField = () => {
    // Add validation and field saving logic here
    if (markers.length < 3) {
      message.error("A field must have at least 3 points");
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
      name: fieldName,
      description: fieldDescription,
      location: markers,
      owner: auth.userId,
    };
    dispatch(setAddingNewField(false));
    addField({ field: newField })
      .unwrap()
      .then((res) => {
        message.success("Field saved successfully");
        resetField();
        navigate("/fields/list");
      })
      .catch((err) => {
        message.error("Error saving field");
      });
  };

  const MapEvents = () => {
    useMapEvents({
      click(e) {
        setMarkers([...markers, e.latlng]);
      },
    });
    return null;
  };

  const handleCancelUpdate = () => {
    resetField();
    navigate("/fields/list");
  };
  return (
    <Row style={{ width: "100%", height: "100vh" }}>
      <Col span={6} style={{ padding: "10px", marginTop: "10px" }}>
        <Card>
          <div>
            <Input
              placeholder="Field Name"
              value={fieldName}
              onChange={(e) => setFieldName(e.target.value)}
            />
            <Input
              placeholder="Field Description"
              value={fieldDescription}
              onChange={(e) => setFieldDescription(e.target.value)}
            />
          </div>
          <div style={{ marginTop: "10px" }}>
            <Button onClick={handleCancelUpdate}>Cancel</Button>

            <Button
              type="primary"
              onClick={saveField}
              style={{ marginLeft: "10px" }}
            >
              Save Field
            </Button>
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
                center={[48.864, 12.61601]}
                zoom={13.5}
                style={{ height: "100%", width: "100%" }}
              >
                <TileLayer
                        attribution='&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                        url= {tile_layer_url}
                />
                <MapEvents />
                {markers.map((marker, index) => (
                  <Marker position={marker} key={`marker-${index}`} />
                ))}
                {markers.length >= 3 && (
                  <Polygon pathOptions={{ color: "red" }} positions={markers} />
                )}
              </MapContainer>
            </div>
          </Card>
        </div>
      </Col>
    </Row>
  );
};

export default AddFieldComponent;
