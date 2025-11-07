<template>
  <div class="w-full">
    <h1 class="text-3xl font-bold text-neutral-900 mb-8">Received Submissions</h1>
    
    <div v-if="error" class="text-red-500">{{ error }}</div>
    
    <div v-if="topicsWithSubmissions.length > 0" class="space-y-4">
      <div v-for="topic in topicsWithSubmissions" :key="topic.id" class="bg-white rounded-2xl shadow-lg overflow-hidden">
        <!-- Topic Header (Accordion Trigger) -->
        <button @click="toggleTopic(topic.id)" class="w-full text-left p-6 hover:bg-gray-50 focus:outline-none">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-xl font-bold text-neutral-900">{{ topic.title }}</h2>
              <p class="text-sm text-neutral-500 mt-1">
                {{ topic.stream.name }} &mdash; {{ topic.stream.academic_year }} - Semester {{ topic.stream.semester }}
              </p>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-sm font-semibold text-neutral-600">{{ topic.submissions.length }} submission(s)</span>
              <svg class="w-5 h-5 text-gray-500 transition-transform" :class="isTopicExpanded(topic.id) ? 'rotate-180' : ''" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </button>
        
        <!-- Expanded Content (Submissions List) -->
        <div v-if="isTopicExpanded(topic.id)" class="bg-gray-50 p-6 space-y-4">
          <div v-for="submission in topic.submissions" :key="submission.id" class="bg-white rounded-xl shadow-md p-4 flex flex-col">
            <!-- Student Name -->
            <p class="text-sm text-neutral-600 mb-2">From: <span class="font-semibold">{{ formatStudentName(submission.student) }}</span></p>

            <!-- Student Vision -->
            <p v-if="submission.student_vision" class="text-sm text-neutral-700 italic border-l-4 border-gray-200 pl-3 mb-4">"{{ submission.student_vision }}"</p>

            <div class="flex justify-between items-center mt-auto pt-3 border-t border-gray-100">
                <!-- Submitted Date -->
                <span class="text-xs text-neutral-500">Submitted: {{ formatDate(submission.created_at) }}</span>

                <div class="flex items-center gap-2">
                    <!-- Status Pill -->
                    <span class="font-bold rounded-full px-2 py-0.5 text-xs" :class="statusBgClass(submission.status)">
                        {{ submission.status.toUpperCase() }}
                    </span>
                    <!-- Approve/Reject buttons (if pending) -->
                    <template v-if="submission.status.toLowerCase() === 'pending'">
                        <button @click="reject(submission.id)" class="p-1.5 rounded-full text-red-800 bg-red-100 hover:bg-red-200 transition-colors group">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                          </svg>
                        </button>
                        <button @click="approve(submission.id)" class="p-1.5 rounded-full text-green-800 bg-green-100 hover:bg-green-200 transition-colors group">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                          </svg>
                        </button>
                    </template>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="!error" class="text-neutral-600 text-center py-10">No submissions received</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import coursesService from '@/services/courses';

const topicsWithSubmissions = ref([]);
const error = ref(null);
const expandedTopics = ref(new Set());

const toggleTopic = (topicId) => {
  if (expandedTopics.value.has(topicId)) {
    expandedTopics.value.delete(topicId);
  } else {
    expandedTopics.value.add(topicId);
  }
};

const isTopicExpanded = (topicId) => {
  return expandedTopics.value.has(topicId);
};

const fetchSubmissions = async () => {
  try {
    const response = await coursesService.getReceivedSubmissions();
    topicsWithSubmissions.value = response.data;
  } catch (err) {
    error.value = 'Failed to load submissions.';
    console.error(err);
  }
};

const approve = async (submissionId) => {
  try {
    await coursesService.approveSubmission(submissionId);
    fetchSubmissions(); // Refetch to show updated statuses
  } catch (err) {
    console.error('Failed to approve submission', err);
    alert('Approval failed. The topic might already be taken.');
  }
};

const reject = async (submissionId) => {
  try {
    await coursesService.rejectSubmission(submissionId);
    fetchSubmissions(); // Refetch to show updated statuses
  } catch (err) {
    console.error('Failed to reject submission', err);
    alert('Rejection failed.');
  }
};

// --- Helper Functions ---

function statusBgClass(status) {
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'approved') return 'bg-green-100 text-green-800';
  if (lowerStatus === 'rejected') return 'bg-red-100 text-red-800';
  if (lowerStatus === 'pending') return 'bg-yellow-100 text-yellow-800';
  return 'bg-gray-100 text-gray-800';
}

function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString(undefined, options);
}

function formatStudentName(student) {
  if (!student) return '';
  return `${student.last_name || ''} ${student.first_name || ''} ${student.middle_name || ''}`.trim();
}

onMounted(fetchSubmissions);
</script>
