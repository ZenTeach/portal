import service_config from "@/service/service_config";
import axios from "axios";

const singleton = Symbol();
const singletonEnforcer = Symbol();

class ApiService {

    constructor(enforcer) {
        if (enforcer !== singletonEnforcer) {
            throw new Error('Cannot construct singleton');
        }

		this.session = axios.create(service_config);

		this.session.interceptors.response.use((response) => { return response },
			(response) => {
				// TODO: perform silent refresh
				// if (response.status == 401) {
				// }
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
