<template>
  <div class="flex flex-col items-center">
    <h1 class="text-3xl font-bold text-neutral-900 mb-6">Create New Topic</h1>
    <TopicForm 
      @submit="handleCreateTopic" 
      :is-submitting="isSubmitting" 
      :error="error" 
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import TopicForm from '@/components/TopicForm.vue';
import coursesService from '@/services/courses';

const router = useRouter();
const isSubmitting = ref(false);
const error = ref(null);

const handleCreateTopic = async (topicData) => {
  isSubmitting.value = true;
  error.value = null;
  try {
    await coursesService.createTopic(topicData);
    router.push('/my-topics');
  } catch (err) {
    error.value = 'Failed to create topic.';
    console.error(err);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
