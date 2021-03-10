export default {
  baseURL: `${process.env.VUE_APP_API_ENDPOINT}`,
  withCredentials: true,
  headers: {
    'Access-Control-Allow-Origin': 'SET_THIS_TO_SOME_SANE_VALUE',
    'X-Requested-With': 'XMLHttpRequest'
  }
}
