import React, { useEffect, useState } from "react";
import { Modal, List, Card, Button, message } from "antd";
import { useGetMyFieldsQuery } from "../../store/fieldsApi";
import { useAppSelector } from "../../store/hooks";
import {
  FieldSelectorProps,
  fieldProps,
  fieldsProps,
} from "../../interfaces/fieldsProps";
import {
  useAddFieldsToSeasonMutation,
  useListFieldsInSeasonQuery,
} from "../../store/seasonsApi";

const FieldSelector: React.FC<FieldSelectorProps> = ({
  visible,
  onClose,
  seasonId,
}) => {
  const auth = useAppSelector((state) => state.auth);
  const [addFields] = useAddFieldsToSeasonMutation();
  const { data: listFieldsInSeason, isFetching: isFetchingSeason } =
    useListFieldsInSeasonQuery(seasonId);

  const { data: fields, isLoading: isLoadingFields } = useGetMyFieldsQuery({
    user_id: auth.userId,
  });

  const uniqueFields =
    fields?.filter(
      (field: { id: any }) =>
        !listFieldsInSeason?.some(
          (inSeasonField: { id: any }) => inSeasonField.id === field.id
        )
    ) || [];

  const [selectedFields, setSelectedFields] = useState<any[]>([]);

  const handleFieldSelect = (fieldId: any) => {
    if (selectedFields.includes(fieldId)) {
      setSelectedFields(selectedFields.filter((id) => id !== fieldId));
    } else {
      setSelectedFields([...selectedFields, fieldId]);
    }
  };

  const handleAddFields = async () => {
    try {
      await addFields({
        season_id: seasonId,
        field_ids: selectedFields,
      });
      message.success("Fields added to season successfully");
      onClose();
      setSelectedFields([]);
    } catch (error) {
      message.error("Error adding fields to season");
    }
  };

  return (
    <Modal
      visible={visible}
      title="Select Fields"
      onCancel={onClose}
      footer={[
        <Button key="cancel" onClick={onClose}>
          Cancel
        </Button>,
        <Button key="add" type="primary" onClick={handleAddFields}>
          Add to Season
        </Button>,
      ]}
    >
      <List
        grid={{ gutter: 16, column: 4 }}
        dataSource={uniqueFields}
        renderItem={(field: any) => (
          <List.Item>
            <Card
              title={field.name}
              style={{
                cursor: "pointer",
                border: selectedFields.includes(field.id)
                  ? "2px solid blue"
                  : "1px solid #f0f0f0",
              }}
              onClick={() => handleFieldSelect(field.id)}
            >
              <p>{field.description}</p>
              {/* Add more field details here */}
            </Card>
          </List.Item>
        )}
      />
    </Modal>
  );
};

export default FieldSelector;
