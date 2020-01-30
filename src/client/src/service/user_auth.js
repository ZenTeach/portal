import Api from "@/service/Api"

export async function loginUser(payload) {
  const result = await Api.post(
    "/teacher/login",
    payload
	);
	// console.log("loginUser data", result)
  if (result.status === 200) {
    return result.data;
  }
  return result;
}

export async function logoutUser() {
  const result = await Api.post("/teacher/logout");
	// console.log("logoutUser data", result)
  return result;
}

export async function registerUser(payload) {
  const result = await Api.post(
    "/teacher/registration",
    payload
  );
	console.log("registerUser data", result)
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
