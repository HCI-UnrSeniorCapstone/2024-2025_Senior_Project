import api from '@/axiosInstance'
import { auth } from '@/stores/auth'

export async function pingServer() {
  const res = await api.get('/accounts/get_user_profile_info')
  const user = res.data

  auth.isAuthenticated = true
  auth.user = user

  return user
}
