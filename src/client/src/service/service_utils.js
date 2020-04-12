export function handleResponse (response) {
  const data = response.data
  if (!checkIfResponseIsOk(response.status)) {
    const error = (data && data.message) || response.statusText
    return Promise.reject(error)
  }

  return Promise.resolve(data)
}

function checkIfResponseIsOk (status) {
  return status > 199 && status < 300
}
