export const getApiHost = () => process.env.FRONTEND_API_URL || 'http://10.154.6.34:8000';
export const addAuthHeaders = (headers: Headers, token: string | undefined) => {
  headers.set("Authorization", `Bearer ${token}`);
  headers.set("Content-Type", `application/json`);
};
