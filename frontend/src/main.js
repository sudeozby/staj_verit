import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Yönlendiriciyi import ettik

const app = createApp(App)
app.use(router) // Sisteme router'ı kullanmasını söyledik
app.mount('#app')