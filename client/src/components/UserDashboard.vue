<template>
  <div class="flex h-100">
      <activity-list />
  </div>
</template>

<script>
import ActivityList from './ActivityList.vue'

export default {
  name: 'UserDashboard',
  components: { ActivityList }
}
</script>
