<template>
  <div id="app" class="flex flex-col min-h-screen bg-gray-100 text-neutral-900">
    <header v-if="authStore.isAuthenticated" class="bg-white shadow-md sticky top-0 z-10">
      <nav class="container mx-auto px-6 py-3 flex justify-between items-center">
        <div class="flex items-center gap-4">
          <RouterLink to="/" class="text-xl font-bold text-[#1062a3]">eKafedra Core</RouterLink>
          <span class="text-neutral-600 font-medium pt-0.5">{{ formatUserName(authStore.user) }}</span>
        </div>
        <div>
          <!-- Student Links -->
          <RouterLink v-if="authStore.isStudent" to="/my-streams" class="text-neutral-600 hover:text-[#1062a3] mr-4">My Streams</RouterLink>
          <RouterLink v-if="authStore.isStudent" to="/my-submissions" class="text-neutral-600 hover:text-[#1062a3] mr-4">My Submissions</RouterLink>

          <!-- Teacher Links -->
          <RouterLink v-if="authStore.isTeacher" to="/my-topics" class="text-neutral-600 hover:text-[#1062a3] mr-4">My Topics</RouterLink>
          <RouterLink v-if="authStore.isTeacher" to="/received-submissions" class="text-neutral-600 hover:text-[#1062a3] mr-4">Received</RouterLink>
          
          <!-- Common Links -->
          <RouterLink to="/change-password" class="text-neutral-600 hover:text-[#1062a3] mr-4">Change Password</RouterLink>
          <button @click="handleLogout" class="text-neutral-600 hover:text-[#1062a3]">Logout</button>
        </div>
      </nav>
    </header>
    <main class="grow flex flex-col container mx-auto p-6 md:p-8">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
};

const formatUserName = (user) => {
  if (!user) return '';
  const parts = [
    user.last_name || '',
    user.first_name || '',
    user.middle_name || ''
  ].filter(Boolean);
  return parts.join(' ');
};
</script>