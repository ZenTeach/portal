const baseURL = `${process.env.VUE_APP_API_ENDPOINT}`
const corsOrigin = `${process.env.VUE_APP_CORS_ORIGIN}`
export default {
  baseURL: baseURL,
  withCredentials: true,
  headers: {
    'Access-Control-Allow-Origin': corsOrigin,
    'X-Requested-With': 'XMLHttpRequest'
  }
}
