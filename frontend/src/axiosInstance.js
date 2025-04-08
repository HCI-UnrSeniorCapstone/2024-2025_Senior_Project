import axios from 'axios'
import Cookies from 'js-cookie'
// const backendHost = import.meta.env.VITE_APP_BACKEND_URL
// const backendPort = import.meta.env.VITE_APP_BACKEND_PORT
// const baseURL = `http://${backendHost}:${backendPort}`
// const backendUrl = this.$backendUrl

// console.log('API baseURL:', backendUrl)

const api = axios.create({
    // backendUrl,
    // baseURL: 'http://100.82.85.28:5002',
    baseURL: '/api',
  withCredentials: true,
})

// api.interceptors.request.use(config => {
//   const csrf = Cookies.get('XSRF-TOKEN')
//   if (csrf) {
//     config.headers['X-CSRFToken'] = csrf
//   }
//   return config
// })

api.interceptors.request.use(config => {
    const xsrfCookie = Cookies.get('XSRF-TOKEN')
    const rawToken = xsrfCookie?.split('.')[0]
  
    console.log('[axios interceptor] Cookie:', xsrfCookie)
    console.log('[axios interceptor] Raw Token:', rawToken)
  
    if (rawToken) {
      config.headers['X-CSRFToken'] = rawToken
    }
  
    return config
  })
  

export default api