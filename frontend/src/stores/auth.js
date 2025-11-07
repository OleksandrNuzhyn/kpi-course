import { defineStore } from 'pinia';
import authService from '@/services/auth';
import router from '@/router';
import api from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('authToken') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isStudent: (state) => state.user?.role?.toLowerCase() === 'student',
    isTeacher: (state) => state.user?.role?.toLowerCase() === 'teacher',
  },
  actions: {
    async login(credentials) {
      try {
        const response = await authService.login(credentials);
        const token = response.data.key;
        this.token = token;
        localStorage.setItem('authToken', token);
        await this.fetchUser();
        
        if (this.isStudent) {
          router.push('/my-streams');
        }
        else if (this.isTeacher) {
          router.push('/my-topics');
        }
        else {
          router.push('/'); 
        }
      }
      catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    async logout() {
      try {
        await authService.logout();
      }
      catch (error) {
        console.error('Logout failed, but clearing client-side session anyway:', error);
      }
      finally {
        this.token = null;
        this.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        router.push('/login');
      }
    },
    async fetchUser() {
      if (!this.token) return;
      try {
        const response = await api.get('/auth/user/');
        this.user = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      catch (error) {
        console.error('Failed to fetch user:', error);
        this.logout();
      }
    },
    async changePassword(passwords) {
        try {
            await authService.changePassword(passwords);
        } catch (error) {
            console.error('Password change failed:', error);
            throw error;
        }
    }
  },
});