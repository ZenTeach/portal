import axios from "axios";

export async function loginUser(payload) {
  const _api = window._vm.$http;
  const result = await _api.post(
    "http://localhost:5001/api/v1/teacher/login",
    payload
  );
  if (result.status === 200) {
    return result.data;
  }
  return result;
}

export async function logoutUser() {
  const _api = window._vm.$http;
  const result = await _api.post("http://localhost:5001/api/v1/teacher/logout");

  return result;
}

export async function registerUser(payload) {
  const _api = window._vm.$http;
  const result = await _api.post(
    "http://localhost:5001/api/v1/teacher/registration",
    payload
  );

  if (result.status === 200) {
    return result.data;
  }

  return result;
}

export async function getCurrentUser() {
  const _api = window._vm.$http;
  const result = await _api.get("http://localhost:5001/api/v1/teacher/current");

  // if (result.status === 200) {
  //   return result.data;
  // }

  return result;
}
