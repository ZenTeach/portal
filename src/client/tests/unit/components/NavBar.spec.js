import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import Vuetify from "vuetify";
import NavBar from "@/components/NavBar.vue";
const localVue = createLocalVue();

localVue.use(Vuex);
// localVue.use(Vuetify);
describe("NavBar.vue", () => {
  let actions;
  let store;
  // let vuetify;
  beforeEach(() => {
    // jest.clearAllMocks();
    actions = {
      SIGNOUT_USER: jest.fn()
    };
    store = new Vuex.Store({
      modules: {
        user: {
          actions
        }
      }
    });
    // vuetify = new Vuetify();
  });

  it("renders component", () => {
    const wrapper = shallowMount(NavBar, { store, localVue });
    expect(wrapper.isVueInstance()).toBe(true);
  });
});
