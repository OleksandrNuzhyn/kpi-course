import api from './api';

export default {
  getMyStreams(isActive = true) {
    return api.get('/courses/streams/my/', { params: { is_active: isActive } });
  },
  
  getStreamTopics(streamId) {
    return api.get(`/courses/streams/${streamId}/topics/`);
  },

  getMyTopics(isActive = true) {
    return api.get('/courses/topics/my/', { params: { is_active: isActive } });
  },

  createTopic(topicData) {
    return api.post('/courses/topics/', topicData);
  },

  updateTopic(topicId, topicData) {
    return api.put(`/courses/topics/${topicId}/`, topicData);
  },

  deleteTopic(topicId) {
    return api.delete(`/courses/topics/${topicId}/delete/`);
  },

  getMySubmissions() {
    return api.get('/courses/submissions/my/');
  },

  createSubmission(submissionData) {
    return api.post('/courses/submissions/', submissionData);
  },

  cancelSubmission(submissionId) {
    return api.patch(`/courses/submissions/${submissionId}/`);
  },

  getReceivedSubmissions() {
    return api.get('/courses/submissions/received/');
  },

  approveSubmission(submissionId) {
    return api.post(`/courses/submissions/${submissionId}/approve/`);
  },

  rejectSubmission(submissionId) {
    return api.post(`/courses/submissions/${submissionId}/reject/`);
  }
};