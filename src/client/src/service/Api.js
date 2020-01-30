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

		this.session = axios.create(service_config);

		const silentRefreshLogic = failedRequest => {
			console.log("In Auth-Refresher")
			console.log("Encountered an error", failedRequest.config.url)
			console.log(failedRequest.config.url)
			// if (failedRequest.status === 422) {
			// 	store.dispatch("user/SIGNOUT_USER", {}, { root: true })
			// 	router.push({ name: "login"})
			// }
			return new Promise((resolve, _reject) => {
				console.log("Refreshing...")
				this.session.post("/teacher/token/refresh").then(response => {
					console.log(response)
					if(response.status == 200) {
						console.log("Session Refreshed!")
						resolve(response)
					}
					else {
							store.dispatch("user/SIGNOUT_USER", {}, { root: true })
							router.push({ name: "login"})
					}

				})
			})
		}
		createAuthRefreshInterceptor(this.session, silentRefreshLogic, {
			statusCodes: [401, 422, 403]
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

    async get(...params) {
		return Promise.resolve(this.session.get(...params))
	}

	async post(...params) {
		return Promise.resolve(this.session.post(...params))
	}

	async put(...params) {
		return Promise.resolve(this.session.put(...params))
	}

	async patch(...params) {
		return Promise.resolve(this.session.patch(...params))
	}

	async remove(...params) {
		return Promise.resolve(this.session.delete(...params))
	}
}
export default ApiService.instance;
