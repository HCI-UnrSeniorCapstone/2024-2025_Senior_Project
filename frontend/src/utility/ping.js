import api from '@/axiosInstance'

export function pingServer() {
  return api.get('/ping', {
    withCredentials: true,
    headers: {
      'Authentication-Token': localStorage.getItem('auth_token'),
    },
  })
}
