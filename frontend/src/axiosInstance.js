import axios from 'axios'
import Cookies from 'js-cookie'
import router from './router'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

 
api.interceptors.request.use(config => {
  const rawToken = Cookies.get('XSRF-TOKEN');

  console.log('[axios interceptor] XSRF-TOKEN:', rawToken);

  if (rawToken) {
    config.headers['X-CSRFToken'] = rawToken;
  }

  config.headers['Accept'] = 'application/json';
  config.headers['Content-Type'] = 'application/json';

  return config;
});
  

api.interceptors.response.use(
  response => response,
  error => {
    // Unauthorized so redirect
    if (error.response && (error.response.status === 401 || error.response.status === 400)) {
      console.warn('[axios interceptor] Unauthenticated — clearing storage and redirecting to login')

      // Clear tokens and user state from localStorage and sessionStorage
      localStorage.clear()
      sessionStorage.clear()

      // Remove accessible cookies
      document.cookie.split(';').forEach(cookie => {
        const eqPos = cookie.indexOf('=')
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
      })

      // Redirect to login
      router.push({ name: 'UserLogin' })
    }

    return Promise.reject(error)
  }
)



export default api