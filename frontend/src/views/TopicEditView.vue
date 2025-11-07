<template>
  <div class="flex flex-col items-center">
    <h1 class="text-3xl font-bold text-neutral-900 mb-6">Edit Topic</h1>
    <TopicForm 
      v-if="topic"
      :initial-data="topic"
      @submit="handleUpdateTopic" 
      :is-submitting="isSubmitting" 
      :error="error" 
    />
    <div v-if="!topic && !loading" class="text-red-500 mt-4">Could not find topic to edit.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import TopicForm from '@/components/TopicForm.vue';
import coursesService from '@/services/courses';

const route = useRoute();
const router = useRouter();
const topic = ref(null);
const loading = ref(true);
const isSubmitting = ref(false);
const error = ref(null);

onMounted(async () => {
  const topicId = route.params.id;
  try {
    // We don't have a getTopicById endpoint, so we fetch all and find it.
    // This is not efficient, but works with the current API.
    // A dedicated `GET /api/courses/topics/<id>/` would be better.
    const response = await coursesService.getMyTopics();
    topic.value = response.data.find(t => t.id == topicId);
  } catch(err) {
      error.value = "Failed to load topic data.";
      console.error(err);
  } finally {
      loading.value = false;
  }
});

const handleUpdateTopic = async (topicData) => {
  isSubmitting.value = true;
  error.value = null;
  const topicId = route.params.id;
  try {
    await coursesService.updateTopic(topicId, topicData);
    router.push('/my-topics');
  } catch (err) {
    error.value = 'Failed to update topic.';
    console.error(err);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
