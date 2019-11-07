import { shallowMount, createLocalVue } from "@vue/test-utils";
import App from "@/App.vue";
import Vuetify from "vuetify";
import Vuex from "vuex";

const localVue = createLocalVue();

localVue.use(Vuex);
localVue.use(Vuetify);

describe("App.vue", () => {
  let actions;
  let state;
  let store;

  beforeEach(() => {
    state = actions = {
      FETCHCURRENTUSER: jest.fn()
    };

    store = new Vuex.Store({
      modules: {
        user: {
          state: {
            loggedIn: true,
            drawer: true
          },
          actions
        }
      }
    });
  });

  it("has 'drawer' set to true", () => {
    const wrapper = shallowMount(App, { store, localVue });
    expect(wrapper.vm.drawer).toBeFalsy();
  });

  it.skip("dispatches 'FETCHCURRENTUSER' action with each update", () => {
    const wrapper = shallowMount(App, { store, localVue });
  });
});
