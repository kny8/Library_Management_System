<template>
    <div>
      <h2>Delete Book</h2>
      <p>Are you sure you want to delete this book?</p>
      <button @click="deleteBook">Delete</button>
      <button @click="$router.push('/librarian/dashboard')">Cancel</button>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { useRoute, useRouter } from 'vue-router';
  
  export default {
    setup() {
      const route = useRoute();
      const router = useRouter();
  
      const deleteBook = async () => {
        try {
          await axios.post(`/librarian/delete_book/${route.params.bookId}`);
          router.push('/librarian/dashboard');
        } catch (error) {
          console.error('Failed to delete book:', error);
          alert('Failed to delete book.');
        }
      };
  
      return { deleteBook };
    }
  };
  </script>
  
  <style scoped>
  /* Add your styles here */
  </style>
  