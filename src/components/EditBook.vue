<template>
  <div>
    <h2>Edit Book</h2>
    <form @submit.prevent="editBook">
      <div>
        <label for="name">Book Name:</label>
        <input v-model="book.name" id="name" type="text" required />
      </div>

      <div>
        <label for="authors">Authors:</label>
        <input v-model="book.authors" id="authors" type="text" required />
      </div>

      <div>
        <label for="section">Section:</label>
        <select v-model="book.section_id" id="section" required>
          <option v-for="section in sections" :key="section.id" :value="section.id">
            {{ section.name }}
          </option>
        </select>
      </div>

      <button type="submit">Save Changes</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const book = ref({ name: '', authors: '', section_id: '' });
    const sections = ref([]);

    const fetchBook = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/librarian/book/${route.params.bookId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        book.value = response.data;
      } catch (error) {
        console.error('Failed to fetch book:', error);
      }
    };

    const fetchSections = async () => {
      try {
        const response = await axios.get('http://localhost:5000/librarian/sections', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        sections.value = response.data.sections;
      } catch (error) {
        console.error('Failed to fetch sections:', error);
      }
    };

    const editBook = async () => {
      try {
        await axios.put(`http://localhost:5000/librarian/update_book/${route.params.bookId}`, book.value, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        router.push('/librarian-dashboard');
      } catch (error) {
        console.error('Failed to update book:', error);
        alert('Failed to update book.');
      }
    };

    onMounted(() => {
      fetchBook();
      fetchSections();
    });

    return {
      book,
      sections,
      editBook
    };
  }
};
</script>
