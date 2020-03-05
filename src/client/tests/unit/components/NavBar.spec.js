import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import NavBar from "@/components/NavBar.vue";
const localVue = createLocalVue();

localVue.use(Vuex);
describe("NavBar.vue", () => {
  let actions;
  let store;
  beforeEach(() => {
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
  });

  it("renders component", () => {
    const wrapper = shallowMount(NavBar, { store, localVue });
    expect(wrapper.isVueInstance()).toBe(true);
  });
});
