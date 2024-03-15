import React, { useState, useEffect } from "react";
import { Card, Tooltip, message, Modal, Pagination } from "antd";
import { MapContainer, Polygon, TileLayer, useMap } from "react-leaflet";
import { useAppSelector } from "../../store/hooks";
import {
  useDeleteFieldMutation,
  useGetMyFieldsQuery,
} from "../../store/fieldsApi";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css";
import "leaflet-defaulticon-compatibility";
import { fieldProps } from "../../interfaces/fieldsProps";
import {
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { wktToLeafletCoords } from "../../utils/mapUtils";
import { tile_layer_url } from "../../api/endpoints/endpoints";
const { confirm } = Modal;
const pageSize = 3;

const ListFieldsComponent: React.FC = () => {
  const auth = useAppSelector((state) => state.auth);
  const [deleteField] = useDeleteFieldMutation();
  const navigate = useNavigate();

  const [currentPage, setCurrentPage] = useState(1);
  const [selectedField, setSelectedField] = useState({} as fieldProps);

  const { data: fields, isLoading } = useGetMyFieldsQuery({
    user_id: auth.userId,
  });

  useEffect(() => {
    if (fields && fields.length > 0) {
      // Optionally set an initial field as selected
      setSelectedField(fields[0]);
    }
  }, [fields]);

  if (isLoading) return <p>Loading...</p>;

  const indexOfLastField = currentPage * pageSize;
  const indexOfFirstField = indexOfLastField - pageSize;
  const currentFields = fields.slice(indexOfFirstField, indexOfLastField);

  const onPaginationChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleFieldSelect = (field: fieldProps) => {
    if (field.id === selectedField.id) {
      setSelectedField({} as fieldProps);
      return;
    }
    setSelectedField(field);
  };

  const handleEditField = (field: any) => {
    navigate("/fields/update", { state: { field: field } });
  };
  const handleAddField = () => {
    navigate("/fields/add");
  };

  const handleDeleteField = () => {
    confirm({
      title: "Do you want to delete this field?",
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        try {
          await deleteField(selectedField.id).unwrap();
          message.success("Field deleted successfully");
          setSelectedField({} as fieldProps);
        } catch (err) {
          message.error("Error deleting field");
        }
      },
    });
  };
  const MapEffect = ({ selectedField }: { selectedField: any }) => {
    const map = useMap();

    useEffect(() => {
      if (selectedField?.location) {
        const edgeCoordList = wktToLeafletCoords(selectedField.location);
        const coord = edgeCoordList[0];
        map.setView([coord[0], coord[1]], map.getZoom());
      }
    }, [selectedField, map]);

    return null;
  };
  return (
    <div style={{ display: "flex", width: "100%" }}>
      <div style={{ width: "30%", padding: "10px" }}>
        <Card
          style={{
            borderStyle: "dashed",
            cursor: "pointer",
            marginBottom: "10px",
          }}
          onClick={handleAddField}
          bodyStyle={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <PlusOutlined key={"add"} onClick={() => handleAddField()} />
          Add Field
        </Card>

        {currentFields.map((field: fieldProps) => (
          <Card
            key={field.id}
            style={{
              marginBottom: "10px",
              cursor: "pointer",
              border:
                field.id === selectedField?.id
                  ? "2px solid blue"
                  : "1px solid #f0f0f0",
            }}
            onClick={() => handleFieldSelect(field)}
            title={"Name: " + field.name}
            actions={[
              <EditOutlined
                key="edit"
                onClick={() => handleEditField(field)}
                style={{ fontSize: "20px" }}
              />,
              <DeleteOutlined
                key="delete"
                onClick={() => handleDeleteField()}
                style={{ fontSize: "20px" }}
              />,
            ]}
          >
            <div style={{ padding: "10px" }}>
              {" "}
              {field.id === selectedField?.id && (
                <div style={{ marginTop: "5px", color: "#666" }}>
                  Description: {field.description}
                </div>
              )}
            </div>
          </Card>
        ))}
        <Pagination
          current={currentPage}
          onChange={onPaginationChange}
          total={fields.length}
          pageSize={pageSize}
          hideOnSinglePage
        />
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
                fields[0]
                  ? [
                      wktToLeafletCoords(fields[0].location)[0][0],
                      wktToLeafletCoords(fields[0].location)[0][1],
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
              {fields?.map((field: any) => (
                <Polygon
                  key={field.id}
                  pathOptions={
                    field.id === selectedField?.id
                      ? { color: "blue" }
                      : { color: "green" }
                  }
                  positions={wktToLeafletCoords(field.location)}
                >
                  <Tooltip> {field.name} </Tooltip>
                </Polygon>
              ))}
              <MapEffect selectedField={selectedField} />
            </MapContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ListFieldsComponent;
