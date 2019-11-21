import Api from "@/service/Api"

export async function loginUser(payload) {
  const result = await Api.post(
    "http://localhost:5001/api/v1/teacher/login",
    payload
  );
  if (result.status === 200) {
    return result.data;
  }
  return result;
}

export async function logoutUser() {
  const result = await Api.post("http://localhost:5001/api/v1/teacher/logout");

  return result;
}

export async function registerUser(payload) {
  const result = await Api.post(
    "http://localhost:5001/api/v1/teacher/registration",
    payload
  );

  if (result.status === 200) {
    return result.data;
  }

  return result;
}

export async function getCurrentUser() {
  const result = await Api.get("http://localhost:5001/api/v1/teacher/current");

  // if (result.status === 200) {
  //   return result.data;
  // }

  return result;
}
