<template>
  <div class="grow flex items-center justify-center">
    <div class="p-8 bg-white rounded-2xl shadow-xl w-full max-w-sm">
      <h1 class="text-2xl font-bold mb-6 text-center text-neutral-900">Change Password</h1>
      <form @submit.prevent="handleChangePassword">
        <div class="mb-4">
          <label for="new_password1" class="block mb-2 text-sm font-medium text-neutral-600">New Password</label>
          <input 
            type="password" 
            v-model="new_password1" 
            id="new_password1" 
            class="w-full px-3 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1062a3]"
            required 
          />
        </div>
        <div class="mb-6">
          <label for="new_password2" class="block mb-2 text-sm font-medium text-neutral-600">Confirm New Password</label>
          <input 
            type="password" 
            v-model="new_password2" 
            id="new_password2" 
            class="w-full px-3 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1062a3]"
            required
          />
        </div>
        <button 
          type="submit" 
          class="w-full bg-[#1062a3] text-white py-3 font-semibold rounded-xl hover:bg-opacity-90 active:bg-opacity-80 transition-colors"
        >
          Change Password
        </button>
        <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
        <p v-if="success" class="text-green-500 text-sm mt-4">{{ success }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const new_password1 = ref('');
const new_password2 = ref('');
const error = ref(null);
const success = ref(null);
const authStore = useAuthStore();

const handleChangePassword = async () => {
  error.value = null;
  success.value = null;
  if (new_password1.value !== new_password2.value) {
    error.value = 'Passwords do not match.';
    return;
  }
  try {
    await authStore.changePassword({ new_password1: new_password1.value, new_password2: new_password2.value });
    success.value = 'Password changed successfully!';
    new_password1.value = '';
    new_password2.value = '';
  } catch (err) {
    error.value = 'Failed to change password.';
    console.error(err);
  }
};
</script>
