import service_config from "@/service/service_config";
import axios from "axios";
import createAuthRefreshInterceptor from "axios-auth-refresh";
import store from "../store";
import router from "../router";
const singleton = Symbol();
const singletonEnforcer = Symbol();
class ApiService {
  constructor(enforcer) {
    if (enforcer !== singletonEnforcer) {
      throw new Error("Cannot construct singleton");
    }

    this.session = axios.create(service_config);

    const silentRefreshLogic = failedRequest => {
      console.log("In Auth-Refresher");
      console.log("Encountered an error", failedRequest.config.url);
      console.log(failedRequest.config.url);
      return new Promise((resolve, _reject) => {
        if (failedRequest.status == 400 || failedRequest.status == 404) {
          const { message } = failedRequest.response.data;
          store.dispatch("app/TOGGLE_ERROR", message, { root: true });
          store.dispatch("user/SIGNOUT_USER", {}, { root: true });
          router.push({ name: "login" });
          resolve();
        } else {
          console.log("Refreshing...");
          this.session.post("/teacher/token/refresh").then(response => {
            console.log(response);
            if (response.status == 200) {
              console.log("Session Refreshed!");
              resolve(response);
            } else {
              const { message } = response.data;
              store.dispatch("app/TOGGLE_ERROR", message, { root: true });
              store.dispatch("user/SIGNOUT_USER", {}, { root: true });
              router.push({ name: "login" });
            }
          });
        }
      });
    };
    createAuthRefreshInterceptor(this.session, silentRefreshLogic, {
      statusCodes: [400, 401]
    });
  }

  static get instance() {
    if (!this[singleton]) {
      const instance = new ApiService(singletonEnforcer);
      this[singleton] = new Proxy(instance, {
        get: (obj, prop) => {
          return obj[prop];
        }
      });
    }

    return this[singleton];
  }

  async get(...params) {
    return Promise.resolve(this.session.get(...params));
  }

  async post(...params) {
    return Promise.resolve(this.session.post(...params));
  }

  async put(...params) {
    return Promise.resolve(this.session.put(...params));
  }

  async patch(...params) {
    return Promise.resolve(this.session.patch(...params));
  }

  async remove(...params) {
    return Promise.resolve(this.session.delete(...params));
  }
}
export default ApiService.instance;
