<template>
  <div class="w-full">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-neutral-900">My Streams</h1>
      <div class="flex space-x-1 bg-gray-200 p-1 rounded-lg">
        <button 
          @click="setActiveTab('active')"
          :class="['px-4 py-1.5 text-sm font-semibold rounded-md transition-colors', activeTab === 'active' ? 'bg-white text-[#1062a3] shadow' : 'bg-transparent text-gray-600 hover:text-gray-800']"
        >
          Active
        </button>
        <button 
          @click="setActiveTab('archive')"
          :class="['px-4 py-1.5 text-sm font-semibold rounded-md transition-colors', activeTab === 'archive' ? 'bg-white text-[#1062a3] shadow' : 'bg-transparent text-gray-600 hover:text-gray-800']"
        >
          Archive
        </button>
      </div>
    </div>
    <div v-if="error" class="text-red-500">{{ error }}</div>
    <div v-if="streams.length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div 
        v-for="stream in streams" 
        :key="stream.id" 
        class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow flex flex-col"
      >
        <div class="grow">
          <h2 class="text-xl font-bold text-neutral-900 mb-3">{{ stream.name }}</h2>
          <div class="text-neutral-600 text-sm space-y-2">
            <p><strong>Specialty:</strong> {{ stream.specialty.name }} ({{ stream.specialty.code }})</p>
            <p><strong>Academic Year:</strong> {{ stream.academic_year }}</p>
            <p><strong>Course:</strong> {{ stream.course_number }}</p>
            <p><strong>Semester:</strong> {{ stream.semester }}</p>
          </div>
        </div>
        <div class="mt-5 pt-5 border-t">
          <RouterLink 
            :to="`/streams/${stream.id}/topics`" 
            class="font-semibold text-[#1062a3] hover:underline"
          >
            View Available Topics →
          </RouterLink>
        </div>
      </div>
    </div>
    <div v-else-if="!loading" class="text-neutral-600 text-center py-10 bg-gray-50 rounded-lg">
      <p>No {{ activeTab }} streams found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { RouterLink } from 'vue-router';
import coursesService from '@/services/courses';

const streams = ref([]);
const loading = ref(true);
const error = ref(null);
const activeTab = ref('active');

const fetchStreams = async () => {
  loading.value = true;
  error.value = null;
  try {
    const isActive = activeTab.value === 'active';
    const response = await coursesService.getMyStreams(isActive);
    streams.value = response.data;
  } catch (err) {
    error.value = 'Failed to load streams.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const setActiveTab = (tab) => {
  activeTab.value = tab;
};

watch(activeTab, fetchStreams);

onMounted(fetchStreams);
</script>
