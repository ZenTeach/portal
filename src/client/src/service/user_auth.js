import Api from "@/service/Api";

export async function loginUser(payload) {
  return Api.post("/teacher/login", payload)
    .then(handleResponse)
    .then(data => data);
}

export async function logoutUser() {
  const result = await Api.post("/teacher/logout");
  // console.log("logoutUser data", result)
  return result;
}

export async function registerUser(payload) {
  const result = await Api.post("/teacher/registration", payload);
  console.log("registerUser data", result);
  if (result.status === 200) {
    return result.data;
  }

  return result;
}

export async function getCurrentUser() {
  const result = await Api.get("/teacher/current");

  // if (result.status === 200) {
  //   return result.data;
  // }
  // console.log("getCurrentUser data", result)
  return result;
}

function handleResponse(response) {
  const data = response.data;
  if (!check_if_response_is_ok(response.status)) {
    const error = (data && data.message) || response.statusText;
    return Promise.reject(error);
  }

  return Promise.resolve(data);
}

function check_if_response_is_ok(status) {
  return status > 199 && status < 300;
}
