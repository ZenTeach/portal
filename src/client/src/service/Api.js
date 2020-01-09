import service_config from "@/service/service_config";
import axios from "axios";
import createAuthRefreshInterceptor from 'axios-auth-refresh';
const singleton = Symbol();
const singletonEnforcer = Symbol();
import store from '../store';
import router from '../router';
class ApiService {

    constructor(enforcer) {
        if (enforcer !== singletonEnforcer) {
            throw new Error('Cannot construct singleton');
        }

		this.session = axios(service_config);

		const authRefresher = (failedRequest) => {
			let current_user_role = store.modules['user'].state.current_user["role"]
			if (current_user_role == "Teacher") {
				this.session.post("/teacher/token/refresh").then(response => {
					if(response.status == 200) console.log("Session Refreshed!")
					else router.push("login")
				})
			}
			else {
				this.session.post("/teacher/student/refresh").then(response => {
					console.log("Session Refreshed!")
				})
			}
			return Promise.resolve();
		}
		createAuthRefreshInterceptor(this.session, authRefresher)

		this.session.interceptors.response.use((response) => {
			if(response.status == 422) return router.push("login")
		})
    }

    static get instance() {
        if (!this[singleton]) {
			let instance = new ApiService(singletonEnforcer);
			this[singleton] = new Proxy(instance, {
				get: (obj, prop) => {
					return obj[prop]
				}
			})
        }

        return this[singleton];
    }

    get(...params) {
		return this.session.get(...params);
	}

	post(...params) {
		return this.session.post(...params);
	}

	put(...params) {
		return this.session.put(...params);
	}

	patch(...params) {
		return this.session.patch(...params);
	}
    remove(...params) {
		return this.session.delete(...params);
	}
}
export default ApiService.instance;
