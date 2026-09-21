import { createRouter, createWebHistory } from 'vue-router'; // Import the necessary functions from vue-router
import UserLogin from '@/components/UserLogin.vue'; // Import the UserLogin component
import LibrarianDashboard from '@/components/LibrarianDashboard.vue'; // Import the LibrarianDashboard component
import UserDashboard from '@/components/UserDashboard.vue'; // Import the UserDashboard component
import AddBook from '@/components/AddBook.vue'; // Import the AddBook component
import EditBook from '@/components/EditBook.vue'; // Import the EditBook component
import AddSection from '@/components/AddSection.vue'; // Import the AddSection component
import EditSection from '@/components/EditSection.vue'; // Import the EditSection component
import DeleteSection from '@/components/DeleteSection.vue'; // Import the DeleteSection component
import UserRegister from '@/components/UserRegister.vue'; // Import the UserRegister component
import BookRequests from '@/components/BookRequests.vue';


const routes = [
  {
    path: '/login',
    component: UserLogin
  },
  {
    path: '/librarian-dashboard',
    component: LibrarianDashboard,
    meta: { requiresAuth: true, role: 'librarian' }
  },
  {
    path: '/user-dashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/add-book',
    component: AddBook,
    meta: { requiresAuth: true, role: 'librarian' }
  },
  {
    path: '/edit-book/:bookId',
    name: 'editBook',
    component: EditBook,
    meta: { requiresAuth: true, role: 'librarian' }
  },
  {
    path: '/add-section',
    component: AddSection,
    meta: { requiresAuth: true, role: 'librarian' }
  },
  {
    path: '/edit-section/:sectionId',
    name: 'editSection',
    component: EditSection,
    meta: { requiresAuth: true, role: 'librarian' }
  },
  {
    path: '/delete-section',
    component: DeleteSection,
    meta: { requiresAuth: true, role: 'librarian' }
  },
  {
    path: '/book-requests',
    name: 'BookRequests',  // Ensure you're using the correct name here
    component: BookRequests,
  },
  
  {
    path: '/register',
    name: 'UserRegister',
    component: UserRegister
  },
  

  
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
