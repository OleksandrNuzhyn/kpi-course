<template>
  <div>
    <h1 class="text-3xl font-bold text-neutral-900 mb-6">Topics for Stream</h1>
    <div v-if="error" class="text-red-500">{{ error }}</div>
    <div v-if="topics.length > 0" class="space-y-6">
      <div 
        v-for="topic in topics" 
        :key="topic.id"
        class="bg-white p-6 rounded-xl shadow-lg flex justify-between items-center"
      >
        <div>
            <h2 class="text-xl font-bold text-neutral-900">{{ topic.title }}</h2>
        </div>
        <RouterLink :to="`/topics/${topic.id}/submit`" class="ml-6 flex-shrink-0 bg-[#1062a3] text-white py-2 px-5 rounded-lg hover:bg-opacity-90 transition-colors">
            Submit Application
        </RouterLink>
      </div>
    </div>
    <div v-else-if="!loading" class="text-neutral-600 text-center py-10">No topics found for this stream.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import coursesService from '@/services/courses';

const topics = ref([]);
const loading = ref(true);
const error = ref(null);
const route = useRoute();

onMounted(async () => {
  const streamId = route.params.streamId;
  try {
    const response = await coursesService.getStreamTopics(streamId);
    topics.value = response.data;
  } catch (err) {
    error.value = 'Failed to load topics.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>
