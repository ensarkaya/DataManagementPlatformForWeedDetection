const add_field = `api/add-field/`;
const my_fields = `api/my-fields/`;
const delete_field = `api/delete-field/`;
const update_field = `api/update-field/`;

const signup = `api/signup/`;
const login = `api/login/`;
const logout = `api/logout/`;
const user = `api/user/`;
const user_update = `api/user/update/`;
const user_delete = `api/user/delete/`;
const change_password = `api/change-password/`;

const create_season = `api/create-season/`;
const list_seasons = `api/list-seasons/`;
const update_season = `api/update-season/`;
const delete_season = `api/delete-season/`;
const get_season = `api/get-season/`;
const add_field_to_season = `api/add-field-to-season/`;
const remove_field_from_season = `api/remove-field-from-season/`;
const list_fields_in_season = `api/list-fields-in-season/`;
const add_image_to_field_season = `api/add-image-to-field-season/`;
const add_processing_result_to_field_image = `api/add-processing-result-to-field-image/`;

const create_uav_flight = `api/create-uav-flight/`;
const link_uav_flight_to_field_season = `api/link-uav-flight-to-field-season/`;
const get_uav_flights_for_field_season = `api/get-uav-flights-for-field-season/`;
const get_images_for_uav_flight = `api/get-images-for-uav-flight/`;
const get_uav_flights_by_owner = `api/get-uav-flights-by-owner/`;
const delete_uav_flight = `api/delete-uav-flight/`;

const start_analysis = `api/analysis-job/`;
const get_generated_images_for_uav_flight = `api/get-generated-images-for-uav-flight/`;
const uav_flights_with_completed_analysis = `api/uav-flights-with-completed-analysis/`;

export const tile_layer_url = process.env.TILE_LAYER_URL || 'http://10.154.6.34:8080/tile/{z}/{x}/{y}.png';
export {
  add_processing_result_to_field_image,
  add_image_to_field_season,
  remove_field_from_season,
  add_field_to_season,
  get_season,
  delete_season,
  update_season,
  list_seasons,
  create_season,
  list_fields_in_season,
};
export { update_field, delete_field, add_field, my_fields };
export {
  signup,
  login,
  logout,
  user,
  user_update,
  user_delete,
  change_password,
};
export {
  create_uav_flight,
  link_uav_flight_to_field_season,
  get_uav_flights_for_field_season,
  get_images_for_uav_flight,
  get_uav_flights_by_owner,
  delete_uav_flight,
};

export { start_analysis, get_generated_images_for_uav_flight, uav_flights_with_completed_analysis };
