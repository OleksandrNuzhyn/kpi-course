import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import ChangePasswordView from '../views/ChangePasswordView.vue';
import MyStreamsView from '../views/MyStreamsView.vue';
import StreamTopicsView from '../views/StreamTopicsView.vue';
import MyTopicsView from '../views/MyTopicsView.vue';
import TopicCreateView from '../views/TopicCreateView.vue';
import TopicEditView from '../views/TopicEditView.vue';
import MySubmissionsView from '../views/MySubmissionsView.vue';
import ReceivedSubmissionsView from '../views/ReceivedSubmissionsView.vue';
import SubmissionCreateView from '../views/SubmissionCreateView.vue';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    redirect: to => {
      const authStore = useAuthStore();
      if (authStore.isAuthenticated) {
        if (authStore.isStudent) return '/my-streams';
        if (authStore.isTeacher) return '/my-topics';
      }
      return '/login';
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/change-password',
    name: 'change-password',
    component: ChangePasswordView,
    meta: { requiresAuth: true },
  },
  {
    path: '/my-streams',
    name: 'my-streams',
    component: MyStreamsView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/streams/:streamId/topics',
    name: 'stream-topics',
    component: StreamTopicsView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/my-topics',
    name: 'my-topics',
    component: MyTopicsView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/topics/create',
    name: 'topic-create',
    component: TopicCreateView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/topics/edit/:id',
    name: 'topic-edit',
    component: TopicEditView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/my-submissions',
    name: 'my-submissions',
    component: MySubmissionsView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/received-submissions',
    name: 'received-submissions',
    component: ReceivedSubmissionsView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/topics/:topicId/submit',
    name: 'submission-create',
    component: SubmissionCreateView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser();
  }

  const { requiresAuth, roles } = to.meta;
  const { isAuthenticated, user } = authStore;

  if (requiresAuth) {
    if (!isAuthenticated) {
      return next('/login');
    }
    
    if (roles && !roles.includes(user.role.toLowerCase())) {
      if (authStore.isStudent) return next('/my-streams');
      if (authStore.isTeacher) return next('/my-topics');
      return next('/login');
    }
  }

  if (to.path === '/login' && isAuthenticated) {
    if (authStore.isStudent) return next('/my-streams');
    if (authStore.isTeacher) return next('/my-topics');
    return next('/');
  }

  next();
});

export default router;