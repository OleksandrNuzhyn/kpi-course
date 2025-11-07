<template>
  <form @submit.prevent="handleSubmit" class="p-8 bg-white rounded-lg shadow-lg w-full max-w-lg">
    <div class="mb-4">
      <label for="name" class="block mb-2 text-sm font-medium text-neutral-600">Topic Name</label>
      <input 
        type="text" 
        v-model="formData.title" 
        id="name" 
        class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-[#1062a3]"
        required 
      />
    </div>
    <div class="mb-4">
      <label for="description" class="block mb-2 text-sm font-medium text-neutral-600">Description</label>
      <textarea 
        v-model="formData.description" 
        id="description" 
        rows="4"
        class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-[#1062a3]"
        required
      ></textarea>
    </div>
    <div class="mb-6">
        <label for="stream" class="block mb-2 text-sm font-medium text-neutral-600">Stream</label>
        <select 
            v-model="formData.stream_id" 
            id="stream" 
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-[#1062a3]"
            required
        >
            <option disabled value="">Please select one</option>
            <option v-for="stream in streams" :key="stream.id" :value="stream.id">
                {{ stream.name }}
            </option>
        </select>
    </div>
    <button 
      type="submit" 
      class="w-full bg-[#1062a3] text-white py-2 rounded-lg hover:bg-opacity-90 active:bg-opacity-80 transition-colors"
      :disabled="isSubmitting"
    >
      {{ isSubmitting ? 'Submitting...' : 'Submit' }}
    </button>
    <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import coursesService from '@/services/courses';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ name: '', description: '', stream: '' }),
  },
  isSubmitting: Boolean,
  error: String,
});

const emit = defineEmits(['submit']);

const formData = reactive({
  title: '',
  description: '',
  stream_id: '',
});
const streams = ref([]);

watch(() => props.initialData, (newData) => {
  formData.title = newData.title || newData.name || '';
  formData.description = newData.description || '';
  // Handle both cases: `stream` as an object (on edit) or as an ID.
  formData.stream_id = newData.stream?.id || newData.stream || '';
}, { deep: true, immediate: true });


const fetchStreams = async () => {
    try {
        const response = await coursesService.getMyStreams();
        streams.value = response.data;
    } catch (err) {
        console.error("Failed to load streams for form", err);
    }
};

const handleSubmit = () => {
  emit('submit', formData);
};

onMounted(fetchStreams);
</script>