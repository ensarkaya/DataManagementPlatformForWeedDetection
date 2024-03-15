import React, { useState } from "react";
import {
  useListSeasonsQuery,
  useDeleteSeasonMutation,
} from "../../store/seasonsApi";
import { List, Card, Button, message, Modal, Space, Drawer, Row } from "antd";
import { ExclamationCircleOutlined } from "@ant-design/icons";
import { useAppSelector } from "../../store/hooks";
import FieldSelector from "./FieldSelector";
import ViewFieldsInSeason from "./ViewFieldsInSeason";
import { EditOutlined, DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { SeasonProps } from "../../interfaces/seasonsProps";

const { confirm } = Modal;

const ListSeasons = () => {
  const auth = useAppSelector((state) => state.auth);

  const { data: seasons, isFetching } = useListSeasonsQuery({
    user_id: auth.userId,
  });
  const [deleteSeason] = useDeleteSeasonMutation();
  const navigate = useNavigate();

  const [selectedSeason, setSelectedSeason] = useState({} as SeasonProps);
  const [fieldSelectorVisible, setFieldSelectorVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);

  const pageSize = 6; // 2 rows x 3 columns

  const openFieldSelector = (season: SeasonProps) => {
    setFieldSelectorVisible(true);
  };

  const handleSeasonSelect = (season: SeasonProps) => {
    if (season.id === selectedSeason.id) {
      setSelectedSeason({} as SeasonProps);
    } else {
      setSelectedSeason(season);
    }
  };

  const handleDeleteSeason = (id: number) => {
    confirm({
      title: "Do you want to delete this season?",
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        try {
          await deleteSeason(id).unwrap();
          message.success("Season deleted successfully");
          setSelectedSeason({} as SeasonProps); // Reset selection
        } catch (error) {
          message.error("Error deleting season");
        }
      },
    });
  };

  const showDrawer = () => {
    setDrawerVisible(true);
  };

  const onCloseDrawer = () => {
    setDrawerVisible(false);
  };
  const handleUpdateSeason = (season: any) => {
    navigate("/seasons/update", { state: { season: season } });
  };
  const handleCreateSeason = () => {
    navigate("/seasons/create");
  };

  if (isFetching) return <p>Loading...</p>;

  const getDataSource = () => {
    return [
      { id: -1, special: true }, // Special entry for 'Create Season' card
      ...(seasons || []), // Include all seasons
    ];
  };

  return (
    <div>
      <div>
        <List
          grid={{ gutter: 16, column: 3 }}
          dataSource={getDataSource()}
          pagination={{
            pageSize: pageSize,
            position: "bottom",
          }}
          renderItem={(season: SeasonProps) =>
            season.id === -1 ? (
              <List.Item>
                <Card
                  style={{
                    borderStyle: "dashed",
                    cursor: "pointer",
                  }}
                  onClick={handleCreateSeason}
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
                    onClick={() => handleCreateSeason()}
                  />
                  Create Season
                </Card>
              </List.Item>
            ) : (
              <List.Item>
                <Card
                  title={season.name}
                  style={{
                    cursor: "pointer",
                    border:
                      season.id === selectedSeason.id
                        ? "2px solid blue"
                        : "1px solid #f0f0f0",
                  }}
                  onClick={() => handleSeasonSelect(season)}
                  actions={[
                    <EditOutlined
                      key="edit"
                      onClick={() => handleUpdateSeason(season)}
                      style={{ fontSize: "20px" }}
                    />,
                    <DeleteOutlined
                      key="delete"
                      onClick={() => handleDeleteSeason(season.id)}
                      style={{ fontSize: "20px" }}
                    />,
                  ]}
                >
                  {season.id === selectedSeason.id && (
                    <Space direction="vertical">
                      <div>Description: {season.description}</div>
                      <div>Start Date: {season.start_date}</div>
                      <div>End Date: {season.end_date}</div>
                      <Row>
                        <Button
                          type="primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            openFieldSelector(season);
                          }}
                          style={{ marginTop: "5px" }}
                        >
                          Add Fields
                        </Button>
                        <Button
                          type="primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            showDrawer();
                          }}
                          style={{ marginTop: "5px", marginLeft: "5px" }}
                        >
                          Show Fields
                        </Button>
                      </Row>
                    </Space>
                  )}
                </Card>
              </List.Item>
            )
          }
        />
        <FieldSelector
          visible={fieldSelectorVisible}
          onClose={() => setFieldSelectorVisible(false)}
          seasonId={selectedSeason.id}
        />
        <Drawer
          title="Fields in Season"
          placement="bottom"
          onClose={onCloseDrawer}
          open={drawerVisible}
          height={800}
          style={{ maxHeight: "100vh" }}
        >
          {drawerVisible && selectedSeason.id && (
            <ViewFieldsInSeason
              key={selectedSeason.id}
              seasonId={selectedSeason.id}
              drawerVisible={drawerVisible}
            />
          )}
        </Drawer>
      </div>
    </div>
  );
};

export default ListSeasons;
