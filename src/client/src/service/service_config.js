export default {
  baseURL: `${process.env.VUE_APP_API_ENDPOINT}`,
  withCredentials: true,
  headers: {
    "Access-Control-Allow-Origin": "*",
    "X-Requested-With": "XMLHttpRequest"
  }
};
