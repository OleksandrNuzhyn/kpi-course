<template>
    <div class="flex flex-col items-center w-full">
        <div class="w-full max-w-2xl">
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-neutral-900">{{ topic.title }}</h1>
                <p v-if="topic.description" class="mt-2 text-lg text-neutral-600">{{ topic.description }}</p>
            </div>
            <form @submit.prevent="handleSubmit" class="p-8 bg-white rounded-2xl shadow-xl">
                <div class="mb-6">
                    <label for="student_vision" class="block mb-2 text-sm font-medium text-neutral-600">
                        Your Vision (Optional)
                    </label>
                    <textarea 
                        v-model="student_vision"
                        id="student_vision"
                        rows="6"
                        class="w-full px-3 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1062a3]"
                        placeholder="Briefly describe your vision for this topic, what you plan to research, or what technologies you intend to use."
                    ></textarea>
                </div>
                <button 
                    type="submit" 
                    class="w-full bg-[#1062a3] text-white py-3 font-semibold rounded-xl hover:bg-opacity-90 active:bg-opacity-80 transition-colors"
                    :disabled="isSubmitting"
                >
                    {{ isSubmitting ? 'Submitting...' : 'Submit Application' }}
                </button>
                <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import coursesService from '@/services/courses';

const route = useRoute();
const router = useRouter();

const topic = reactive({
    id: null,
    title: 'Loading...',
    description: '',
});
const student_vision = ref('');
const isSubmitting = ref(false);
const error = ref('');

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = '';
  try {
    const submissionData = {
      topic_id: topic.id,
      student_vision: student_vision.value,
    };
    await coursesService.createSubmission(submissionData);
    router.push('/my-submissions');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit application.';
    console.error(err);
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(async () => {
    const topicId = parseInt(route.params.topicId, 10);
    topic.id = topicId;

    try {
        const streamsResponse = await coursesService.getMyStreams();
        const streams = streamsResponse.data;
        let foundTopic = null;

        for (const stream of streams) {
            try {
                const topicsResponse = await coursesService.getStreamTopics(stream.id);
                const topicData = topicsResponse.data.find(t => t.id === topicId);
                if (topicData) {
                    foundTopic = topicData;
                    break;
                }
            } catch (e) {
                console.warn(`Could not check stream ${stream.id} for topic.`);
            }
        }

        if (foundTopic) {
            topic.title = foundTopic.title;
            topic.description = foundTopic.description;
        } else {
            topic.title = "Topic not found";
        }
    } catch(err) {
        console.error("Could not fetch topic details", err);
        topic.title = "Error loading topic"
    }
});
</script>
