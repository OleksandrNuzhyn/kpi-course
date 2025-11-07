<template>
  <div class="grow flex items-center justify-center">
    <div class="p-8 bg-white rounded-2xl shadow-xl w-full max-w-sm">
      <h1 class="text-2xl font-bold mb-6 text-center text-neutral-900">Login</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label for="email" class="block mb-2 text-sm font-medium text-neutral-600">Email</label>
          <input 
            type="email" 
            v-model="email" 
            id="email" 
            class="w-full px-3 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1062a3]"
            required 
          />
        </div>
        <div class="mb-6">
          <label for="password" class="block mb-2 text-sm font-medium text-neutral-600">Password</label>
          <input 
            type="password" 
            v-model="password" 
            id="password" 
            class="w-full px-3 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1062a3]"
            required
          />
        </div>
        <button 
          type="submit" 
          class="w-full bg-[#1062a3] text-white py-3 font-semibold rounded-xl hover:bg-opacity-90 active:bg-opacity-80 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1062a3]"
        >
          Login
        </button>
        <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const email = ref('');
const password = ref('');
const error = ref(null);
const authStore = useAuthStore();

const handleLogin = async () => {
  error.value = null;
  try {
    await authStore.login({ email: email.value, password: password.value });
  } catch (err) {
    error.value = 'Failed to login. Please check your credentials.';
    console.error(err);
  }
};
</script>
