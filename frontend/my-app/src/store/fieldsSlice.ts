import { createSlice } from "@reduxjs/toolkit";
import { fieldsProps } from "../interfaces/fieldsProps";

const initialState: fieldsProps = {
  fieldList: [],
  isAddingNewField: true,
};

const fieldsSlice = createSlice({
  name: "fieldStates",
  initialState: initialState,
  reducers: {
    //set settings project_name
    setFieldList: (state, action) => {
      state.fieldList = action.payload;
    },
    setAddingNewField: (state, action) => {
      state.isAddingNewField = action.payload;
    },
  },
});

export const { setFieldList, setAddingNewField } = fieldsSlice.actions;

export default fieldsSlice.reducer;
