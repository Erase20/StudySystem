<template>
  <div class="layout">
    <Header />
    <main class="main-content">
      <slot></slot>
    </main>
    <Footer />
    <Message />
  </div>
</template>

<script>
import Header from './Header.vue'
import Footer from './Footer.vue'
import Message from './Message.vue'

export default {
  components: {
    Header,
    Footer,
    Message
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}
</style>