<template>
  <div>
    <notification-banner v-if="showBanner" @close="closeBanner" />
    <virtual-panhandle />
    <top-menu />
    <game-grid :class="$style.grid" />
    <game-grid-hard :class="$style.grid" />
    <SearchDialog />
    <SearchDialogHard />
    <welcome-screen />
    <share-popup />
    <end-game />
    <end-game-hard />
  </div>
</template>

<script>
export default {
  name: 'IndexPage',
  data () {
    return {
      showBanner: false
    }
  },

  methods: {
    closeBanner () {
      this.showBanner = false
    }
  },
  // send a Google Analytics page view on page load
  mounted () {
    this.$gtm.trackView('/')
  }
}
</script>

<style module>
  .grid {
    margin-top: 0.7%;
  }
</style>
