<template>
  <div class="w-full">
    <h1 class="text-3xl font-bold text-neutral-900 mb-8">My Submissions</h1>
    <div v-if="error" class="text-red-500">{{ error }}</div>
    <div v-if="submissions.length > 0" class="space-y-6">
      <div v-for="submission in submissions" :key="submission.id" class="bg-white p-6 rounded-xl shadow-lg flex flex-col">
        <div class="grow mb-4">
          <h2 class="text-xl font-bold text-neutral-900 mb-2">{{ submission.topic.title }}</h2>
          <p v-if="submission.topic.description" class="text-neutral-600 max-w-prose">{{ submission.topic.description }}</p>

          <p v-if="submission.student_vision" class="mt-4 text-neutral-700 italic border-l-4 border-gray-200 pl-4">"{{ submission.student_vision }}"</p>
        </div>
        
        <div class="mt-5 pt-4 border-t text-sm">
          <div class="flex justify-between items-center mb-3">
            <span class="font-semibold text-neutral-700">{{ formatDate(submission.created_at) }}</span>
            <span class="px-2.5 py-1 text-xs font-bold rounded-full" :class="statusClass(submission.status)">
              {{ submission.status.toUpperCase() }}
            </span>
          </div>
          <div class="pt-3 border-t border-gray-100 space-y-1">
            <div class="flex justify-between items-center">
              <span class="text-gray-500 font-medium">Academic Year</span>
              <span class="font-semibold text-neutral-700">{{ submission.topic.stream.academic_year }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 font-medium">Semester</span>
              <span class="font-semibold text-neutral-700">{{ submission.topic.stream.semester }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="!loading" class="text-neutral-600 text-center py-10">You have not made any submissions.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import coursesService from '@/services/courses';

const submissions = ref([]);
const loading = ref(true);
const error = ref(null);

function statusClass(status) {
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'approved') {
    return 'bg-green-100 text-green-800';
  }
  if (lowerStatus === 'rejected') {
    return 'bg-red-100 text-red-800';
  }
  if (lowerStatus === 'pending') {
    return 'bg-yellow-100 text-yellow-800';
  }
  return 'bg-gray-100 text-gray-800';
}

onMounted(async () => {
  try {
    const response = await coursesService.getMySubmissions();
    submissions.value = response.data;
  } catch (err) {
    error.value = 'Failed to load submissions.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString(undefined, options);
}
</script>