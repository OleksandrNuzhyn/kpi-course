<template>
  <div class="flex flex-col h-full w-full">
    <!-- Header -->
    <div class="flex flex-wrap gap-4 items-baseline justify-between mb-8">
      <div class="flex items-baseline gap-6">
        <h1 class="text-3xl font-bold text-neutral-900">My Topics</h1>
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
      <RouterLink to="/topics/create" class="bg-[#1062a3] text-white py-2 px-5 rounded-lg hover:bg-opacity-90 transition-colors ml-auto">Create Topic</RouterLink>
    </div>

    <!-- Content -->
    <div class="grow">
      <div v-if="error" class="text-red-500 p-4 bg-red-100 rounded-lg">{{ error }}</div>
      <div v-else-if="topics.length > 0" class="space-y-6">
        <div v-for="topic in topics" :key="topic.id" class="bg-white rounded-2xl shadow-lg flex flex-col">
          <!-- Main Content -->
          <div class="p-6 grow">
            <div class="flex justify-between items-start gap-4">
              <h2 class="text-xl font-bold text-neutral-900">{{ topic.title }}</h2>
              <span :class="statusBgClass(topic.status)" class="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full shrink-0">{{ topic.status }}</span>
            </div>
            <p class="mt-2 text-neutral-600 max-w-prose">{{ topic.description }}</p>
            
            <div class="mt-4 pt-4 border-t text-neutral-600 text-sm space-y-2">
              <p><strong>Stream:</strong> {{ topic.stream.name }}</p>
              <p><strong>Specialty:</strong> {{ topic.stream.specialty.name }} ({{ topic.stream.specialty.code }})</p>
              <p><strong>Academic Year:</strong> {{ topic.stream.academic_year }}</p>
              <p><strong>Course:</strong> {{ topic.stream.course_number }}</p>
              <p><strong>Semester:</strong> {{ topic.stream.semester }}</p>
            </div>
          </div>
          <!-- Actions -->
          <div class="bg-gray-50 rounded-b-2xl px-6 py-4 flex justify-end items-center gap-4">
            <RouterLink :to="`/topics/edit/${topic.id}`" class="font-semibold text-[#1062a3] hover:underline">Edit</RouterLink>
            <button @click="deleteTopic(topic.id)" class="font-semibold text-red-500 hover:underline">Delete</button>
          </div>
        </div>
      </div>
      <!-- Empty State -->
      <div v-else-if="!loading" class="h-full flex items-center justify-center">
        <div class="text-center bg-white rounded-2xl shadow-lg py-16 px-6">
          <h3 class="text-xl font-semibold text-neutral-800">No {{ activeTab }} topics have been created yet</h3>
          <p class="mt-2 text-neutral-500">Click the "Create Topic" button to get started.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { RouterLink } from 'vue-router';
import coursesService from '@/services/courses';

const topics = ref([]);
const loading = ref(true);
const error = ref(null);
const activeTab = ref('active');

const statusBgClass = (status) => {
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'taken') {
    return 'bg-red-100 text-red-800';
  }
  if (lowerStatus === 'available') {
    return 'bg-green-100 text-green-800';
  }
  return 'bg-gray-100 text-gray-800';
};

const fetchTopics = async () => {
  loading.value = true;
  error.value = null;
  try {
    const isActive = activeTab.value === 'active';
    const response = await coursesService.getMyTopics(isActive);
    topics.value = response.data;
  } catch (err) {
    error.value = 'Failed to load topics.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const setActiveTab = (tab) => {
  activeTab.value = tab;
};

watch(activeTab, fetchTopics);

onMounted(fetchTopics);

const deleteTopic = async (topicId) => {
  if (confirm('Are you sure you want to delete this topic?')) {
    try {
      await coursesService.deleteTopic(topicId);
      await fetchTopics(); // Refresh the list
    } catch (err) {
      alert('Failed to delete topic.');
      console.error(err);
    }
  }
};
</script>