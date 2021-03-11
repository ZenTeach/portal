export default {
  baseURL: `${process.env.VUE_APP_API_ENDPOINT}`,
  withCredentials: true,
  headers: {
    'Access-Control-Allow-Origin': `${process.env.VUE_CORS_API_ORIGIN}`,
    'X-Requested-With': 'XMLHttpRequest'
  }
}
