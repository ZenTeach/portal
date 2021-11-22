import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function fetchAppSetting () {
  return Api.get('/settings')
    .then(handleResponse).then(data => data)
}
