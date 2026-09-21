<template>
  <div>
    <h2>Protected Page</h2>
    <p>Welcome, you have access to this protected page.</p>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'ProtectedPage',
  setup() {
    const router = useRouter();
    const isLoading = ref(true);
    const isAuthenticated = ref(false);

    onMounted(async () => {
      try {
        // Retrieve the JWT token from localStorage
        const token = localStorage.getItem('token');

        if (!token) {
          // Redirect to login if no token is found
          router.push('/login');
          return;
        }

        // Check the token by making an authenticated request
        await axios.get('/protected', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        isAuthenticated.value = true;
      } catch (error) {
        // Redirect to login if the token is invalid or the request fails
        router.push('/login');
      } finally {
        isLoading.value = false;
      }
    });

    return {
      isLoading,
      isAuthenticated
    };
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
