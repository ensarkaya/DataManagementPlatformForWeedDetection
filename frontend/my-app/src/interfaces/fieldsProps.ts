import { LatLngTuple } from "leaflet";

interface fieldProps {
  id: string | any;
  name: string;
  owner: string;
  location: LatLngTuple[];
  description: string;
}

interface fieldsProps {
  fieldList: fieldProps[];
  isAddingNewField: boolean;
}

interface FieldSelectorProps {
  visible: boolean;
  onClose: () => void;
  seasonId: number;
}
export type { fieldProps, fieldsProps, FieldSelectorProps };
