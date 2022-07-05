<template>
    <nav class="breadcrumbs" v-if="getCrumbs().length">
        <ul class="">
            <li v-for="(crumb, key) in breadcrumbs" :key="key">
                <router-link :to="linkProp(crumb)" class="text-caption text-md-body-1 text-decoration-none text-sm-truncate">{{ crumb | crumbText }}</router-link>
                <span v-if="key < breadcrumbs.length - 1" class="mx-auto text-caption text-md-body-1">{{ separator }}</span>
            </li>
        </ul>
    </nav>
</template>
<script>
export default {
  name: 'Breadcrumb',
  props: {
    separator: {
      type: String,
      default: '/'
    },
    exclude_last: {
      type: Boolean,
      default: true
    }

  },
  computed: {
    breadcrumbs () {
      if (this.exclude_last === true) {
        return this.getCrumbs().slice(0, -1)
      } else {
        return this.getCrumbs().slice()
      }
    }
  },
  methods: {
    linkProp: function (crumb) {
      // If it's a named route, we'll base the route
      // off of that instead
      if (crumb.name || (crumb.handler && crumb.handler.name)) {
        return {
          name: crumb.name || crumb.handler.name,
          params: this.$route.params
        }
      }

      return {
        path: (crumb.handler && crumb.handler.fullPath)
          ? crumb.handler.fullPath
          : crumb.path,
        params: this.$route.params
      }
    },
    getCrumbs: function () {
      var crumbs = []

      var matched = this.$route.matched
      matched.forEach(function (route) {
        var hasBreadcrumb = route.meta && route.meta.breadcrumb
        if (hasBreadcrumb) {
          crumbs.push(route)
        }
      })
      return crumbs
    }
  },
  filters: {
    crumbText: function (crumb) {
      return crumb.meta.breadcrumb
    }
  }
}
</script>

<style scoped>
    ul {
        list-style: none;
        padding: 0;
        margin: 0;
        display: inline-block;
    }
    ul > li {
        display: inline-block;
    }
    .breadcrumbs {
    margin: 0;
    padding: 0;
    list-style: none;
    background-color: #f5f5f5;
    border-radius: 0.25rem;
    overflow: hidden;
    }
</style>
