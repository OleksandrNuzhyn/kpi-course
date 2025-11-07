import api from './api';

export default {
  login(credentials) {
    return api.post('/auth/login/', credentials);
  },
  logout() {
    return api.post('/auth/logout/');
  },
  changePassword(passwords) {
    return api.post('/auth/password/change/', passwords);
  },
};
