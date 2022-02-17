import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function fetchSubjects () {
  return Api.get('/subjects')
    .then(handleResponse)
    .then(data => data.subjects)
}

export function fetchActivities () {
  return Api.get('/activity_logs')
    .then(handleResponse)
    .then(data => data)
}
